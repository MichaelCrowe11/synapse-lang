/**
 * Enhanced Visualization Engine for Quantum Trinity Playground
 * 
 * Provides advanced visualizations for uncertainty, quantum states, and networks.
 */

class EnhancedVisualizationEngine {
    constructor() {
        this.plotlyReady = typeof Plotly !== 'undefined';
        this.chartjsReady = typeof Chart !== 'undefined';
        this.currentVisualizations = [];
    }
    
    render(data, container) {
        // Clear previous visualizations
        this.clear();
        
        if (!data || !data.visualizations) return;
        
        data.visualizations.forEach(viz => {
            switch (viz.type) {
                case 'uncertainty':
                    this.renderUncertaintyPlot(viz, container);
                    break;
                case 'histogram':
                    this.renderHistogram(viz, container);
                    break;
                case 'quantum_state':
                    this.renderQuantumState(viz, container);
                    break;
                case 'network':
                    this.renderNetwork(viz, container);
                    break;
                case 'heatmap':
                    this.renderHeatmap(viz, container);
                    break;
                case 'time_series':
                    this.renderTimeSeries(viz, container);
                    break;
                default:
                    this.renderGeneric(viz, container);
            }
        });
    }
    
    renderUncertaintyPlot(viz, container) {
        const div = document.createElement('div');
        div.className = 'visualization uncertainty-plot';
        div.style.height = '400px';
        container.appendChild(div);
        
        // Generate data with uncertainty bands
        const x = viz.data.x || Array.from({length: 100}, (_, i) => i);
        const y = viz.data.values || x.map(val => Math.sin(val * 0.1) * 10);
        const uncertainty = viz.data.uncertainty || y.map(() => Math.random() * 2);
        
        const trace1 = {
            x: x,
            y: y,
            type: 'scatter',
            mode: 'lines',
            name: 'Mean',
            line: { color: '#00d4ff', width: 2 }
        };
        
        // Upper bound
        const trace2 = {
            x: x,
            y: y.map((val, i) => val + uncertainty[i]),
            type: 'scatter',
            mode: 'lines',
            name: 'Upper bound',
            line: { color: 'rgba(0, 212, 255, 0.3)', width: 0 },
            showlegend: false,
            hoverinfo: 'skip'
        };
        
        // Lower bound
        const trace3 = {
            x: x,
            y: y.map((val, i) => val - uncertainty[i]),
            type: 'scatter',
            mode: 'lines',
            name: 'Lower bound',
            fill: 'tonexty',
            fillcolor: 'rgba(0, 212, 255, 0.2)',
            line: { color: 'rgba(0, 212, 255, 0.3)', width: 0 },
            showlegend: false,
            hoverinfo: 'skip'
        };
        
        const layout = {
            title: viz.title || 'Measurement with Uncertainty',
            xaxis: { 
                title: viz.xlabel || 'X',
                gridcolor: '#3c3c3c',
                color: '#e0e0e0'
            },
            yaxis: { 
                title: viz.ylabel || 'Y ± σ',
                gridcolor: '#3c3c3c',
                color: '#e0e0e0'
            },
            paper_bgcolor: '#1e1e1e',
            plot_bgcolor: '#252526',
            font: { color: '#e0e0e0' },
            showlegend: true,
            legend: {
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(0,0,0,0.5)'
            }
        };
        
        Plotly.newPlot(div, [trace3, trace2, trace1], layout, {responsive: true});
        this.currentVisualizations.push(div);
    }
    
