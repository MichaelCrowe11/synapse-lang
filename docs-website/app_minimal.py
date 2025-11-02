"""
Minimal Synapse Documentation App for Testing Deployment
"""

import os

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")

# Minimal HTML template
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Synapse Language v2</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 12px;
            padding: 40px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            font-size: 48px;
            margin-bottom: 20px;
        }
        .status {
            background: #10b981;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            display: inline-block;
            margin-bottom: 20px;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }
        .feature {
            padding: 20px;
            background: #f3f4f6;
            border-radius: 8px;
        }
        .links {
            margin-top: 40px;
            display: flex;
            gap: 20px;
        }
        a {
            color: #6366f1;
            text-decoration: none;
            font-weight: 500;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="status">✅ Deployment Successful</div>
        <h1>🧠 Synapse Language v2.3.2</h1>
        <p>Modern documentation site with real-time features</p>

        <div class="features">
            <div class="feature">
                <h3>✨ Modern UI</h3>
                <p>Vercel/npm-inspired design</p>
            </div>
            <div class="feature">
                <h3>🚀 Real-time</h3>
                <p>WebSocket collaboration</p>
            </div>
            <div class="feature">
                <h3>📚 Interactive</h3>
                <p>Live code playground</p>
            </div>
            <div class="feature">
                <h3>🎨 Themes</h3>
                <p>Dark/light mode support</p>
            </div>
        </div>

        <div class="links">
            <a href="/health">Health Check</a>
            <a href="/api/status">API Status</a>
            <a href="https://github.com/michaelcrowe11/synapse-lang">GitHub</a>
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "version": "2.3.2",
        "deployment": "successful"
    })

@app.route("/api/status")
def status():
    return jsonify({
        "status": "operational",
        "app": "synapse-lang-docs",
        "version": "2.3.2",
        "features": [
            "Modern UI",
            "Real-time collaboration",
            "Code playground",
            "API documentation"
        ]
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
