/**
 * Execution Engine for Quantum Trinity Playground
 * 
 * Handles code execution for Synapse, Qubit-Flow, and Quantum-Net languages.
 * Provides sandboxed execution with proper output capture and error handling.
 */

class ExecutionEngine {
    constructor() {
        this.worker = null;
        this.initializeWorker();
    }
    
    initializeWorker() {
        // Create a web worker for sandboxed execution
        const workerCode = `
            // Synapse Language Runtime
            class UncertainValue {
                constructor(value, uncertainty) {
                    this.value = value;
                    this.uncertainty = uncertainty;
                }
                
                toString() {
                    return \`\${this.value} ± \${this.uncertainty}\`;
                }
                
                add(other) {
                    if (other instanceof UncertainValue) {
                        const newValue = this.value + other.value;
                        const newUncertainty = Math.sqrt(
                            this.uncertainty ** 2 + other.uncertainty ** 2
                        );
                        return new UncertainValue(newValue, newUncertainty);
                    }
                    return new UncertainValue(this.value + other, this.uncertainty);
                }
                
                multiply(other) {
                    if (other instanceof UncertainValue) {
                        const newValue = this.value * other.value;
                        const relUnc1 = this.uncertainty / this.value;
                        const relUnc2 = other.uncertainty / other.value;
                        const newRelUnc = Math.sqrt(relUnc1 ** 2 + relUnc2 ** 2);
                        return new UncertainValue(newValue, newValue * newRelUnc);
                    }
                    return new UncertainValue(
                        this.value * other,
                        this.uncertainty * Math.abs(other)
                    );
                }
            }
            
            // Quantum State for Qubit-Flow
            class QuantumState {
                constructor(amplitudes) {
                    this.amplitudes = amplitudes;
                    this.normalize();
                }
                
                normalize() {
                    const norm = Math.sqrt(
                        this.amplitudes.reduce((sum, a) => sum + Math.abs(a) ** 2, 0)
                    );
                    this.amplitudes = this.amplitudes.map(a => a / norm);
                }
                
                measure() {
                    const probabilities = this.amplitudes.map(a => Math.abs(a) ** 2);
                    const random = Math.random();
                    let cumulative = 0;
                    
                    for (let i = 0; i < probabilities.length; i++) {
                        cumulative += probabilities[i];
                        if (random < cumulative) {
                            return i;
                        }
                    }
                    return probabilities.length - 1;
                }
            }
            
            // Output buffer
            const output = [];
            
            // Override console.log for output capture
            const originalLog = console.log;
            console.log = (...args) => {
                output.push({
                    type: 'log',
                    text: args.map(a => String(a)).join(' ')
                });
            };
            
            // Custom print function
            function print(...args) {
                output.push({
                    type: 'log',
                    text: args.map(a => String(a)).join(' ')
                });
            }
            
            // Monte Carlo simulation
            function monte_carlo(config, callback) {
                const samples = config.samples || 10000;
                const results = [];
                
                for (let i = 0; i < samples; i++) {
                    // Sample from uncertain values
                    const sampledValues = {};
                    for (const [key, value] of Object.entries(config.inputs || {})) {
                        if (value instanceof UncertainValue) {
                            // Sample from normal distribution
                            const sample = value.value + value.uncertainty * gaussianRandom();
                            sampledValues[key] = sample;
                        } else {
                            sampledValues[key] = value;
                        }
                    }
                    
                    // Execute callback with sampled values
                    const result = callback(sampledValues);
                    results.push(result);
                }
                
                // Calculate statistics
                const mean = results.reduce((a, b) => a + b, 0) / results.length;
                const variance = results.reduce((sum, r) => sum + (r - mean) ** 2, 0) / results.length;
                const std = Math.sqrt(variance);
                
                return new UncertainValue(mean, std);
            }
            
            // Gaussian random number generator
            function gaussianRandom() {
                let u = 0, v = 0;
                while (u === 0) u = Math.random();
                while (v === 0) v = Math.random();
                return Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
            }
            
            // Parallel execution simulation
            async function parallel(tasks) {
                const promises = tasks.map(task => 
                    new Promise(resolve => setTimeout(() => resolve(task()), 0))
                );
                return await Promise.all(promises);
            }
            
            // Quantum gates for Qubit-Flow
            const QuantumGates = {
                H: (state) => {
                    // Hadamard gate
                    const h = 1 / Math.sqrt(2);
                    return new QuantumState([
                        h * (state.amplitudes[0] + state.amplitudes[1]),
                        h * (state.amplitudes[0] - state.amplitudes[1])
                    ]);
                },
                
                X: (state) => {
                    // Pauli-X gate
                    return new QuantumState([
                        state.amplitudes[1],
                        state.amplitudes[0]
                    ]);
                },
                
                CNOT: (control, target) => {
                    // Simplified 2-qubit CNOT
                    // This is a placeholder - full implementation would be more complex
                    return [control, target];
                }
            };
            
            // Message handler
            self.onmessage = function(e) {
                const { code, language } = e.data;
                const startTime = performance.now();
                
                try {
                    // Clear output
                    output.length = 0;
                    
                    // Parse and execute based on language
                    let result;
                    
                    if (language === 'synapse') {
                        result = executeSynapse(code);
                    } else if (language === 'qubit-flow') {
                        result = executeQubitFlow(code);
                    } else if (language === 'quantum-net') {
                        result = executeQuantumNet(code);
                    }
                    
                    const executionTime = Math.round(performance.now() - startTime);
                    
                    self.postMessage({
                        success: true,
                        output: output,
                        result: result,
                        executionTime: executionTime
                    });
                    
                } catch (error) {
                    self.postMessage({
                        success: false,
                        error: {
                            message: error.message,
                            stack: error.stack
                        }
                    });
                }
            };
            
            function executeSynapse(code) {
                // Simple Synapse interpreter
                // This is a simplified version - real implementation would be more complex
                
                // Replace uncertain syntax
                let processedCode = code.replace(
                    /uncertain\\s+(\\w+)\\s*=\\s*([\\d.]+)\\s*±\\s*([\\d.]+)/g,
                    (match, name, value, uncertainty) => {
                        return \`const \${name} = new UncertainValue(\${value}, \${uncertainty})\`;
                    }
                );
                
                // Replace print statements
                processedCode = processedCode.replace(/print\\(/g, 'print(');
                
                // Execute the code
                eval(processedCode);
                
                return { language: 'synapse' };
            }
            
            function executeQubitFlow(code) {
                // Simple Qubit-Flow interpreter
                const lines = code.split('\\n');
                const qubits = {};
                
                for (const line of lines) {
                    const trimmed = line.trim();
                    
                    // Parse qubit declarations
                    if (trimmed.startsWith('qubit')) {
                        const match = trimmed.match(/qubit\\s+(\\w+)\\s*=\\s*\\|([01])⟩/);
                        if (match) {
                            const [, name, state] = match;
                            qubits[name] = new QuantumState(
                                state === '0' ? [1, 0] : [0, 1]
                            );
                            output.push({
                                type: 'log',
                                text: \`Created qubit \${name} in state |\${state}⟩\`
                            });
                        }
                    }
                    
                    // Parse gate applications
                    if (trimmed.match(/H\\[\\w+\\]/)) {
                        const match = trimmed.match(/H\\[(\\w+)\\]/);
                        if (match && qubits[match[1]]) {
                            qubits[match[1]] = QuantumGates.H(qubits[match[1]]);
                            output.push({
                                type: 'log',
                                text: \`Applied Hadamard gate to \${match[1]}\`
                            });
                        }
                    }
                }
                
                // Return quantum state for visualization
                return {
                    language: 'qubit-flow',
                    quantumState: {
                        qubits: Object.keys(qubits).length,
                        amplitudes: Object.values(qubits)[0]?.amplitudes || []
                    }
                };
            }
            
            function executeQuantumNet(code) {
                // Simple Quantum-Net interpreter
                const lines = code.split('\\n');
                const network = { nodes: [], connections: [] };
                
                for (const line of lines) {
                    const trimmed = line.trim();
                    
                    // Parse network definition
                    if (trimmed.includes('nodes:')) {
                        const match = trimmed.match(/nodes:\\s*\\[([^\\]]+)\\]/);
                        if (match) {
                            network.nodes = match[1].split(',').map(n => 
                                n.trim().replace(/['"]/g, '')
                            );
                            output.push({
                                type: 'log',
                                text: \`Created network with nodes: \${network.nodes.join(', ')}\`
                            });
                        }
                    }
                }
                
                return { language: 'quantum-net', network };
            }
        `;
        
        const blob = new Blob([workerCode], { type: 'application/javascript' });
        const workerUrl = URL.createObjectURL(blob);
        this.worker = new Worker(workerUrl);
    }
    
