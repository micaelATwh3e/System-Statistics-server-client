#!/bin/bash

# System Statistics Server Startup Script (Linux/macOS)
# This script starts the Flask dashboard server

echo "=== System Statistics Server Startup ==="
echo "Starting Flask Dashboard Server..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_DIR="$SCRIPT_DIR"

# Navigate to server directory
cd "$SERVER_DIR"

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

# Display server information
echo ""
echo "=================================="
echo "  SYSTEM STATISTICS SERVER"
echo "=================================="
echo "Server will start on: http://localhost:8001"
echo "Default login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "⚠️  IMPORTANT: Change default password after first login!"
echo "=================================="
echo ""

# Start the server
echo "Starting server..."
python server.py