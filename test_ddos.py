import time
import requests

print("⚡ STARTING DEMO DUAL-HOTSPOT DDoS ANOMALY ATTACK SIMULATOR...")
target_url = "http://127.0.0.1:5000/api/add_log"

# Hotspot 1 & Hotspot 2 Configurations
HOTSPOT_A = {
    "ip": "192.168.137.88",
    "gateway_ip": "172.16.46.175",
    "router_id": 1,
    "router_name": "Laptop_A_Hotspot"
}

HOTSPOT_B = {
    "ip": "192.168.137.99",
    "gateway_ip": "172.16.40.167",
    "router_id": 2,
    "router_name": "Laptop_B_Hotspot"
}

print("\n🚀 [1/2] Launching Anomaly Attack on Laptop_A_Hotspot (172.16.46.175)...")
for i in range(12):
    payload = {
        "ip": HOTSPOT_A["ip"],
        "gateway_ip": HOTSPOT_A["gateway_ip"],
        "router_id": HOTSPOT_A["router_id"],
        "router_name": HOTSPOT_A["router_name"],
        "url": "http://google.com/search?q=ddos_attack_burst_a",
        "category": "Web Browsing",
        "decision": "CONNECTED"
    }
    try:
        res = requests.post(target_url, json=payload, timeout=1)
        print(f"  Laptop_A Request {i+1} -> Status: {res.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(0.02)  # Ultra fast burst

print("\n🚀 [2/2] Launching Anomaly Attack on Laptop_B_Hotspot (172.16.40.167)...")
for i in range(12):
    payload = {
        "ip": HOTSPOT_B["ip"],
        "gateway_ip": HOTSPOT_B["gateway_ip"],
        "router_id": HOTSPOT_B["router_id"],
        "router_name": HOTSPOT_B["router_name"],
        "url": "http://google.com/search?q=ddos_attack_burst_b",
        "category": "Web Browsing",
        "decision": "CONNECTED"
    }
    try:
        res = requests.post(target_url, json=payload, timeout=1)
        print(f"  Laptop_B Request {i+1} -> Status: {res.status_code}")
    except Exception as e:
        print(f"  Error: {e}")
    time.sleep(0.02)  # Ultra fast burst

print("\n✅ Dual-Hotspot DDoS Simulation Complete!")
print("👉 Immediately open/refresh http://127.0.0.1:5000/dashboard to see AI Blocked Badges on BOTH Hotspot Tables!")