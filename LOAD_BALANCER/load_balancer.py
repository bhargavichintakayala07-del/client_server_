import time
import requests
from flask import Flask, request, jsonify, render_template
from datetime import datetime

app = Flask(__name__)

# BACKEND SERVERS CONFIGURATION (Update IPs if running across different laptops)
SERVER_1 = "http://127.0.0.1:5002"
SERVER_2 = "http://127.0.0.1:5003"

s1_requests = 0
s2_requests = 0
current_turn = 0
traffic_logs = []

def check_health(server_url):
    try:
        r = requests.get(f"{server_url}/health", timeout=1)
        return r.status_code == 200
    except:
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
        "logs": traffic_logs
    })

# 🔀 MAIN LOAD BALANCER TRAFFIC ROUTER
@app.route('/route', methods=['GET', 'POST'])
def route_traffic():
    global s1_requests, s2_requests, current_turn, traffic_logs
    
    client_ip = request.remote_addr or "192.168.137.122"
    s1_up = check_health(SERVER_1)
    s2_up = check_health(SERVER_2)

    target_server = None
    target_name = ""

    # ROUND-ROBIN & AUTO FAILOVER LOGIC
    if s1_up and s2_up:
        if current_turn == 0:
            target_server = SERVER_1
            target_name = "SERVER_1 (5002)"
            s1_requests += 1
            current_turn = 1
        else:
            target_server = SERVER_2
            target_name = "SERVER_2 (5003)"
            s2_requests += 1
            current_turn = 0
    elif s1_up:
        target_server = SERVER_1
        target_name = "SERVER_1 (5002) [FAILOVER]"
        s1_requests += 1
    elif s2_up:
        target_server = SERVER_2
        target_name = "SERVER_2 (5003) [FAILOVER]"
        s2_requests += 1
    else:
        return "❌ ALL BACKEND SERVERS DOWN!", 503

    # Log Traffic
    traffic_logs.append({
        "time": datetime.now().strftime("%I:%M:%S %p"),
        "client_ip": client_ip,
        "target": target_name
    })

    # Forward Request to Selected Target Server
    try:
        res = requests.get(target_server)
        return res.text, res.status_code
    except:
        return "Server Error", 500

if __name__ == '__main__':
    print("🚀 LOAD BALANCER ENGINE RUNNING ON http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000, debug=False)