    renderHistogram(viz, container) {
        const div = document.createElement('div');
        div.className = 'visualization histogram';
        div.style.height = '350px';
        container.appendChild(div);
        
        // Monte Carlo results visualization
        const values = viz.data.values || this.generateNormalDistribution(1000, 10, 2);
        const mean = viz.data.mean || values.reduce((a, b) => a + b) / values.length;
        const std = viz.data.std || Math.sqrt(
            values.reduce((sum, x) => sum + (x - mean) ** 2, 0) / values.length
        );
        
        const trace = {
            x: values,
            type: 'histogram',
            nbinsx: 30,
            marker: {
                color: 'rgba(0, 212, 255, 0.7)',
                line: {
                    color: '#00d4ff',
                    width: 1
                }
            },
            name: 'Distribution'
        };
        
        // Add normal curve overlay
        const xRange = [Math.min(...values), Math.max(...values)];
        const xCurve = Array.from({length: 100}, (_, i) => 
            xRange[0] + (xRange[1] - xRange[0]) * i / 99
        );
        const yCurve = xCurve.map(x => 
            (1 / (std * Math.sqrt(2 * Math.PI))) * 
            Math.exp(-0.5 * ((x - mean) / std) ** 2) * 
            values.length * (xRange[1] - xRange[0]) / 30
        );
        
        const normalCurve = {
            x: xCurve,
            y: yCurve,
            type: 'scatter',
            mode: 'lines',
            name: 'Normal fit',
            line: {
                color: '#ff6b6b',
                width: 2
            }
        };
        
        const layout = {
            title: `Monte Carlo Results (μ=${mean.toFixed(2)}, σ=${std.toFixed(2)})`,
            xaxis: {
                title: 'Value',
                gridcolor: '#3c3c3c',
                color: '#e0e0e0'
            },
            yaxis: {
                title: 'Frequency',
                gridcolor: '#3c3c3c',
                color: '#e0e0e0'
            },
            paper_bgcolor: '#1e1e1e',
            plot_bgcolor: '#252526',
            font: { color: '#e0e0e0' },
            showlegend: true
        };
        
        Plotly.newPlot(div, [trace, normalCurve], layout, {responsive: true});
        this.currentVisualizations.push(div);
    }
    
    renderQuantumState(viz, container) {
        const div = document.createElement('div');
        div.className = 'visualization quantum-state';
        container.appendChild(div);
        
        const qubits = viz.qubits || 2;
        const amplitudes = viz.amplitudes || this.generateRandomQuantumState(2 ** qubits);
        
        // Create Bloch sphere for single qubit
        if (qubits === 1) {
            this.renderBlochSphere(amplitudes, div);
        } else {
            // Multi-qubit state visualization
            this.renderStateVector(amplitudes, qubits, div);
        }
    }
    
    renderBlochSphere(amplitudes, container) {
        const div = document.createElement('div');
        div.style.height = '400px';
        container.appendChild(div);
        
        // Convert amplitudes to Bloch sphere coordinates
        const alpha = amplitudes[0];
        const beta = amplitudes[1];
        
        const theta = 2 * Math.acos(Math.abs(alpha));
        const phi = Math.atan2(beta.imag || 0, beta.real || beta);
        
        const x = Math.sin(theta) * Math.cos(phi);
        const y = Math.sin(theta) * Math.sin(phi);
        const z = Math.cos(theta);
        
        // Create sphere
        const sphere = {
            type: 'mesh3d',
            x: this.generateSphere().x,
            y: this.generateSphere().y,
            z: this.generateSphere().z,
            opacity: 0.2,
            color: '#3c3c3c',
            name: 'Bloch Sphere'
        };
        
        // State vector
        const stateVector = {
            type: 'scatter3d',
            mode: 'lines+markers',
            x: [0, x],
            y: [0, y],
            z: [0, z],
            line: {
                color: '#00d4ff',
                width: 4
            },
            marker: {
                size: [0, 8],
                color: '#00d4ff'
            },
            name: 'State Vector'
        };
        
        // Axes
        const axes = {
            type: 'scatter3d',
            mode: 'lines+text',
            x: [0, 1.2, 0, 0, 0, 0],
            y: [0, 0, 0, 1.2, 0, 0],
            z: [0, 0, 0, 0, 0, 1.2],
            text: ['', 'X', '', 'Y', '', 'Z'],
            textposition: 'top center',
            line: {
                color: '#666',
                width: 2
            },
            showlegend: false
        };
        
        const layout = {
            title: 'Qubit State on Bloch Sphere',
            scene: {
                xaxis: { range: [-1.5, 1.5], showgrid: false },
                yaxis: { range: [-1.5, 1.5], showgrid: false },
                zaxis: { range: [-1.5, 1.5], showgrid: false },
                bgcolor: '#1e1e1e'
            },
            paper_bgcolor: '#1e1e1e',
            font: { color: '#e0e0e0' }
        };
        
        Plotly.newPlot(div, [sphere, axes, stateVector], layout, {responsive: true});
        this.currentVisualizations.push(div);
    }
    
