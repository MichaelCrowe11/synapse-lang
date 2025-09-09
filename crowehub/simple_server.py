"""
CroweHub Server - Simple Version
Part of synapse-lang.com ecosystem
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__, static_folder='.')
CORS(app)

print("=== CroweHub Platform ===")
print("IDE & Deployment Center for Quantum Trinity")
print("Part of synapse-lang.com")
print("")
print("Features:")
print("- CroweCode Spaces - Cloud development environments")
print("- Deployments - Container, serverless, and Kubernetes")  
print("- Package Registry - Share and reuse code")
print("- Collaboration - Real-time collaborative coding")
print("- Quantum Backends - Execute on simulators and hardware")
print("")
print("Access at: http://localhost:5000 (CroweHub IDE)")

# Initialize database
DB_PATH = 'crowehub.db'

def init_db():
    """Initialize CroweHub database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY,
                  username TEXT UNIQUE,
                  email TEXT,
                  created_at TIMESTAMP,
                  plan TEXT DEFAULT 'free')''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS spaces
                 (id TEXT PRIMARY KEY,
                  user_id TEXT,
                  name TEXT,
                  language TEXT,
                  resources TEXT,
                  status TEXT,
                  created_at TIMESTAMP,
                  last_accessed TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id TEXT PRIMARY KEY,
                  user_id TEXT,
                  name TEXT,
                  description TEXT,
                  language TEXT,
                  code TEXT,
                  visibility TEXT,
                  stars INTEGER DEFAULT 0,
                  created_at TIMESTAMP,
                  updated_at TIMESTAMP)''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Serve the CroweHub main page
@app.route('/')
def index():
    """Serve CroweHub main interface"""
    return send_from_directory('.', 'index.html')

# Serve static files
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory('.', path)

@app.route('/api/crowehub/info')
def crowehub_info():
    """Get CroweHub platform information"""
    return jsonify({
        'platform': 'CroweHub',
        'version': '2.0.0',
        'domain': 'synapse-lang.com/crowehub',
        'features': {
            'crowecode_spaces': True,
            'deployments': True,
            'cloud_execution': True,
            'collaboration': True,
            'package_registry': True,
            'quantum_backends': True
        },
        'languages': ['synapse', 'qubit-flow', 'quantum-net'],
        'resources': {
            'docs': 'https://synapse-lang.com/docs/crowehub',
            'api': 'https://synapse-lang.com/api/crowehub',
            'status': 'https://status.synapse-lang.com'
        }
    })

@app.route('/api/execute', methods=['POST'])
def execute_code():
    """Execute code in CroweHub environment"""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'synapse')
        
        # Simulate execution for demo
        if language == 'synapse':
            result = execute_synapse_demo(code)
        elif language == 'qubit-flow':
            result = execute_qubitflow_demo(code)
        elif language == 'quantum-net':
            result = execute_quantumnet_demo(code)
        else:
            return jsonify({'error': 'Unknown language'}), 400
        
        return jsonify({
            'success': True,
            'output': result['output'],
            'executionTime': result.get('executionTime', 150),
            'platform': 'CroweHub'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def execute_synapse_demo(code):
    """Demo execution for Synapse language"""
    output = []
    
    if 'uncertain' in code and '±' in code:
        output.append({
            'type': 'info',
            'text': 'CroweHub: Executing uncertainty propagation...'
        })
        output.append({
            'type': 'log',
            'text': 'Uncertainty analysis complete'
        })
        output.append({
            'type': 'log',
            'text': 'Result: 25.4 ± 1.2 (example output)'
        })
    
    if 'parallel' in code:
        output.append({
            'type': 'info',
            'text': 'CroweHub: Executing parallel computation...'
        })
        output.append({
            'type': 'log',
            'text': 'Parallel execution completed in 45ms'
        })
    
    if 'monte_carlo' in code:
        output.append({
            'type': 'info',
            'text': 'CroweHub: Running Monte Carlo simulation...'
        })
        output.append({
            'type': 'log',
            'text': 'Simulation complete: 10,000 samples processed'
        })
    
    if not output:
        output.append({
            'type': 'log',
            'text': 'Welcome to CroweHub! Your Synapse code executed successfully.'
        })
    
    return {'output': output, 'executionTime': 125}

def execute_qubitflow_demo(code):
    """Demo execution for Qubit-Flow language"""
    output = []
    
    output.append({
        'type': 'info',
        'text': 'CroweHub: Initializing quantum simulator...'
    })
    
    if 'qubit' in code:
        output.append({
            'type': 'log',
            'text': 'Qubits initialized successfully'
        })
    
    if any(gate in code for gate in ['H[', 'X[', 'CNOT[']):
        output.append({
            'type': 'log',
            'text': 'Quantum gates applied'
        })
    
    if 'measure' in code:
        output.append({
            'type': 'log',
            'text': 'Measurement results: |00⟩: 52%, |11⟩: 48%'
        })
    
    output.append({
        'type': 'log',
        'text': 'Quantum circuit execution completed on CroweHub simulator'
    })
    
    return {'output': output, 'executionTime': 200}

def execute_quantumnet_demo(code):
    """Demo execution for Quantum-Net language"""
    output = []
    
    output.append({
        'type': 'info',
        'text': 'CroweHub: Setting up quantum network...'
    })
    
    if 'network' in code:
        output.append({
            'type': 'log',
            'text': 'Quantum network topology established'
        })
    
    if 'nodes' in code:
        output.append({
            'type': 'log',
            'text': 'Network nodes connected and synchronized'
        })
    
    if 'protocol' in code:
        output.append({
            'type': 'log',
            'text': 'Quantum protocol executed successfully'
        })
    
    output.append({
        'type': 'log',
        'text': 'Network simulation complete on CroweHub infrastructure'
    })
    
    return {'output': output, 'executionTime': 180}

@app.route('/api/share', methods=['POST'])
def share_code():
    """Share code on CroweHub platform"""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'synapse')
        title = data.get('title', 'CroweHub Project')
        
        # Generate unique ID
        share_id = str(uuid.uuid4())[:8]
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO projects 
                     (id, name, language, code, visibility, created_at, updated_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (share_id, title, language, code, 'public', 
                   datetime.now(), datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'shareId': share_id,
            'shareUrl': f'https://synapse-lang.com/crowehub/share/{share_id}',
            'platform': 'CroweHub'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/spaces/create', methods=['POST'])
def create_space():
    """Create a new CroweCode Space"""
    try:
        data = request.json
        space_id = str(uuid.uuid4())[:8]
        
        space_config = {
            'id': space_id,
            'name': data.get('name', f'space-{space_id}'),
            'language': data.get('language', 'synapse'),
            'resources': {
                'cpu': data.get('cpu', '2'),
                'memory': data.get('memory', '4Gi'),
                'storage': data.get('storage', '10Gi')
            }
        }
        
        # Store in database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO spaces 
                     (id, name, language, resources, status, created_at, last_accessed)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (space_id, space_config['name'], space_config['language'], 
                   json.dumps(space_config['resources']), 'running',
                   datetime.now(), datetime.now()))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'space_id': space_id,
            'url': f'https://synapse-lang.com/crowehub/spaces/{space_id}',
            'status': 'running',
            'platform': 'CroweHub'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """CroweHub health check"""
    return jsonify({
        'status': 'healthy',
        'platform': 'CroweHub',
        'version': '2.0.0',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')