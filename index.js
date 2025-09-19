#!/usr/bin/env node

/**
 * Synapse Language v2.3.1
 * JavaScript/Node.js wrapper for the Synapse scientific programming language
 *
 * Features:
 * - Quantum computing with visual circuit designer
 * - AI-powered code suggestions
 * - Real-time collaboration
 * - Blockchain verification
 * - Distributed computing
 * - Visual programming interface
 * - Mobile app framework
 * - Advanced type inference
 */

const { spawn, exec } = require('child_process');
const path = require('path');
const fs = require('fs');

// Package metadata
const PACKAGE_NAME = 'synapse-lang-core';
const VERSION = '2.3.2';

// Synapse Language API wrapper
class SynapseLanguage {
    constructor() {
        this.version = VERSION;
        this.pythonInstalled = this.checkPython();
    }

    checkPython() {
        try {
            const result = require('child_process').execSync('python --version', { encoding: 'utf8' });
            return result.includes('Python');
        } catch (e) {
            try {
                const result = require('child_process').execSync('python3 --version', { encoding: 'utf8' });
                return result.includes('Python');
            } catch (e2) {
                console.warn('⚠️  Python not found. Synapse Language requires Python 3.8+');
                console.log('Install Python from: https://www.python.org/downloads/');
                return false;
            }
        }
    }

    // Run Synapse code
    run(code, callback) {
        if (!this.pythonInstalled) {
            callback(new Error('Python is required to run Synapse code'));
            return;
        }

        const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
        const child = spawn(pythonCmd, ['-c', `
import sys
sys.path.insert(0, '${__dirname}')
try:
    import synapse_lang
    # Execute the provided code
    exec('''${code}''')
except ImportError:
    print("Synapse Language not installed. Run: pip install synapse-lang")
    sys.exit(1)
        `], {
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let output = '';
        let error = '';

        child.stdout.on('data', (data) => {
            output += data.toString();
        });

        child.stderr.on('data', (data) => {
            error += data.toString();
        });

        child.on('close', (code) => {
            if (callback) {
                callback(code === 0 ? null : new Error(error), output);
            }
        });
    }

    // Get information about Synapse
    info() {
        return {
            name: PACKAGE_NAME,
            version: VERSION,
            features: [
                'Quantum Computing',
                'AI Code Assistance',
                'Real-time Collaboration',
                'Blockchain Verification',
                'Distributed Computing',
                'Visual Programming',
                'Mobile Framework',
                'Type Inference'
            ],
            installation: {
                npm: `npm install ${PACKAGE_NAME}`,
                pip: 'pip install synapse-lang',
                docker: 'docker pull michaelcrowe11/synapse-lang'
            },
            links: {
                github: 'https://github.com/michaelcrowe11/synapse-lang',
                pypi: 'https://pypi.org/project/synapse-lang/',
                docker: 'https://hub.docker.com/r/michaelcrowe11/synapse-lang',
                npm: `https://www.npmjs.com/package/${PACKAGE_NAME}`
            }
        };
    }
}

// CLI handling
if (require.main === module) {
    const args = process.argv.slice(2);

    // Show help
    if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
        console.log(`
🧠 Synapse Language v${VERSION}

Usage:
  synapse-lang [options] [file]

Options:
  --help, -h      Show this help message
  --version, -v   Show version information
  --info          Show package information
  --demo          Run the demo
  --install       Install Python dependencies

Examples:
  synapse-lang script.syn       Run a Synapse script
  synapse-lang --demo           Run the feature demo
  synapse-lang --info           Show package information

Installation:
  npm:    npm install ${PACKAGE_NAME}
  Python: pip install synapse-lang
  Docker: docker pull michaelcrowe11/synapse-lang

Learn more: https://github.com/michaelcrowe11/synapse-lang
        `);
        process.exit(0);
    }

    // Show version
    if (args[0] === '--version' || args[0] === '-v') {
        console.log(`Synapse Language v${VERSION}`);
        process.exit(0);
    }

    // Show info
    if (args[0] === '--info') {
        const synapse = new SynapseLanguage();
        console.log(JSON.stringify(synapse.info(), null, 2));
        process.exit(0);
    }

    // Run demo
    if (args[0] === '--demo') {
        const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
        const demoPath = path.join(__dirname, 'examples', 'demo_all_features.py');

        if (fs.existsSync(demoPath)) {
            const demo = spawn(pythonCmd, [demoPath], {
                stdio: 'inherit'
            });
            demo.on('close', (code) => process.exit(code));
        } else {
            console.log('Demo file not found. Creating simple demo...');
            const synapse = new SynapseLanguage();
            synapse.run(`
print("🧠 Synapse Language v${VERSION} Demo")
print("=" * 40)
try:
    from synapse_lang.quantum_designer import QuantumCircuit
    circuit = QuantumCircuit(2)
    circuit.add_gate("H", [0])
    circuit.add_gate("CNOT", [0, 1])
    print("✅ Quantum circuit created successfully!")
    print(f"   Qubits: {circuit.num_qubits}")
    print(f"   Gates: {len(circuit.gates)}")
except ImportError:
    print("⚠️  Synapse Language Python package not installed")
    print("   Run: pip install synapse-lang")
            `, (err, output) => {
                if (output) console.log(output);
                if (err) console.error(err.message);
            });
        }
    } else if (args[0] === '--install') {
        // Install Python dependencies
        console.log('Installing Synapse Language Python package...');
        const install = spawn('pip', ['install', 'synapse-lang'], {
            stdio: 'inherit'
        });
        install.on('close', (code) => {
            if (code === 0) {
                console.log('✅ Installation complete!');
            } else {
                console.log('❌ Installation failed. Try: pip install synapse-lang');
            }
            process.exit(code);
        });
    } else {
        // Default: try to run Python with synapse_lang module
        const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
        const synapseCmd = spawn(pythonCmd, ['-m', 'synapse_lang', ...args], {
            stdio: 'inherit',
            shell: true
        });

        synapseCmd.on('error', (err) => {
            console.error('Error running Synapse:', err.message);
            console.log('Make sure Python is installed and synapse-lang package is installed:');
            console.log('  pip install synapse-lang');
            process.exit(1);
        });

        synapseCmd.on('close', (code) => {
            process.exit(code);
        });
    }
}

// Export for use as a library
module.exports = SynapseLanguage;
