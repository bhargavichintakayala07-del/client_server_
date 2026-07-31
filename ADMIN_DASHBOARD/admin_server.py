import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify
import joblib

# 🧠 IMPORT AI ENGINE MODULE FROM ROOT DIRECTORY
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from AI_ENGINE.ai_engine import inspect_traffic_ai
    AI_ENGINE_ENABLED = True
    print("🤖 NetFlow-AI Smart Engine Loaded Successfully!")
except ImportError as e:
    AI_ENGINE_ENABLED = False
    print(f"⚠️ Warning: AI_ENGINE not found ({e}). Using default rules.")

try:
    from tracker import get_active_client_count
    TRACKER_ENABLED = True
except ImportError:
    TRACKER_ENABLED = False
    def get_active_client_count():
        return 0

try:
    from database import save_log, get_logs, get_statistics
    DB_ENABLED = True
except ImportError:
    DB_ENABLED = False

app = Flask(__name__)
app.secret_key = "netflow_ai_secret_key"

# Memory State Fallbacks with BOTH ROUTERS DEFAULT
owner_data = {
    "name": "Bhargavi", 
    "phone": "9032174260", 
    "age": "19", 
    "city": "vijayawada", 
    "org_type": "nri"
}

routers_list = [
    {
        "id": 1,
        "name": "Laptop_A_Hotspot",
        "ssid": "Laptop_A_Hotspot",
        "ip": "192.168.137.1",
        "password": "••••••••",
        "active_clients": 0,
        "max_limit": 10,
        "live_speed": "450 Mbps"
    },
    {
        "id": 2,
        "name": "Laptop_B_Hotspot",
        "ssid": "Laptop_B_Hotspot",
        "ip": "192.168.15.89",
        "password": "••••••••",
        "active_clients": 0,
        "max_limit": 10,
        "live_speed": "420 Mbps"
    }
]

device_tracker = {}

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
    return render_template('dashboard.html', 
                           owner=owner_data, 
                           routers_list=routers_list, 
                           logs=list(device_tracker.values()), 
                           active_clients_count=len(device_tracker))

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
        new_list = []
        for idx, r in enumerate(data["routers"]):
            new_list.append({
                "id": idx + 1,
                "name": r.get("name", f"Router_{idx+1}"),
                "ssid": r.get("name", f"Router_{idx+1}"),
                "ip": r.get("ip", "192.168.137.1" if idx == 0 else "192.168.15.89"),
                "password": r.get("password", "12345678"),
                "active_clients": 0,
                "max_limit": 10,
                "live_speed": "450 Mbps"
            })
        routers_list = new_list
    return jsonify({"success": True})

# 📡 LIVE GATEWAY RECEIVER API WITH INTEGRATED AI TRAFFIC ENGINE
@app.route('/api/add_log', methods=['POST'])
@app.route('/log', methods=['POST'])
def add_log():
    global device_tracker, routers_list
    data = request.get_json() or {}
    
    if data:
        ip = data.get('ip', '127.0.0.1')
        
        # Ignore Host Gateways
        if ip in ["192.168.137.1", "192.168.15.1", "192.168.15.89", "127.0.0.1"]:
            return jsonify({"status": "ignored"}), 200

        time_val = data.get('time', datetime.now().strftime("%I:%M:%S %p"))
        url_val = data.get('url', data.get('website', ''))
        cat_val = data.get('category', 'Wi-Fi Traffic')
        dec_val = str(data.get('decision', 'CONNECTED')).upper()

        # 🧠 RUN SMART AI INSPECTION ON REQUESTED URL / QUERY
        ai_decision = dec_val
        ai_category = cat_val

        if url_val and AI_ENGINE_ENABLED:
            ai_eval = inspect_traffic_ai(url_val)
            if ai_eval["action"] == "BLOCK":
                ai_decision = str(ai_eval["decision"]).upper()
                ai_category = ai_eval["category"]

        current_timestamp = datetime.now().timestamp()

        # Connect / Register Device (Single Row per Client IP)
        if ip not in device_tracker:
            device_tracker[ip] = {
                'ip': ip,
                'time': time_val,
                'last_seen': current_timestamp,
                'url': 'Active Connection',
                'category': 'Wi-Fi Access',
                'decision': 'CONNECTED',
                'blocked_count': 0
            }
        
        device_tracker[ip]['time'] = time_val
        device_tracker[ip]['last_seen'] = current_timestamp

        # Update row details if Blocked by Rule/AI or Specific Site request
        if "BLOCK" in ai_decision or "RESTRICTED" in ai_category.upper() or (url_val and url_val != "Hotspot Client Network Sync"):
            if "BLOCK" in ai_decision or "RESTRICTED" in ai_category.upper():
                device_tracker[ip]['url'] = url_val
                device_tracker[ip]['category'] = ai_category
                device_tracker[ip]['decision'] = ai_decision
                device_tracker[ip]['blocked_count'] += 1
            elif url_val != "Hotspot Client Network Sync":
                device_tracker[ip]['url'] = url_val

    return jsonify({"status": "success"}), 200

# 🔄 REALTIME DASHBOARD STATS API
@app.route('/api/get_logs', methods=['GET'])
@app.route('/api/get_live_stats', methods=['GET'])
def get_live_stats():
    global device_tracker, routers_list
    
    # Auto-remove inactive devices (> 20 sec)
    now = datetime.now().timestamp()
    active_devices = {}
    for ip, dev in device_tracker.items():
        if now - dev.get('last_seen', now) < 20:
            active_devices[ip] = dev

    device_tracker = active_devices

    # Count clients per subnet for both Routers
    if len(routers_list) >= 1:
        routers_list[0]['active_clients'] = len([d for d in device_tracker.keys() if d.startswith("192.168.137.")])
    if len(routers_list) >= 2:
        routers_list[1]['active_clients'] = len([d for d in device_tracker.keys() if d.startswith("192.168.15.")])

    return jsonify({
        "active_clients": len(device_tracker),
        "active_clients_count": len(device_tracker),
        "routers": routers_list,
        "logs": list(device_tracker.values())
    })

if __name__ == '__main__':
    print("🚀 NETFLOW-AI ADMIN SERVER RUNNING ON http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)