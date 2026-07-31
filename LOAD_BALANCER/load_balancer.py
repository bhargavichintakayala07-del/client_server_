import time
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# 📡 REAL BACKEND SERVERS NETWORK IP CONFIGURATION
LAPTOP_A_IP = "172.16.46.175"
LAPTOP_B_IP = "172.16.40.167"

SERVER_1 = f"http://{LAPTOP_A_IP}:5002"
SERVER_2 = f"http://{LAPTOP_B_IP}:5003"

s1_requests = 0
s2_requests = 0
current_turn = 0
traffic_logs = []

def check_health(server_url):
    """Checks health via real IP or Localhost fallback"""
    try:
        r = requests.get(f"{server_url}/health", timeout=1.5)
        if r.status_code == 200:
            return True
    except:
        pass
    
    # Localhost fallback check if running on same host
    if "5002" in server_url:
        try:
            r = requests.get("http://127.0.0.1:5002/health", timeout=1.5)
            return r.status_code == 200
        except:
            return False
    elif "5003" in server_url:
        try:
            r = requests.get("http://127.0.0.1:5003/health", timeout=1.5)
            return r.status_code == 200
        except:
            return False
    return False

@app.route('/')
def lb_panel():
    return render_template('lb_dashboard.html')

@app.route('/api/lb_stats')
def lb_stats():
    s1_up = check_health(SERVER_1)
    s2_up = check_health(SERVER_2)
    return jsonify({
        "server1_up": s1_up,
        "server2_up": s2_up,
        "server1_count": s1_requests,
        "server2_count": s2_requests,
        "logs": traffic_logs[-15:]  # Send latest 15 logs
    })

# 🔀 MAIN LOAD BALANCER TRAFFIC ROUTER
@app.route('/route', methods=['GET', 'POST'])
@app.route('/', methods=['POST'])
def route_traffic():
    global s1_requests, s2_requests, current_turn, traffic_logs
    
    client_ip = request.remote_addr or "172.16.46.175"
    s1_up = check_health(SERVER_1)
    s2_up = check_health(SERVER_2)

    target_server = None
    target_name = ""

    # ROUND-ROBIN & AUTO FAILOVER LOGIC
    if s1_up and s2_up:
        if current_turn == 0:
            target_server = SERVER_1
            target_name = "SERVER_1 (Port 5002)"
            s1_requests += 1
            current_turn = 1
        else:
            target_server = SERVER_2
            target_name = "SERVER_2 (Port 5003)"
            s2_requests += 1
            current_turn = 0
    elif s1_up:
        target_server = SERVER_1
        target_name = "SERVER_1 (Port 5002) [FAILOVER]"
        s1_requests += 1
    elif s2_up:
        target_server = SERVER_2
        target_name = "SERVER_2 (Port 5003) [FAILOVER]"
        s2_requests += 1
    else:
        return jsonify({
            "error": "CRITICAL: ALL BACKEND SERVERS ARE UNREACHABLE!",
            "status": "CRASHED"
        }), 503

    # Log Traffic Dispatch
    traffic_logs.append({
        "time": datetime.now().strftime("%I:%M:%S %p"),
        "client_ip": client_ip,
        "target": target_name,
        "response": "200 OK"
    })

    # Forward Request to Selected Target Server
    try:
        res = requests.get(target_server, timeout=2.5)
        return res.text, res.status_code
    except Exception as e:
        # Fallback to Localhost route if target fails
        fallback_url = "http://127.0.0.1:5002" if "5002" in target_server else "http://127.0.0.1:5003"
        try:
            res = requests.get(fallback_url, timeout=2.5)
            return res.text, res.status_code
        except:
            return f"Backend Node Connection Error ({e})", 500

if __name__ == '__main__':
    print("🚀 LOAD BALANCER ENGINE RUNNING ON http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)