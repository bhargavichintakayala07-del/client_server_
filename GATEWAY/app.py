import csv
import datetime
import os
import subprocess
import threading
import time
from flask import Flask, request, redirect, jsonify
import requests
import tldextract

app = Flask(__name__)

# Admin Dashboard API Endpoint (/log & /api/add_log both supported)
APP_SERVER_URL = "http://127.0.0.1:5000/api/add_log"

# Path to Dataset CSV directly inside GATEWAY folder
DATASET_PATH = os.path.join(os.path.dirname(__file__), 'dataset.csv')

HOSTS_PATH = r"C:\Windows\System32\drivers\etc\hosts"
REDIRECT_IP = "192.168.137.1"

connected_clients_set = set()
domain_policy_map = {}      # {domain: (category, status)}
blocked_domains_set = set()

def load_local_dataset_and_sync_hosts():
    global domain_policy_map, blocked_domains_set
    domain_policy_map.clear()
    blocked_domains_set.clear()

    if os.path.exists(DATASET_PATH):
        try:
            with open(DATASET_PATH, mode='r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header
                
                for row in reader:
                    if len(row) >= 3:
                        site = row[0].strip().lower()
                        cat = row[1].strip()
                        status = row[2].strip().lower()
                        
                        if site not in ['website', 'domain']:
                            domain_policy_map[site] = (cat, status)
                            
                            if status == 'blocked':
                                blocked_domains_set.add(site)
                                blocked_domains_set.add(f"www.{site}")

            print(f"✅ GATEWAY DATASET LOADED: {len(domain_policy_map)} Domains ({len(blocked_domains_set)} Blocked Domains Target Mapped)!")
            apply_hosts_blocking()

        except Exception as e:
            print(f"⚠️ Error reading GATEWAY/dataset.csv: {e}")
    else:
        print(f"❌ dataset.csv missing in GATEWAY directory: {DATASET_PATH}")

def apply_hosts_blocking():
    """Sync blocked domains into Windows system HOSTS file for instant Hotspot ICS routing."""
    try:
        with open(HOSTS_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        clean_lines = [line for line in lines if "# NETFLOW-AI BLOCK" not in line]

        for domain in sorted(blocked_domains_set):
            clean_lines.append(f"{REDIRECT_IP} {domain} # NETFLOW-AI BLOCK\n")

        with open(HOSTS_PATH, 'w', encoding='utf-8') as f:
            f.writelines(clean_lines)

        print("🛡️  HOTSPOT HOSTS NETWORK RULES APPLIED SUCCESSFULLY!")
        subprocess.call("ipconfig /flushdns", shell=True)

    except PermissionError:
        print("❌ PERMISSION ERROR: Open VS Code as ADMINISTRATOR to apply Network Host Rules!")
    except Exception as e:
        print(f"⚠️ Hosts sync error: {e}")

load_local_dataset_and_sync_hosts()

def evaluate_domain_policy(domain):
    domain_clean = domain.lower().strip()
    
    # 1. Direct dataset lookup
    for dataset_domain, (cat, status) in domain_policy_map.items():
        if dataset_domain in domain_clean or domain_clean.endswith('.' + dataset_domain):
            if status == 'blocked':
                return True, f"Blocked ({cat})"
            else:
                return False, f"Allowed ({cat})"

    # 2. Hardcoded fallback check for unlisted domains
    fallback_block_keywords = ["instagram", "snapchat", "facebook", "tiktok", "netflix", "gaming", "steam", "roblox", "bet365"]
    if any(kw in domain_clean for kw in fallback_block_keywords):
        return True, "Blocked (Restricted Category)"

    return False, "Allowed (General Resource)"

# ---------------- LIVE HOTSPOT MONITOR ---------------- #

def scan_hotspot_clients():
    global connected_clients_set
    while True:
        try:
            cmd = 'powershell -Command "Get-NetNeighbor -AddressFamily IPv4 | Where-Object {$_.IPAddress -like \'192.168.137.*\' -and $_.State -ne \'Unreachable\'} | Select-Object -ExpandProperty IPAddress"'
            output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore').strip()
            
            lines = [ip.strip() for ip in output.split('\n') if ip.strip()]
            live_ips = {ip for ip in lines if ip != "192.168.137.1" and not ip.endswith(".255")}

            connected_clients_set = live_ips
            client_count = len(connected_clients_set)
            
            try:
                res = requests.post(APP_SERVER_URL, json={
                    "time": datetime.datetime.now().strftime("%I:%M:%S %p"),
                    "ip": list(connected_clients_set)[0] if connected_clients_set else "192.168.137.1",
                    "url": "Hotspot Client Network Sync",
                    "category": "Wi-Fi Access",
                    "decision": "CONNECTED",
                    "active_clients_count": client_count
                }, timeout=1.5)
            except Exception as req_err:
                pass
        except Exception:
            pass
            
        time.sleep(2)

threading.Thread(target=scan_hotspot_clients, daemon=True).start()

# ---------------- GATEWAY BLOCK DISPATCHER ---------------- #

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'CONNECT'])
@app.route('/<path:path>', methods=['GET', 'POST', 'CONNECT'])
def network_interceptor(path):
    client_ip = request.remote_addr
    target_domain = request.headers.get('Host', '') or path

    extracted = tldextract.extract(target_domain)
    domain = f"{extracted.domain}.{extracted.suffix}" if extracted.suffix else target_domain

    is_blocked, category_desc = evaluate_domain_policy(domain)
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")

    # Send activity log to Admin Dashboard
    try:
        res = requests.post(APP_SERVER_URL, json={
            "time": current_time,
            "ip": client_ip,
            "url": domain,
            "category": category_desc,
            "decision": "BLOCKED" if is_blocked else "ALLOWED",
            "active_clients_count": max(len(connected_clients_set), 1)
        }, timeout=1.5)
        print(f"📡 LOG SENT TO DASHBOARD -> Domain: {domain} | Status: {res.status_code}")
    except Exception as err:
        print(f"⚠️ LOG ERROR: {err}")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Access Restricted - NETFLOW-AI</title>
        <style>
            body {{ background: #07080a; color: #fff; font-family: 'Segoe UI', sans-serif; text-align: center; padding-top: 80px; }}
            .box {{ background: #12161d; border: 1px solid rgba(239, 68, 68, 0.4); max-width: 500px; margin: 0 auto; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            h1 {{ color: #ef4444; font-size: 26px; margin-bottom: 10px; }}
            p {{ color: #8e95a5; font-size: 14px; line-height: 1.6; }}
            .badge {{ background: rgba(239, 68, 68, 0.15); color: #ef4444; padding: 6px 12px; border-radius: 8px; font-weight: bold; font-size: 12px; display: inline-block; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h1>🚫 ACCESS RESTRICTED BY NETFLOW-AI</h1>
            <p>The website <strong>{domain}</strong> is restricted on this academic hotspot network.</p>
            <div class="badge">{category_desc.upper()}</div>
            <hr style="border: 0; border-top: 1px solid rgba(255,255,255,0.1); margin: 20px 0;">
            <p style="color: #10b981; font-size: 12px;">Only Educational, University, and Research domains are permitted.</p>
        </div>
    </body>
    </html>
    """, 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)