    renderStateVector(amplitudes, qubits, container) {
        const div = document.createElement('div');
        div.className = 'state-vector-viz';
        container.appendChild(div);
        
        // Create bar chart for amplitudes
        const states = Array.from({length: 2 ** qubits}, (_, i) => 
            '|' + i.toString(2).padStart(qubits, '0') + '⟩'
        );
        
        const probabilities = amplitudes.map(a => 
            (Math.abs(a.real || a) ** 2 + (a.imag || 0) ** 2)
        );
        
        const barDiv = document.createElement('div');
        barDiv.style.height = '300px';
        div.appendChild(barDiv);
        
        const trace = {
            x: states,
            y: probabilities,
            type: 'bar',
            marker: {
                color: probabilities.map(p => `rgba(0, 212, 255, ${p})`),
                line: {
                    color: '#00d4ff',
                    width: 1
                }
            }
        };
        
        const layout = {
            title: `${qubits}-Qubit Quantum State`,
            xaxis: {
                title: 'Basis State',
                color: '#e0e0e0'
            },
            yaxis: {
                title: 'Probability',
                range: [0, 1],
                color: '#e0e0e0'
            },
            paper_bgcolor: '#1e1e1e',
            plot_bgcolor: '#252526',
            font: { color: '#e0e0e0' }
        };
        
        Plotly.newPlot(barDiv, [trace], layout, {responsive: true});
        
        // Add phase visualization
        this.addPhaseVisualization(amplitudes, states, div);
        
        this.currentVisualizations.push(div);
    }
    
    addPhaseVisualization(amplitudes, states, container) {
        const phaseDiv = document.createElement('div');
        phaseDiv.className = 'phase-viz';
        phaseDiv.style.marginTop = '20px';
        container.appendChild(phaseDiv);
        
        const phaseTitle = document.createElement('h4');
        phaseTitle.textContent = 'Amplitude Phases';
        phaseTitle.style.color = '#e0e0e0';
        phaseTitle.style.marginBottom = '10px';
        phaseDiv.appendChild(phaseTitle);
        
        const phaseGrid = document.createElement('div');
        phaseGrid.style.display = 'grid';
        phaseGrid.style.gridTemplateColumns = 'repeat(auto-fill, minmax(100px, 1fr))';
        phaseGrid.style.gap = '10px';
        phaseDiv.appendChild(phaseGrid);
        
        amplitudes.forEach((amp, i) => {
            const phase = Math.atan2(amp.imag || 0, amp.real || amp);
            const magnitude = Math.sqrt((amp.real || amp) ** 2 + (amp.imag || 0) ** 2);
            
            const phaseItem = document.createElement('div');
            phaseItem.className = 'phase-item';
            phaseItem.style.textAlign = 'center';
            phaseItem.style.padding = '5px';
            phaseItem.style.backgroundColor = '#252526';
            phaseItem.style.borderRadius = '4px';
            
            // Create phase circle
            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.setAttribute('width', '60');
            svg.setAttribute('height', '60');
            
            // Background circle
            const bgCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            bgCircle.setAttribute('cx', '30');
            bgCircle.setAttribute('cy', '30');
            bgCircle.setAttribute('r', '25');
            bgCircle.setAttribute('fill', 'none');
            bgCircle.setAttribute('stroke', '#3c3c3c');
            bgCircle.setAttribute('stroke-width', '2');
            svg.appendChild(bgCircle);
            
            // Phase arrow
            const arrow = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            arrow.setAttribute('x1', '30');
            arrow.setAttribute('y1', '30');
            arrow.setAttribute('x2', 30 + 20 * Math.cos(phase));
            arrow.setAttribute('y2', 30 - 20 * Math.sin(phase));
            arrow.setAttribute('stroke', '#00d4ff');
            arrow.setAttribute('stroke-width', '2');
            arrow.setAttribute('marker-end', 'url(#arrowhead)');
            svg.appendChild(arrow);
            
            phaseItem.appendChild(svg);
            
            const label = document.createElement('div');
            label.style.fontSize = '12px';
            label.style.color = '#999';
            label.textContent = states[i];
            phaseItem.appendChild(label);
            
            phaseGrid.appendChild(phaseItem);
        });
    }
    
