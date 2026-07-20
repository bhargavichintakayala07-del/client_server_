from flask import Flask, render_template, request, jsonify
from database import save_log, get_logs, get_statistics
from datetime import datetime
import joblib
import os

app = Flask(__name__)

# ============================
# Load AI Model
# ============================

model = None
vectorizer = None

model_path = os.path.join("admin", "model", "model.pkl")
vectorizer_path = os.path.join("admin", "model", "vectorizer.pkl")

if os.path.exists(model_path) and os.path.exists(vectorizer_path):
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    print("✅ AI Model Loaded Successfully")
else:
    print("⚠️ AI Model Not Found")


# ============================
# Server Status
# ============================

server_status = {
    "server1": "Online",
    "server2": "Online"
}


# ============================
# Home Page
# ============================

@app.route("/")
def home():

    logs = get_logs()

    total, allowed, blocked, clients = get_statistics()

    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    return render_template(
        "index.html",
        logs=logs,
        total=total,
        allowed=allowed,
        blocked=blocked,
        clients=clients,
        current_time=current_time,
        server_status=server_status
    )


# ============================
# Save Log API
# ============================

@app.route("/log", methods=["POST"])
def receive_log():

    data = request.get_json()

    save_log(
        data["time"],
        data["ip"],
        data["website"],
        data["category"],
        data["decision"],
        data["server"]
    )

    return jsonify({
        "status": "success",
        "message": "Log Saved Successfully"
    })


# ============================
# Update Server Status API
# ============================

@app.route("/server_status", methods=["POST"])
def update_server_status():

    global server_status

    data = request.get_json()

    server_status["server1"] = data["server1"]
    server_status["server2"] = data["server2"]

    return jsonify({
        "status": "success",
        "message": "Server Status Updated"
    })


# ============================
# AI Prediction API
# ============================

@app.route("/predict", methods=["POST"])
def predict():

    if model is None or vectorizer is None:

        return jsonify({
            "status": "error",
            "message": "AI Model Not Loaded"
        })

    data = request.get_json()

    website = data["website"]

    website_vector = vectorizer.transform([website])

    prediction = model.predict(website_vector)

    return jsonify({
        "website": website,
        "category": prediction[0]
    })


# ============================
# Run Flask
# ============================

if __name__ == "__main__":
    app.run(debug=True)