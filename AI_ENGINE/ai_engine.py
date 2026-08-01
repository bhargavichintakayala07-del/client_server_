import re
import time
from difflib import SequenceMatcher

# 🚫 Blocked Categories & Target Keywords Dataset
BLOCKED_KEYWORDS = {
    "social_media": [
        "snapchat", "facebook", "instagram", "tiktok", "twitter", "x", 
        "youtube", "reddit", "whatsapp", "telegram"
    ],
    "gaming": [
        "pubg", "freefire", "roblox", "steam", "minecraft", "epicgames"
    ],
    "phishing_and_malicious": [
        "free-recharge", "claim-bonus", "login-verify", "bank-update", 
        "account-security-alert", "free-coins", "win-prize"
    ]
}

# ⚡ DDoS ANOMALY TRACKER MEMORY
client_request_history = {}  # {client_ip: [timestamps]}

def detect_ddos_anomaly(client_ip, max_requests_per_sec=8):
    """
    DDoS & Anomaly Detection Engine:
    Tracks request frequency per client IP.
    If frequency exceeds threshold, tags it as DDoS Anomaly Attack.
    """
    now = time.time()
    if client_ip not in client_request_history:
        client_request_history[client_ip] = []

    # Keep timestamps within the last 3 seconds
    client_request_history[client_ip] = [
        t for t in client_request_history[client_ip] if now - t < 3
    ]
    client_request_history[client_ip].append(now)

    request_count = len(client_request_history[client_ip])
    
    # Calculate Risk Score (0% to 100%)
    risk_score = min(int((request_count / (max_requests_per_sec * 2)) * 100), 100)

    if request_count > max_requests_per_sec:
        return True, risk_score, f"DDoS Anomaly ({request_count} req/3s)"
    
    return False, risk_score, "Normal Traffic"

def normalize_text(text):
    if not text:
        return ""
    text = text.lower().strip()
    if "q=" in text:
        text = text.split("q=")[-1].split("&")[0]
    elif "search=" in text:
        text = text.split("search=")[-1].split("&")[0]
    text = re.sub(r'https?://|www\.|[_\-+%20\s\.\/]', '', text)
    return text

def inspect_traffic_ai(url_or_query, client_ip="127.0.0.1"):
    """
    Core AI Decision Engine:
    Combines DDoS Anomaly Engine + Phishing/Keyword Pattern Inspector.
    """
    # 1. DDoS Anomaly Inspection
    is_ddos, risk_score, ddos_msg = detect_ddos_anomaly(client_ip)
    if is_ddos:
        return {
            "action": "BLOCK",
            "decision": "AI BLOCKED (DDoS Traffic Anomaly)",
            "category": "Cyber Attack / Anomaly",
            "risk_score": risk_score
        }

    if not url_or_query:
        return {
            "action": "ALLOW",
            "decision": "CONNECTED",
            "category": "General Traffic",
            "risk_score": risk_score
        }

    clean_input = normalize_text(url_or_query)
    raw_input = url_or_query.lower()

    # 2. Phishing & Restricted Keyword Inspection
    for category, keywords in BLOCKED_KEYWORDS.items():
        for kw in keywords:
            if kw in clean_input or kw in raw_input:
                category_name = category.replace('_', ' ').title()
                return {
                    "action": "BLOCK",
                    "decision": f"AI BLOCKED ({category_name} Keyword)",
                    "category": category_name,
                    "risk_score": risk_score
                }
            
            similarity = SequenceMatcher(None, kw, clean_input).ratio()
            if len(clean_input) >= 4 and similarity > 0.72:
                category_name = category.replace('_', ' ').title()
                return {
                    "action": "BLOCK",
                    "decision": "AI BLOCKED (Fuzzy Pattern Match)",
                    "category": category_name,
                    "risk_score": risk_score
                }

    return {
        "action": "ALLOW",
        "decision": "CONNECTED",
        "category": "General Traffic",
        "risk_score": risk_score
    }
# -------------------------------------------------------------
# 🔮 AI TIME-SERIES TRAFFIC FORECASTING ENGINE
# -------------------------------------------------------------
def predict_future_traffic(history_rates):
    """
    Takes past traffic data points and predicts next 5 interval bandwidth trends.
    Uses Moving Average + Trend Slope Forecasting algorithm.
    """
    if not history_rates or len(history_rates) < 2:
        return [120, 140, 160, 150, 180] # Default fallback baseline forecast

    # Calculate average growth rate (slope)
    n = len(history_rates)
    recent_avg = sum(history_rates[-3:]) / min(n, 3)
    overall_avg = sum(history_rates) / n
    trend_slope = (recent_avg - overall_avg) * 0.25

    forecast_points = []
    last_val = history_rates[-1]

    for i in range(1, 6):
        # Predict next points with trend variation
        predicted = last_val + (trend_slope * i) + (i * 5)
        predicted = max(20, min(500, round(predicted))) # Clamp between 20 Mbps to 500 Mbps
        forecast_points.append(predicted)

    return forecast_points