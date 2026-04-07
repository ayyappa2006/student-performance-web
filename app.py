from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import os

app = Flask(__name__)
app.secret_key = "secret123"

# Load model
model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
model = pickle.load(open(model_path, 'rb'))

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['user'] = 'admin'
            return redirect(url_for('home'))
        else:
            return "Invalid Login ❌"
    return render_template('login.html')

# HOME
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

# PREDICT
@app.route('/predict', methods=['POST'])
def predict():
    study_hours = float(request.form['study_hours'])
    attendance = float(request.form['attendance'])

    prediction = model.predict([[study_hours, attendance]])[0]

    # Attendance status
    if attendance < 80:
        status = "Low ⚠️"
    elif attendance == 80:
        status = "Moderate ⚡"
    else:
        status = "Safe ✅"

    # Absent %
    absent = 100 - attendance

    # Study feedback
    if study_hours < 3:
        study_msg = "Study more 📚"
    elif study_hours <= 5:
        study_msg = "Good 👍"
    else:
        study_msg = "Excellent 🔥"

    return render_template('index.html',
                           prediction_text=f"Predicted Score: {prediction:.2f}",
                           attendance_status=status,
                           absent=absent,
                           study_msg=study_msg)

if __name__ == "__main__":
    app.run()
