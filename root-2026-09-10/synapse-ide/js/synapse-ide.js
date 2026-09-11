/**
 * Synapse IDE Main Controller
 * Orchestrates all IDE components and integrates with CroweHub platform
 */

class SynapseIDE {
    constructor() {
        this.version = '1.0.0';
        this.initialized = false;
        this.editor = null;
        this.currentLanguage = 'synapse';
        this.currentTheme = 'synapse-dark';
        this.extensions = new Map();
        this.plugins = new Map();
        this.settings = {};
        
        this.init();
    }
    
    async init() {
        console.log('Initializing Synapse IDE v' + this.version);
        
        try {
            // Show loading overlay
            this.showLoading('Initializing Synapse IDE...');
            
            // Load settings
            await this.loadSettings();
            
            // Initialize Monaco Editor
            await this.initializeEditor();
            
            // Register languages
            this.registerLanguages();
            
            // Setup UI components
            this.setupUI();
            
            // Initialize components
            await this.initializeComponents();
            
            // Setup keyboard shortcuts
            this.setupKeyboardShortcuts();
            
            // Connect to backend
            await this.connectToBackend();
            
            // Load welcome content
            this.loadWelcomeContent();
            
            // Hide loading overlay
            this.hideLoading();
            
            this.initialized = true;
            console.log('Synapse IDE initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize IDE:', error);
            this.showError('Failed to initialize IDE: ' + error.message);
        }
    }
    
    async loadSettings() {
        try {
            const response = await fetch('/api/ide/settings');
            this.settings = await response.json();
        } catch (error) {
            // Use default settings
            this.settings = {
                theme: 'synapse-dark',
                fontSize: 14,
                fontFamily: 'JetBrains Mono',
                autoSave: true,
                aiAssistance: true,
                minimap: true,
                wordWrap: 'on',
                tabSize: 4,
                insertSpaces: true
            };
        }
    }
    
    async initializeEditor() {
        return new Promise((resolve, reject) => {
            require(['vs/editor/editor.main'], () => {
                try {
                    // Configure Monaco
                    monaco.editor.defineTheme('synapse-dark', {
                        base: 'vs-dark',
                        inherit: true,
                        rules: [
                            { token: 'keyword', foreground: '7A5CFF', fontStyle: 'bold' },
                            { token: 'operator.scientific', foreground: '43E5FF', fontStyle: 'bold' },
                            { token: 'number.uncertainty', foreground: 'F39C12', fontStyle: 'bold' },
                            { token: 'string', foreground: '27AE60' },
                            { token: 'comment', foreground: '6C7B7F', fontStyle: 'italic' }
                        ],
                        colors: {
                            'editor.background': '#0B0F14',
                            'editor.foreground': '#E6E8EB',
                            'editorCursor.foreground': '#43E5FF',
                            'editor.lineHighlightBackground': '#1A1E23',
                            'editorLineNumber.foreground': '#6C7B7F',
                            'editor.selectionBackground': '#7A5CFF33'
                        }
                    });
                    
                    // Create editor instance
                    this.editor = monaco.editor.create(document.getElementById('monaco-editor'), {
                        value: '',
                        language: this.currentLanguage,
                        theme: this.currentTheme,
                        fontSize: this.settings.fontSize,
                        fontFamily: this.settings.fontFamily,
                        automaticLayout: true,
                        minimap: { enabled: this.settings.minimap },
                        wordWrap: this.settings.wordWrap,
                        tabSize: this.settings.tabSize,
                        insertSpaces: this.settings.insertSpaces,
                        scrollBeyondLastLine: false,
                        renderWhitespace: 'selection',
                        glyphMargin: true,
                        lightbulb: { enabled: true },
                        suggestOnTriggerCharacters: true,
                        acceptSuggestionOnEnter: 'on',
                        quickSuggestions: true
                    });
                    
                    // Set up editor events
                    this.setupEditorEvents();
                    
                    // Make editor globally accessible
                    window.monacoEditor = this.editor;
                    
                    resolve();
                } catch (error) {
                    reject(error);
                }
            });
        });
    }
    
    registerLanguages() {
        if (window.registerLanguages) {
            window.registerLanguages();
        }
    }
    
