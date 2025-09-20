"""
Synapse Language Documentation Website
Deployable on Fly.io
"""

from flask import Flask, render_template, jsonify, request
import markdown
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Version info
SYNAPSE_VERSION = "2.3.2"
FEATURES = [
    {"name": "Type Inference", "icon": "🔍", "description": "Hindley-Milner type system with scientific extensions"},
    {"name": "Real-time Collaboration", "icon": "👥", "description": "Operational Transformation for concurrent editing"},
    {"name": "Visual Programming", "icon": "🎨", "description": "Node-based drag-and-drop interface"},
    {"name": "Distributed Computing", "icon": "🌐", "description": "MapReduce framework with fault tolerance"},
    {"name": "AI Code Suggestions", "icon": "🤖", "description": "Context-aware code completions"},
    {"name": "Quantum Circuit Designer", "icon": "⚛️", "description": "Visual quantum circuit builder"},
    {"name": "Mobile App Framework", "icon": "📱", "description": "Cross-platform app development"},
    {"name": "Blockchain Verification", "icon": "🔐", "description": "Cryptographic code verification"}
]

@app.route('/')
def index():
    """Main documentation page"""
    return render_template('index.html',
                         version=SYNAPSE_VERSION,
                         features=FEATURES)

@app.route('/docs/<section>')
def docs_section(section):
    """Render documentation sections"""
    sections = {
        'quickstart': 'Quick Start Guide',
        'installation': 'Installation',
        'features': 'Features',
        'api': 'API Reference',
        'examples': 'Examples',
        'quantum': 'Quantum Computing',
        'collaboration': 'Real-time Collaboration',
        'blockchain': 'Blockchain Verification'
    }

    if section not in sections:
        return "Section not found", 404

    return render_template('docs.html',
                         section=section,
                         title=sections[section],
                         version=SYNAPSE_VERSION)

@app.route('/playground')
def playground():
    """Interactive code playground"""
    return render_template('playground.html', version=SYNAPSE_VERSION)

@app.route('/api/run', methods=['POST'])
def run_code():
    """API endpoint to run Synapse code (demo only)"""
    code = request.json.get('code', '')

    # This is a demo endpoint - in production, this would run in a sandboxed environment
    result = {
        'success': True,
        'output': f'Code received ({len(code)} characters)\nDemo mode - actual execution coming soon!',
        'timestamp': datetime.now().isoformat()
    }

    return jsonify(result)

@app.route('/api/version')
def api_version():
    """Get version information"""
    return jsonify({
        'version': SYNAPSE_VERSION,
        'features': len(FEATURES),
        'platforms': {
            'pypi': 'synapse_lang',
            'npm': 'synapse-lang-core',
            'docker': 'michaelcrowe11/synapse-lang'
        }
    })

@app.route('/health')
def health():
    """Health check endpoint for Fly.io"""
    return jsonify({'status': 'healthy', 'version': SYNAPSE_VERSION})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)