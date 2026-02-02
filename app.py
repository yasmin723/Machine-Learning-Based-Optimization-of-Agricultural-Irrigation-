import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DEMO_MODE = os.getenv('DEMO_MODE', 'True').lower() == 'true'

# Import modules
# Note: Removed init_firebase because it's not in your config file
from firebase_config import get_sensor_data, update_motor_status
from ml_prediction import predict_moisture

app = Flask(__name__)

# --- GLOBAL SYSTEM STATE ---
current_algorithm = "random_forest"
control_mode = "auto"   # auto | manual

# Algorithm mapping
ALGO_MAP = {
    "rf": "random_forest",
    "nn": "neural_network",
    "gb": "gradient_boosting",
    "svm": "svm"
}

# -------- ROUTES --------

@app.route('/', endpoint='index')
def index_page():
    return render_template('index.html')

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

# API for sensor data
@app.route('/api/sensor-data', endpoint='sensor_data')
def sensor_data():
    global control_mode
    data = get_sensor_data() or {}

    predicted = None
    motor_status = data.get("motor", 0)

    if data.get("moisture") is not None:
        predicted = predict_moisture(data)

        # Only automate if in AUTO mode
        if control_mode == "auto":
            new_status = 1 if predicted > data["moisture"] else 0
            if new_status != motor_status:
                motor_status = new_status
                update_motor_status(motor_status)

    decision = "IRRIGATION REQUIRED" if (predicted and predicted > data.get("moisture", 0)) else "SOIL MOISTURE OPTIMAL"
    
    return jsonify({
        "success": True,
        "data": {
            **data,
            "control_mode": control_mode,
            "motor": motor_status,
            "predicted_moisture": predicted,
            "decision": decision
        }
    })

# API to set control mode
@app.route('/api/control-mode', methods=['POST'], endpoint='control_mode_update')
def api_set_control_mode():
    global control_mode
    data = request.get_json()
    if data and "mode" in data:
        control_mode = data["mode"]
        print(f"DEBUG: Mode changed to {control_mode}")
        return jsonify({"success": True, "mode": control_mode})
    return jsonify({"success": False}), 400

# API for manual motor control
@app.route('/api/motor/control', methods=['POST'])
def api_motor_control():
    global control_mode
    
    if control_mode != "manual":
        return jsonify({
            "success": False,
            "message": "Manual control allowed only in MANUAL mode"
        }), 403

    try:
        req_data = request.get_json()
        status = int(req_data.get("status", 0))
        update_motor_status(status)
        return jsonify({"success": True, "motor": status})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 400

# API to select algorithm
@app.route('/api/algorithm/select', methods=['POST'], endpoint='algorithm_select')
def api_select_algorithm():
    global current_algorithm
    data = request.get_json()
    if data and "algorithm" in data:
        current_algorithm = ALGO_MAP.get(data["algorithm"], "random_forest")
        return jsonify({"success": True, "selected": current_algorithm})
    return jsonify({"success": False}), 400

# -------- RUN APP --------
if __name__ == "__main__":
    # Removed the line causing the ImportError
    print("=" * 50)
    print(" SMART IRRIGATION SYSTEM RUNNING ")
    print(f" MODE: {'DEMO' if DEMO_MODE else 'REAL'}")
    print(" URL: http://127.0.0.1:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)