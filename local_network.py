"""
Run Sndr on your local network

This script starts Sndr on your local IP address so you can access
it from other devices on the same network (like your phone).

Note: This is for TESTING ONLY and won't provide HTTPS, 
so PWA installation might not work properly.
"""

import os
import socket
from app import app, init_db, DATABASE

# Initialize the database if it doesn't exist
if not os.path.exists(DATABASE):
    with app.app_context():
        init_db()
        print("Database initialized")

# Get local IP address for LAN access
def get_local_ip():
    try:
        # Connect to a public DNS to get local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"  # Fallback to localhost

local_ip = get_local_ip()
print("\n===================================================")
print(f"RUNNING SNDR ON LOCAL NETWORK: http://{local_ip}:5000")
print("===================================================\n")
print("Access the app from your phone by:")
print(f"1. Connecting to the same WiFi network as this computer")
print(f"2. Opening http://{local_ip}:5000 in your phone's browser")
print("\nNOTE: This won't use HTTPS, so some PWA features may not work properly.")
print("For full PWA functionality, deploy to a hosting service with HTTPS.")
print("See DEPLOY.md for hosting instructions.")
print("\nPress CTRL+C to stop the server when done.")
print("===================================================\n")

# Run the app with the host set to the local IP
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False) 