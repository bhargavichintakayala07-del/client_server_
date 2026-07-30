import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
import joblib

# Try importing active client scanner from tracker.py
try:
    from tracker import get_active_client_count
    TRACKER_ENABLED = True
except ImportError:
    TRACKER_ENABLED = False
    def get_active_client_count():
        return 0

# Database functions import (If database.py exists)
try:
    from database import save_log, get_logs, get_statistics
    DB_ENABLED = True
except ImportError:
    DB_ENABLED = False

app = Flask(__name__)
app.secret_key = "netflow_ai_secret_key"

# ============================
# 🤖 LOAD AI MODEL & VECTORIZER
# ============================
model = None
vectorizer = None

model_path = os.path.join("model", "model.pkl")
vectorizer_path = os.path.join("model", "vectorizer.pkl")

if os.path.exists(model_path) and os.path.exists(vectorizer_path):
    try:
        model = joblib.load(model_path)
        vectorizer = joblib.load(vectorizer_path)
        print("✅ AI Model & Vectorizer Loaded Successfully!")
    except Exception as e:
        print(f"⚠️ Error loading AI Model: {e}")
else:
    print("⚠️ AI Model Files Not Found in 'model/' directory")

# Memory State Fallbacks
owner_data = {
    "name": "Bhargavi", 
    "phone": "9999999999", 
    "age": "19", 
    "city": "Vijayawada", 
    "org_type": "NRI institution"
}

routers_list = [{
    "id": 1,
    "name": "LAPTOP-242LMJ5R 8267",
    "ssid": "LAPTOP-242LMJ5R 8267",
    "ip": "192.168.137.1",
    "password": "srgwrrg",
    "active_clients": 0,
    "max_limit": 10,
    "live_speed": "485.2 Mbps"
}]

logs = []

# ============================
# 🌐 PAGE ROUTES
# ============================

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/setup')
@app.route('/setup_routers')
@app.route('/owner_setup')
def owner_setup():
    return render_template('owner_setup.html', owner=owner_data)

@app.route('/dashboard')
def dashboard():
    db_logs = logs
    if DB_ENABLED:
        try:
            db_logs = get_logs()
        except Exception:
            pass

    return render_template('dashboard.html', 
                           owner=owner_data, 
                           routers_list=routers_list, 
                           logs=db_logs, 
                           active_clients_count=routers_list[0]['active_clients'])

# ============================
# 📡 GATEWAY & DASHBOARD APIs
# ============================

@app.route('/api/signup', methods=['POST'])
def api_signup():
    global owner_data
    data = request.get_json() or {}
    owner_data["name"] = data.get("name", owner_data["name"])
    owner_data["phone"] = data.get("phone", owner_data["phone"])
    owner_data["city"] = data.get("location", owner_data["city"])
    owner_data["org_type"] = data.get("org_type", owner_data["org_type"])
    return jsonify({"success": True})

@app.route('/api/login', methods=['POST'])
def api_login():
    return jsonify({"success": True})

@app.route('/api/save_setup', methods=['POST'])
def save_setup():
    global owner_data, routers_list
    data = request.get_json() or {}
    owner_data["name"] = data.get("name", owner_data["name"])
    owner_data["phone"] = data.get("phone", owner_data["phone"])
    owner_data["city"] = data.get("city", owner_data["city"])
    owner_data["org_type"] = data.get("org_type", owner_data["org_type"])
    
    if "routers" in data and len(data["routers"]) > 0:
        routers_list = []
        for idx, r in enumerate(data["routers"]):
            routers_list.append({
                "id": idx + 1,
                "name": r.get("name", f"Router_{idx+1}"),
                "ssid": r.get("name", f"Router_{idx+1}"),
                "ip": r.get("ip", "192.168.137.1"),
                "password": r.get("password", "12345678"),
                "active_clients": 0,
                "max_limit": 10,
                "live_speed": "450 Mbps"
            })
    return jsonify({"success": True})

# 📡 LIVE GATEWAY RECEIVER API
@app.route('/api/add_log', methods=['POST'])
@app.route('/log', methods=['POST'])
def add_log():
    global logs, routers_list
    data = request.get_json() or {}
    
    if data:
        # Always fetch EXACT Live active count
        live_count = get_active_client_count()
        incoming_count = data.get('active_clients_count', 0)
        
        # Priority to live PowerShell tracker scanner
        actual_count = live_count if live_count > 0 else incoming_count
        routers_list[0]['active_clients'] = actual_count

        time_val = data.get('time', datetime.now().strftime("%I:%M:%S %p"))
        ip_val = data.get('ip', '127.0.0.1')
        url_val = data.get('url', data.get('website', ''))
        cat_val = data.get('category', 'Wi-Fi Traffic')
        dec_val = data.get('decision', 'CONNECTED')
        server_val = data.get('server', 'Hotspot Gateway Node')

        if DB_ENABLED:
            try:
                save_log(time_val, ip_val, url_val, cat_val, dec_val, server_val)
            except Exception as e:
                print(f"DB Error: {e}")

        log_entry = [len(logs) + 1, time_val, ip_val, url_val, cat_val, dec_val, server_val]
        logs.insert(0, log_entry)

    return jsonify({"status": "success"}), 200


# 🔄 REALTIME DASHBOARD STATS API
@app.route('/api/get_logs', methods=['GET'])
@app.route('/api/get_live_stats', methods=['GET'])
def get_live_stats():
    # Direct Live Scanner sync (Increase/Decrease Both Handled Instantly)
    routers_list[0]['active_clients'] = get_active_client_count()

    formatted_logs = []
    for l in logs[:20]:
        formatted_logs.append({
            "time": l[1],
            "ip": l[2],
            "url": l[3],
            "category": l[4],
            "decision": l[5]
        })

    return jsonify({
        "active_clients": routers_list[0]['active_clients'],
        "active_clients_count": routers_list[0]['active_clients'],
        "routers": routers_list,
        "logs": formatted_logs
    })

if __name__ == '__main__':
    print("🚀 NETFLOW-AI ALL-IN-ONE ADMIN SERVER RUNNING ON http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)