from flask import Flask, request, jsonify
import requests
import config
import server_manager
import threading
import health_checker
import logger
import time

app = Flask(__name__)

# --- 1. ROUTE FOR FORWARDING TRAFFIC (POST) ---
@app.route('/forward', methods=['POST'])
def forward_request():
    data = request.get_json()
    target_website = data.get("website")
    print(f"[*] Received request from Gateway. Target: {target_website}")
    
    # Dynamically select the next available healthy server via Round-Robin
    selected_server_url = server_manager.get_next_server()
    
    if not selected_server_url:
        return jsonify({"error": "No backend servers are currently available"}), 503
    
    try:
        # Start execution timer
        start_time = time.time()
        
        # Forward the packet to the server's process endpoint
        backend_response = requests.post(f"{selected_server_url}/process", json=data)
        
        # Calculate elapsed time
        duration = time.time() - start_time
        
        # Log telemetry metrics
        logger.log_transaction(selected_server_url, duration, backend_response.status_code)
        
        return backend_response.text
        
    except requests.exceptions.ConnectionError:
        print(f"[!] Error: Could not connect to backend server: {selected_server_url}")
        return jsonify({"error": f"Backend Server {selected_server_url} Offline"}), 503


# --- 2. ROUTE FOR ADMIN METRICS DASHBOARD (GET) ---
@app.route('/metrics', methods=['GET'])
def get_metrics():
    from server_manager import server_status
    readable_metrics = dict(logger.system_metrics)
    readable_metrics["server_statuses"] = server_status
    return jsonify(readable_metrics)


# --- 3. SYSTEM BOOT MANAGER ---
if __name__ == '__main__':
    # Initialize the background daemon checker thread
    checker_thread = threading.Thread(target=health_checker.run_health_check, daemon=True)
    checker_thread.start()
    
    # Run the web application doorstep
    app.run(host='0.0.0.0', port=config.PORT)