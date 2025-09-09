/**
 * CroweHub - Main Application Controller
 * Integrated IDE for Quantum Trinity Languages
 * Created by Michael Crowe
 */

class CroweHub {
    constructor() {
        this.name = 'CroweHub';
        this.version = '1.0.0';
        this.currentLanguage = 'synapse';
        this.editor = null;
        this.socket = null;
        this.user = null;
        this.executionEngine = null;
        this.aiAssistant = null;
        
        this.init();
    }
    
    init() {
        console.log(`
╔═══════════════════════════════════╗
║     Welcome to CroweHub IDE      ║
║  Quantum Trinity Development      ║
║        Version ${this.version}           ║
╚═══════════════════════════════════╝
        `);
        
        this.setupEditor();
        this.setupWebSocket();
        this.setupUI();
        this.loadUserPreferences();
        this.initializeEngines();
    }
    
    setupEditor() {
        // Wait for Monaco to load
        require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' }});
        
        require(['vs/editor/editor.main'], () => {
            // Register CroweHub custom themes
            this.registerCroweHubThemes();
            
            // Initialize Monaco Editor
            this.editor = monaco.editor.create(document.getElementById('editor'), {
                value: this.getWelcomeCode(),
                language: 'synapse',
                theme: 'crowehub-dark',
                fontSize: 14,
                automaticLayout: true,
                minimap: { enabled: true },
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                suggestOnTriggerCharacters: true,
                quickSuggestions: true,
                folding: true,
                lineNumbers: 'on',
                renderWhitespace: 'selection',
                roundedSelection: true,
                cursorBlinking: 'smooth',
                cursorStyle: 'line',
                scrollbar: {
                    vertical: 'visible',
                    horizontal: 'visible',
                    verticalScrollbarSize: 10,
                    horizontalScrollbarSize: 10
                }
            });
            
            // Register language definitions
            this.registerLanguages();
            
            // Setup auto-completion
            this.setupAutoCompletion();
        });
    }
    
    registerCroweHubThemes() {
        monaco.editor.defineTheme('crowehub-dark', {
            base: 'vs-dark',
            inherit: true,
            rules: [
                { token: 'uncertainty', foreground: 'FFA500', fontStyle: 'bold' },
                { token: 'parallel', foreground: '00CED1', fontStyle: 'bold' },
                { token: 'quantum', foreground: 'DA70D6', fontStyle: 'bold' },
                { token: 'entangle', foreground: '32CD32' },
                { token: 'qubit', foreground: '9370DB' },
                { token: 'network', foreground: '20B2AA' },
                { token: 'monte_carlo', foreground: 'FFD700' },
                { token: 'measure', foreground: 'FF6347' },
                { token: 'comment', foreground: '608B4E', fontStyle: 'italic' },
                { token: 'string', foreground: 'CE9178' }
            ],
            colors: {
                'editor.background': '#1a1a2e',
                'editor.foreground': '#f1f1f1',
                'editorCursor.foreground': '#e94560',
                'editor.lineHighlightBackground': '#16213e',
                'editorLineNumber.foreground': '#666',
                'editor.selectionBackground': '#0f3460',
                'editorSuggestWidget.background': '#16213e',
                'editorSuggestWidget.border': '#0f3460',
                'editorSuggestWidget.foreground': '#f1f1f1',
                'editorSuggestWidget.selectedBackground': '#0f3460',
                'editorHoverWidget.background': '#16213e',
                'editorHoverWidget.border': '#0f3460'
            }
        });
    }
    
    registerLanguages() {
        // Register Synapse language
        monaco.languages.register({ id: 'synapse' });
        monaco.languages.setMonarchTokensProvider('synapse', {
            keywords: [
                'uncertain', 'parallel', 'monte_carlo', 'correlation',
                'for', 'if', 'else', 'while', 'function', 'return',
                'import', 'from', 'as', 'class', 'def', 'print'
            ],
            operators: ['±', '+', '-', '*', '/', '=', '>', '<', '!', '~', '?', ':', '==', '<=', '>=', '!='],
            symbols: /[=><!~?:&|+\-*\/\^%]+/,
            tokenizer: {
                root: [
                    [/uncertain/, 'uncertainty'],
                    [/parallel/, 'parallel'],
                    [/monte_carlo/, 'monte_carlo'],
                    [/[a-z_$][\w$]*/, {
                        cases: {
                            '@keywords': 'keyword',
                            '@default': 'identifier'
                        }
                    }],
                    [/[0-9]+(\.[0-9]+)?/, 'number'],
                    [/"([^"\\]|\\.)*$/, 'string.invalid'],
                    [/"/, 'string', '@string'],
                    [/\/\/.*$/, 'comment']
                ]
            }
        });
        
