from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import psutil
import uuid
import platform
import os
import time
import threading

# Global variables for network tracking
previous_net_io = None
previous_time = None
network_usage_lock = threading.Lock()

# Function to get or create a persistent token
def get_persistent_token():
    token_file = "client_token.txt"
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return f.read().strip()
    else:
        # Generate new token and save it
        token = str(uuid.uuid4())
        with open(token_file, 'w') as f:
            f.write(token)
        return token

TOKEN = get_persistent_token()

print(f"=== CLIENT STARTED ===")
print(f"Computer: {platform.node()}")
print(f"Token: {TOKEN}")
print(f"Add this computer to the dashboard using the above token")
print(f"======================")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"FastAPI client started. Token: {TOKEN}")
    yield
    # Shutdown (if needed)

app = FastAPI(lifespan=lifespan)

# Middleware to check token
@app.middleware("http")
async def verify_token(request: Request, call_next):
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

@app.get("/systeminfo")
def get_system_info():
    global previous_net_io, previous_time
    
    # Get disk usage - try different paths for Windows/Linux
    disk_path = "C:\\" if platform.system() == "Windows" else "/"
    
    # Get current network stats
    current_net_io = psutil.net_io_counters()
    current_time = time.time()
    
    network_usage_rate = {"bytes_sent_per_sec": 0, "bytes_recv_per_sec": 0}
    
    with network_usage_lock:
        if previous_net_io is not None and previous_time is not None:
            time_diff = current_time - previous_time
            if time_diff > 0:
                bytes_sent_diff = current_net_io.bytes_sent - previous_net_io.bytes_sent
                bytes_recv_diff = current_net_io.bytes_recv - previous_net_io.bytes_recv
                
                network_usage_rate["bytes_sent_per_sec"] = max(0, bytes_sent_diff / time_diff)
                network_usage_rate["bytes_recv_per_sec"] = max(0, bytes_recv_diff / time_diff)
        
        # Update previous values
        previous_net_io = current_net_io
        previous_time = current_time
    
    # Get top 20 processes by CPU usage
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time']):
            try:
                pinfo = proc.info
                if pinfo['cpu_percent'] is not None:
                    processes.append({
                        'pid': pinfo['pid'],
                        'name': pinfo['name'] or 'Unknown',
                        'cpu_percent': pinfo['cpu_percent'],
                        'memory_percent': round(pinfo['memory_percent'] or 0, 2),
                        'create_time': pinfo['create_time']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Sort by CPU usage and get top 20
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        top_processes = processes[:20]
        
    except Exception as e:
        print(f"Error getting processes: {e}")
        top_processes = []
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage(disk_path)._asdict(),
        "network": current_net_io._asdict(),
        "network_usage": network_usage_rate,
        "top_processes": top_processes,
        "hostname": platform.node(),
        "system": platform.system()
    }

if __name__ == "__main__":
    import uvicorn
    PORT = 8000  # Default port for the client
    print(f"Starting server on port {PORT}")
    print(f"Dashboard should connect to: http://{platform.node()}:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
