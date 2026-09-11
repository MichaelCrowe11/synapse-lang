/**
 * Quantum Trinity Playground - Main Application Logic
 */

class QuantumTrinityPlayground {
    constructor() {
        this.currentLanguage = 'synapse';
        this.editor = null;
        this.examples = {};
        this.executionEngine = null;
        this.visualizationEngine = null;
        
        this.initialize();
    }
    
    initialize() {
        // Initialize Monaco Editor
        this.initializeEditor();
        
        // Load examples
        this.loadExamples();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize execution engines
        this.executionEngine = new ExecutionEngine();
        this.visualizationEngine = new VisualizationEngine();
        
        // Load saved code or default example
        this.loadInitialCode();
    }
    
    initializeEditor() {
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});
        
        require(['vs/editor/editor.main'], () => {
            // Register custom languages
            this.registerSynapseLanguage();
            this.registerQubitFlowLanguage();
            this.registerQuantumNetLanguage();
            
            // Create editor
            this.editor = monaco.editor.create(document.getElementById('editor'), {
                value: this.getDefaultCode('synapse'),
                language: 'synapse',
                theme: 'vs-dark',
                automaticLayout: true,
                fontSize: 14,
                minimap: {
                    enabled: true
                },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                lineNumbers: 'on',
                renderWhitespace: 'selection',
                suggestOnTriggerCharacters: true,
                quickSuggestions: {
                    other: true,
                    comments: false,
                    strings: false
                }
            });
            
            // Add custom commands
            this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
                this.runCode();
            });
            
            this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
                this.saveCode();
            });
        });
    }
    
    registerSynapseLanguage() {
        monaco.languages.register({ id: 'synapse' });
        
        monaco.languages.setMonarchTokensProvider('synapse', {
            keywords: [
                'uncertain', 'monte_carlo', 'parallel', 'parameter_sweep',
                'reasoning_chain', 'hypothesis', 'evidence', 'conclusion',
                'if', 'else', 'for', 'while', 'def', 'class', 'return',
                'import', 'from', 'as', 'with', 'try', 'except'
            ],
            
            operators: [
                '±', '+', '-', '*', '/', '**', '=', '==', '!=', '<', '>', '<=', '>='
            ],
            
            symbols: /[=><!~?:&|+\-*\/\^%]+/,
            
            tokenizer: {
                root: [
                    // Keywords
                    [/\b(uncertain|monte_carlo|parallel)\b/, 'keyword'],
                    
                    // Uncertainty notation
                    [/±/, 'operator.special'],
                    
                    // Numbers with uncertainty
                    [/\d+\.?\d*\s*±\s*\d+\.?\d*/, 'number.uncertainty'],
                    
                    // Regular numbers
                    [/\d+\.?\d*/, 'number'],
                    
                    // Strings
                    [/"([^"\\]|\\.)*$/, 'string.invalid'],
                    [/"/, { token: 'string.quote', bracket: '@open', next: '@string' }],
                    
                    // Comments
                    [/#.*$/, 'comment'],
                    
                    // Identifiers
                    [/[a-zA-Z_]\w*/, {
                        cases: {
                            '@keywords': 'keyword',
                            '@default': 'identifier'
                        }
                    }]
                ],
                
                string: [
                    [/[^\\"]+/, 'string'],
                    [/"/, { token: 'string.quote', bracket: '@close', next: '@pop' }]
                ]
            }
        });
        
        // Register completion provider
        monaco.languages.registerCompletionItemProvider('synapse', {
            provideCompletionItems: (model, position) => {
                const suggestions = [
                    {
                        label: 'uncertain',
                        kind: monaco.languages.CompletionItemKind.Keyword,
                        insertText: 'uncertain ${1:name} = ${2:value} ± ${3:uncertainty}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Declare an uncertain value'
                    },
                    {
                        label: 'monte_carlo',
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: 'monte_carlo(samples=${1:10000}) {\n    ${2:// calculation}\n}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Run Monte Carlo simulation'
                    },
                    {
                        label: 'parallel',
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: 'parallel {\n    branch ${1:name}: {\n        ${2:// task}\n    }\n}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Execute tasks in parallel'
                    }
                ];
                
                return { suggestions };
            }
        });
    }
    
    registerQubitFlowLanguage() {
        monaco.languages.register({ id: 'qubit-flow' });
        
        monaco.languages.setMonarchTokensProvider('qubit-flow', {
            keywords: [
                'qubit', 'circuit', 'measure', 'run', 'on', 'simulator',
                'backend', 'shots', 'if', 'else', 'for', 'while', 'return'
            ],
            
            gates: [
                'H', 'X', 'Y', 'Z', 'CNOT', 'CZ', 'SWAP', 'TOFFOLI',
                'RX', 'RY', 'RZ', 'PHASE', 'S', 'T'
            ],
            
            tokenizer: {
                root: [
                    // Keywords
                    [/\b(qubit|circuit|measure|run)\b/, 'keyword'],
                    
                    // Quantum states
                    [/\|[01+\-]+⟩/, 'string.quantum'],
                    
                    // Gates
                    [/\b(H|X|Y|Z|CNOT|CZ|SWAP|TOFFOLI|RX|RY|RZ)\b/, 'keyword.gate'],
                    
                    // Gate application
                    [/\[[^\]]+\]/, 'operator.gate'],
                    
                    // Numbers
                    [/\d+\.?\d*/, 'number'],
                    
                    // Comments
                    [/\/\/.*$/, 'comment'],
                    
                    // Identifiers
                    [/[a-zA-Z_]\w*/, 'identifier']
                ]
            }
        });
    }
    
    registerQuantumNetLanguage() {
        monaco.languages.register({ id: 'quantum-net' });
        
        monaco.languages.setMonarchTokensProvider('quantum-net', {
            keywords: [
                'network', 'nodes', 'quantum_channel', 'teleport', 'send',
                'receive', 'entangled_pair', 'bell_measurement', 'protocol'
            ],
            
            tokenizer: {
                root: [
                    // Keywords
                    [/\b(network|nodes|teleport|protocol)\b/, 'keyword'],
                    
                    // Network operations
                    [/<->|->|<-/, 'operator.network'],
                    
                    // Numbers
                    [/\d+\.?\d*/, 'number'],
                    
                    // Strings
                    [/"[^"]*"/, 'string'],
                    
                    // Comments
                    [/\/\/.*$/, 'comment'],
                    
                    // Identifiers
                    [/[a-zA-Z_]\w*/, 'identifier']
                ]
            }
        });
    }
    
    setupEventListeners() {
        // Language selector
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchLanguage(e.target.closest('.lang-btn').dataset.lang);
            });
        });
        
        // Run button
        document.getElementById('runBtn').addEventListener('click', () => {
            this.runCode();
        });
        
        // Share button
        document.getElementById('shareBtn').addEventListener('click', () => {
            this.shareCode();
        });
        
        // Save button
        document.getElementById('saveBtn').addEventListener('click', () => {
            this.saveCode();
        });
        
        // Format button
        document.getElementById('formatBtn').addEventListener('click', () => {
            this.formatCode();
        });
        
        // Clear button
        document.getElementById('clearBtn').addEventListener('click', () => {
            this.clearEditor();
        });
        
        // Fullscreen button
        document.getElementById('fullscreenBtn').addEventListener('click', () => {
            this.toggleFullscreen();
        });
        
        // Output tabs
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchOutputTab(e.target.dataset.tab);
            });
        });
        
        // Reference links
        document.querySelectorAll('.ref-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showReference(e.target.closest('.ref-link').dataset.ref);
            });
        });
        
        // Close info panel
        document.querySelector('.close-btn').addEventListener('click', () => {
            this.hideInfoPanel();
        });
    }
    
    switchLanguage(language) {
        this.currentLanguage = language;
        
        // Update UI
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.lang === language);
        });
        
        // Update editor language
        if (this.editor) {
            monaco.editor.setModelLanguage(this.editor.getModel(), language);
            this.editor.setValue(this.getDefaultCode(language));
        }
        
        // Update examples
        this.updateExamplesList(language);
    }
    
    runCode() {
        const code = this.editor.getValue();
        const language = this.currentLanguage;
        
        // Show loading
        this.showLoading();
        
        // Clear previous output
        this.clearOutput();
        
        // Update status
        this.updateStatus('running', 'Running...');
        
        // Execute code
        this.executionEngine.execute(code, language)
            .then(result => {
                this.displayOutput(result);
                this.updateStatus('success', 'Completed');
                
                // Update visualizations if needed
                if (result.visualizations) {
                    this.visualizationEngine.render(result.visualizations);
                }
            })
            .catch(error => {
                this.displayError(error);
                this.updateStatus('error', 'Error');
            })
            .finally(() => {
                this.hideLoading();
            });
    }
    
    displayOutput(result) {
        const consoleOutput = document.querySelector('.console-text');
        
        // Display text output
        if (result.output) {
            result.output.forEach(line => {
                const lineElement = document.createElement('div');
                lineElement.className = `output-line ${line.type || ''}`;
                lineElement.textContent = line.text || line;
                consoleOutput.appendChild(lineElement);
            });
        }
        
        // Display execution time
        if (result.executionTime) {
            document.getElementById('executionTime').textContent = 
                `Execution time: ${result.executionTime}ms`;
        }
        
        // Switch to appropriate tab
        if (result.visualizations) {
            this.switchOutputTab('visualization');
        } else if (result.quantumState) {
            this.switchOutputTab('quantum');
            this.displayQuantumState(result.quantumState);
        }
    }
    
    displayError(error) {
        const consoleOutput = document.querySelector('.console-text');
        
        const errorElement = document.createElement('div');
        errorElement.className = 'output-line error';
        errorElement.textContent = `Error: ${error.message || error}`;
        consoleOutput.appendChild(errorElement);
        
        if (error.stack) {
            const stackElement = document.createElement('div');
            stackElement.className = 'output-line error';
            stackElement.textContent = error.stack;
            consoleOutput.appendChild(stackElement);
        }
    }
    
    displayQuantumState(state) {
        const viewer = document.querySelector('.quantum-state-viewer');
        viewer.innerHTML = '';
        
        // Create state vector visualization
        state.amplitudes.forEach((amplitude, index) => {
            const stateElement = document.createElement('div');
            stateElement.className = 'state-vector';
            
            const label = document.createElement('span');
            label.className = 'state-label';
            label.textContent = `|${index.toString(2).padStart(state.qubits, '0')}⟩`;
            
            const bar = document.createElement('div');
            bar.className = 'amplitude-bar';
            
            const fill = document.createElement('div');
            fill.className = 'amplitude-fill';
            fill.style.width = `${Math.abs(amplitude) * 100}%`;
            bar.appendChild(fill);
            
            const value = document.createElement('span');
            value.className = 'probability-value';
            value.textContent = `${(Math.abs(amplitude) ** 2).toFixed(3)}`;
            
            stateElement.appendChild(label);
            stateElement.appendChild(bar);
            stateElement.appendChild(value);
            
            viewer.appendChild(stateElement);
        });
    }
    
    clearOutput() {
        document.querySelector('.console-text').innerHTML = '';
        document.getElementById('executionTime').textContent = '';
    }
    
    updateStatus(status, text) {
        const statusElement = document.getElementById('statusText');
        statusElement.textContent = text;
        statusElement.className = status;
    }
    
    showLoading() {
        document.getElementById('loadingOverlay').classList.add('show');
    }
    
    hideLoading() {
        document.getElementById('loadingOverlay').classList.remove('show');
    }
    
    switchOutputTab(tab) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tab);
        });
        
        // Update tab content
        document.querySelectorAll('.output-tab').forEach(content => {
            content.classList.toggle('active', content.id === `${tab}Output`);
        });
    }
    
    shareCode() {
        const code = this.editor.getValue();
        const language = this.currentLanguage;
        
        // Create shareable URL
        const params = new URLSearchParams({
            lang: language,
            code: btoa(encodeURIComponent(code))
        });
        
        const shareUrl = `${window.location.origin}${window.location.pathname}?${params}`;
        
        // Copy to clipboard
        navigator.clipboard.writeText(shareUrl).then(() => {
            this.showNotification('Link copied to clipboard!');
        });
    }
    
    saveCode() {
        const code = this.editor.getValue();
        const language = this.currentLanguage;
        
        // Save to localStorage
        localStorage.setItem(`quantum-trinity-${language}`, code);
        localStorage.setItem('quantum-trinity-last-language', language);
        
        this.showNotification('Code saved!');
    }
    
    loadInitialCode() {
        // Check for shared code in URL
        const params = new URLSearchParams(window.location.search);
        if (params.has('code')) {
            try {
                const code = decodeURIComponent(atob(params.get('code')));
                const language = params.get('lang') || 'synapse';
                
                this.switchLanguage(language);
                this.editor.setValue(code);
                return;
            } catch (e) {
                console.error('Failed to load shared code:', e);
            }
        }
        
        // Load from localStorage
        const lastLanguage = localStorage.getItem('quantum-trinity-last-language') || 'synapse';
        const savedCode = localStorage.getItem(`quantum-trinity-${lastLanguage}`);
        
        if (savedCode) {
            this.switchLanguage(lastLanguage);
            this.editor.setValue(savedCode);
        }
    }
    
    formatCode() {
        if (this.editor) {
            this.editor.getAction('editor.action.formatDocument').run();
        }
    }
    
    clearEditor() {
        if (confirm('Clear all code?')) {
            this.editor.setValue('');
        }
    }
    
    toggleFullscreen() {
        const editorContainer = document.querySelector('.editor-container');
        editorContainer.classList.toggle('fullscreen');
        
        if (editorContainer.classList.contains('fullscreen')) {
            document.querySelector('.sidebar').style.display = 'none';
        } else {
            document.querySelector('.sidebar').style.display = 'block';
        }
    }
    
    showReference(topic) {
        const references = {
            uncertainty: `
                <h2>Uncertainty in Synapse</h2>
                <p>Synapse Language provides native support for uncertainty quantification.</p>
                <h3>Basic Syntax</h3>
                <pre>uncertain temperature = 25.3 ± 0.2</pre>
                <h3>Operations</h3>
                <p>Uncertainty propagates automatically through calculations:</p>
                <pre>result = temperature * 2  # 50.6 ± 0.4</pre>
            `,
            parallel: `
                <h2>Parallel Computing</h2>
                <p>Execute tasks in parallel for better performance.</p>
                <h3>Parallel Block</h3>
                <pre>parallel {
    branch task1: { /* ... */ }
    branch task2: { /* ... */ }
}</pre>
            `,
            quantum: `
                <h2>Quantum Computing</h2>
                <p>Build quantum circuits and algorithms.</p>
                <h3>Quantum States</h3>
                <pre>qubit q = |0⟩
H[q]  // Hadamard gate</pre>
            `
        };
        
        document.getElementById('infoPanelContent').innerHTML = references[topic] || '';
        document.getElementById('infoPanel').classList.add('show');
    }
    
    hideInfoPanel() {
        document.getElementById('infoPanel').classList.remove('show');
    }
    
    showNotification(message) {
        // Simple notification (could be enhanced with a toast library)
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: var(--success-color);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 6px;
            z-index: 3000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    getDefaultCode(language) {
        const defaults = {
            synapse: `# Uncertainty Quantification Example
uncertain temperature = 25.3 ± 0.2  # °C
uncertain pressure = 1013.25 ± 1.5  # mbar

# Calculations with automatic uncertainty propagation
result = temperature * 2 + pressure / 100

print(f"Result: {result}")

# Monte Carlo simulation
monte_carlo(samples=10000) {
    complex_result = temperature * sin(pressure / 1000)
}

print(f"Monte Carlo result: {complex_result}")`,
            
            'qubit-flow': `// Quantum Bell State Example
qubit alice = |0⟩
qubit bob = |0⟩

// Create Bell state circuit
circuit bell_state(alice, bob) {
    H[alice]           // Hadamard gate
    CNOT[alice, bob]   // Entanglement
    
    measure alice -> result_a
    measure bob -> result_b
}

// Run on simulator
run bell_state on simulator {
    shots: 1000
}`,
            
            'quantum-net': `// Quantum Network Example
network quantum_lan {
    nodes: ["Alice", "Bob", "Charlie"]
    topology: "fully_connected"
}

// Quantum teleportation protocol
teleportation_protocol {
    // Create entangled pair
    bell_pair = create_bell_pair()
    send bell_pair.qubit_b to Bob
    
    // Teleport quantum state
    teleport mystery_qubit from Alice to Bob
}`
        };
        
        return defaults[language] || '';
    }
    
    loadExamples() {
        // This would load from the examples.js file
        // For now, using placeholder
        this.updateExamplesList(this.currentLanguage);
    }
    
    updateExamplesList(language) {
        const examplesList = document.getElementById('examplesList');
        examplesList.innerHTML = '';
        
        const examples = {
            synapse: [
                {
                    title: 'Basic Uncertainty',
                    desc: 'Simple uncertainty propagation',
                    code: 'uncertain x = 10 ± 0.5\nuncertain y = 5 ± 0.2\nresult = x * y\nprint(result)'
                },
                {
                    title: 'Monte Carlo',
                    desc: 'Monte Carlo simulation',
                    code: 'monte_carlo(samples=100000) {\n    // Your calculation\n}'
                }
            ],
            'qubit-flow': [
                {
                    title: 'Bell State',
                    desc: 'Create quantum entanglement',
                    code: '// Bell state code'
                },
                {
                    title: "Grover's Algorithm",
                    desc: 'Quantum search',
                    code: '// Grover code'
                }
            ],
            'quantum-net': [
                {
                    title: 'Teleportation',
                    desc: 'Quantum state transfer',
                    code: '// Teleportation code'
                },
                {
                    title: 'QKD',
                    desc: 'Quantum key distribution',
                    code: '// QKD code'
                }
            ]
        };
        
        const langExamples = examples[language] || [];
        
        langExamples.forEach(example => {
            const item = document.createElement('div');
            item.className = 'example-item';
            item.innerHTML = `
                <div class="example-title">${example.title}</div>
                <div class="example-desc">${example.desc}</div>
            `;
            
            item.addEventListener('click', () => {
                this.editor.setValue(example.code);
            });
            
            examplesList.appendChild(item);
        });
    }
}

// Initialize playground when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.playground = new QuantumTrinityPlayground();
});