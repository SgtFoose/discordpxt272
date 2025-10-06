from flask import Flask
import threading
import requests
import time
import os
from datetime import datetime

app = Flask('')

@app.route('/')
def home():
    return f"""
    <h1>🐻 Bear Hunt Rally Calculator Bot</h1>
    <p>✅ Bot is alive and running!</p>
    <p>🕐 Last ping: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    <p>🎯 Features:</p>
    <ul>
        <li>11 unique heroes with expedition skills</li>
        <li>Multiplicative bonuses for hero diversity</li>
        <li>Color-coded optimization results</li>
        <li>Support for duplicate heroes</li>
    </ul>
    <p>🚀 Use <code>/rally_calculator</code> in Discord to start!</p>
    """

@app.route('/health')
def health():
    return "OK"

@app.route('/ping')
def ping():
    return f"Pong! {datetime.now().strftime('%H:%M:%S')}"

def self_ping():
    """Ping the server every 25 minutes to keep it awake"""
    while True:
        try:
            time.sleep(1500)  # 25 minutes
            # Try to get the service URL from environment or use localhost
            service_url = os.getenv('KOYEB_PUBLIC_DOMAIN', 'http://localhost:8080')
            if not service_url.startswith('http'):
                service_url = f"https://{service_url}"
            
            response = requests.get(f"{service_url}/ping", timeout=10)
            print(f"🏓 Self-ping successful: {response.status_code} at {datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Self-ping failed: {e}")

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Start Flask server
    server_thread = threading.Thread(target=run)
    server_thread.daemon = True
    server_thread.start()
    print("🌐 Keep-alive web server started on port 8080")
    
    # Start self-ping mechanism
    ping_thread = threading.Thread(target=self_ping)
    ping_thread.daemon = True
    ping_thread.start()
    print("🏓 Self-ping mechanism started (every 25 minutes)")