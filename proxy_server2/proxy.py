from flask import request, jsonify
import requests

def handle_proxy_request():
    # 1. Parse the incoming JSON bundle sent by the load balancer
    data = request.get_json()
    if not data or "website" not in data:
        return jsonify({"error": "Missing 'website' parameter in request payload"}), 400
        
    target_url = data["website"]
    print(f"\n[HTTP] Proxying request to external destination: {target_url}")
    
    try:
        # 2. Safely perform a real network request out to the internet
        # We include a timeout so the server doesn't hang forever if the site is slow
        internet_response = requests.get(target_url, timeout=5)
        
        # 3. Return the exact HTML webpage body and status code back to the load balancer
        return internet_response.text, internet_response.status_code
        
    except requests.exceptions.RequestException as e:
        print(f"[!] Network Error: Failed to reach destination. Details: {e}")
        return jsonify({"error": f"Failed to connect to target website: {target_url}"}), 502