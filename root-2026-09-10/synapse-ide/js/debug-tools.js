/**
 * Advanced Debugging and Testing Tools for Synapse IDE
 * Supports multi-language debugging with quantum state visualization
 */

class SynapseDebugger {
    constructor() {
        this.isDebugging = false;
        this.breakpoints = new Map();
        this.callStack = [];
        this.variables = new Map();
        this.quantumStates = new Map();
        this.uncertaintyValues = new Map();
        this.debugSession = null;
        this.stepMode = 'over'; // 'over', 'into', 'out'
        
        this.init();
    }
    
    init() {
        this.setupDebugUI();
        this.registerDebugEvents();
        console.log('Synapse Debugger initialized');
    }
    
    setupDebugUI() {
        // Add debug gutter to Monaco editor
        if (window.monacoEditor) {
            window.monacoEditor.onMouseDown((e) => {
                if (e.target.type === monaco.editor.MouseTargetType.GUTTER_GLYPH_MARGIN) {
                    this.toggleBreakpoint(e.target.position.lineNumber);
                }
            });
        }
    }
    
    registerDebugEvents() {
        // Listen for debug control buttons
        document.addEventListener('click', (e) => {
            const action = e.target.getAttribute('data-action');
            
            switch (action) {
                case 'step-over':
                    this.stepOver();
                    break;
                case 'step-into':
                    this.stepInto();
                    break;
                case 'step-out':
                    this.stepOut();
                    break;
                case 'continue':
                    this.continue();
                    break;
                case 'stop-debug':
                    this.stopDebugging();
                    break;
            }
        });
    }
    
