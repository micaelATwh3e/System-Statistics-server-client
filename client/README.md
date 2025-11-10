# System Monitor Client

A FastAPI-based system monitoring client that provides real-time system information through a REST API.

## Features

- **Persistent Authentication**: Uses a token-based authentication system with persistent tokens
- **System Monitoring**: Provides CPU, memory, disk, and network statistics
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **RESTful API**: Clean JSON API for system information

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd client
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the client**
   ```bash
   python client.py
   ```

2. **Note the token and connection details**
   The client will display:
   ```
   === CLIENT STARTED ===
   Computer: your-hostname
   Token: a79a6575-3178-44fa-8ed0-48581ae5caec
   Add this computer to the dashboard using the above token
   Starting server on port 8000
   Dashboard should connect to: http://your-hostname:8000
   ======================
   ```

3. **Add to dashboard**
   - Use the displayed token to add this computer to your monitoring dashboard
   - The client runs on port **8000** by default
   - Connect to `http://hostname:8000`

## API Endpoints

### GET /systeminfo
Returns real-time system information including:
- CPU usage percentage
- Memory statistics (total, available, used, etc.)
- Disk usage (total, used, free)
- Network I/O counters
- System hostname and OS type

**Authentication**: Requires `Authorization: Bearer <token>` header

**Example Response**:
```json
{
  "cpu_percent": 15.2,
  "memory": {
    "total": 16777216000,
    "available": 8388608000,
    "used": 8388608000,
    "percent": 50.0
  },
  "disk": {
    "total": 1000000000000,
    "used": 500000000000,
    "free": 500000000000,
    "percent": 50.0
  },
  "network": {
    "bytes_sent": 1024000,
    "bytes_recv": 2048000
  },
  "hostname": "laptop",
  "system": "Linux"
}
```

## Token Persistence

The client generates a unique token on first run and saves it to `client_token.txt`. This ensures:
- The same token is used across restarts
- You only need to add the computer to your dashboard once
- To generate a new token, delete `client_token.txt` and restart

## Configuration

- **Port**: Default is 8000, modify the `PORT` variable in `client.py` to change
- **Host**: Binds to `0.0.0.0` (all interfaces) by default for dashboard connectivity

## Security

- All API endpoints require Bearer token authentication
- Token is automatically generated and persisted locally
- Only the `/systeminfo` endpoint is exposed