    renderNetwork(viz, container) {
        const div = document.createElement('div');
        div.className = 'visualization network';
        div.style.height = '400px';
        container.appendChild(div);
        
        const nodes = viz.nodes || ['Alice', 'Bob', 'Charlie'];
        const edges = viz.edges || this.generateFullyConnectedEdges(nodes);
        
        // Create network graph
        const nodeTrace = {
            x: nodes.map((_, i) => Math.cos(2 * Math.PI * i / nodes.length)),
            y: nodes.map((_, i) => Math.sin(2 * Math.PI * i / nodes.length)),
            text: nodes,
            mode: 'markers+text',
            type: 'scatter',
            marker: {
                size: 30,
                color: '#00d4ff',
                line: {
                    color: '#fff',
                    width: 2
                }
            },
            textposition: 'top center',
            textfont: {
                size: 12,
                color: '#e0e0e0'
            }
        };
        
        // Create edges
        const edgeTraces = edges.map(edge => ({
            x: [nodeTrace.x[nodes.indexOf(edge[0])], nodeTrace.x[nodes.indexOf(edge[1])]],
            y: [nodeTrace.y[nodes.indexOf(edge[0])], nodeTrace.y[nodes.indexOf(edge[1])]],
            mode: 'lines',
            type: 'scatter',
            line: {
                color: 'rgba(0, 212, 255, 0.3)',
                width: 2
            },
            hoverinfo: 'skip'
        }));
        
        const layout = {
            title: 'Quantum Network Topology',
            showlegend: false,
            xaxis: {
                showgrid: false,
                zeroline: false,
                showticklabels: false
            },
            yaxis: {
                showgrid: false,
                zeroline: false,
                showticklabels: false
            },
            paper_bgcolor: '#1e1e1e',
            plot_bgcolor: '#252526',
            font: { color: '#e0e0e0' }
        };
        
        Plotly.newPlot(div, [...edgeTraces, nodeTrace], layout, {responsive: true});
        this.currentVisualizations.push(div);
    }
    
    renderHeatmap(viz, container) {
        const div = document.createElement('div');
        div.className = 'visualization heatmap';
        div.style.height = '400px';
        container.appendChild(div);
        
        const data = viz.data || this.generateRandomMatrix(10, 10);
        
        const trace = {
            z: data,
            type: 'heatmap',
            colorscale: [
                [0, '#1e1e1e'],
                [0.5, '#00d4ff'],
                [1, '#ff6b6b']
            ],
            showscale: true
        };
        
        const layout = {
            title: viz.title || 'Parameter Sweep Results',
            xaxis: {
                title: viz.xlabel || 'Parameter 1',
                color: '#e0e0e0'
            },
            yaxis: {
                title: viz.ylabel || 'Parameter 2',
                color: '#e0e0e0'
            },
            paper_bgcolor: '#1e1e1e',
            plot_bgcolor: '#252526',
            font: { color: '#e0e0e0' }
        };
        
        Plotly.newPlot(div, [trace], layout, {responsive: true});
        this.currentVisualizations.push(div);
    }
    