    async startDebugging(language, code) {
        if (this.isDebugging) {
            this.stopDebugging();
        }
        
        this.isDebugging = true;
        this.debugSession = {
            id: Date.now(),
            language,
            code,
            currentLine: 1,
            startTime: new Date()
        };
        
        try {
            // Initialize debug session with backend
            const response = await fetch('/api/debug/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    language,
                    code,
                    breakpoints: Array.from(this.breakpoints.keys())
                })
            });
            
            const debugInfo = await response.json();
            this.updateDebugUI(debugInfo);
            
            this.logDebug('Debug session started', 'info');
            
        } catch (error) {
            this.logDebug(`Debug start error: ${error.message}`, 'error');
            this.stopDebugging();
        }
    }
    
    toggleBreakpoint(lineNumber) {
        if (this.breakpoints.has(lineNumber)) {
            this.breakpoints.delete(lineNumber);
            this.removeBreakpointGutter(lineNumber);
            this.logDebug(`Breakpoint removed at line ${lineNumber}`, 'info');
        } else {
            this.breakpoints.set(lineNumber, {
                line: lineNumber,
                condition: null,
                hitCount: 0,
                enabled: true
            });
            this.addBreakpointGutter(lineNumber);
            this.logDebug(`Breakpoint added at line ${lineNumber}`, 'info');
        }
        
        // Sync with debug session
        if (this.isDebugging) {
            this.syncBreakpoints();
        }
    }
    
    addBreakpointGutter(lineNumber) {
        if (!window.monacoEditor) return;
        
        const model = window.monacoEditor.getModel();
        const decorations = model.deltaDecorations([], [{
            range: new monaco.Range(lineNumber, 1, lineNumber, 1),
            options: {
                isWholeLine: true,
                className: 'debug-breakpoint-line',
                glyphMarginClassName: 'debug-breakpoint-glyph',
                stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
            }
        }]);
        
        this.breakpoints.get(lineNumber).decorationId = decorations[0];
    }
    
    removeBreakpointGutter(lineNumber) {
        if (!window.monacoEditor) return;
        
        const model = window.monacoEditor.getModel();
        const breakpoint = this.breakpoints.get(lineNumber);
        
        if (breakpoint && breakpoint.decorationId) {
            model.deltaDecorations([breakpoint.decorationId], []);
        }
    }
    
    async stepOver() {
        if (!this.isDebugging) return;
        
        this.stepMode = 'over';
        await this.executeDebugStep();
    }
    
    async stepInto() {
        if (!this.isDebugging) return;
        
        this.stepMode = 'into';
        await this.executeDebugStep();
    }
    
    async stepOut() {
        if (!this.isDebugging) return;
        
        this.stepMode = 'out';
        await this.executeDebugStep();
    }
    
    async continue() {
        if (!this.isDebugging) return;
        
        try {
            const response = await fetch('/api/debug/continue', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId: this.debugSession.id })
            });
            
            const debugInfo = await response.json();
            this.updateDebugUI(debugInfo);
            
        } catch (error) {
            this.logDebug(`Continue error: ${error.message}`, 'error');
        }
    }
    
    async executeDebugStep() {
        try {
            const response = await fetch('/api/debug/step', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: this.debugSession.id,
                    stepType: this.stepMode
                })
            });
            
            const debugInfo = await response.json();
            this.updateDebugUI(debugInfo);
            
        } catch (error) {
            this.logDebug(`Step error: ${error.message}`, 'error');
        }
    }
    
    stopDebugging() {
        if (!this.isDebugging) return;
        
        this.isDebugging = false;
        this.clearDebugHighlights();
        
        if (this.debugSession) {
            // Notify backend
            fetch('/api/debug/stop', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sessionId: this.debugSession.id })
            }).catch(console.error);
            
            this.debugSession = null;
        }
        
        this.logDebug('Debug session stopped', 'info');
        this.updateDebugUI({ stopped: true });
    }
    
    updateDebugUI(debugInfo) {
        // Update current line highlight
        if (debugInfo.currentLine) {
            this.highlightCurrentLine(debugInfo.currentLine);
        }
        
        // Update variables panel
        if (debugInfo.variables) {
            this.updateVariablesPanel(debugInfo.variables);
        }
        
        // Update quantum states if applicable
        if (debugInfo.quantumStates) {
            this.updateQuantumStatesPanel(debugInfo.quantumStates);
        }
        
        // Update uncertainty values for Synapse
        if (debugInfo.uncertaintyValues) {
            this.updateUncertaintyPanel(debugInfo.uncertaintyValues);
        }
        
        // Update call stack
        if (debugInfo.callStack) {
            this.updateCallStackPanel(debugInfo.callStack);
        }
        
        // Update status
        this.updateDebugStatus(debugInfo);
    }
    
    highlightCurrentLine(lineNumber) {
        if (!window.monacoEditor) return;
        
        this.clearDebugHighlights();
        
        const model = window.monacoEditor.getModel();
        const decorations = model.deltaDecorations([], [{
            range: new monaco.Range(lineNumber, 1, lineNumber, 1),
            options: {
                isWholeLine: true,
                className: 'debug-current-line',
                stickiness: monaco.editor.TrackedRangeStickiness.NeverGrowsWhenTypingAtEdges
            }
        }]);
        
        this.currentLineDecoration = decorations[0];
        
        // Scroll to current line
        window.monacoEditor.revealLineInCenter(lineNumber);
    }
    
    clearDebugHighlights() {
        if (!window.monacoEditor || !this.currentLineDecoration) return;
        
        const model = window.monacoEditor.getModel();
        model.deltaDecorations([this.currentLineDecoration], []);
        this.currentLineDecoration = null;
    }
    
    updateVariablesPanel(variables) {
        const panel = document.getElementById('variables-content');
        if (!panel) return;
        
        panel.innerHTML = '';
        
        variables.forEach(variable => {
            const varElement = document.createElement('div');
            varElement.className = 'debug-variable';
            varElement.innerHTML = `
                <div class="variable-header">
                    <span class="variable-name">${variable.name}</span>
                    <span class="variable-type">${variable.type}</span>
                </div>
                <div class="variable-value">${this.formatVariableValue(variable)}</div>
            `;
            panel.appendChild(varElement);
        });
    }
    
    updateQuantumStatesPanel(states) {
        const panel = document.getElementById('quantum-states-content');
        if (!panel) return;
        
        panel.innerHTML = '';
        
        states.forEach(state => {
            const stateElement = document.createElement('div');
            stateElement.className = 'quantum-state';
            stateElement.innerHTML = `
                <div class="state-header">
                    <span class="state-name">${state.name}</span>
                    <span class="state-probability">${(state.probability * 100).toFixed(2)}%</span>
                </div>
                <div class="state-visualization">
                    ${this.renderQuantumState(state)}
                </div>
            `;
            panel.appendChild(stateElement);
        });
    }
    
    updateUncertaintyPanel(uncertainties) {
        const panel = document.getElementById('uncertainty-content');
        if (!panel) return;
        
        panel.innerHTML = '';
        
        uncertainties.forEach(uncertainty => {
            const uncElement = document.createElement('div');
            uncElement.className = 'uncertainty-value';
            uncElement.innerHTML = `
                <div class="uncertainty-header">
                    <span class="uncertainty-name">${uncertainty.name}</span>
                </div>
                <div class="uncertainty-display">
                    ${uncertainty.value} ± ${uncertainty.error}
                    <div class="uncertainty-bar">
                        <div class="uncertainty-range" style="width: ${uncertainty.confidence * 100}%"></div>
                    </div>
                </div>
            `;
            panel.appendChild(uncElement);
        });
    }
    
    updateCallStackPanel(callStack) {
        const panel = document.getElementById('callstack-content');
        if (!panel) return;
        
        panel.innerHTML = '';
        
        callStack.forEach((frame, index) => {
            const frameElement = document.createElement('div');
            frameElement.className = 'callstack-frame';
            frameElement.innerHTML = `
                <div class="frame-function">${frame.function}</div>
                <div class="frame-location">${frame.file}:${frame.line}</div>
            `;
            
            frameElement.addEventListener('click', () => {
                this.jumpToFrame(frame);
            });
            
            panel.appendChild(frameElement);
        });
    }
    
    formatVariableValue(variable) {
        switch (variable.type) {
            case 'uncertain':
                return `${variable.value} ± ${variable.error}`;
            case 'quantum_state':
                return `|${variable.state}⟩ (${(variable.probability * 100).toFixed(1)}%)`;
            case 'array':
                return `[${variable.value.length} items]`;
            case 'object':
                return `{${Object.keys(variable.value).length} properties}`;
            default:
                return variable.value.toString();
        }
    }
    
    renderQuantumState(state) {
        // Create a simple visualization of quantum state
        const canvas = document.createElement('canvas');
        canvas.width = 200;
        canvas.height = 100;
        const ctx = canvas.getContext('2d');
        
        // Draw Bloch sphere representation
        ctx.strokeStyle = '#43E5FF';
        ctx.lineWidth = 2;
        
        // Sphere outline
        ctx.beginPath();
        ctx.arc(100, 50, 40, 0, 2 * Math.PI);
        ctx.stroke();
        
        // State vector
        const angle = state.phase || 0;
        const x = 100 + 35 * Math.cos(angle);
        const y = 50 + 35 * Math.sin(angle);
        
        ctx.beginPath();
        ctx.moveTo(100, 50);
        ctx.lineTo(x, y);
        ctx.strokeStyle = '#7A5CFF';
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // State point
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = '#7A5CFF';
        ctx.fill();
        
        return canvas.outerHTML;
    }
    
    jumpToFrame(frame) {
        if (!window.monacoEditor) return;
        
        // Scroll to the frame location
        window.monacoEditor.setPosition({
            lineNumber: frame.line,
            column: frame.column || 1
        });
        
        this.logDebug(`Jumped to ${frame.function} at line ${frame.line}`, 'info');
    }
    
    updateDebugStatus(debugInfo) {
        const statusElement = document.getElementById('debug-status');
        if (!statusElement) return;
        
        if (debugInfo.stopped) {
            statusElement.textContent = 'Stopped';
            statusElement.className = 'debug-status stopped';
        } else if (debugInfo.paused) {
            statusElement.textContent = 'Paused';
            statusElement.className = 'debug-status paused';
        } else if (debugInfo.running) {
            statusElement.textContent = 'Running';
            statusElement.className = 'debug-status running';
        }
    }
    
    async syncBreakpoints() {
        if (!this.debugSession) return;
        
        try {
            await fetch('/api/debug/breakpoints', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: this.debugSession.id,
                    breakpoints: Array.from(this.breakpoints.entries()).map(([line, bp]) => ({
                        line,
                        condition: bp.condition,
                        enabled: bp.enabled
                    }))
                })
            });
        } catch (error) {
            this.logDebug(`Breakpoint sync error: ${error.message}`, 'error');
        }
    }
    
    logDebug(message, level = 'info') {
        const debugArea = document.getElementById('debug-area');
        if (!debugArea) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `debug-log debug-log-${level}`;
        logEntry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-message">${message}</span>
        `;
        
        debugArea.appendChild(logEntry);
        debugArea.scrollTop = debugArea.scrollHeight;
    }
    
    // Evaluation methods for interactive debugging
    async evaluateExpression(expression, language) {
        if (!this.debugSession) {
            throw new Error('No active debug session');
        }
        
        try {
            const response = await fetch('/api/debug/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: this.debugSession.id,
                    expression,
                    language
                })
            });
            
            const result = await response.json();
            return result;
            
        } catch (error) {
            throw new Error(`Evaluation error: ${error.message}`);
        }
    }
    
    // Watch expressions
    addWatchExpression(expression) {
        const watchPanel = document.getElementById('watch-content');
        if (!watchPanel) return;
        
        const watchElement = document.createElement('div');
        watchElement.className = 'watch-expression';
        watchElement.innerHTML = `
            <div class="watch-expr">${expression}</div>
            <div class="watch-value">Evaluating...</div>
            <button class="watch-remove" onclick="this.parentElement.remove()">×</button>
        `;
        
        watchPanel.appendChild(watchElement);
        
        // Evaluate immediately if debugging
        if (this.isDebugging) {
            this.evaluateWatch(watchElement, expression);
        }
    }
    
    async evaluateWatch(watchElement, expression) {
        try {
            const result = await this.evaluateExpression(expression, this.debugSession.language);
            const valueElement = watchElement.querySelector('.watch-value');
            valueElement.textContent = this.formatVariableValue(result);
            valueElement.className = 'watch-value watch-success';
        } catch (error) {
            const valueElement = watchElement.querySelector('.watch-value');
            valueElement.textContent = `Error: ${error.message}`;
            valueElement.className = 'watch-value watch-error';
        }
    }
}

// Test runner for all supported languages
class SynapseTestRunner {
    constructor() {
        this.testSuites = new Map();
        this.testResults = new Map();
        this.isRunning = false;
    }
    
    addTestSuite(name, language, tests) {
        this.testSuites.set(name, {
            name,
            language,
            tests,
            lastRun: null,
            results: null
        });
    }
    
    async runTests(suiteName = null) {
        if (this.isRunning) return;
        
        this.isRunning = true;
        
        try {
            const suitesToRun = suiteName 
                ? [this.testSuites.get(suiteName)]
                : Array.from(this.testSuites.values());
            
            for (const suite of suitesToRun) {
                if (suite) {
                    await this.runTestSuite(suite);
                }
            }
            
        } finally {
            this.isRunning = false;
        }
    }
    
    async runTestSuite(suite) {
        this.logTest(`Running test suite: ${suite.name}`, 'info');
        
        const results = {
            passed: 0,
            failed: 0,
            errors: [],
            details: []
        };
        
        for (const test of suite.tests) {
            try {
                const testResult = await this.runSingleTest(test, suite.language);
                results.details.push(testResult);
                
                if (testResult.passed) {
                    results.passed++;
                } else {
                    results.failed++;
                    results.errors.push(testResult.error);
                }
                
            } catch (error) {
                results.failed++;
                results.errors.push(error.message);
                results.details.push({
                    name: test.name,
                    passed: false,
                    error: error.message
                });
            }
        }
        
        suite.results = results;
        suite.lastRun = new Date();
        
        this.updateTestUI(suite);
        this.logTest(`Suite ${suite.name}: ${results.passed} passed, ${results.failed} failed`, 
                    results.failed > 0 ? 'error' : 'success');
    }
    
    async runSingleTest(test, language) {
        const response = await fetch('/api/test/run', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                language,
                code: test.code,
                expectedOutput: test.expected,
                assertions: test.assertions
            })
        });
        
        return response.json();
    }
    
    updateTestUI(suite) {
        const testPanel = document.getElementById('test-results');
        if (!testPanel) return;
        
        let suiteElement = document.getElementById(`test-suite-${suite.name}`);
        if (!suiteElement) {
            suiteElement = document.createElement('div');
            suiteElement.id = `test-suite-${suite.name}`;
            suiteElement.className = 'test-suite';
            testPanel.appendChild(suiteElement);
        }
        
        const results = suite.results;
        const status = results.failed > 0 ? 'failed' : 'passed';
        
        suiteElement.innerHTML = `
            <div class="test-suite-header ${status}">
                <span class="suite-name">${suite.name}</span>
                <span class="suite-stats">${results.passed}/${results.passed + results.failed}</span>
                <span class="suite-language">${suite.language}</span>
            </div>
            <div class="test-details">
                ${results.details.map(detail => `
                    <div class="test-result ${detail.passed ? 'passed' : 'failed'}">
                        <span class="test-name">${detail.name}</span>
                        ${detail.error ? `<span class="test-error">${detail.error}</span>` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    logTest(message, level = 'info') {
        const testArea = document.getElementById('test-output');
        if (!testArea) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `test-log test-log-${level}`;
        logEntry.innerHTML = `
            <span class="log-timestamp">${timestamp}</span>
            <span class="log-message">${message}</span>
        `;
        
        testArea.appendChild(logEntry);
        testArea.scrollTop = testArea.scrollHeight;
    }
}

// Initialize debugging tools
window.synapseDebugger = new SynapseDebugger();
window.synapseTestRunner = new SynapseTestRunner();

// Export for integration
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { SynapseDebugger, SynapseTestRunner };
}