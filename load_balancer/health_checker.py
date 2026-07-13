import time
import requests
import config
import server_manager

def run_health_check():
    print("[*] Background Health Checker Daemon Started...")
    
    while True:
        for server_url in config.BACKEND_SERVERS:
            try:
                response = requests.get(f"{server_url}/health", timeout=2)
                
                if response.status_code == 200:
            
                    if server_manager.server_status[server_url] == 0:
                        print(f"[+] Recovery Detected: {server_url} is back ONLINE!")
                    server_manager.server_status[server_url] = 1
                else:
                   
                    if server_manager.server_status[server_url] == 1:
                        print(f"[!] Warning: {server_url} returned unhealthy status. Marking DOWN.")
                    server_manager.server_status[server_url] = 0
                    
            except requests.exceptions.RequestException:
               
                if server_manager.server_status[server_url] == 1:
                    print(f"[💥] Alert: Can no longer reach {server_url}. Diverting traffic!")
                server_manager.server_status[server_url] = 0
                
      
        time.sleep(3)