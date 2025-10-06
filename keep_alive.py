from flask import Flask
import threading
import time
import os
from datetime import datetime

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
    """

@app.route('/health')
def health():
    return "OK"

@app.route('/ping')
def ping():
    return f"Pong! {datetime.now().strftime('%H:%M:%S')}"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    # Start Flask server
    server_thread = threading.Thread(target=run)
    server_thread.daemon = True
    server_thread.start()
    print("🌐 Keep-alive web server started on port 8080")