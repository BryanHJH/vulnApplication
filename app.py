from flask import Flask, request, render_template, redirect, session
import sqlite3
import subprocess
import random
import platform

app = Flask(__name__)
app.secret_key = 'secret_key'

# SQLite database setup
conn = sqlite3.connect('instance/database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT NOT NULL,
             password TEXT NOT NULL)''')
# Insert a user record
c.execute("INSERT INTO users (username, password) VALUES ('admin', 'password')")
conn.commit()
conn.close()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('instance/database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'")
        user = c.fetchone()
        conn.close()
        
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect('/otp')
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/otp', methods=['GET', 'POST'])
def otp():
    if 'logged_in' in session:
        if request.method == 'POST':
            otp = request.form['otp']
            if 'otp' in session and session['otp'] == otp:
                return redirect('/lookup')
            else:
                return render_template('otp.html', error='Invalid OTP')
        else:
            otp = str(random.randint(1000, 9999))
            session['otp'] = otp
            return render_template('otp.html', otp=otp)
    else:
        return redirect('/login')

@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if 'logged_in' in session:
        if request.method == 'POST':
            link = request.form['link']
            if platform.system() == 'Windows':
                command = f'nslookup {link}'
            else:
                command = f'dig {link}'
            output = subprocess.check_output(command, shell=True, universal_newlines=True)
            return render_template('lookup.html', username=session['username'], output=output)
        else:
            return render_template('lookup.html', username=session['username'])
    else:
        return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)