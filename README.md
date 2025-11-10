# 📊 Distributed System Monitor

A comprehensive distributed system monitoring solution with a centralized Flask dashboard server and lightweight FastAPI clients for real-time system statistics collection.

## 🌟 Features

### 🖥️ Server Dashboard
- **Web-based Dashboard**: Clean, responsive interface for monitoring multiple computers
- **User Authentication**: Secure login system with password management
- **Real-time Monitoring**: Live system statistics with 30-second update intervals
- **Historical Data**: Track and visualize system performance over time
- **Computer Management**: Add/remove computers from monitoring
- **Multi-user Support**: Admin user management with secure password hashing

### 📡 Client Agents
- **Lightweight Monitoring**: Minimal resource usage FastAPI client
- **Cross-platform**: Works on Windows, Linux, and macOS
- **Persistent Authentication**: Token-based auth with automatic token persistence
- **Real-time Metrics**: CPU, memory, disk, and network statistics
- **Secure Communication**: Bearer token authentication for all API calls

### 📈 Monitored Metrics
- **CPU Usage**: Real-time processor utilization
- **Memory**: Total, used, available, and percentage utilization
- **Disk Space**: Total, used, free space and percentage
- **Network I/O**: Bytes sent and received counters
- **System Info**: Hostname, OS type, last seen timestamps

## 🏗️ Architecture

```
┌─────────────────┐    HTTP/REST API    ┌─────────────────┐
│                 │ ◄─────────────────► │                 │
│  Server         │                     │  Client Agent   │
│  (Flask)        │                     │  (FastAPI)      │
│  Port: 8001     │                     │  Port: 8000     │
│                 │                     │                 │
└─────────────────┘                     └─────────────────┘
         │                                       │
         ▼                                       ▼
┌─────────────────┐                     ┌─────────────────┐
│   SQLite DB     │                     │   System APIs   │
│   (stats.db)    │                     │   (psutil)      │
└─────────────────┘                     └─────────────────┘
```

## 🚀 Quick Start

### 1. Server Setup (Dashboard)

```bash
# Clone the repository
git clone <your-repo-url>
cd stat_server/server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

The server will be available at: `http://localhost:8001`

**Default Login:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important**: Change the default password immediately after first login!

### 2. Client Setup (Monitoring Agent)

```bash
# Navigate to client directory
cd stat_server/client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the client
python client.py
```

The client will display:
```
=== CLIENT STARTED ===
Computer: your-hostname
Token: a79a6575-3178-44fa-8ed0-48581ae5caec
Add this computer to the dashboard using the above token
Dashboard should connect to: http://your-hostname:8000
======================
```

### 3. Connect Client to Server

1. Open the server dashboard at `http://localhost:8001`
2. Login with default credentials
3. Navigate to "Manage Computers"
4. Add a new computer using:
   - **Name**: A friendly name for the computer
   - **URL**: `http://client-hostname:8000` (or IP address)
   - **Token**: The token displayed by the client

## 📖 Detailed Setup

### Server Configuration

The server uses several configurable parameters:

```python
# Security (change these!)
app.secret_key = 'your-secret-key-change-this-in-production'
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin123'

# Database
DB_PATH = 'stats.db'

# Collection interval
time.sleep(30)  # Collect stats every 30 seconds
```

### Client Configuration

```python
# Port configuration
PORT = 8000  # Default client port

# Token persistence
TOKEN_FILE = "client_token.txt"
```

## 🔐 Security Features

- **Password Hashing**: SHA-256 hashed passwords stored in database
- **Session Management**: Secure Flask sessions with login/logout
- **Token Authentication**: Clients use Bearer tokens for API access
- **Input Validation**: Form validation and SQL injection protection
- **Persistent Tokens**: Client tokens survive restarts

## 🗃️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Computers Table
```sql
CREATE TABLE computers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    url TEXT NOT NULL,
    token TEXT NOT NULL,
    last_seen TIMESTAMP,
    status TEXT DEFAULT 'offline'
)
```

### Stats Table
```sql
CREATE TABLE stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    computer_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cpu_percent REAL,
    memory_total INTEGER,
    memory_used INTEGER,
    memory_percent REAL,
    disk_total INTEGER,
    disk_used INTEGER,
    disk_percent REAL,
    network_bytes_sent INTEGER,
    network_bytes_recv INTEGER,
    FOREIGN KEY (computer_id) REFERENCES computers (id)
)
```

## 🔌 API Endpoints

### Server API

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/login` | GET/POST | Login page and authentication | No |
| `/logout` | GET | Logout and clear session | No |
| `/` | GET | Main dashboard | Yes |
| `/api/computers` | GET | List all computers | Yes |
| `/api/stats/<id>` | GET | Latest stats for computer | Yes |
| `/api/history/<id>` | GET | Historical stats | Yes |
| `/api/add_computer` | POST | Add new computer | Yes |
| `/change_password` | GET/POST | Password management | Yes |
| `/manage` | GET | Computer management page | Yes |

### Client API

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/systeminfo` | GET | Current system statistics | Bearer Token |

## 🔧 Development

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Running in Development

**Server (with debug mode):**
```bash
cd server
python server.py
# Server runs with debug=True by default
```

**Client (with auto-reload):**
```bash
cd client
uvicorn client:app --host 0.0.0.0 --port 8000 --reload
```

### Project Structure
```
stat_server/
├── server/
│   ├── server.py           # Flask server application
│   ├── requirements.txt    # Server dependencies
│   ├── stats.db           # SQLite database (auto-created)
│   ├── .gitignore         # Server-specific gitignore
│   └── templates/         # HTML templates
│       ├── dashboard.html
│       ├── login.html
│       ├── manage.html
│       └── change_password.html
├── client/
│   ├── client.py          # FastAPI client application
│   ├── requirements.txt   # Client dependencies
│   ├── client_token.txt   # Persistent token (auto-created)
│   └── README.md          # Client-specific documentation
└── README.md              # This file
```

## 🔒 Production Deployment

### Security Checklist
- [ ] Change default admin password
- [ ] Update Flask secret key
- [ ] Use HTTPS in production
- [ ] Configure proper firewall rules
- [ ] Use environment variables for sensitive data
- [ ] Enable Flask production mode (`debug=False`)
- [ ] Set up proper logging
- [ ] Configure database backups

### Environment Variables
```bash
# Recommended production setup
export FLASK_SECRET_KEY="your-super-secret-key"
export ADMIN_USERNAME="your-admin-username" 
export ADMIN_PASSWORD="your-secure-password"
export DATABASE_PATH="/path/to/production/stats.db"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🐛 Troubleshooting

### Common Issues

**Client can't connect to server:**
- Check firewall settings on both machines
- Verify the client URL in server management
- Ensure client is running on the specified port

**Authentication failures:**
- Verify the token matches between client and server
- Check that client_token.txt exists and contains valid token
- Restart client to regenerate token if corrupted

**Database errors:**
- Ensure server has write permissions to database directory
- Check disk space availability
- Restart server to recreate database if corrupted

**Missing system information:**
- Ensure psutil is installed and working
- Check client logs for permission errors
- Verify client has access to system metrics

## 📊 Screenshots

### Dashboard View
The main dashboard provides an overview of all monitored systems with real-time status indicators.

### Computer Management
Easy addition and management of monitored computers through the web interface.

### Historical Charts
Track system performance trends over time with detailed historical data visualization.

---

**Created with ❤️ for distributed system monitoring**