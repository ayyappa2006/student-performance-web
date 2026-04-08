from flask import Flask, render_template, request
import pickle, numpy as np

app = Flask(__name__)

# Load model
model = pickle.load(open('model.pkl', 'rb'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():

    
    university = request.form['university']
    study_hours = float(request.form['study_hours'])
    attendance = float(request.form['attendance'])

    # Score (limit 0–100)
    prediction = model.predict(np.array([[study_hours, attendance]]))[0]
    score = max(0, min(100, round(prediction, 2)))

    # University rules
    if university == "Saveetha University":
        min_attendance = 80
    else:
        min_attendance = 75

    # Status
    if attendance < min_attendance:
        status = "Not Eligible ❌"
        color = "red"
    elif attendance < (min_attendance + 10):
        status = "Warning ⚠️"
        color = "orange"
    else:
        status = "Eligible ✅"
        color = "green"

    # Absent
    absent = round(100 - attendance, 2)

    # Suggestion
    if attendance < min_attendance:
        needed = round(min_attendance - attendance, 2)
        suggestion = f"You need {needed}% more attendance"
    else:
        suggestion = "You are safe for exams 🎉"

    # Classes needed
    total_classes = 100
    attended = (attendance / 100) * total_classes
    required = (min_attendance / 100) * total_classes
    classes_needed = int(required - attended) if attended < required else 0

    # 🔥 FUTURE PREDICTION FEATURE
    miss_classes = 3
    attend_classes = 5

    future_miss = max(0, round(attendance - (miss_classes * 1), 2))
    future_attend = min(100, round(attendance + (attend_classes * 1), 2))

    return render_template('index.html',
        score=score,
        attendance=attendance,
        absent=absent,
        status=status,
        color=color,
        suggestion=suggestion,
        classes_needed=classes_needed,
        future_miss=future_miss,
        future_attend=future_attend
    )

if __name__ == "__main__":
    app.run(debug=True)