        // Register Qubit-Flow language
        monaco.languages.register({ id: 'qubit-flow' });
        monaco.languages.setMonarchTokensProvider('qubit-flow', {
            keywords: [
                'qubit', 'gate', 'circuit', 'measure', 'entangle',
                'H', 'X', 'Y', 'Z', 'CNOT', 'Toffoli', 'SWAP',
                'if', 'else', 'for', 'while', 'return'
            ],
            tokenizer: {
                root: [
                    [/qubit/, 'qubit'],
                    [/measure/, 'measure'],
                    [/entangle/, 'entangle'],
                    [/\|[01]⟩/, 'quantum'],
                    [/[HXYZCNOTToffoliSWAP]+\[/, 'quantum'],
                    [/[a-z_$][\w$]*/, {
                        cases: {
                            '@keywords': 'keyword',
                            '@default': 'identifier'
                        }
                    }]
                ]
            }
        });
        
        // Register Quantum-Net language
        monaco.languages.register({ id: 'quantum-net' });
        monaco.languages.setMonarchTokensProvider('quantum-net', {
            keywords: [
                'network', 'node', 'connection', 'protocol', 'teleport',
                'distribute', 'entangle', 'communicate', 'sync'
            ],
            tokenizer: {
                root: [
                    [/network/, 'network'],
                    [/node/, 'network'],
                    [/protocol/, 'network'],
                    [/[a-z_$][\w$]*/, {
                        cases: {
                            '@keywords': 'keyword',
                            '@default': 'identifier'
                        }
                    }]
                ]
            }
        });
    }
    
    setupAutoCompletion() {
        // Register completion providers for each language
        monaco.languages.registerCompletionItemProvider('synapse', {
            provideCompletionItems: (model, position) => {
                const suggestions = [
                    {
                        label: 'uncertain',
                        kind: monaco.languages.CompletionItemKind.Keyword,
                        insertText: 'uncertain ${1:variable} = ${2:value} ± ${3:error}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Declare a variable with uncertainty'
                    },
                    {
                        label: 'parallel',
                        kind: monaco.languages.CompletionItemKind.Keyword,
                        insertText: 'parallel {\n    ${1:// parallel code}\n}',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Execute code in parallel'
                    },
                    {
                        label: 'monte_carlo',
                        kind: monaco.languages.CompletionItemKind.Function,
                        insertText: 'monte_carlo(samples=${1:10000}, function=${2:func})',
                        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                        documentation: 'Run Monte Carlo simulation'
                    }
                ];
                return { suggestions };
            }
        });
    }
    
    getWelcomeCode() {
        return `// Welcome to CroweHub - Quantum Trinity IDE
// Created by Michael Crowe
// 
// CroweHub provides an integrated development environment for:
// • Synapse Language - Scientific computing with uncertainty
// • Qubit-Flow - Quantum circuit design and execution  
// • Quantum-Net - Distributed quantum networking
//
// Get started with an example or write your own code!

// Example: Uncertainty-aware computation in Synapse
uncertain temperature = 300 ± 5  // Kelvin
uncertain pressure = 101.325 ± 0.5  // kPa

// Calculate ideal gas properties with uncertainty propagation
uncertain volume = (8.314 * temperature) / pressure  // L

// Parallel Monte Carlo simulation for complex calculations
parallel {
    monte_carlo(samples=10000, inputs={temperature, pressure}) {
        // Your simulation code here
        result = calculate_property(temperature, pressure)
        return result
    }
}

print("Volume: {volume.value} ± {volume.uncertainty} L")
print("Relative uncertainty: {(volume.uncertainty/volume.value)*100}%")
`;
    }
    
    setupWebSocket() {
        // Connect to CroweHub server
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                console.log('Connected to CroweHub server');
                this.updateStatus('Connected', 'green');
            };
            
