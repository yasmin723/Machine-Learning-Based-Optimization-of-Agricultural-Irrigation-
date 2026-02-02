import os
import random
import firebase_admin
from firebase_admin import credentials, db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")
DATABASE_URL = "https://irrigation-control-d5ac5-default-rtdb.firebaseio.com"

USING_REAL_HARDWARE = False

# ✅ DEMO MODE MOTOR MEMORY
DEMO_MOTOR_STATE = 0

if os.path.exists(CERT_PATH):
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(CERT_PATH)
            firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
        USING_REAL_HARDWARE = True
        print("✅ Firebase Connected")
    except Exception as e:
        print("⚠️ Firebase Error:", e)

def get_sensor_data():
    global DEMO_MOTOR_STATE

    if USING_REAL_HARDWARE:
        ref = db.reference("test")
        data = ref.get()
        if data:
            if "motor" not in data:
                data["motor"] = 0
            return data

    # ✅ DEMO DATA WITH PERSISTENT MOTOR STATE
    return {
        "temperature_in_C": round(random.uniform(24, 30), 1),
        "humidity": round(random.uniform(50, 70), 1),
        "moisture": round(random.uniform(30, 85), 1),
        "phValue": round(random.uniform(6.5, 7.2), 2),
        "N": random.randint(40, 60),
        "P": random.randint(40, 60),
        "K": random.randint(40, 60),
        "motor": DEMO_MOTOR_STATE
    }

def update_motor_status(status):
    global DEMO_MOTOR_STATE

    if USING_REAL_HARDWARE:
        ref = db.reference("test")
        ref.update({"motor": int(status)})
        print(f"REAL HARDWARE → Motor {status}")
    else:
        DEMO_MOTOR_STATE = int(status)  # ✅ STORE STATE
        print(f"DEMO MODE → Motor {status}")
