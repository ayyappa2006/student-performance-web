from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import os

app = Flask(__name__)
app.secret_key = "secret123"

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
            return "Invalid Login"

    return render_template('login.html')

# HOME (Protected)
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

# PREDICTION
@app.route('/predict', methods=['POST'])
def predict():
    study_hours = float(request.form['study_hours'])
    attendance = float(request.form['attendance'])

    prediction = model.predict([[study_hours, attendance]])[0]

    return render_template('index.html',
                           prediction_text=f"Predicted Score: {prediction:.2f}")

if __name__ == "__main__":
    app.run()