            this.socket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleServerMessage(data);
            };
            
            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateStatus('Connection Error', 'red');
            };
            
            this.socket.onclose = () => {
                console.log('Disconnected from CroweHub server');
                this.updateStatus('Disconnected', 'orange');
                // Attempt reconnection
                setTimeout(() => this.setupWebSocket(), 5000);
            };
        } catch (error) {
            console.error('Failed to establish WebSocket connection:', error);
        }
    }
    
    setupUI() {
        // Language selector
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchLanguage(e.target.closest('.lang-btn').dataset.lang);
            });
        });
        
        // Run button
        document.getElementById('runBtn').addEventListener('click', () => {
            this.executeCode();
        });
        
        // Share button
        document.getElementById('shareBtn').addEventListener('click', () => {
            this.shareCode();
        });
        
        // Save button
        document.getElementById('saveBtn').addEventListener('click', () => {
            this.saveCode();
        });
        
        // Tool buttons
        document.getElementById('ai-assist').addEventListener('click', () => {
            this.toggleAIAssistant();
        });
        
        document.getElementById('collaborate').addEventListener('click', () => {
            this.startCollaboration();
        });
        
        document.getElementById('deploy').addEventListener('click', () => {
            this.deployProject();
        });
        
        document.getElementById('analytics').addEventListener('click', () => {
            this.showAnalytics();
        });
        
        document.getElementById('packages').addEventListener('click', () => {
            this.openPackageManager();
        });
        
        document.getElementById('quantum-backends').addEventListener('click', () => {
            this.selectQuantumBackend();
        });
        
        // Example buttons
        document.getElementById('example-uncertainty').addEventListener('click', () => {
            this.loadExample('uncertainty');
        });
        
        document.getElementById('example-bell-state').addEventListener('click', () => {
            this.loadExample('bell-state');
        });
        
        document.getElementById('example-network').addEventListener('click', () => {
            this.loadExample('network');
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.executeCode();
                }
                if (e.key === 's') {
                    e.preventDefault();
                    this.saveCode();
                }
            }
        });
    }
    
    initializeEngines() {
        // Initialize execution engine
        if (typeof ExecutionEngine !== 'undefined') {
            this.executionEngine = new ExecutionEngine();
        }
        
        // Initialize AI assistant
        if (typeof AIAssistant !== 'undefined') {
            this.aiAssistant = new AIAssistant();
        }
    }
    
    switchLanguage(language) {
        this.currentLanguage = language;
        
        // Update UI
        document.querySelectorAll('.lang-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-lang="${language}"]`).classList.add('active');
        
        // Update editor language
        if (this.editor) {
            monaco.editor.setModelLanguage(this.editor.getModel(), language);
        }
        
        // Update status bar
        const displayName = {
            'synapse': 'Synapse',
            'qubit-flow': 'Qubit-Flow',
            'quantum-net': 'Quantum-Net'
        };
        document.getElementById('current-lang').textContent = displayName[language] || language;
        
        console.log(`Switched to ${displayName[language]} language`);
    }
    
    async executeCode() {
        const code = this.editor.getValue();
        const outputElement = document.getElementById('output-content');
        
        outputElement.innerHTML = '<div style="color: #00CED1;">Executing on CroweHub...</div>';
        
        try {
            const startTime = performance.now();
            
            // Use execution engine if available
            if (this.executionEngine) {
                const result = await this.executionEngine.execute(code, this.currentLanguage);
                this.displayOutput(result);
                
                const execTime = (performance.now() - startTime).toFixed(2);
                document.getElementById('exec-time').textContent = `Execution: ${execTime}ms`;
            } else {
                // Fallback to server execution
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        code,
                        language: this.currentLanguage
                    })
                });
                
                const result = await response.json();
                this.displayOutput(result);
            }
        } catch (error) {
            outputElement.innerHTML = `<div style="color: #ff6b6b;">Error: ${error.message}</div>`;
        }
    }
    
    displayOutput(result) {
        const outputElement = document.getElementById('output-content');
        
        if (result.success) {
            let html = '<div style="color: #4caf50;">✓ Execution successful</div><br>';
            
            if (result.output && Array.isArray(result.output)) {
                result.output.forEach(item => {
                    if (item.type === 'log') {
                        html += `<div>${item.text}</div>`;
                    } else if (item.type === 'error') {
                        html += `<div style="color: #ff6b6b;">Error: ${item.text}</div>`;
                    } else if (item.type === 'info') {
                        html += `<div style="color: #00CED1;">${item.text}</div>`;
                    }
                });
            }
            
            outputElement.innerHTML = html;
        } else {
            outputElement.innerHTML = `<div style="color: #ff6b6b;">Error: ${result.error}</div>`;
        }
    }
    
    async shareCode() {
        const code = this.editor.getValue();
        
        try {
            const response = await fetch('/api/share', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code,
                    language: this.currentLanguage,
                    title: 'CroweHub Share'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                const shareUrl = `${window.location.origin}/share/${result.shareId}`;
                navigator.clipboard.writeText(shareUrl);
                alert(`Code shared! URL copied to clipboard:\n${shareUrl}`);
            }
        } catch (error) {
            alert('Failed to share code: ' + error.message);
        }
    }
    
    saveCode() {
        const code = this.editor.getValue();
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `crowehub-${this.currentLanguage}-${Date.now()}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    }
    
    loadExample(exampleId) {
        const examples = {
            'uncertainty': `// Uncertainty Propagation Example
uncertain measurement1 = 10.5 ± 0.2
uncertain measurement2 = 5.3 ± 0.1

// Arithmetic operations propagate uncertainty
result = measurement1 + measurement2
print("Sum: {result}")

// More complex calculation
uncertain resistance = 100 ± 5  // Ohms
uncertain current = 0.5 ± 0.02   // Amperes
voltage = resistance * current
print("Voltage: {voltage} V")`,
            
            'bell-state': `// Bell State Creation in Qubit-Flow
qubit q0 = |0⟩
qubit q1 = |0⟩

// Create Bell state
H[q0]         // Hadamard on first qubit
CNOT[q0, q1]  // Entangle qubits

// Measure
result0 = measure(q0)
result1 = measure(q1)

print("Measured: q0={result0}, q1={result1}")
print("Results are correlated!")`,
            
            'network': `// Quantum Network Example
network quantum_internet {
    nodes: ["Alice", "Bob", "Charlie"]
    
    connections: [
        {from: "Alice", to: "Bob", type: "quantum"},
        {from: "Bob", to: "Charlie", type: "quantum"}
    ]
    
    protocol teleportation {
        // Teleport state from Alice to Charlie via Bob
        entangle(Alice.qubit, Bob.qubit)
        entangle(Bob.qubit, Charlie.qubit)
        teleport(Alice.state -> Charlie.state)
    }
}`
        };
        
        if (examples[exampleId]) {
            this.editor.setValue(examples[exampleId]);
            
            // Switch to appropriate language
            const langMap = {
                'uncertainty': 'synapse',
                'bell-state': 'qubit-flow',
                'network': 'quantum-net'
            };
            this.switchLanguage(langMap[exampleId]);
        }
    }
    
    toggleAIAssistant() {
        console.log('CroweHub AI Assistant activated');
        // AI assistant implementation
    }
    
    startCollaboration() {
        console.log('Starting CroweHub collaboration session');
        // Collaboration implementation
    }
    
    deployProject() {
        console.log('Deploying to CroweHub Cloud');
        // Deployment implementation
    }
    
    showAnalytics() {
        console.log('Opening CroweHub Analytics');
        // Analytics implementation
    }
    
    openPackageManager() {
        console.log('Opening CroweHub Package Manager');
        // Package manager implementation
    }
    
    selectQuantumBackend() {
        console.log('Selecting quantum backend');
        // Backend selection implementation
    }
    
    loadUserPreferences() {
        const prefs = localStorage.getItem('crowehub-preferences');
        if (prefs) {
            const preferences = JSON.parse(prefs);
            // Apply preferences
            if (preferences.language) {
                this.switchLanguage(preferences.language);
            }
            if (preferences.theme && this.editor) {
                this.editor.updateOptions({ theme: preferences.theme });
            }
        }
    }
    
    saveUserPreferences() {
        const preferences = {
            language: this.currentLanguage,
            theme: 'crowehub-dark',
            fontSize: 14
        };
        localStorage.setItem('crowehub-preferences', JSON.stringify(preferences));
    }
    
    updateStatus(status, color) {
        const indicator = document.querySelector('.status-indicator');
        if (indicator) {
            indicator.style.background = color === 'green' ? '#4caf50' : 
                                       color === 'red' ? '#f44336' : 
                                       color === 'orange' ? '#ff9800' : '#9e9e9e';
        }
    }
    
    handleServerMessage(data) {
        // Handle messages from CroweHub server
        if (data.type === 'execution-result') {
            this.displayOutput(data.result);
        } else if (data.type === 'collaboration-update') {
            // Handle collaboration updates
        } else if (data.type === 'notification') {
            // Show notification
        }
    }
}

// Initialize CroweHub when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.crowehub = new CroweHub();
});