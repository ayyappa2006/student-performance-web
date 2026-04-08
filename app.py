from flask import Flask, render_template, request
import pickle, os, sqlite3, numpy as np

app = Flask(__name__)

# ---------------- MODEL ----------------
model = pickle.load(open('model.pkl', 'rb'))

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('students.db')
    conn.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        university TEXT,
        study_hours REAL,
        attendance REAL,
        score REAL,
        status TEXT
    )
    ''')
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- PREDICT ----------------
@app.route('/predict', methods=['POST'])
def predict():

    email = request.form['email']
    university = request.form['university']
    study_hours = float(request.form['study_hours'])
    attendance = float(request.form['attendance'])

    prediction = model.predict(np.array([[study_hours, attendance]]))[0]

    # 🎓 UNIVERSITY RULES
    if university == "Saveetha University":
        min_attendance = 80
    else:
        min_attendance = 75

    # STATUS
    if attendance < min_attendance:
        status = "Not Eligible ❌"
        color = "red"
    elif attendance < (min_attendance + 10):
        status = "Warning ⚠️"
        color = "orange"
    else:
        status = "Eligible ✅"
        color = "green"

    # ABSENT
    absent = 100 - attendance

    # SMART SUGGESTION
    if attendance < min_attendance:
        needed = round(min_attendance - attendance, 2)
        suggestion = f"Increase attendance by {needed}% to be eligible"
    else:
        suggestion = "You are eligible for exams 🎉"

    # CLASSES CALCULATION
    total_classes = 100
    attended = (attendance / 100) * total_classes
    required = (min_attendance / 100) * total_classes

    classes_needed = int(required - attended) if attended < required else 0

    # SAVE DB
    conn = sqlite3.connect('students.db')
    conn.execute(
        "INSERT INTO records (email, university, study_hours, attendance, score, status) VALUES (?,?,?,?,?,?)",
        (email, university, study_hours, attendance, prediction, status)
    )
    conn.commit()
    conn.close()

    return render_template('index.html',
        prediction_text=f"{prediction:.2f}",
        attendance_status=status,
        status_color=color,
        absent=absent,
        university=university,
        suggestion=suggestion,
        classes_needed=classes_needed
    )

# ---------------- HISTORY ----------------
@app.route('/history')
def history():
    conn = sqlite3.connect('students.db')
    data = conn.execute("SELECT * FROM records").fetchall()
    conn.close()
    return render_template('history.html', records=data)

# ---------------- ADMIN ----------------
@app.route('/admin')
def admin():
    conn = sqlite3.connect('students.db')
    data = conn.execute("SELECT * FROM records").fetchall()
    conn.close()

    total = len(data)
    avg = sum([row[4] for row in data]) / total if total else 0

    return render_template('admin.html',
                           total=total,
                           avg=round(avg, 2))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
