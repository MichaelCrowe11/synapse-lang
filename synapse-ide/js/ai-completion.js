/**
 * AI-Powered Code Completion Engine for Synapse IDE
 * Provides intelligent code suggestions, error detection, and optimization
 */

class AICompletionEngine {
    constructor() {
        this.apiKey = null;
        this.provider = 'anthropic'; // 'anthropic' or 'openai'
        this.isEnabled = true;
        this.completionCache = new Map();
        this.contextWindow = 2000; // tokens
        this.debounceDelay = 500;
        this.debounceTimer = null;
        
        this.languagePatterns = {
            synapse: {
                keywords: ['uncertain', 'parallel', 'monte_carlo', 'correlation', 'experiment', 'hypothesis'],
                operators: ['±', '∈', '∼', '⊗', '∇', '∂'],
                patterns: {
                    uncertainty: /uncertain\s+(\w+)\s*=\s*([0-9.]+)\s*±\s*([0-9.]+)/,
                    parallel: /parallel\s*\{([^}]+)\}/,
                    reasoning: /reason\s+chain\s+(\w+)\s*\{([^}]+)\}/
                }
            },
            'qubit-flow': {
                keywords: ['qubit', 'gate', 'circuit', 'measure', 'entangle', 'superposition'],
                operators: ['|0⟩', '|1⟩', '|+⟩', '|-⟩', 'H', 'X', 'Y', 'Z', 'CNOT'],
                patterns: {
                    qubit: /qubit\s+(\w+)\s*=\s*\|([01+\-])\⟩/,
                    gate: /(\w+)\s+gate\s+on\s+(\w+)/,
                    circuit: /circuit\s+(\w+)\s*\{([^}]+)\}/
                }
            },
            'quantum-net': {
                keywords: ['node', 'quantum_link', 'entanglement', 'protocol', 'teleport', 'distribute'],
                operators: ['⊗', '⊕', '≈', '→', '↔', '⟷'],
                patterns: {
                    node: /node\s+(\w+)\s*at\s*\(([^)]+)\)/,
                    link: /quantum_link\s+(\w+)\s*↔\s*(\w+)/,
                    protocol: /protocol\s+(\w+)\s*\{([^}]+)\}/
                }
            }
        };
        
        this.initializeCompletion();
    }
    
    async initializeCompletion() {
        // Load API configuration
        await this.loadAPIConfig();
        
        // Set up event listeners
        this.setupEventListeners();
        
        console.log('AI Completion Engine initialized');
    }
    
    async loadAPIConfig() {
        try {
            const response = await fetch('/api/ai-config');
            const config = await response.json();
            this.apiKey = config.apiKey;
            this.provider = config.provider || 'anthropic';
        } catch (error) {
            console.warn('AI API not configured, using pattern-based completion only');
        }
    }
    
    setupEventListeners() {
        // Listen for editor changes
        if (window.monacoEditor) {
            window.monacoEditor.onDidChangeModelContent((e) => {
                this.handleEditorChange(e);
            });
            
            window.monacoEditor.onDidChangeCursorPosition((e) => {
                this.handleCursorChange(e);
            });
        }
    }
    
    handleEditorChange(event) {
        if (!this.isEnabled) return;
        
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.triggerCompletion();
        }, this.debounceDelay);
    }
    
    handleCursorChange(event) {
        if (!this.isEnabled) return;
        
        const position = event.position;
        const model = window.monacoEditor.getModel();
        const lineContent = model.getLineContent(position.lineNumber);
        
        // Check for specific triggers
        if (this.shouldTriggerCompletion(lineContent, position.column)) {
            this.triggerCompletion();
        }
    }
    
    shouldTriggerCompletion(lineContent, column) {
        const triggers = ['.', ' ', '(', '{', '=', '±', '∼'];
        const charBefore = lineContent[column - 2];
        return triggers.includes(charBefore);
    }
    
    async triggerCompletion() {
        const editor = window.monacoEditor;
        const model = editor.getModel();
        const position = editor.getPosition();
        const language = model.getLanguageId();
        
        // Get context around cursor
        const context = this.getCompletionContext(model, position);
        
        // Try pattern-based completion first
        const patternSuggestions = this.getPatternBasedCompletions(context, language);
        
        // If we have AI API, get AI suggestions
        let aiSuggestions = [];
        if (this.apiKey) {
            aiSuggestions = await this.getAICompletions(context, language);
        }
        
        // Combine and show suggestions
        const allSuggestions = [...patternSuggestions, ...aiSuggestions];
        
        if (allSuggestions.length > 0) {
            this.showCompletionSuggestions(allSuggestions, position);
        }
    }
    
    getCompletionContext(model, position) {
        const lineNumber = position.lineNumber;
        const column = position.column;
        
        // Get text before cursor (context window)
        const startLine = Math.max(1, lineNumber - 20);
        const endLine = Math.min(model.getLineCount(), lineNumber + 5);
        
        let textBefore = '';
        let textAfter = '';
        
        for (let i = startLine; i <= lineNumber; i++) {
            const lineContent = model.getLineContent(i);
            if (i === lineNumber) {
                textBefore += lineContent.substring(0, column - 1);
            } else {
                textBefore += lineContent + '\n';
            }
        }
        
        for (let i = lineNumber; i <= endLine; i++) {
            const lineContent = model.getLineContent(i);
            if (i === lineNumber) {
                textAfter += lineContent.substring(column - 1);
            } else {
                textAfter += lineContent + '\n';
            }
        }
        
        return {
            textBefore,
            textAfter,
            currentLine: model.getLineContent(lineNumber),
            position: { lineNumber, column },
            language: model.getLanguageId()
        };
    }
    
    getPatternBasedCompletions(context, language) {
        const suggestions = [];
        const langConfig = this.languagePatterns[language];
        
        if (!langConfig) return suggestions;
        
        const { textBefore, currentLine } = context;
        const lastWord = this.getLastWord(textBefore);
        
        // Keyword completions
        langConfig.keywords.forEach(keyword => {
            if (keyword.startsWith(lastWord.toLowerCase())) {
                suggestions.push({
                    type: 'keyword',
                    text: keyword,
                    detail: `${language} keyword`,
                    insertText: keyword,
                    kind: 'Keyword'
                });
            }
        });
        
        // Operator completions
        langConfig.operators.forEach(operator => {
            if (this.shouldSuggestOperator(textBefore, operator)) {
                suggestions.push({
                    type: 'operator',
                    text: operator,
                    detail: `${language} operator`,
                    insertText: operator,
                    kind: 'Operator'
                });
            }
        });
        
        // Pattern-based suggestions
        if (language === 'synapse') {
            suggestions.push(...this.getSynapsePatternSuggestions(context));
        } else if (language === 'qubit-flow') {
            suggestions.push(...this.getQubitFlowPatternSuggestions(context));
        } else if (language === 'quantum-net') {
            suggestions.push(...this.getQuantumNetPatternSuggestions(context));
        }
        
        return suggestions;
    }
    
    getSynapsePatternSuggestions(context) {
        const suggestions = [];
        const { textBefore } = context;
        
        if (textBefore.includes('uncertain') && !textBefore.includes('±')) {
            suggestions.push({
                type: 'pattern',
                text: 'uncertain value with error',
                detail: 'Uncertainty declaration',
                insertText: 'uncertain ${1:variable} = ${2:value} ± ${3:error}',
                kind: 'Snippet'
            });
        }
        
        if (textBefore.includes('parallel') && !textBefore.includes('{')) {
            suggestions.push({
                type: 'pattern',
                text: 'parallel execution block',
                detail: 'Parallel computation',
                insertText: 'parallel {\n    branch ${1:A}: ${2:computation}\n    branch ${3:B}: ${4:computation}\n}',
                kind: 'Snippet'
            });
        }
        
        if (textBefore.includes('experiment')) {
            suggestions.push({
                type: 'pattern',
                text: 'experiment block',
                detail: 'Scientific experiment',
                insertText: 'experiment ${1:ExperimentName} {\n    ${2:setup}\n    ${3:execution}\n    ${4:analysis}\n}',
                kind: 'Snippet'
            });
        }
        
        return suggestions;
    }
    
    getQubitFlowPatternSuggestions(context) {
        const suggestions = [];
        const { textBefore } = context;
        
        if (textBefore.includes('qubit')) {
            suggestions.push({
                type: 'pattern',
                text: 'qubit declaration',
                detail: 'Quantum bit initialization',
                insertText: 'qubit ${1:name} = |${2:0}⟩',
                kind: 'Snippet'
            });
        }
        
        if (textBefore.includes('circuit')) {
            suggestions.push({
                type: 'pattern',
                text: 'quantum circuit',
                detail: 'Quantum circuit definition',
                insertText: 'circuit ${1:CircuitName} {\n    ${2:gates}\n    measure ${3:qubits}\n}',
                kind: 'Snippet'
            });
        }
        
        return suggestions;
    }
    
    getQuantumNetPatternSuggestions(context) {
        const suggestions = [];
        const { textBefore } = context;
        
        if (textBefore.includes('node')) {
            suggestions.push({
                type: 'pattern',
                text: 'quantum node',
                detail: 'Network node definition',
                insertText: 'node ${1:NodeName} at (${2:x}, ${3:y})',
                kind: 'Snippet'
            });
        }
        
        if (textBefore.includes('protocol')) {
            suggestions.push({
                type: 'pattern',
                text: 'quantum protocol',
                detail: 'Communication protocol',
                insertText: 'protocol ${1:ProtocolName} {\n    ${2:steps}\n}',
                kind: 'Snippet'
            });
        }
        
        return suggestions;
    }
    
    async getAICompletions(context, language) {
        if (!this.apiKey) return [];
        
        const cacheKey = this.generateCacheKey(context);
        if (this.completionCache.has(cacheKey)) {
            return this.completionCache.get(cacheKey);
        }
        
        try {
            const prompt = this.buildCompletionPrompt(context, language);
            const response = await this.callAIAPI(prompt);
            const suggestions = this.parseAIResponse(response);
            
            // Cache the results
            this.completionCache.set(cacheKey, suggestions);
            
            return suggestions;
        } catch (error) {
            console.error('AI completion error:', error);
            return [];
        }
    }
    
    buildCompletionPrompt(context, language) {
        const { textBefore, textAfter } = context;
        
        return `You are an expert in the ${language} programming language for scientific computing. 
        
Context:
${textBefore}<cursor>${textAfter}

Please provide intelligent code completion suggestions for the cursor position. Consider:
1. Syntax and semantics of ${language}
2. Scientific computing patterns
3. Error handling and best practices
4. Type safety and uncertainty propagation

Respond with a JSON array of suggestions in this format:
[
  {
    "text": "suggestion text",
    "detail": "description",
    "insertText": "text to insert with placeholders",
    "kind": "Function|Variable|Keyword|Snippet",
    "documentation": "detailed explanation"
  }
]`;
    }
    
    async callAIAPI(prompt) {
        const url = this.provider === 'anthropic' 
            ? 'https://api.anthropic.com/v1/messages'
            : 'https://api.openai.com/v1/chat/completions';
            
        const headers = {
            'Content-Type': 'application/json',
            'Authorization': this.provider === 'anthropic' 
                ? `Bearer ${this.apiKey}`
                : `Bearer ${this.apiKey}`,
        };
        
        const body = this.provider === 'anthropic' 
            ? {
                model: 'claude-3-sonnet-20240229',
                max_tokens: 500,
                messages: [{ role: 'user', content: prompt }]
            }
            : {
                model: 'gpt-4',
                max_tokens: 500,
                messages: [{ role: 'user', content: prompt }]
            };
            
        const response = await fetch(url, {
            method: 'POST',
            headers,
            body: JSON.stringify(body)
        });
        
        return response.json();
    }
    
    parseAIResponse(response) {
        try {
            let content = '';
            if (this.provider === 'anthropic') {
                content = response.content[0].text;
            } else {
                content = response.choices[0].message.content;
            }
            
            // Extract JSON from response
            const jsonMatch = content.match(/\[[\s\S]*\]/);
            if (jsonMatch) {
                return JSON.parse(jsonMatch[0]);
            }
            
            return [];
        } catch (error) {
            console.error('Error parsing AI response:', error);
            return [];
        }
    }
    
    showCompletionSuggestions(suggestions, position) {
        // Create Monaco completion items
        const completionItems = suggestions.map(suggestion => ({
            label: suggestion.text,
            kind: this.getMonacoKind(suggestion.kind),
            detail: suggestion.detail,
            documentation: suggestion.documentation || suggestion.detail,
            insertText: suggestion.insertText || suggestion.text,
            insertTextRules: suggestion.insertText?.includes('${') 
                ? monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet 
                : undefined,
            range: {
                startLineNumber: position.lineNumber,
                endLineNumber: position.lineNumber,
                startColumn: position.column,
                endColumn: position.column
            }
        }));
        
        // Show completion widget
        window.monacoEditor.trigger('ai-completion', 'editor.action.triggerSuggest');
    }
    
    getMonacoKind(kind) {
        const kindMap = {
            'Keyword': monaco.languages.CompletionItemKind.Keyword,
            'Function': monaco.languages.CompletionItemKind.Function,
            'Variable': monaco.languages.CompletionItemKind.Variable,
            'Snippet': monaco.languages.CompletionItemKind.Snippet,
            'Operator': monaco.languages.CompletionItemKind.Operator,
            'Class': monaco.languages.CompletionItemKind.Class,
            'Method': monaco.languages.CompletionItemKind.Method
        };
        
        return kindMap[kind] || monaco.languages.CompletionItemKind.Text;
    }
    
    getLastWord(text) {
        const match = text.match(/(\w+)$/);
        return match ? match[1] : '';
    }
    
    shouldSuggestOperator(textBefore, operator) {
        const context = textBefore.slice(-20);
        
        // Context-aware operator suggestions
        if (operator === '±' && context.includes('uncertain')) return true;
        if (operator === '∼' && (context.includes('distribution') || context.includes('sample'))) return true;
        if (operator === '⊗' && context.includes('tensor')) return true;
        
        return false;
    }
    
    generateCacheKey(context) {
        const { textBefore, language } = context;
        const relevant = textBefore.slice(-100); // Last 100 chars
        return `${language}:${btoa(relevant)}`;
    }
    
    // Public methods for IDE integration
    enable() {
        this.isEnabled = true;
        console.log('AI completion enabled');
    }
    
    disable() {
        this.isEnabled = false;
        console.log('AI completion disabled');
    }
    
    clearCache() {
        this.completionCache.clear();
        console.log('Completion cache cleared');
    }
    
    setProvider(provider) {
        this.provider = provider;
        this.loadAPIConfig();
    }
    
    async explainCode(selectedText, language) {
        if (!this.apiKey) {
            return "AI explanation not available. Please configure API key.";
        }
        
        const prompt = `Explain this ${language} code in detail:

\`\`\`${language}
${selectedText}
\`\`\`

Focus on:
1. What the code does
2. Scientific concepts involved
3. Potential optimizations
4. Best practices`;
        
        try {
            const response = await this.callAIAPI(prompt);
            return this.provider === 'anthropic' 
                ? response.content[0].text 
                : response.choices[0].message.content;
        } catch (error) {
            return `Error explaining code: ${error.message}`;
        }
    }
    
    async optimizeCode(selectedText, language) {
        if (!this.apiKey) {
            return "AI optimization not available. Please configure API key.";
        }
        
        const prompt = `Optimize this ${language} code for better performance and readability:

\`\`\`${language}
${selectedText}
\`\`\`

Provide:
1. Optimized version
2. Explanation of changes
3. Performance benefits`;
        
        try {
            const response = await this.callAIAPI(prompt);
            return this.provider === 'anthropic' 
                ? response.content[0].text 
                : response.choices[0].message.content;
        } catch (error) {
            return `Error optimizing code: ${error.message}`;
        }
    }
}

// Initialize the AI completion engine
window.aiCompletion = new AICompletionEngine();