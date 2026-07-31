from flask import Flask, jsonify, request
import time

app = Flask(__name__)

SERVER_NAME = "SERVER_1 (Primary Backend Node)"
PORT = 5002
request_count = 0

@app.route('/')
@app.route('/index')
def home():
    global request_count
    request_count += 1
    return f"""
    <div style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background-color: #0f172a; color: #fff; min-height: 80vh;">
        <h1 style="color: #38bdf8;">🎓 Educational Content Portal</h1>
        <h2 style="color: #4ade80;">Served by: {SERVER_NAME}</h2>
        <p style="font-size: 18px; color: #94a3b8;">Port: {PORT}</p>
        <hr style="border-color: #334155; width: 60%; margin: 20px auto;">
        <p style="font-size: 20px;">Total Handled Requests by Server 1: <strong style="color: #facc15;">{request_count}</strong></p>
        <div style="background: #1e293b; display: inline-block; padding: 15px 30px; border-radius: 10px; margin-top: 20px; border: 1px solid #475569;">
            ✅ Node Health Status: <strong>HEALTHY & ONLINE</strong>
        </div>
    </div>
    """

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "UP",
        "server": SERVER_NAME,
        "port": PORT,
        "handled_requests": request_count,
        "load": min(request_count * 5, 100)
    }), 200

if __name__ == '__main__':
    print(f"🚀 {SERVER_NAME} Running on http://0.0.0.0:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)