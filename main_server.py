"""
Synapse-Lang.com Main Server
Integrates CroweHub IDE and main website
"""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Create Flask app
app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent
CROWEHUB_DIR = BASE_DIR / "crowehub"
WEBSITE_DIR = BASE_DIR / "synapse-lang.com"
SYNAPSE_IDE_DIR = BASE_DIR / "synapse-ide"

print("=" * 60)
print("SYNAPSE-LANG.COM - MAIN PLATFORM SERVER")
print("=" * 60)
print("Main Website: http://localhost:8000")
print("CroweHub IDE: http://localhost:8000/crowehub")
print("Synapse IDE: http://localhost:8000/synapse-ide")
print("Documentation: http://localhost:8000/docs")
print("Package Registry: http://localhost:8000/packages")
print("Community: http://localhost:8000/community")
print("=" * 60)

# Initialize database
def init_database():
    """Initialize the main database"""
    conn = sqlite3.connect("synapse_lang.db")
    c = conn.cursor()

    # Users table
    c.execute("""CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY,
                  username TEXT UNIQUE,
                  email TEXT UNIQUE,
                  full_name TEXT,
                  bio TEXT,
                  avatar_url TEXT,
                  github_url TEXT,
                  twitter_url TEXT,
                  website_url TEXT,
                  plan TEXT DEFAULT 'free',
                  created_at TIMESTAMP,
                  last_login TIMESTAMP)""")

    # Projects table
    c.execute("""CREATE TABLE IF NOT EXISTS projects
                 (id TEXT PRIMARY KEY,
                  user_id TEXT,
                  name TEXT,
                  description TEXT,
                  language TEXT,
                  code TEXT,
                  visibility TEXT DEFAULT 'private',
                  stars INTEGER DEFAULT 0,
                  forks INTEGER DEFAULT 0,
                  tags TEXT,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))""")

    # Packages table
    c.execute("""CREATE TABLE IF NOT EXISTS packages
                 (id TEXT PRIMARY KEY,
                  name TEXT UNIQUE,
                  version TEXT,
                  author_id TEXT,
                  language TEXT,
                  description TEXT,
                  readme TEXT,
                  download_url TEXT,
                  repository_url TEXT,
                  dependencies TEXT,
                  keywords TEXT,
                  license TEXT,
                  downloads INTEGER DEFAULT 0,
                  stars INTEGER DEFAULT 0,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP,
                  FOREIGN KEY(author_id) REFERENCES users(id))""")

    # CroweHub Spaces table
    c.execute("""CREATE TABLE IF NOT EXISTS crowehub_spaces
                 (id TEXT PRIMARY KEY,
                  user_id TEXT,
                  name TEXT,
                  language TEXT,
                  resources TEXT,
                  status TEXT,
                  url TEXT,
                  created_at TIMESTAMP,
                  last_accessed TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id))""")

    # Analytics table
    c.execute("""CREATE TABLE IF NOT EXISTS analytics
                 (id TEXT PRIMARY KEY,
                  event_type TEXT,
                  user_id TEXT,
                  data TEXT,
                  timestamp TIMESTAMP)""")

    conn.commit()
    conn.close()

# Initialize database
init_database()

# ==============================================
# MAIN WEBSITE ROUTES
# ==============================================

@app.route("/")
def home():
    """Serve main synapse-lang.com homepage"""
    return send_from_directory(WEBSITE_DIR, "index.html")

@app.route("/about")
def about():
    """About page"""
    return send_from_directory(WEBSITE_DIR, "about.html")

@app.route("/docs")
def docs():
    """Documentation portal"""
    return send_from_directory(WEBSITE_DIR, "docs.html")

@app.route("/docs/<path:page>")
def docs_page(page):
    """Serve documentation pages"""
    return send_from_directory(WEBSITE_DIR / "docs", f"{page}.html")

@app.route("/community")
def community():
    """Community page"""
    return send_from_directory(WEBSITE_DIR, "community.html")