    async execute(code, language) {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Execution timeout'));
            }, 5000); // 5 second timeout
            
            this.worker.onmessage = (e) => {
                clearTimeout(timeout);
                
                if (e.data.success) {
                    resolve(e.data);
                } else {
                    reject(e.data.error);
                }
            };
            
            this.worker.onerror = (error) => {
                clearTimeout(timeout);
                reject(error);
            };
            
            this.worker.postMessage({ code, language });
        });
    }
}

// Visualization Engine
class VisualizationEngine {
    constructor() {
        this.plotlyReady = false;
        this.chartjsReady = false;
        this.checkLibraries();
    }
    
    checkLibraries() {
        // Check if Plotly is loaded
        if (typeof Plotly !== 'undefined') {
            this.plotlyReady = true;
        }
        
        // Check if Chart.js is loaded
        if (typeof Chart !== 'undefined') {
            this.chartjsReady = true;
        }
    }
    
    render(visualizations) {
        if (!visualizations || visualizations.length === 0) {
            return;
        }
        
        const canvas = document.getElementById('plotCanvas');
        const container = canvas.parentElement;
        
        // Clear previous visualizations
        container.innerHTML = '';
        
        visualizations.forEach(viz => {
            if (viz.type === 'plot' && this.plotlyReady) {
                this.renderPlotly(viz, container);
            } else if (viz.type === 'chart' && this.chartjsReady) {
                this.renderChart(viz, container);
            } else {
                this.renderCustom(viz, container);
            }
        });
    }
    
