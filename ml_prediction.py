import joblib
import os
import numpy as np

# Get the directory where this script is located (E:\Development\server)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the possible paths where your model might be
possible_paths = [
    os.path.join(BASE_DIR, 'model', 'irrigation_model.pkl'),       # server/model/
    os.path.join(BASE_DIR, '..', 'model', 'irrigation_model.pkl'),  # Development/model/
    os.path.join(BASE_DIR, 'irrigation_model.pkl')                 # server/ (same folder)
]

MODEL_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        MODEL_PATH = path
        break

if MODEL_PATH:
    print(f"--- Successfully found model at: {MODEL_PATH} ---")
    model = joblib.load(MODEL_PATH)
else:
    print("--- ERROR: irrigation_model.pkl not found in any expected folder! ---")
    # This will prevent the crash but you must put the file in one of the paths above
    model = None 

def predict_moisture(sensor_data):
    if model is None:
        return "Model Error"
    
    try:
        # Match your training features: N, P, K, temp, hum, ph, rain
        features = np.array([[
            sensor_data.get('N', 50),
            sensor_data.get('P', 50),
            sensor_data.get('K', 50),
            sensor_data.get('temperature_in_C', 25),
            sensor_data.get('humidity', 50),
            sensor_data.get('phValue', 7.0),
            sensor_data.get('rainfall', 100)
        ]])
        prediction = model.predict(features)
        return round(float(prediction[0]), 2)
    except Exception as e:
        print(f"Prediction logic error: {e}")
        return 0.0