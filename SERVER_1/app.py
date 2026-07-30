from flask import Flask
import config
import health
import proxy

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def check_health():
    return health.get_health_status()


@app.route('/process', methods=['POST'])
def process_traffic():
    return proxy.handle_proxy_request()


if __name__ == '__main__':
    print(f"[*] Initializing Replica Proxy Server instance on port {config.PORT}...")
   
    app.run(host='0.0.0.0', port=config.PORT)