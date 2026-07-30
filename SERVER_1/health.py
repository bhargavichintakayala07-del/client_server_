from flask import jsonify

def get_health_status():
    
    return jsonify({"status": "UP"}), 200