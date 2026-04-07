import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# Sample dataset
data = {
    'study_hours': [1,2,3,4,5,6,7,8],
    'attendance': [50,60,65,70,75,80,85,90],
    'score': [35,40,50,55,65,70,80,90]
}

df = pd.DataFrame(data)

# Features and target
X = df[['study_hours','attendance']]
y = df['score']

# Train model
model = LinearRegression()
model.fit(X, y)

# Save model
pickle.dump(model, open('model.pkl','wb'))

print("Model created successfully!")