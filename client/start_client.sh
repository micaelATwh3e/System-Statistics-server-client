#!/bin/bash

# System Statistics Client Startup Script (Linux/macOS)
# This script starts the FastAPI monitoring client

echo "=== System Statistics Client Startup ==="
echo "Starting FastAPI Monitoring Client..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLIENT_DIR="$SCRIPT_DIR"

# Navigate to client directory
cd "$CLIENT_DIR"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed or not in PATH"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/requirements_installed.flag" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        touch venv/requirements_installed.flag
        echo "Requirements installed successfully"
    else
        echo "Error: Failed to install requirements"
        exit 1
    fi
else
    echo "Requirements already installed"
fi

# Get hostname and IP
HOSTNAME=$(hostname)
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")

# Display client information
echo ""
echo "=================================="
echo "  SYSTEM STATISTICS CLIENT"
echo "=================================="
echo "Computer: $HOSTNAME"
echo "Client will start on port: 8000"
echo "Local access: http://localhost:8000"
echo "Network access: http://$LOCAL_IP:8000"
echo ""
echo "📋 SETUP INSTRUCTIONS:"
echo "1. Copy the token that will be displayed below"
echo "2. Open your server dashboard at http://server-ip:8001"
echo "3. Login and go to 'Manage Computers'"
echo "4. Add this computer using:"
echo "   - Name: $HOSTNAME (or custom name)"
echo "   - URL: http://$LOCAL_IP:8000"
echo "   - Token: [copy from below]"
echo "=================================="
echo ""

# Start the client
echo "Starting client..."
python client.py