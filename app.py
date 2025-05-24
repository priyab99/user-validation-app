from flask import Flask, render_template_string, request, redirect, url_for
import psycopg2

app = Flask(__name__)

db = psycopg2.connect(
    host="dpg-d0oqt0muk2gs738vqnr0-a",
    dbname="flaskdb_xbfr",
    user="flaskdb_xbfr_user",
    password="UCty7HeGMSg64NLM0EDlcL7ljbkqnlW6",
    port="5432"
)
cursor = db.cursor()

# Create users table with unique username
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username VARCHAR(50) PRIMARY KEY,
        password VARCHAR(100)
    );
""")
db.commit()

HTML_STYLE = """
<style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(to right, #e3f2fd, #ffffff); display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .container { background: #ffffff; padding: 40px; border-radius: 16px; box-shadow: 0 15px 25px rgba(0,0,0,0.1); width: 320px; animation: fadeIn 0.5s ease-in-out; text-align: center; }
    h2 { color: #333; margin-bottom: 20px; }
    input { width: 100%; padding: 12px 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; }
    input[type="submit"] { background-color: #007bff; color: white; border: none; transition: background-color 0.3s ease; cursor: pointer; }
    input[type="submit"]:hover { background-color: #0056b3; }
    p, a { font-size: 14px; color: #333; text-decoration: none; }
    a:hover { text-decoration: underline; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>
"""

@app.route('/')
def index():
    return HTML_STYLE + '''
    <div class="container">
        <h2>Register</h2>
        <form action="/register" method="post">
            <input name="username" placeholder="Username" required><br>
            <input name="password" type="password" placeholder="Password (min 8 chars)" required><br>
            <input type="submit" value="Register">
        </form>
        <p>Already registered? <a href="/login">Login here</a></p>
    </div>
    '''

@app.route('/login')
def login_page():
    return HTML_STYLE + '''
    <div class="container">
        <h2>Login</h2>
        <form action="/login" method="post">
            <input name="username" placeholder="Username" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <input type="submit" value="Login">
        </form>
        <p><a href="/forgot">Forgot Password?</a></p>
    </div>
    '''

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if len(password) < 8:
        return HTML_STYLE + f'''
        <div class="container">
            <h2>❌ Password too short!</h2>
            <p><a href="/">Back to Register</a></p>
        </div>
        '''
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        return redirect("/login")
    except psycopg2.errors.UniqueViolation:
        db.rollback()
        return HTML_STYLE + f'''
        <div class="container">
            <h2>❌ Username already taken!</h2>
            <p><a href="/">Back to Register</a></p>
        </div>
        '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    if cursor.fetchone():
        return HTML_STYLE + f'''
        <div class="container">
            <h2>✅ Login Successful</h2>
            <p><a href="/">Home</a></p>
        </div>
        '''
    else:
        return HTML_STYLE + f'''
        <div class="container">
            <h2>❌ Invalid credentials</h2>
            <p><a href="/login">Try again</a></p>
        </div>
        '''

@app.route('/forgot')
def forgot_page():
    return HTML_STYLE + '''
    <div class="container">
        <h2>Reset Password</h2>
        <form action="/forgot" method="post">
            <input name="username" placeholder="Username" required><br>
            <input name="new_password" type="password" placeholder="New Password" required><br>
            <input type="submit" value="Reset">
        </form>
        <p><a href="/login">Back to Login</a></p>
    </div>
    '''

@app.route('/forgot', methods=['POST'])
def forgot():
    username = request.form['username']
    new_password = request.form['new_password']

    if len(new_password) < 8:
        return HTML_STYLE + '''
        <div class="container">
            <h2>❌ Password must be at least 8 characters.</h2>
            <p><a href="/forgot">Try again</a></p>
        </div>
        '''

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    if cursor.fetchone():
        cursor.execute("UPDATE users SET password=%s WHERE username=%s", (new_password, username))
        db.commit()
        return HTML_STYLE + '''
        <div class="container">
            <h2>✅ Password updated successfully!</h2>
            <p><a href="/login">Go to Login</a></p>
        </div>
        '''
    else:
        return HTML_STYLE + '''
        <div class="container">
            <h2>❌ Username not found!</h2>
            <p><a href="/forgot">Try again</a></p>
        </div>
        '''

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
