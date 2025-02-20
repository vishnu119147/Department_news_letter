from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'newsletter_platform'

mysql = MySQL(app)
bcrypt = Bcrypt(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hardcoded credentials for testing
        if username == 'admin' and password == 'admin123':
            session['loggedin'] = True
            session['id'] = 1  # Example ID
            session['username'] = 'admin'
            session['role'] = 'admin'
            flash('Admin login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
            
    return render_template('admin_login.html')


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = %s AND role = "user"', (username,))
        account = cursor.fetchone()
        if account and bcrypt.check_password_hash(account['password'], password):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['role'] = 'user'
            flash('User login successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('user_login.html')

@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO user (username, email, password, role) VALUES (%s, %s, %s, "user")', (username, email, hashed_password))
        mysql.connection.commit()
        flash('User registration successful', 'success')
        return redirect(url_for('user_login'))
    return render_template('user_signup.html')

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/research_projects')
def research_projects():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM events WHERE category = "research_projects"')
    events = cursor.fetchall()
    return render_template('research_projects.html', events=events)

@app.route('/student_achievements')
def student_achievements():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM events WHERE category = "student_achievements"')
    events = cursor.fetchall()
    return render_template('student_achievements.html', events=events)

@app.route('/faculty_publications')
def faculty_publications():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM events WHERE category = "faculty_publications"')
    events = cursor.fetchall()
    return render_template('faculty_publications.html', events=events)

@app.route('/upcoming_events')
def upcoming_events():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM events WHERE category = "upcoming_events"')
    events = cursor.fetchall()
    return render_template('upcoming_events.html', events=events)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if 'loggedin' in session and session['role'] == 'admin':
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            category = request.form['category']
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO events (title, description, category) VALUES (%s, %s, %s)', (title, description, category))
            mysql.connection.commit()
            flash('Event added successfully', 'success')
            return redirect(url_for(category))
        return render_template('add_event.html')
    else:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('index'))
    
@app.route('/contactus', methods=['GET', 'POST'])
def contact_us():
    return render_template('contactus.html')

if __name__ == '__main__':
    app.run(debug=True)
