from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import os
import secrets

app = Flask(__name__, template_folder='templates')

# Generate a random 32-byte (256-bit) hexadecimal key
secret_key = secrets.token_hex(32)

# Set the generated key as the Flask app's secret key
app.secret_key = secret_key
print("Generated Secret Key:", secret_key)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Wedemboyz@2002'
app.config['MYSQL_DB'] = 'stack'

mysql = MySQL(app)

# Define the directory path for CSS, JS, and image files
file_directory = os.path.abspath(os.path.dirname(__file__))

# Check for session authentication before accessing these routes
def check_authentication(route_function):
    def wrapper(*args, **kwargs):
        if 'loggedin' in session:
            return route_function(*args, **kwargs)
        else:
            return render_template('login.html', message="For accessing the ChatBot, you need to login or signup.")
    return wrapper

@app.route('/css/<path:filename>')
def css(filename):
    return send_from_directory(os.path.join(file_directory, 'css'), filename)

@app.route('/js/<path:filename>')
def js(filename):
    return send_from_directory(os.path.join(file_directory, 'js'), filename)

@app.route('/img/<path:filename>')
def img(filename):
    return send_from_directory(os.path.join(file_directory, 'img'), filename)

@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('index.html', username=session['name'])
    else:
        return render_template('index.html')  # If not logged in, render the home page without the username


# Accessible even if not logged in
@app.route('/about')
def about():
    if 'loggedin' in session:
        return render_template('about.html', username=session['name'])
    else:
        return redirect(url_for('login', next=request.endpoint))

# Accessible even if not logged in
@app.route('/contact')
def contact():
    if 'loggedin' in session:
        return render_template('contact.html', username=session['name'])
    else:
        return redirect(url_for('login'))


# Accessible even if not logged in
@app.route('/courses')
def courses():
    return render_template('courses.html', username=session.get('name'))

# Check for session authentication before accessing these routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return render_template('index.html', message=message)
        else:
            message = 'Invalid email or password. Please try again.'
    return render_template('login.html', message=message)

# Add route for the logout functionality
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('home'))

def is_valid_email(email):
    return re.match(r'[^@]+@[^@]+\.[^@]+', email)

# Accessible even if not logged in
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if not userName or not password or not email:
            message = 'Please fill out all the fields.'
        elif not is_valid_email(email):
            message = 'Invalid email address.'
        else:
            cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
            account = cursor.fetchone()
            if account:
                message = 'Account already exists. Please login or use a different email.'
            else:
                cursor.execute('INSERT INTO user VALUES (NULL, %s, %s, %s)', (userName, email, password))
                mysql.connection.commit()
                message = 'You have successfully registered!'
    return render_template('register.html', message=message)

if __name__ == "__main__":
    app.run(debug=True)
