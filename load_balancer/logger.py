import time

system_metrics = {
    "total_requests": 0,
    "server_hits": {},    
    "last_response_time": 0.0,
    "logs": []             
}

def log_transaction(server_url, execution_time, status_code):

    system_metrics["total_requests"] += 1
    
   
    if server_url not in system_metrics["server_hits"]:
        system_metrics["server_hits"][server_url] = 0
    system_metrics["server_hits"][server_url] += 1
    
    
    system_metrics["last_response_time"] = round(execution_time, 4)
    
   
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Route -> {server_url} | HTTP {status_code} | Time: {system_metrics['last_response_time']}s"
    
    system_metrics["logs"].append(log_entry)
    print(log_entry)