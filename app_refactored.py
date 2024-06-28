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
    if request.method != 'POST':
        return render_template('login.html')
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('instance/database.db')
    c = conn.cursor()
    c.execute(
        f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    )
    user = c.fetchone()
    conn.close()

    if not user:
        return render_template('login.html', error='Invalid username or password')

    session['logged_in'] = True
    session['username'] = username
    return redirect('/otp')

@app.route('/otp', methods=['GET', 'POST'])
def otp():
    if 'logged_in' not in session:
        return redirect('/login')
    if request.method == 'POST':
        otp = request.form['otp']
        if 'otp' in session and session['otp'] == otp:
            return redirect('/lookup')
        else:
            return render_template('otp.html', error='Invalid OTP')
    else:
        otp = str(random.randint(100, 999))
        session['otp'] = otp
        return render_template('otp.html', otp=otp)

@app.route('/lookup', methods=['GET', 'POST'])
def lookup():
    if 'logged_in' not in session:
        return redirect('/login')
    if request.method != 'POST':
        return render_template('lookup.html', username=session['username'])
    link = request.form['link']
    command = (
        f'nslookup {link}' if platform.system() == 'Windows' else f'dig {link}'
    )
    output = subprocess.check_output(command, shell=True, universal_newlines=True)
    return render_template('lookup.html', username=session['username'], output=output)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)