    setupEditorEvents() {
        // Content change events
        this.editor.onDidChangeModelContent((e) => {
            this.handleContentChange(e);
        });
        
        // Cursor position change
        this.editor.onDidChangeCursorPosition((e) => {
            this.updateCursorPosition(e.position);
        });
        
        // Language change
        this.editor.onDidChangeModelLanguage((e) => {
            this.currentLanguage = e.newLanguage;
            this.updateLanguageStatus();
        });
        
        // Key down events
        this.editor.onKeyDown((e) => {
            this.handleKeyDown(e);
        });
    }
    
    setupUI() {
        // Setup sidebar tabs
        this.setupSidebarTabs();
        
        // Setup output tabs
        this.setupOutputTabs();
        
        // Setup menu actions
        this.setupMenuActions();
        
        // Setup theme selector
        this.setupThemeSelector();
        
        // Setup language selector
        this.setupLanguageSelector();
    }
    
    setupSidebarTabs() {
        const tabs = document.querySelectorAll('.sidebar-tabs .tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                this.switchSidebarTab(tabName);
            });
        });
    }
    
    setupOutputTabs() {
        const tabs = document.querySelectorAll('.output-tab');
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab');
                this.switchOutputTab(tabName);
            });
        });
    }
    
    setupMenuActions() {
        document.addEventListener('click', (e) => {
            const action = e.target.getAttribute('data-action');
            if (action) {
                this.handleAction(action, e);
            }
        });
    }
    
    setupThemeSelector() {
        const themeSelect = document.getElementById('theme-select');
        if (themeSelect) {
            themeSelect.value = this.currentTheme;
            themeSelect.addEventListener('change', (e) => {
                this.changeTheme(e.target.value);
            });
        }
    }
    
    setupLanguageSelector() {
        const langSelect = document.getElementById('language-select');
        if (langSelect) {
            langSelect.value = this.currentLanguage;
            langSelect.addEventListener('change', (e) => {
                this.changeLanguage(e.target.value);
            });
        }
    }
    
    async initializeComponents() {
        // Initialize AI completion engine
        if (window.aiCompletion) {
            await window.aiCompletion.initializeCompletion();
        }
        
        // Initialize debugger
        if (window.synapseDebugger) {
            window.synapseDebugger.init();
        }
        
        // Initialize project manager
        if (window.projectManager) {
            window.projectManager.init();
        }
        
        // Initialize test runner
        if (window.synapseTestRunner) {
            // Add default test suites
            this.addDefaultTestSuites();
        }
    }
    
    setupKeyboardShortcuts() {
        const shortcuts = {
            'Ctrl+N': () => this.newFile(),
            'Ctrl+O': () => this.openFile(),
            'Ctrl+S': () => this.saveFile(),
            'Ctrl+Shift+S': () => this.saveAs(),
            'F5': () => this.runCode(),
            'F9': () => this.toggleBreakpoint(),
            'F10': () => this.stepOver(),
            'F11': () => this.stepInto(),
            'Shift+F11': () => this.stepOut(),
            'Ctrl+F5': () => this.runWithoutDebugging(),
            'Ctrl+Shift+F5': () => this.restartDebugging(),
            'Ctrl+Shift+P': () => this.showCommandPalette(),
            'Ctrl+Shift+X': () => this.showExtensions(),
            'Ctrl+`': () => this.toggleTerminal(),
            'Ctrl+Shift+`': () => this.newTerminal(),
            'Ctrl+/': () => this.toggleComment(),
            'Ctrl+Shift+/': () => this.toggleBlockComment(),
            'Alt+Shift+F': () => this.formatDocument(),
            'F12': () => this.goToDefinition(),
            'Shift+F12': () => this.findReferences(),
            'F2': () => this.rename(),
            'Ctrl+Space': () => this.triggerSuggest(),
            'Ctrl+Shift+Space': () => this.triggerParameterHints(),
            'Ctrl+K Ctrl+I': () => this.showHover(),
            'Ctrl+Shift+O': () => this.goToSymbol()
        };
        
        document.addEventListener('keydown', (e) => {
            const key = this.getKeyCombo(e);
            const action = shortcuts[key];
            if (action && typeof action === 'function') {
                e.preventDefault();
                action();
            }
        });
    }
    
    getKeyCombo(e) {
        const parts = [];
        if (e.ctrlKey) parts.push('Ctrl');
        if (e.altKey) parts.push('Alt');
        if (e.shiftKey) parts.push('Shift');
        if (e.metaKey) parts.push('Meta');
        
        const key = e.key === ' ' ? 'Space' : e.key;
        parts.push(key);
        
        return parts.join('+');
    }
    
    async connectToBackend() {
        try {
            const response = await fetch('/api/ide/status');
            const status = await response.json();
            
            if (status.connected) {
                this.updateServerStatus('Connected');
            } else {
                this.updateServerStatus('Disconnected');
            }
        } catch (error) {
            this.updateServerStatus('Error');
        }
    }
    
    loadWelcomeContent() {
        const welcomeContent = `// Welcome to Synapse IDE v${this.version}
// Advanced IDE for Scientific Computing Languages

// Synapse Language Example
experiment WelcomeDemo {
    // Uncertainty quantification
    uncertain temperature = 300.0 ± 5.0
    uncertain pressure = 1.0 ± 0.1
    
    // Parallel computation
    parallel {
        branch physics: calculate_ideal_gas(temperature, pressure)
        branch monte_carlo: simulate_molecular_dynamics(1000)
        branch ai_analysis: predict_phase_transition(temperature, pressure)
    }
    
    // Synthesize results
    synthesize: combine_scientific_insights(physics, monte_carlo, ai_analysis)
}

// Features:
// - AI-powered code completion (Ctrl+Space)
// - Real-time error detection
// - Cross-language transpilation
// - Integrated debugging with quantum state visualization
// - Project management with multi-language support
// - Built-in testing framework

// Quick Start:
// 1. Create a new project (Ctrl+Shift+N)
// 2. Choose your primary language (Synapse, Qubit-Flow, Quantum-Net, Flux, Crowe)
// 3. Start coding with AI assistance
// 4. Run your code (F5) or debug (F9 for breakpoints)
// 5. Use the transpiler to convert to other languages

// Press F1 or Ctrl+Shift+P to open the command palette
// Visit the documentation for detailed examples and tutorials
`;
        
        this.editor.setValue(welcomeContent);
        this.editor.setPosition({ lineNumber: 1, column: 1 });
    }
    
    // Action handlers
    handleAction(action, event) {
        switch (action) {
            case 'new-file':
                this.newFile();
                break;
            case 'open-project':
                this.openProject();
                break;
            case 'save':
                this.saveFile();
                break;
            case 'run-code':
                this.runCode();
                break;
            case 'debug-code':
                this.debugCode();
                break;
            case 'ai-assist':
                this.showAIAssist();
                break;
            case 'format':
                this.formatDocument();
                break;
            case 'ai-explain':
                this.aiExplainCode();
                break;
            case 'ai-optimize':
                this.aiOptimizeCode();
                break;
            case 'clear-console':
                this.clearConsole();
                break;
            default:
                console.log('Unknown action:', action);
        }
    }
    
    newFile() {
        this.editor.setValue('');
        this.editor.setPosition({ lineNumber: 1, column: 1 });
        this.logConsole('New file created', 'info');
    }
    
    async openProject() {
        if (window.projectManager) {
            window.projectManager.showOpenProjectDialog();
        }
    }
    
    async saveFile() {
        if (window.projectManager && window.projectManager.currentProject) {
            await window.projectManager.saveProject();
        } else {
            // Save as new file
            this.saveAs();
        }
    }
    
    saveAs() {
        // Implement save as dialog
        this.logConsole('Save As not implemented yet', 'warning');
    }
    
    async runCode() {
        const code = this.editor.getValue();
        const language = this.currentLanguage;
        
        this.logConsole(`Running ${language} code...`, 'info');
        
        try {
            const response = await fetch('/api/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code, language })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.logConsole('Execution completed successfully', 'success');
                this.logConsole(result.output, 'output');
            } else {
                this.logConsole('Execution failed', 'error');
                this.logConsole(result.error, 'error');
            }
            
        } catch (error) {
            this.logConsole(`Execution error: ${error.message}`, 'error');
        }
    }
    
    async debugCode() {
        const code = this.editor.getValue();
        const language = this.currentLanguage;
        
        if (window.synapseDebugger) {
            await window.synapseDebugger.startDebugging(language, code);
        }
    }
    
    showAIAssist() {
        this.switchSidebarTab('ai');
        const aiInput = document.getElementById('ai-input');
        if (aiInput) {
            aiInput.focus();
        }
    }
    
    async aiExplainCode() {
        const selectedText = this.getSelectedText();
        if (!selectedText) {
            this.logConsole('Please select code to explain', 'warning');
            return;
        }
        
        if (window.aiCompletion) {
            const explanation = await window.aiCompletion.explainCode(selectedText, this.currentLanguage);
            this.showAIResponse('Code Explanation', explanation);
        }
    }
    
    async aiOptimizeCode() {
        const selectedText = this.getSelectedText();
        if (!selectedText) {
            this.logConsole('Please select code to optimize', 'warning');
            return;
        }
        
        if (window.aiCompletion) {
            const optimization = await window.aiCompletion.optimizeCode(selectedText, this.currentLanguage);
            this.showAIResponse('Code Optimization', optimization);
        }
    }
    
    formatDocument() {
        // Implement code formatting
        this.logConsole('Code formatting not implemented yet', 'warning');
    }
    
    clearConsole() {
        const consoleArea = document.getElementById('console-area');
        if (consoleArea) {
            consoleArea.innerHTML = '';
        }
    }
    
    // UI update methods
    switchSidebarTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.sidebar-tabs .tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update panels
        document.querySelectorAll('.sidebar-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`${tabName}-panel`).classList.add('active');
    }
    
    switchOutputTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.output-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
        
        // Update content areas
        document.querySelectorAll('.output-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-output`).classList.add('active');
    }
    
    changeTheme(themeName) {
        this.currentTheme = themeName;
        monaco.editor.setTheme(themeName);
        this.logConsole(`Theme changed to ${themeName}`, 'info');
    }
    
    changeLanguage(language) {
        this.currentLanguage = language;
        monaco.editor.setModelLanguage(this.editor.getModel(), language);
        this.updateLanguageStatus();
        this.logConsole(`Language changed to ${language}`, 'info');
    }
    
    updateCursorPosition(position) {
        const statusElement = document.getElementById('cursor-position');
        if (statusElement) {
            statusElement.textContent = `Ln ${position.lineNumber}, Col ${position.column}`;
        }
    }
    
    updateLanguageStatus() {
        const statusElement = document.getElementById('language-status');
        if (statusElement) {
            statusElement.textContent = this.currentLanguage;
        }
    }
    
    updateServerStatus(status) {
        const statusElement = document.getElementById('server-status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `status-item status-${status.toLowerCase()}`;
        }
    }
    
    // Utility methods
    getSelectedText() {
        const selection = this.editor.getSelection();
        const model = this.editor.getModel();
        return model.getValueInRange(selection);
    }
    
    logConsole(message, level = 'info') {
        const consoleArea = document.getElementById('console-area');
        if (!consoleArea) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `console-log console-log-${level}`;
        logEntry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-message">${message}</span>
        `;
        
        consoleArea.appendChild(logEntry);
        consoleArea.scrollTop = consoleArea.scrollHeight;
    }
    
    showAIResponse(title, content) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;
        
        const messageElement = document.createElement('div');
        messageElement.className = 'ai-message';
        messageElement.innerHTML = `
            <div class="message-header">
                <span class="message-title">${title}</span>
                <span class="message-time">${new Date().toLocaleTimeString()}</span>
            </div>
            <div class="message-content">${content}</div>
        `;
        
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    showLoading(message) {
        const overlay = document.getElementById('loading-overlay');
        const text = document.querySelector('.loading-text');
        if (overlay && text) {
            text.textContent = message;
            overlay.classList.remove('hidden');
        }
    }
    
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    showError(message) {
        alert(message); // Replace with better error dialog
    }
    
    addDefaultTestSuites() {
        if (!window.synapseTestRunner) return;
        
        // Add Synapse test suite
        window.synapseTestRunner.addTestSuite('Synapse Core Tests', 'synapse', [
            {
                name: 'Uncertainty Propagation',
                code: 'uncertain x = 10.0 ± 1.0\nuncertain y = 20.0 ± 2.0\nuncertain result = x + y',
                expected: '30.0 ± 2.236'
            },
            {
                name: 'Parallel Execution',
                code: 'parallel {\n    branch a: compute_fast()\n    branch b: compute_slow()\n}',
                expected: 'parallel_completion'
            }
        ]);
    }
    
    // Extension system
    loadExtension(extensionId) {
        // Implementation for loading IDE extensions
        console.log(`Loading extension: ${extensionId}`);
    }
    
    registerPlugin(pluginId, plugin) {
        this.plugins.set(pluginId, plugin);
        console.log(`Plugin registered: ${pluginId}`);
    }
}

// Initialize IDE when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.synapseIDE = new SynapseIDE();
});

// Global error handler
window.addEventListener('error', (e) => {
    console.error('IDE Error:', e.error);
    if (window.synapseIDE) {
        window.synapseIDE.logConsole(`Error: ${e.error.message}`, 'error');
    }
});