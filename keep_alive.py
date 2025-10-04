from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return """
    <h1>🐻 Bear Hunt Rally Calculator Bot</h1>
    <p>✅ Bot is alive and running!</p>
    <p>🎯 Features:</p>
    <ul>
        <li>11 unique heroes with expedition skills</li>
        <li>Multiplicative bonuses for hero diversity</li>
        <li>Color-coded optimization results</li>
        <li>Support for duplicate heroes</li>
    </ul>
    <p>🚀 Use <code>!rally</code> in Discord to start!</p>
    """

@app.route('/health')
def health():
    return "OK"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Keep-alive web server started on port 8080")