    renderTimeSeries(viz, container) {
        const div = document.createElement('div');
        div.className = 'visualization time-series';
        div.style.height = '350px';
        container.appendChild(div);
        
        const time = viz.time || Array.from({length: 100}, (_, i) => i);
        const series = viz.series || [
            {
                name: 'Measurement 1',
                values: time.map(t => Math.sin(t * 0.1) * 10 + Math.random() * 2)
            },
            {
                name: 'Measurement 2',
                values: time.map(t => Math.cos(t * 0.1) * 8 + Math.random() * 1.5)
            }
        ];
        
        const traces = series.map((s, i) => ({
            x: time,
            y: s.values,
            type: 'scatter',
            mode: 'lines',
            name: s.name,
            line: {
                color: ['#00d4ff', '#ff6b6b', '#4ecdc4', '#f7b731'][i % 4],
                width: 2
            }
        }));
        
        const layout = {
            title: viz.title || 'Time Series Data',
            xaxis: {
                title: 'Time',
                gridcolor: '#3c3c3c',
                color: '#e0e0e0'
            },
            yaxis: {
                title: 'Value',
                gridcolor: '#3c3c3c',
                color: '#e0e0e0'
            },
            paper_bgcolor: '#1e1e1e',
            plot_bgcolor: '#252526',
            font: { color: '#e0e0e0' },
            showlegend: true,
            legend: {
                x: 0.02,
                y: 0.98,
                bgcolor: 'rgba(0,0,0,0.5)'
            }
        };
        
        Plotly.newPlot(div, traces, layout, {responsive: true});
        this.currentVisualizations.push(div);
    }
    
    renderGeneric(viz, container) {
        const div = document.createElement('div');
        div.className = 'visualization generic';
        div.innerHTML = viz.html || '<p>Custom visualization</p>';
        container.appendChild(div);
        this.currentVisualizations.push(div);
    }
    
    clear() {
        this.currentVisualizations.forEach(viz => {
            if (viz && viz.parentNode) {
                viz.parentNode.removeChild(viz);
            }
        });
        this.currentVisualizations = [];
    }
    
    // Helper methods
    generateNormalDistribution(n, mean, std) {
        const data = [];
        for (let i = 0; i < n; i++) {
            let u = 0, v = 0;
            while (u === 0) u = Math.random();
            while (v === 0) v = Math.random();
            const z = Math.sqrt(-2.0 * Math.log(u)) * Math.cos(2.0 * Math.PI * v);
            data.push(z * std + mean);
        }
        return data;
    }
    
    generateRandomQuantumState(n) {
        const amplitudes = [];
        let norm = 0;
        
        for (let i = 0; i < n; i++) {
            const real = Math.random() - 0.5;
            const imag = Math.random() - 0.5;
            amplitudes.push({ real, imag });
            norm += real * real + imag * imag;
        }
        
        // Normalize
        norm = Math.sqrt(norm);
        return amplitudes.map(a => ({
            real: a.real / norm,
            imag: a.imag / norm
        }));
    }
    
    generateSphere() {
        const n = 20;
        const x = [], y = [], z = [];
        
        for (let i = 0; i <= n; i++) {
            const theta = (i / n) * Math.PI;
            for (let j = 0; j <= n; j++) {
                const phi = (j / n) * 2 * Math.PI;
                x.push(Math.sin(theta) * Math.cos(phi));
                y.push(Math.sin(theta) * Math.sin(phi));
                z.push(Math.cos(theta));
            }
        }
        
        return { x, y, z };
    }
    
    generateFullyConnectedEdges(nodes) {
        const edges = [];
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                edges.push([nodes[i], nodes[j]]);
            }
        }
        return edges;
    }
    
    generateRandomMatrix(rows, cols) {
        const matrix = [];
        for (let i = 0; i < rows; i++) {
            const row = [];
            for (let j = 0; j < cols; j++) {
                row.push(Math.random() * 100);
            }
            matrix.push(row);
        }
        return matrix;
    }
}

// Export for use in playground
window.EnhancedVisualizationEngine = EnhancedVisualizationEngine;