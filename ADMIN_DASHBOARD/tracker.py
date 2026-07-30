import subprocess

def get_connected_clients():
    clients = []
    try:
        # PowerShell command use chesi Hotspot subnet (192.168.137.x) lo STALE/Reachable unna active devices ni matrame Instant ga scan chesthumdi
        cmd = 'powershell -Command "Get-NetNeighbor -AddressFamily IPv4 | Where-Object {$_.IPAddress -like \'192.168.137.*\' -and $_.State -ne \'Unreachable\'} | Select-Object -ExpandProperty IPAddress"'
        output = subprocess.check_output(cmd, shell=True).decode('utf-8', errors='ignore').strip()
        
        lines = [ip.strip() for ip in output.split('\n') if ip.strip()]
        for ip in lines:
            if ip != "192.168.137.1" and not ip.endswith(".255"):
                clients.append({'ip': ip})
    except Exception as e:
        # Fallback to ARP Table if PowerShell fails
        try:
            output = subprocess.check_output("arp -a", shell=True).decode('utf-8', errors='ignore')
            for line in output.split('\n'):
                if "192.168.137." in line and not "255" in line and not "192.168.137.1 " in line:
                    parts = line.split()
                    if len(parts) >= 2 and ("-" in parts[1] or ":" in parts[1]):
                        clients.append({'ip': parts[0]})
        except Exception:
            pass

    return clients

def get_active_client_count():
    return len(get_connected_clients())

if __name__ == "__main__":
    print(f"📡 Dynamic Live Hotspot Devices Count: {get_active_client_count()}")