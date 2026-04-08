from flask import Flask, render_template, request, redirect, session
import pickle
import os
import sqlite3
import numpy as np

app = Flask(__name__)
app.secret_key = "secret123"

# ------------------ MODEL LOAD ------------------
model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
model = pickle.load(open(model_path, 'rb'))

# ------------------ DATABASE ------------------
db_path = os.path.join(os.path.dirname(__file__), 'students.db')

def init_db():
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university TEXT,
            study_hours REAL,
            attendance REAL,
            score REAL,
            status TEXT
        )
    ''')
    conn.close()

init_db()

# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == "sai" and request.form['password'] == "0000":
            session['user'] = request.form['username']
            return redirect('/')
        else:
            return "Invalid Login ❌"
    return render_template('login.html')

# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ------------------ HOME ------------------
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect('/login')

# ------------------ PREDICT ------------------
@app.route('/predict', methods=['POST'])
def predict():
    university = request.form['university']
    study_hours = float(request.form['study_hours'])
    attendance = float(request.form['attendance'])

    prediction = model.predict(np.array([[study_hours, attendance]]))[0]

    # Attendance rule
    if attendance < 75:
        status = "Not Eligible ❌"
        color = "red"
    elif attendance < 85:
        status = "Warning ⚠️"
        color = "orange"
    else:
        status = "Eligible ✅"
        color = "green"

    absent = 100 - attendance

    # Study feedback
    if study_hours < 3:
        study_msg = "Study more 📚"
    elif study_hours <= 5:
        study_msg = "Good 👍"
    else:
        study_msg = "Excellent 🔥"

    # Save to DB
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO records (university, study_hours, attendance, score, status) VALUES (?, ?, ?, ?, ?)",
        (university, study_hours, attendance, prediction, status)
    )
    conn.commit()
    conn.close()

    return render_template('index.html',
        prediction_text=f"{prediction:.2f}",
        attendance_status=status,
        status_color=color,
        absent=absent,
        study_msg=study_msg,
        university=university
    )

# ------------------ HISTORY ------------------
@app.route('/history')
def history():
    conn = sqlite3.connect(db_path)
    data = conn.execute("SELECT * FROM records").fetchall()
    conn.close()
    return render_template('history.html', records=data)

# ------------------ ADMIN ------------------
@app.route('/admin')
def admin():
    conn = sqlite3.connect(db_path)
    data = conn.execute("SELECT * FROM records").fetchall()
    conn.close()

    total = len(data)
    avg = sum([row[3] for row in data]) / total if total else 0

    return render_template('admin.html',
                           total=total,
                           avg=round(avg, 2))

# ------------------ RUN ------------------
if __name__ == "__main__":
    app.run(debug=True)
