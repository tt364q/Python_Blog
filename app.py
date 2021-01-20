
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from data import Articles
# from flask_mysqldb import MySQL
# import MySQLdb
# import mysql
# import mysql.connector
from flaskext.mysql import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt



app = Flask(__name__)


# config mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '123456'
app.config['MYSQL_DB'] = 'myblogapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
mysql.init_app(app)







Articles = Articles()
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = Articles)

@app.route('/article/<string:id>/')
def article(id):
    return render_template('article.html', id=id)

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')


@app.route('/register', methods =['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # create cursor
        cur = mysql.connection.cursor()
        # cur = mysql.get_db().cursor()
        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))

        # commit to DB
        mysql.connection.commit()

        # close connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
        
        # return render_template('register.html')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password_candidate = request.form['password']

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0: 
            data = cur.fetchone()
            password = data['password']

            if sha256_crypt.verify(password_candidate, password):
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))

            else: 
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else: 
            error = 'Username not found'
            return render_template('login.html', error=error)
            

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():        
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)