    renderPlotly(viz, container) {
        const div = document.createElement('div');
        div.style.width = '100%';
        div.style.height = '100%';
        container.appendChild(div);
        
        const data = viz.data || [{
            x: [1, 2, 3, 4],
            y: [10, 15, 13, 17],
            type: 'scatter'
        }];
        
        const layout = viz.layout || {
            title: viz.title || 'Plot',
            paper_bgcolor: '#1e1e1e',
            plot_bgcolor: '#252526',
            font: { color: '#e0e0e0' },
            xaxis: { gridcolor: '#3c3c3c' },
            yaxis: { gridcolor: '#3c3c3c' }
        };
        
        Plotly.newPlot(div, data, layout, { responsive: true });
    }
    
    renderChart(viz, container) {
        const canvas = document.createElement('canvas');
        container.appendChild(canvas);
        
        new Chart(canvas, {
            type: viz.chartType || 'line',
            data: viz.data || {
                labels: ['January', 'February', 'March', 'April'],
                datasets: [{
                    label: 'Example Data',
                    data: [12, 19, 3, 5],
                    borderColor: '#00d4ff',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: '#e0e0e0' }
                    }
                },
                scales: {
                    x: {
                        grid: { color: '#3c3c3c' },
                        ticks: { color: '#999' }
                    },
                    y: {
                        grid: { color: '#3c3c3c' },
                        ticks: { color: '#999' }
                    }
                }
            }
        });
    }
    
    renderCustom(viz, container) {
        // Custom visualization rendering
        const div = document.createElement('div');
        div.className = 'custom-visualization';
        div.innerHTML = viz.html || '<p>Custom visualization</p>';
        container.appendChild(div);
    }
}