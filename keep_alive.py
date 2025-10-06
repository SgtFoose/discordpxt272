from flask import Flask
import threading
import time
import os
from datetime import datetime
import urllib.request
import urllib.error

app = Flask('')

@app.route('/')
def home():
    return f"""
    <h1>🐻 Bear Hunt Rally Calculator Bot</h1>
    <p>✅ Bot is alive and running!</p>
    <p>🕐 Last check: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    <p>🎯 Features:</p>
    <ul>
        <li>11 unique heroes with expedition skills</li>
        <li>Multiplicative bonuses for hero diversity</li>
        <li>Color-coded optimization results</li>
        <li>Support for duplicate heroes</li>
    </ul>
    <p>🚀 Use <code>/rally_calculator</code> in Discord to start!</p>
    <p>🏓 Self-ping active every 20 minutes</p>
    """

@app.route('/health')
def health():
    return "OK"

@app.route('/ping')
def ping():
    return f"Pong! {datetime.now().strftime('%H:%M:%S')}"

def self_ping():
    """Ping the server every 20 minutes to keep it awake"""
    time.sleep(60)  # Wait 1 minute before starting
    while True:
        try:
            time.sleep(1200)  # 20 minutes
            # Use urllib instead of requests (built-in Python library)
            with urllib.request.urlopen('http://localhost:8080/ping', timeout=10) as response:
                result = response.read().decode()
                print(f"🏓 Self-ping successful: {result}")
        except Exception as e:
            print(f"❌ Self-ping failed: {e}")

def run():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

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
    print("🏓 Self-ping mechanism started (every 20 minutes)")