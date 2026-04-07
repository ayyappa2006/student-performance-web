from flask import Flask, render_template, request
import pickle

app = Flask(__name__)

# Load model
model = pickle.load(open('model.pkl','rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    study_hours = float(request.form['study_hours'])
    attendance = float(request.form['attendance'])

    prediction = model.predict([[study_hours, attendance]])[0]

    return render_template('index.html',
                           prediction_text=f"Predicted Score: {prediction:.2f}")

if __name__ == "__main__":
    app.run()