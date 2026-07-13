import config

server_status = {server: 1 for server in config.BACKEND_SERVERS}

current_index = 0

def get_next_server():
    global current_index
    
    healthy_servers = [server for server, status in server_status.items() if status == 1]
    
    if not healthy_servers:
        return None
        
    selected_server = healthy_servers[current_index % len(healthy_servers)]
    
    current_index = (current_index + 1) % len(healthy_servers)
    return selected_server