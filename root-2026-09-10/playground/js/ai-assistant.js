/**
 * AI-Powered Code Assistant for Quantum Trinity IDE
 * 
 * Provides intelligent code completion, error explanation, and learning assistance
 */

class AIAssistant {
    constructor() {
        this.apiEndpoint = '/api/ai';
        this.context = [];
        this.suggestions = new Map();
        this.learningProfile = this.loadLearningProfile();
        this.initializeAssistant();
    }
    
    initializeAssistant() {
        // Initialize AI models and context
        this.models = {
            completion: 'quantum-completion-v1',
            explanation: 'quantum-explain-v1',
            optimization: 'quantum-optimize-v1',
            teaching: 'quantum-tutor-v1'
        };
        
        // Initialize knowledge base
        this.knowledgeBase = {
            synapse: this.loadSynapseKnowledge(),
            'qubit-flow': this.loadQubitFlowKnowledge(),
            'quantum-net': this.loadQuantumNetKnowledge()
        };
        
        // Setup WebSocket for real-time AI responses
        this.setupWebSocket();
    }
    
    setupWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/ai`);
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleAIResponse(data);
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            // Fallback to HTTP API
            this.useFallbackAPI = true;
        };
    }
    
    // Intelligent Code Completion
    async getCompletions(code, position, language) {
        const context = this.extractContext(code, position);
        
        // Fast local suggestions
        const localSuggestions = this.getLocalSuggestions(context, language);
        
        // Request AI suggestions asynchronously
        const aiSuggestions = await this.requestAISuggestions({
            code,
            position,
            language,
            context: this.context.slice(-10), // Last 10 interactions
            profile: this.learningProfile
        });
        
        return this.rankAndMergeSuggestions(localSuggestions, aiSuggestions);
    }
    
    getLocalSuggestions(context, language) {
        const suggestions = [];
        const patterns = this.knowledgeBase[language].patterns;
        
        // Pattern-based suggestions
        for (const pattern of patterns) {
            if (pattern.trigger.test(context.currentLine)) {
                suggestions.push({
                    label: pattern.suggestion,
                    kind: monaco.languages.CompletionItemKind.Snippet,
                    insertText: pattern.insertText,
                    documentation: pattern.documentation,
                    detail: pattern.detail,
                    sortText: '0' + pattern.priority
                });
            }
        }
        
        // Context-aware suggestions
        if (language === 'synapse') {
            suggestions.push(...this.getSynapseCompletions(context));
        } else if (language === 'qubit-flow') {
            suggestions.push(...this.getQubitFlowCompletions(context));
        } else if (language === 'quantum-net') {
            suggestions.push(...this.getQuantumNetCompletions(context));
        }
        
        return suggestions;
    }
    
    getSynapseCompletions(context) {
        const completions = [];
        
        // Uncertainty operations
        if (context.currentLine.includes('uncertain')) {
            completions.push({
                label: 'uncertain variable',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: 'uncertain ${1:variable} = ${2:value} ± ${3:uncertainty}',
                documentation: 'Declare an uncertain variable with error bounds'
            });
        }
        
        // Monte Carlo simulations
        if (context.currentLine.includes('monte')) {
            completions.push({
                label: 'monte_carlo',
                kind: monaco.languages.CompletionItemKind.Function,
                insertText: `monte_carlo(
    samples=\${1:10000},
    inputs={\${2:variables}},
    function=lambda x: \${3:expression}
)`,
                documentation: 'Run Monte Carlo simulation for uncertainty propagation'
            });
        }
        
        // Parallel operations
        if (context.currentLine.includes('parallel')) {
            completions.push({
                label: 'parallel block',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: `parallel {
    \${1:// Task 1}
    \${2:// Task 2}
}`,
                documentation: 'Execute tasks in parallel'
            });
        }
        
        return completions;
    }
    
    getQubitFlowCompletions(context) {
        const completions = [];
        
        // Quantum gates
        const gates = ['H', 'X', 'Y', 'Z', 'CNOT', 'Toffoli', 'SWAP', 'Rx', 'Ry', 'Rz'];
        
        for (const gate of gates) {
            if (context.currentWord.startsWith(gate.toLowerCase())) {
                completions.push({
                    label: gate,
                    kind: monaco.languages.CompletionItemKind.Function,
                    insertText: gate === 'CNOT' ? `CNOT[\${1:control}, \${2:target}]` : `${gate}[\${1:qubit}]`,
                    documentation: this.getGateDocumentation(gate)
                });
            }
        }
        
        // Qubit declarations
        if (context.currentLine.includes('qubit')) {
            completions.push({
                label: 'qubit initialization',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: 'qubit ${1:q} = |${2:0}⟩',
                documentation: 'Initialize a qubit in a basis state'
            });
        }
        
        return completions;
    }
    
    getQuantumNetCompletions(context) {
        const completions = [];
        
        // Network operations
        if (context.currentLine.includes('network')) {
            completions.push({
                label: 'network definition',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: `network \${1:name} {
    nodes: [\${2:"Alice", "Bob"}],
    connections: [
        {\${3:from: "Alice", to: "Bob", type: "quantum"}}
    ]
}`,
                documentation: 'Define a quantum network topology'
            });
        }
        
        // Protocol definitions
        if (context.currentLine.includes('protocol')) {
            completions.push({
                label: 'protocol',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: `protocol \${1:name} {
    participants: [\${2:nodes}],
    steps: [
        \${3:// Protocol steps}
    ]
}`,
                documentation: 'Define a quantum network protocol'
            });
        }
        
        return completions;
    }
    
    // AI-Powered Error Explanation
    async explainError(error, code, language) {
        const explanation = await this.requestAI({
            action: 'explain_error',
            error: error.message,
            code,
            language,
            line: error.line,
            column: error.column
        });
        
        return {
            explanation: explanation.text,
            suggestions: explanation.fixes,
            examples: explanation.examples,
            resources: explanation.resources
        };
    }
    
    // Code Optimization Suggestions
    async optimizeCode(code, language) {
        const analysis = await this.requestAI({
            action: 'optimize',
            code,
            language,
            profile: this.learningProfile
        });
        
        return {
            optimizations: analysis.suggestions,
            performance: analysis.metrics,
            alternativeImplementations: analysis.alternatives
        };
    }
    
    // Interactive Learning Assistant
    async getHint(code, problem, language) {
        const hint = await this.requestAI({
            action: 'hint',
            code,
            problem,
            language,
            progressLevel: this.learningProfile.level,
            previousHints: this.context.filter(c => c.type === 'hint')
        });
        
        // Update learning profile
        this.updateLearningProfile('hint_requested', { problem, language });
        
        return hint;
    }
    
    // Generate Practice Problems
    async generatePractice(topic, difficulty, language) {
        const practice = await this.requestAI({
            action: 'generate_practice',
            topic,
            difficulty,
            language,
            profile: this.learningProfile
        });
        
        return {
            problem: practice.problem,
            startingCode: practice.template,
            hints: practice.hints,
            solution: practice.solution,
            concepts: practice.concepts
        };
    }
    
    // AI API Communication
    async requestAI(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN && !this.useFallbackAPI) {
            return new Promise((resolve) => {
                const id = Math.random().toString(36).substr(2, 9);
                this.pendingRequests.set(id, resolve);
                this.ws.send(JSON.stringify({ id, ...data }));
            });
        } else {
            // HTTP fallback
            const response = await fetch(this.apiEndpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            return await response.json();
        }
    }
    
    async requestAISuggestions(context) {
        try {
            const response = await this.requestAI({
                action: 'complete',
                ...context
            });
            
            return response.suggestions.map(s => ({
                label: s.label,
                kind: monaco.languages.CompletionItemKind[s.kind],
                insertText: s.insertText,
                documentation: s.documentation,
                detail: s.detail,
                sortText: '1' + s.priority
            }));
        } catch (error) {
            console.error('AI suggestion error:', error);
            return [];
        }
    }
    
    // Learning Profile Management
    loadLearningProfile() {
        const stored = localStorage.getItem('quantum_learning_profile');
        return stored ? JSON.parse(stored) : {
            level: 'beginner',
            completedConcepts: [],
            preferredLanguage: 'synapse',
            practiceHistory: [],
            strengths: [],
            weaknesses: []
        };
    }
    
    updateLearningProfile(action, data) {
        // Update profile based on user actions
        if (action === 'concept_completed') {
            this.learningProfile.completedConcepts.push(data.concept);
        } else if (action === 'practice_completed') {
            this.learningProfile.practiceHistory.push({
                timestamp: Date.now(),
                ...data
            });
        }
        
        // Analyze and update level
        this.analyzeProgress();
        
        // Save profile
        localStorage.setItem('quantum_learning_profile', JSON.stringify(this.learningProfile));
    }
    
    analyzeProgress() {
        const conceptCount = this.learningProfile.completedConcepts.length;
        const practiceCount = this.learningProfile.practiceHistory.length;
        
        if (conceptCount > 20 && practiceCount > 50) {
            this.learningProfile.level = 'advanced';
        } else if (conceptCount > 10 && practiceCount > 25) {
            this.learningProfile.level = 'intermediate';
        }
    }
    
    // Knowledge Base Loading
    loadSynapseKnowledge() {
        return {
            patterns: [
                {
                    trigger: /uncertain\s+\w+\s*=/,
                    suggestion: 'uncertain variable',
                    insertText: 'uncertain ${1:var} = ${2:value} ± ${3:error}',
                    documentation: 'Declare uncertain variable',
                    detail: 'Synapse uncertainty quantification',
                    priority: '00'
                },
                {
                    trigger: /monte_carlo/,
                    suggestion: 'Monte Carlo simulation',
                    insertText: 'monte_carlo(samples=${1:10000})',
                    documentation: 'Run Monte Carlo simulation',
                    detail: 'Statistical sampling method',
                    priority: '01'
                }
            ],
            concepts: ['uncertainty', 'propagation', 'monte_carlo', 'parallel', 'ml_integration'],
            examples: {} // Load from examples.js
        };
    }
    
    loadQubitFlowKnowledge() {
        return {
            patterns: [
                {
                    trigger: /qubit\s+/,
                    suggestion: 'qubit declaration',
                    insertText: 'qubit ${1:q} = |${2:0}⟩',
                    documentation: 'Initialize quantum bit',
                    detail: 'Qubit-Flow quantum state',
                    priority: '00'
                }
            ],
            concepts: ['superposition', 'entanglement', 'measurement', 'gates'],
            examples: {}
        };
    }
    
    loadQuantumNetKnowledge() {
        return {
            patterns: [
                {
                    trigger: /network\s+/,
                    suggestion: 'network topology',
                    insertText: 'network ${1:name} { nodes: [${2}] }',
                    documentation: 'Define network topology',
                    detail: 'Quantum-Net network',
                    priority: '00'
                }
            ],
            concepts: ['topology', 'protocols', 'entanglement_distribution'],
            examples: {}
        };
    }
    
    extractContext(code, position) {
        const lines = code.split('\n');
        const currentLine = lines[position.lineNumber - 1] || '';
        const beforeCursor = currentLine.substring(0, position.column - 1);
        const words = beforeCursor.split(/\s+/);
        
        return {
            currentLine,
            beforeCursor,
            currentWord: words[words.length - 1] || '',
            previousLines: lines.slice(Math.max(0, position.lineNumber - 5), position.lineNumber - 1)
        };
    }
    
    rankAndMergeSuggestions(local, ai) {
        const merged = [...local];
        const seen = new Set(local.map(s => s.label));
        
        for (const suggestion of ai) {
            if (!seen.has(suggestion.label)) {
                merged.push(suggestion);
                seen.add(suggestion.label);
            }
        }
        
        return merged.sort((a, b) => (a.sortText || '').localeCompare(b.sortText || ''));
    }
    
    getGateDocumentation(gate) {
        const docs = {
            'H': 'Hadamard gate: Creates superposition',
            'X': 'Pauli-X gate: Bit flip',
            'Y': 'Pauli-Y gate: Bit and phase flip',
            'Z': 'Pauli-Z gate: Phase flip',
            'CNOT': 'Controlled-NOT: Entanglement gate',
            'Toffoli': 'Toffoli gate: Controlled-controlled-NOT',
            'SWAP': 'SWAP gate: Exchange qubit states',
            'Rx': 'Rotation around X-axis',
            'Ry': 'Rotation around Y-axis',
            'Rz': 'Rotation around Z-axis'
        };
        return docs[gate] || 'Quantum gate operation';
    }
    
    handleAIResponse(data) {
        if (this.pendingRequests.has(data.id)) {
            const resolve = this.pendingRequests.get(data.id);
            this.pendingRequests.delete(data.id);
            resolve(data.result);
        }
    }
}

// Export for use in playground
window.AIAssistant = AIAssistant;