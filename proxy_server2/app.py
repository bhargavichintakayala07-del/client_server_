from flask import Flask
import config
import health
import proxy

app = Flask(__name__)

# --- 1. HEALTH MONITORING ENDPOINT (GET) ---
@app.route('/health', methods=['GET'])
def check_health():
    return health.get_health_status()

# --- 2. TRAFFIC PROCESSING ENDPOINT (POST) ---
@app.route('/process', methods=['POST'])
def process_traffic():
    return proxy.handle_proxy_request()

# --- 3. INFRASTRUCTURE BOOT MANAGER ---
if __name__ == '__main__':
    print(f"[*] Initializing Replica Proxy Server instance on port {config.PORT}...")
    # Listen on all local interfaces so the load balancer can hit this machine remotely
    app.run(host='0.0.0.0', port=config.PORT)