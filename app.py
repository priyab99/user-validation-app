from flask import Flask, render_template_string, request, redirect, session
import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Connect to PostgreSQL
db = psycopg2.connect(
    host="dpg-d0oqt0muk2gs738vqnr0-a",
    dbname="flaskdb_xbfr",
    user="flaskdb_xbfr_user",
    password="UCty7HeGMSg64NLM0EDlcL7ljbkqnlW6",
    port="5432"
)
cursor = db.cursor()

# Create table with unique constraint
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255)
);
""")
db.commit()

HTML_STYLE = """
<style>
    body { font-family: 'Segoe UI'; background: linear-gradient(to right, #e3f2fd, #ffffff); display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
    .container { background: white; padding: 40px; border-radius: 16px; box-shadow: 0 15px 25px rgba(0,0,0,0.1); width: 320px; animation: fadeIn 0.5s ease-in-out; text-align: center; }
    h2 { color: #333; margin-bottom: 20px; }
    input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 16px; }
    input[type="submit"] { background-color: #007bff; color: white; border: none; cursor: pointer; }
    input[type="submit"]:hover { background-color: #0056b3; }
    p, a { font-size: 14px; color: #333; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .error { color: red; font-size: 14px; margin: 5px 0; }
    .success { color: green; font-size: 14px; margin: 5px 0; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }
</style>
"""

@app.route('/')
def index():
    return render_template_string(HTML_STYLE + '''
    <div class="container">
        <h2>Register</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form action="/register" method="post">
            <input name="username" placeholder="Username" required><br>
            <input name="password" type="password" placeholder="Password (min 6 chars)" required><br>
            <input type="submit" value="Register">
        </form>
        <p>Already registered? <a href="/login">Login here</a></p>
    </div>
    ''', error=session.pop('error', None))

@app.route('/login')
def login_page():
    return render_template_string(HTML_STYLE + '''
    <div class="container">
        <h2>Login</h2>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form action="/login" method="post">
            <input name="username" placeholder="Username" required><br>
            <input name="password" type="password" placeholder="Password" required><br>
            <input type="submit" value="Login">
        </form>
    </div>
    ''', error=session.pop('error', None))

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username'].strip()
    password = request.form['password']

    if not username or not password:
        session['error'] = "Username and password cannot be empty."
        return redirect('/')

    if len(password) < 6:
        session['error'] = "Password must be at least 6 characters."
        return redirect('/')

    hashed_pw = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        db.commit()
        return redirect("/login")
    except psycopg2.Error as e:
        if "unique" in str(e).lower():
            session['error'] = "Username already exists. Try another one."
        else:
            session['error'] = "Registration error. Try again."
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password']

    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()

    if row and check_password_hash(row[0], password):
        return render_template_string(HTML_STYLE + '''
        <div class="container">
            <h2>Login Successful ✅</h2>
            <p><a href="/">Back to Home</a></p>
        </div>
        ''')
    else:
        session['error'] = "Invalid username or password."
        return redirect("/login")

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
