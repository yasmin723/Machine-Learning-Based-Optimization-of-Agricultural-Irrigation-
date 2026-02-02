import joblib
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATHS = [
    os.path.join(BASE_DIR, "model", "irrigation_model.pkl"),
    os.path.join(BASE_DIR, "..", "model", "irrigation_model.pkl"),
    os.path.join(BASE_DIR, "irrigation_model.pkl")
]

model = None
for path in MODEL_PATHS:
    if os.path.exists(path):
        model = joblib.load(path)
        print(f"ML Model Loaded From: {path}")
        break

if model is None:
    print("WARNING: ML Model not found. Predictions will fail.")

def predict_moisture(sensor_data):
    """
    Predict optimal soil moisture using trained ML model
    """
    if model is None:
        return 0.0

    try:
        features = np.array([[
            sensor_data.get("N", 50),
            sensor_data.get("P", 50),
            sensor_data.get("K", 50),
            sensor_data.get("temperature_in_C", 25),
            sensor_data.get("humidity", 60),
            sensor_data.get("phValue", 6.5),
            sensor_data.get("rainfall", 120)
        ]])

        prediction = model.predict(features)
        return round(float(prediction[0]), 2)

    except Exception as e:
        print("Prediction Error:", e)
        return 0.0
