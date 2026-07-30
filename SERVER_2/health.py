from flask import jsonify

def get_health_status():
    # Return a lightweight confirmation packet to let the load balancer know we are UP
    return jsonify({"status": "UP"}), 200