# 🚀 System Statistics - Startup Scripts

Easy-to-use startup scripts for both Windows and Linux/macOS to quickly launch your distributed system monitoring solution.

## 📁 Available Scripts

### 🖥️ **Main Startup Manager**
- **Linux/macOS**: `./start_system.sh`
- **Windows**: `start_system.bat`

### 🌐 **Server Scripts (Dashboard)**
- **Linux/macOS**: `./server/start_server.sh`
- **Windows**: `server/start_server.bat`

### 📡 **Client Scripts (Monitoring Agent)**  
- **Linux/macOS**: `./client/start_client.sh`
- **Windows**: `client/start_client.bat`

## 🚀 Quick Start

### Option 1: Use the Main Startup Manager (Recommended)

**Linux/macOS:**
```bash
cd stat_server
./start_system.sh
```

**Windows:**
```cmd
cd stat_server
start_system.bat
```

This will give you a menu to choose what to start:
1. Server only
2. Client only  
3. Both server and client
4. Exit

### Option 2: Start Components Individually

**Start Server (Dashboard):**
```bash
# Linux/macOS
cd stat_server/server
./start_server.sh

# Windows
cd stat_server\server
start_server.bat
```

**Start Client (Monitoring Agent):**
```bash
# Linux/macOS  
cd stat_server/client
./start_client.sh

# Windows
cd stat_server\client
start_client.bat
```

## ✨ What the Scripts Do

### 🔧 **Automatic Setup**
- ✅ Check if Python is installed
- ✅ Create virtual environment if it doesn't exist
- ✅ Install dependencies automatically
- ✅ Activate virtual environment
- ✅ Start the appropriate service

### 📋 **Information Display**
- **Server**: Shows login credentials and dashboard URL
- **Client**: Shows token, hostname, and setup instructions
- **Both**: Clear instructions for connecting client to server

### 🛡️ **Error Handling**
- Validates Python installation
- Checks for dependency installation errors
- Provides clear error messages
- Graceful failure handling

## 📊 What You'll See

### 🌐 Server Startup
```
=== System Statistics Server Startup ===
Starting Flask Dashboard Server...
Activating virtual environment...
Requirements already installed

==================================
  SYSTEM STATISTICS SERVER
==================================
Server will start on: http://localhost:8001
Default login:
  Username: admin
  Password: admin123

⚠️  IMPORTANT: Change default password after first login!
==================================

Starting server...
```

### 📡 Client Startup  
```
=== System Statistics Client Startup ===
Starting FastAPI Monitoring Client...
Activating virtual environment...
Requirements already installed

==================================
  SYSTEM STATISTICS CLIENT
==================================
Computer: laptop-hostname
Client will start on port: 8000
Local access: http://localhost:8000
Network access: http://192.168.1.100:8000

📋 SETUP INSTRUCTIONS:
1. Copy the token that will be displayed below
2. Open your server dashboard at http://server-ip:8001  
3. Login and go to 'Manage Computers'
4. Add this computer using:
   - Name: laptop-hostname (or custom name)
   - URL: http://192.168.1.100:8000
   - Token: [copy from below]
==================================

=== CLIENT STARTED ===
Computer: laptop-hostname
Token: a79a6575-3178-44fa-8ed0-48581ae5caec
Add this computer to the dashboard using the above token
======================
```

## 🔧 Prerequisites

### Required Software
- **Python 3.8+** installed and in PATH
- **Internet connection** (for downloading dependencies)
- **Network access** between client and server machines

### First Time Setup
1. **Download/clone** the project
2. **Run the startup script** - it will handle everything else automatically
3. **Change default password** on first server login

## 🌐 Network Setup

### For Local Testing
- Start both server and client on the same machine
- Server: `http://localhost:8001`  
- Client: `http://localhost:8000`

### For Distributed Monitoring
1. **Start server** on one machine (e.g., main computer)
2. **Start client** on machines you want to monitor
3. **Note the IP addresses** displayed by the scripts
4. **Add clients** to server dashboard using the provided URLs and tokens

## 🛠️ Troubleshooting

### Common Issues

**"Python not found"**
- Install Python 3.8+ from https://python.org
- Make sure Python is added to PATH during installation
- Restart terminal/command prompt after installation

**"Permission denied" (Linux/macOS)**
```bash
chmod +x start_system.sh
chmod +x server/start_server.sh  
chmod +x client/start_client.sh
```

**"Cannot create virtual environment"**
- Ensure you have write permissions in the directory
- Check available disk space
- Try running as administrator/sudo (not recommended for regular use)

**"Failed to install requirements"**  
- Check internet connection
- Try updating pip: `python -m pip install --upgrade pip`
- Check firewall/proxy settings

**Client can't connect to server**
- Verify server is running on port 8001
- Check firewall settings (allow ports 8000 and 8001)
- Ensure client URL in dashboard matches client's actual IP
- Verify token matches between client and server

### Network Configuration

**Firewall Ports to Allow:**
- **Server**: Port 8001 (inbound)
- **Client**: Port 8000 (inbound)  

**For Windows Firewall:**
```cmd
netsh advfirewall firewall add rule name="System Stats Server" dir=in action=allow protocol=TCP localport=8001
netsh advfirewall firewall add rule name="System Stats Client" dir=in action=allow protocol=TCP localport=8000
```

**For Linux iptables:**
```bash
sudo ufw allow 8001/tcp
sudo ufw allow 8000/tcp  
```

## 📈 Advanced Usage

### Custom Ports
Edit the Python files to change default ports:
- **Server**: Modify `port=8001` in `server/server.py`
- **Client**: Modify `PORT = 8000` in `client/client.py`

### Production Deployment
For production use:
1. **Change default passwords** immediately
2. **Use environment variables** for sensitive data
3. **Set up proper SSL/TLS** certificates  
4. **Configure reverse proxy** (nginx/Apache)
5. **Set up systemd services** (Linux) or Windows Services

### Running as System Services

**Linux (systemd):**
```bash
# Create service files in /etc/systemd/system/
sudo systemctl enable stats-server.service
sudo systemctl start stats-server.service
```

**Windows (NSSM):**
```cmd
# Use NSSM (Non-Sucking Service Manager) to create Windows services
nssm install "Stats Server" "C:\path\to\start_server.bat"
```

---

**🎯 These startup scripts make it incredibly easy to deploy your system monitoring solution across multiple machines with just a double-click or single command!**