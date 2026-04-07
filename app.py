from flask import Flask, render_template, request, redirect, url_for, session
import pickle, os, sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Load model
model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
model = pickle.load(open(model_path, 'rb'))

# DB INIT
def init_db():
    conn = sqlite3.connect('students.db')
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

# LOGIN
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['username']=="admin" and request.form['password']=="1234":
            session['user']='admin'
            return redirect('/')
        else:
            return "Invalid Login ❌"
    return render_template('login.html')

# HOME
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect('/login')

# PREDICT
@app.route('/predict', methods=['POST'])
def predict():
    university = request.form['university']
    study_hours = float(request.form['study_hours'])
    attendance = float(request.form['attendance'])

    prediction = model.predict([[study_hours, attendance]])[0]

    # RULE
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

    if study_hours < 3:
        study_msg = "Study more 📚"
    elif study_hours <= 5:
        study_msg = "Good 👍"
    else:
        study_msg = "Excellent 🔥"

    # SAVE TO DB
    conn = sqlite3.connect('students.db')
    conn.execute("INSERT INTO records (university, study_hours, attendance, score, status) VALUES (?,?,?,?,?)",
                 (university, study_hours, attendance, prediction, status))
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

# HISTORY
@app.route('/history')
def history():
    conn = sqlite3.connect('students.db')
    data = conn.execute("SELECT * FROM records").fetchall()
    conn.close()
    return render_template('history.html', records=data)

if __name__ == "__main__":
    app.run()
