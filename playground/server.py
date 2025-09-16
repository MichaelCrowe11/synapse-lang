"""
Quantum Trinity Playground Server

Backend API for code execution, sharing, and persistence.
"""

import json
import sqlite3
import time
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=".")
CORS(app)

# Initialize database
DB_PATH = "playground.db"

def init_db():
    """Initialize SQLite database for storing shared code."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS shared_code
                 (id TEXT PRIMARY KEY,
                  language TEXT,
                  code TEXT,
                  title TEXT,
                  description TEXT,
                  created_at TIMESTAMP,
                  views INTEGER DEFAULT 0)""")

    c.execute("""CREATE TABLE IF NOT EXISTS execution_logs
                 (id TEXT PRIMARY KEY,
                  language TEXT,
                  code TEXT,
                  result TEXT,
                  execution_time REAL,
                  created_at TIMESTAMP)""")

    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Serve the main playground page
@app.route("/")
def index():
    """Serve the main playground HTML."""
    return send_from_directory(".", "index.html")

# Serve static files
@app.route("/<path:path>")
def serve_static(path):
    """Serve static files (CSS, JS, etc.)."""
    return send_from_directory(".", path)

# API endpoint for code execution
@app.route("/api/execute", methods=["POST"])
def execute_code():
    """Execute code in a sandboxed environment."""
    try:
        data = request.json
        code = data.get("code", "")
        language = data.get("language", "synapse")

        start_time = time.time()

        # Execute based on language
        if language == "synapse":
            result = execute_synapse(code)
        elif language == "qubit-flow":
            result = execute_qubit_flow(code)
        elif language == "quantum-net":
            result = execute_quantum_net(code)
        else:
            return jsonify({"error": "Unknown language"}), 400

        execution_time = (time.time() - start_time) * 1000  # ms

        # Log execution
        log_execution(language, code, result, execution_time)

        return jsonify({
            "success": True,
            "output": result["output"],
            "executionTime": execution_time,
            "visualizations": result.get("visualizations", [])
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def execute_synapse(code):
    """Execute Synapse language code."""
    output = []
    visualizations = []

    # Parse and execute Synapse code
    lines = code.split("\n")

    for line in lines:
        line = line.strip()

        # Handle uncertain values
        if "uncertain" in line and "±" in line:
            # Extract variable name and values
            import re
            match = re.match(r"uncertain\s+(\w+)\s*=\s*([\d.]+)\s*±\s*([\d.]+)", line)
            if match:
                var_name, value, uncertainty = match.groups()
                output.append({
                    "type": "log",
                    "text": f"{var_name} = {value} ± {uncertainty}"
                })

        # Handle print statements
        elif line.startswith("print("):
            content = line[6:-1]  # Extract content between print()
            output.append({
                "type": "log",
                "text": content.strip('"\'')
            })

        # Handle Monte Carlo
        elif "monte_carlo" in line:
            output.append({
                "type": "info",
                "text": "Running Monte Carlo simulation..."
            })
            # Add visualization
            visualizations.append({
                "type": "histogram",
                "data": generate_monte_carlo_data()
            })

    return {"output": output, "visualizations": visualizations}

def execute_qubit_flow(code):
    """Execute Qubit-Flow language code."""
    output = []
    visualizations = []

    # Parse quantum circuit code
    lines = code.split("\n")
    qubits = {}

    for line in lines:
        line = line.strip()

        # Handle qubit declarations
        if line.startswith("qubit"):
            import re
            match = re.match(r"qubit\s+(\w+)\s*=\s*\|([01])\⟩", line)
            if match:
                name, state = match.groups()
                qubits[name] = state
                output.append({
                    "type": "log",
                    "text": f"Created qubit {name} in state |{state}⟩"
                })

        # Handle gates
        elif any(gate in line for gate in ["H[", "X[", "CNOT[", "measure"]):
            output.append({
                "type": "info",
                "text": f"Applying: {line}"
            })

    # Add quantum state visualization
    if qubits:
        visualizations.append({
            "type": "quantum_state",
            "qubits": len(qubits),
            "amplitudes": [0.707, 0, 0, 0.707]  # Example Bell state
        })

    return {"output": output, "visualizations": visualizations}

def execute_quantum_net(code):
    """Execute Quantum-Net language code."""
    output = []

    # Parse network code
    lines = code.split("\n")

    for line in lines:
        line = line.strip()

        # Handle network creation
        if "network" in line:
            output.append({
                "type": "log",
                "text": "Creating quantum network..."
            })

        # Handle node definitions
        elif "nodes:" in line:
            output.append({
                "type": "info",
                "text": f"Network configuration: {line}"
            })

    return {"output": output}

def generate_monte_carlo_data():
    """Generate sample Monte Carlo data for visualization."""
    import math
    import random

    # Generate normal distribution
    data = []
    for _ in range(1000):
        value = random.gauss(10, 2)
        data.append(value)

    return {
        "values": data,
        "mean": sum(data) / len(data),
        "std": math.sqrt(sum((x - sum(data)/len(data))**2 for x in data) / len(data))
    }

# API endpoint for sharing code
@app.route("/api/share", methods=["POST"])
def share_code():
    """Share code and generate a unique URL."""
    try:
        data = request.json
        code = data.get("code", "")
        language = data.get("language", "synapse")
        title = data.get("title", "Untitled")
        description = data.get("description", "")

        # Generate unique ID
        share_id = str(uuid.uuid4())[:8]

        # Store in database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO shared_code
                     (id, language, code, title, description, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (share_id, language, code, title, description, datetime.now()))
        conn.commit()
        conn.close()

        return jsonify({
            "success": True,
            "shareId": share_id,
            "shareUrl": f"/playground?share={share_id}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint for loading shared code
@app.route("/api/load/<share_id>")
def load_shared_code(share_id):
    """Load shared code by ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Get shared code
        c.execute("""SELECT language, code, title, description
                     FROM shared_code WHERE id = ?""", (share_id,))
        result = c.fetchone()

        if result:
            # Update view count
            c.execute("""UPDATE shared_code SET views = views + 1
                        WHERE id = ?""", (share_id,))
            conn.commit()

            language, code, title, description = result
            return jsonify({
                "success": True,
                "language": language,
                "code": code,
                "title": title,
                "description": description
            })
        else:
            return jsonify({"error": "Code not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# API endpoint for getting examples
@app.route("/api/examples/<language>")
def get_examples(language):
    """Get examples for a specific language."""
    # This would normally load from the examples.js file
    # For now, return a simple example
    examples = {
        "synapse": [
            {
                "id": "hello-uncertainty",
                "title": "Hello Uncertainty",
                "code": 'uncertain x = 10 ± 0.5\nprint(f"Value: {x}")'
            }
        ],
        "qubit-flow": [
            {
                "id": "bell-state",
                "title": "Bell State",
                "code": "qubit q0 = |0⟩\nqubit q1 = |0⟩\nH[q0]\nCNOT[q0, q1]"
            }
        ],
        "quantum-net": [
            {
                "id": "simple-network",
                "title": "Simple Network",
                "code": 'network qnet {\n  nodes: ["Alice", "Bob"]\n}'
            }
        ]
    }

    return jsonify(examples.get(language, []))

# API endpoint for saving user progress
@app.route("/api/save-progress", methods=["POST"])
def save_progress():
    """Save user's code progress."""
    try:
        data = request.json
        user_id = data.get("userId", "anonymous")
        code = data.get("code", "")
        language = data.get("language", "synapse")

        # Save to user-specific file
        save_path = Path(f"user_saves/{user_id}_{language}.txt")
        save_path.parent.mkdir(exist_ok=True)

        with open(save_path, "w") as f:
            f.write(code)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def log_execution(language, code, result, execution_time):
    """Log code execution for analytics."""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""INSERT INTO execution_logs
                     (id, language, code, result, execution_time, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (str(uuid.uuid4()), language, code, json.dumps(result),
                   execution_time, datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging execution: {e}")

# Health check endpoint
@app.route("/api/health")
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("Quantum Trinity Playground Server")
    print("=" * 40)
    print("Starting server on http://localhost:5000")
    print("Opening playground in browser...")
    print("=" * 40)

    # Open browser automatically
    import threading
    import webbrowser

    def open_browser():
        time.sleep(1.5)  # Wait for server to start
        webbrowser.open("http://localhost:5000")

    threading.Thread(target=open_browser).start()

    # Run Flask server
    app.run(debug=True, port=5000, host="0.0.0.0")
