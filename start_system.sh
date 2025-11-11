#!/bin/bash

# System Statistics - Complete Startup Script (Linux/macOS)
# This script can start both server and client

echo "=== System Statistics Startup Manager ==="
echo ""
echo "What would you like to start?"
echo "1) Server only (Flask Dashboard)"
echo "2) Client only (Monitoring Agent)"  
echo "3) Both Server and Client"
echo "4) Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "Starting Server..."
        cd server
        ./start_server.sh
        ;;
    2)
        echo "Starting Client..."
        cd client
        ./start_client.sh
        ;;
    3)
        echo "Starting both Server and Client..."
        echo "The server will start first, then the client in 5 seconds..."
        
        # Start server in background
        cd server
        gnome-terminal -- bash -c "./start_server.sh; exec bash" 2>/dev/null || \
        xterm -e "./start_server.sh" 2>/dev/null || \
        konsole -e "./start_server.sh" 2>/dev/null || \
        (echo "Could not open new terminal. Starting server in background..." && ./start_server.sh &)
        
        # Wait a moment for server to start
        sleep 5
        
        # Start client in new terminal or current terminal
        cd ../client
        gnome-terminal -- bash -c "./start_client.sh; exec bash" 2>/dev/null || \
        xterm -e "./start_client.sh" 2>/dev/null || \
        konsole -e "./start_client.sh" 2>/dev/null || \
        ./start_client.sh
        ;;
    4)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac