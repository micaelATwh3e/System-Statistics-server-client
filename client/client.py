from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import psutil
import uuid
import platform
import os

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
    # Get disk usage - try different paths for Windows/Linux
    disk_path = "C:\\" if platform.system() == "Windows" else "/"
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": psutil.virtual_memory()._asdict(),
        "disk": psutil.disk_usage(disk_path)._asdict(),
        "network": psutil.net_io_counters()._asdict(),
        "hostname": platform.node(),
        "system": platform.system()
    }

if __name__ == "__main__":
    import uvicorn
    PORT = 8000  # Default port for the client
    print(f"Starting server on port {PORT}")
    print(f"Dashboard should connect to: http://{platform.node()}:{PORT}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)