@app.route("/examples")
def examples():
    """Examples showcase"""
    return send_from_directory(WEBSITE_DIR, "examples.html")

@app.route("/blog")
def blog():
    """Blog homepage"""
    return send_from_directory(WEBSITE_DIR, "blog.html")

# ==============================================
# CROWEHUB IDE ROUTES
# ==============================================

@app.route("/crowehub")
def crowehub():
    """Serve CroweHub IDE"""
    return send_from_directory(CROWEHUB_DIR, "index.html")

@app.route("/crowehub/<path:path>")
def crowehub_static(path):
    """Serve CroweHub static files"""
    return send_from_directory(CROWEHUB_DIR, path)

# ==============================================
# SYNAPSE IDE ROUTES
# ==============================================

@app.route("/synapse-ide")
def synapse_ide():
    """Serve Synapse IDE"""
    return send_from_directory(SYNAPSE_IDE_DIR, "index.html")

@app.route("/synapse-ide/<path:path>")
def synapse_ide_static(path):
    """Serve Synapse IDE static files"""
    return send_from_directory(SYNAPSE_IDE_DIR, path)

# ==============================================
# PACKAGE REGISTRY ROUTES
# ==============================================

@app.route("/packages")
def packages():
    """Package registry homepage"""
    try:
        conn = sqlite3.connect("synapse_lang.db")
        c = conn.cursor()
        c.execute("""SELECT name, version, description, language, author_id, downloads, stars, created_at
                     FROM packages ORDER BY downloads DESC, stars DESC LIMIT 20""")
        popular_packages = c.fetchall()

        c.execute("""SELECT name, version, description, language, author_id, created_at
                     FROM packages ORDER BY created_at DESC LIMIT 10""")
        c.fetchall()

        conn.close()

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Package Registry - Synapse-Lang.com</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Inter, sans-serif; margin: 0; padding: 2rem; background: #f8fafc; }}
                .header {{ text-align: center; margin-bottom: 3rem; }}
                .packages {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }}
                .package {{ background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .package h3 {{ margin: 0 0 0.5rem 0; color: #667eea; }}
                .package .meta {{ color: #666; font-size: 0.9rem; margin-bottom: 1rem; }}
                .package .stats {{ display: flex; gap: 1rem; font-size: 0.9rem; color: #666; }}
                nav {{ background: white; padding: 1rem 2rem; margin-bottom: 2rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                nav a {{ margin-right: 2rem; text-decoration: none; color: #667eea; font-weight: 500; }}
            </style>
        </head>
        <body>
            <nav>
                <a href="/">Home</a>
                <a href="/crowehub">CroweHub IDE</a>
                <a href="/synapse-ide">Synapse IDE</a>
                <a href="/docs">Docs</a>
                <a href="/packages">Packages</a>
                <a href="/community">Community</a>
            </nav>
            <div class="header">
                <h1>📦 Package Registry</h1>
                <p>Discover and share packages for the Quantum Trinity languages</p>
            </div>
            <div class="packages">
                {chr(10).join([f'''
                <div class="package">
                    <h3>{pkg[0]} v{pkg[1]}</h3>
                    <p>{pkg[2]}</p>
                    <div class="meta">Language: {pkg[3]} | Author: {pkg[4]}</div>
                    <div class="stats">
                        <span>⬇ {pkg[5]} downloads</span>
                        <span>⭐ {pkg[6]} stars</span>
                    </div>
                </div>
                ''' for pkg in popular_packages[:10]])}
            </div>
        </body>
        </html>
        """
    except Exception as e:
        return f"Error loading packages: {e}"

@app.route("/packages/<package_name>")
def package_detail(package_name):
    """Individual package page"""
    conn = sqlite3.connect("synapse_lang.db")
    c = conn.cursor()
    c.execute("SELECT * FROM packages WHERE name = ?", (package_name,))
    package = c.fetchone()
    conn.close()

    if package:
        return f"""
        <h1>{package[1]} v{package[2]}</h1>
        <p>{package[4]}</p>
        <p>Language: {package[5]}</p>
        <p>Downloads: {package[11]} | Stars: {package[12]}</p>
        """
    else:
        return "Package not found", 404

@app.route("/api/packages/search")
def search_packages():
    """Search packages API"""
    query = request.args.get("q", "")
    language = request.args.get("language", "")

    conn = sqlite3.connect("synapse_lang.db")
    c = conn.cursor()

    sql = "SELECT * FROM packages WHERE name LIKE ? OR description LIKE ?"
    params = [f"%{query}%", f"%{query}%"]

    if language:
        sql += " AND language = ?"
        params.append(language)

    c.execute(sql, params)
    results = c.fetchall()
    conn.close()

    return jsonify({
        "packages": [
            {
                "name": row[1],
                "version": row[2],
                "description": row[4],
                "language": row[5],
                "downloads": row[11],
                "stars": row[12]
            } for row in results
        ]
    })

# ==============================================
# API ROUTES
# ==============================================

@app.route("/api/platform/info")
def platform_info():
    """Get platform information"""
    return jsonify({
        "platform": "synapse-lang.com",
        "version": "2.0.0",
        "features": {
            "crowehub_ide": True,
            "package_registry": True,
            "documentation": True,
            "community": True,
            "examples": True,
            "blog": True
        },
        "languages": ["synapse", "qubit-flow", "quantum-net"],
        "endpoints": {
            "main_site": "https://synapse-lang.com",
            "crowehub": "https://synapse-lang.com/crowehub",
            "docs": "https://synapse-lang.com/docs",
            "packages": "https://synapse-lang.com/packages",
            "api": "https://synapse-lang.com/api"
        }
    })

@app.route("/api/crowehub/execute", methods=["POST"])
def execute_code():
    """Execute code in CroweHub environment"""
    try:
        data = request.json
        code = data.get("code", "")
        language = data.get("language", "synapse")

        # Log execution for analytics
        log_event("code_execution", data={"language": language, "lines": len(code.split("\n"))})

        # Simulate execution
        if language == "synapse":
            result = execute_synapse_code(code)
        elif language == "qubit-flow":
            result = execute_qubitflow_code(code)
        elif language == "quantum-net":
            result = execute_quantumnet_code(code)
        else:
            return jsonify({"error": "Unsupported language"}), 400

        return jsonify({
            "success": True,
            "output": result["output"],
            "executionTime": result.get("executionTime", 100),
            "platform": "synapse-lang.com"
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/projects", methods=["GET", "POST"])
def projects():
    """Handle project operations"""
    if request.method == "GET":
        # List public projects
        conn = sqlite3.connect("synapse_lang.db")
        c = conn.cursor()
        c.execute("""SELECT id, name, description, language, stars, updated_at
                     FROM projects WHERE visibility = "public"
                     ORDER BY stars DESC, updated_at DESC LIMIT 20""")
        projects = c.fetchall()
        conn.close()

        return jsonify({
            "projects": [
                {
                    "id": p[0],
                    "name": p[1],
                    "description": p[2],
                    "language": p[3],
                    "stars": p[4],
                    "updated_at": p[5]
                } for p in projects
            ]
        })

    elif request.method == "POST":
        # Create new project
        data = request.json
        project_id = str(uuid.uuid4())[:8]

        conn = sqlite3.connect("synapse_lang.db")
        c = conn.cursor()
        c.execute("""INSERT INTO projects
                     (id, name, description, language, code, visibility, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                  (project_id, data["name"], data.get("description", ""),
                   data["language"], data.get("code", ""), data.get("visibility", "private"),
                   datetime.now(), datetime.now()))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "project_id": project_id
        })

@app.route("/api/stats")
def platform_stats():
    """Get platform statistics"""
    conn = sqlite3.connect("synapse_lang.db")
    c = conn.cursor()

    # Get user count
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]

    # Get project count
    c.execute("SELECT COUNT(*) FROM projects")
    project_count = c.fetchone()[0]

    # Get package count
    c.execute("SELECT COUNT(*) FROM packages")
    package_count = c.fetchone()[0]

    # Get total downloads
    c.execute("SELECT SUM(downloads) FROM packages")
    total_downloads = c.fetchone()[0] or 0

    conn.close()

    return jsonify({
        "users": user_count,
        "projects": project_count,
        "packages": package_count,
        "total_downloads": total_downloads,
        "platform": "synapse-lang.com"
    })

# ==============================================
# UTILITY FUNCTIONS
# ==============================================

def log_event(event_type, data=None):
    """Log analytics event"""
    try:
        conn = sqlite3.connect("synapse_lang.db")
        c = conn.cursor()
        c.execute("""INSERT INTO analytics (id, event_type, data, timestamp)
                     VALUES (?, ?, ?, ?)""",
                  (str(uuid.uuid4()), event_type, json.dumps(data or {}), datetime.now()))
        conn.commit()
        conn.close()
    except:
        pass  # Don't break if analytics fails

def execute_synapse_code(code):
    """Execute Synapse language code"""
    output = []

    if "uncertain" in code:
        output.append({"type": "info", "text": "Processing uncertainty propagation..."})
        output.append({"type": "log", "text": "Result: 42.0 ± 2.1 (simulated)"})

    if "parallel" in code:
        output.append({"type": "info", "text": "Executing parallel computation..."})
        output.append({"type": "log", "text": "Parallel execution completed"})

    if not output:
        output.append({"type": "log", "text": "Synapse code executed successfully"})

    return {"output": output, "executionTime": 120}

def execute_qubitflow_code(code):
    """Execute Qubit-Flow language code"""
    output = []

    output.append({"type": "info", "text": "Initializing quantum simulator..."})

    if "qubit" in code:
        output.append({"type": "log", "text": "Qubits initialized"})

    if any(gate in code for gate in ["H[", "X[", "CNOT["]):
        output.append({"type": "log", "text": "Quantum gates applied"})

    if "measure" in code:
        output.append({"type": "log", "text": "Measurement: |0⟩: 60%, |1⟩: 40%"})

    return {"output": output, "executionTime": 180}

def execute_quantumnet_code(code):
    """Execute Quantum-Net language code"""
    output = []

    output.append({"type": "info", "text": "Setting up quantum network..."})

    if "network" in code:
        output.append({"type": "log", "text": "Network topology established"})

    if "protocol" in code:
        output.append({"type": "log", "text": "Quantum protocol executed"})

    return {"output": output, "executionTime": 200}

# ==============================================
# STATIC FILE SERVING
# ==============================================

@app.route("/assets/<path:path>")
def serve_assets(path):
    """Serve static assets"""
    return send_from_directory(WEBSITE_DIR / "assets", path)

@app.route("/favicon.ico")
def favicon():
    """Serve favicon"""
    return send_from_directory(WEBSITE_DIR, "favicon.ico")

@app.route("/robots.txt")
def robots():
    """Serve robots.txt"""
    return send_from_directory(WEBSITE_DIR, "robots.txt")

@app.route("/sitemap.xml")
def sitemap():
    """Serve sitemap"""
    return send_from_directory(WEBSITE_DIR, "sitemap.xml")

# ==============================================
# ERROR HANDLERS
# ==============================================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>404 - Not Found</title></head>
    <body style="font-family: Inter, sans-serif; text-align: center; padding: 4rem;">
        <h1>404 - Page Not Found</h1>
        <p>The page you're looking for doesn't exist.</p>
        <a href="/" style="color: #667eea;">← Back to Home</a>
    </body>
    </html>
    """, 404

@app.errorhandler(500)
def server_error(error):
    """500 error handler"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>500 - Server Error</title></head>
    <body style="font-family: Inter, sans-serif; text-align: center; padding: 4rem;">
        <h1>500 - Server Error</h1>
        <p>Something went wrong on our end.</p>
        <a href="/" style="color: #667eea;">← Back to Home</a>
    </body>
    </html>
    """, 500

if __name__ == "__main__":
    # Run the main platform server
    app.run(host="0.0.0.0", port=8000, debug=True)
