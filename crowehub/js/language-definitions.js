/**
 * Language Definitions for Quantum Trinity Languages
 * Provides syntax highlighting and language features for Monaco Editor
 */

// Synapse Language Definition
const synapseLanguage = {
    id: 'synapse',
    extensions: ['.syn', '.synapse'],
    aliases: ['Synapse', 'synapse'],
    mimetypes: ['text/x-synapse'],
    
    keywords: [
        'uncertain', 'parallel', 'monte_carlo', 'correlation',
        'for', 'if', 'else', 'elif', 'while', 'function', 'return',
        'import', 'from', 'as', 'class', 'def', 'print', 'in',
        'True', 'False', 'None', 'and', 'or', 'not', 'is',
        'try', 'except', 'finally', 'raise', 'with', 'yield'
    ],
    
    typeKeywords: [
        'int', 'float', 'string', 'bool', 'list', 'dict', 'tuple',
        'uncertain', 'quantum', 'complex'
    ],
    
    operators: [
        '±', '+', '-', '*', '/', '//', '%', '**',
        '=', '+=', '-=', '*=', '/=', '//=', '%=', '**=',
        '==', '!=', '<', '>', '<=', '>=',
        '&', '|', '^', '~', '<<', '>>',
        'and', 'or', 'not', 'is', 'in'
    ],
    
    symbols: /[=><!~?:&|+\-*\/\^%±]+/,
    
    tokenizer: {
        root: [
            // Uncertainty syntax
            [/uncertain\s+\w+\s*=\s*[\d.]+\s*±\s*[\d.]+/, 'variable.uncertainty'],
            
            // Keywords
            [/\b(uncertain|parallel|monte_carlo|correlation)\b/, 'keyword.special'],
            
            // Identifiers and keywords
            [/[a-z_$][\w$]*/, {
                cases: {
                    '@keywords': 'keyword',
                    '@typeKeywords': 'type',
                    '@default': 'identifier'
                }
            }],
            
            // Numbers
            [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
            [/0[xX][0-9a-fA-F]+/, 'number.hex'],
            [/\d+/, 'number'],
            
            // Strings
            [/"([^"\\]|\\.)*$/, 'string.invalid'],
            [/'([^'\\]|\\.)*$/, 'string.invalid'],
            [/"/, 'string', '@string_double'],
            [/'/, 'string', '@string_single'],
            
            // Comments
            [/#.*$/, 'comment'],
            
            // Delimiters and operators
            [/[{}()\[\]]/, '@brackets'],
            [/@symbols/, {
                cases: {
                    '@operators': 'operator',
                    '@default': ''
                }
            }]
        ],
        
        string_double: [
            [/[^\\"]+/, 'string'],
            [/\\./, 'string.escape'],
            [/"/, 'string', '@pop']
        ],
        
        string_single: [
            [/[^\\']+/, 'string'],
            [/\\./, 'string.escape'],
            [/'/, 'string', '@pop']
        ]
    }
};

// Qubit-Flow Language Definition
const qubitFlowLanguage = {
    id: 'qubit-flow',
    extensions: ['.qf', '.qubit'],
    aliases: ['QubitFlow', 'qubit-flow', 'Qubit-Flow'],
    mimetypes: ['text/x-qubitflow'],
    
    keywords: [
        'qubit', 'gate', 'circuit', 'measure', 'entangle',
        'teleport', 'if', 'else', 'for', 'while', 'return',
        'import', 'from', 'as', 'def', 'class', 'print'
    ],
    
    gates: [
        'H', 'X', 'Y', 'Z', 'S', 'T', 'CNOT', 'CZ', 'SWAP',
        'Toffoli', 'Fredkin', 'Rx', 'Ry', 'Rz', 'U1', 'U2', 'U3'
    ],
    
    operators: [
        '=', '==', '!=', '<', '>', '<=', '>=',
        '+', '-', '*', '/', '//', '%', '**'
    ],
    
    symbols: /[=><!~?:&|+\-*\/\^%]+/,
    
    tokenizer: {
        root: [
            // Quantum state notation
            [/\|[01]\⟩/, 'quantum.state'],
            [/\|[01+-]\⟩/, 'quantum.state'],
            [/\|Ψ\⟩/, 'quantum.state'],
            [/\|Φ\⟩/, 'quantum.state'],
            
            // Gate applications
            [/[HXYZSCT](?:offoli|redkin)?\[/, 'quantum.gate'],
            [/CNOT\[/, 'quantum.gate'],
            [/SWAP\[/, 'quantum.gate'],
            [/R[xyz]\[/, 'quantum.gate'],
            [/U[123]\[/, 'quantum.gate'],
            
            // Keywords
            [/\b(qubit|gate|circuit|measure|entangle|teleport)\b/, 'keyword.quantum'],
            
            // Identifiers and keywords
            [/[a-z_$][\w$]*/, {
                cases: {
                    '@keywords': 'keyword',
                    '@gates': 'quantum.gate',
                    '@default': 'identifier'
                }
            }],
            
            // Numbers
            [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
            [/\d+/, 'number'],
            
            // Strings
            [/"([^"\\]|\\.)*$/, 'string.invalid'],
            [/'([^'\\]|\\.)*$/, 'string.invalid'],
            [/"/, 'string', '@string_double'],
            [/'/, 'string', '@string_single'],
            
            // Comments
            [/\/\/.*$/, 'comment'],
            [/#.*$/, 'comment'],
            
            // Delimiters and operators
            [/[{}()\[\]]/, '@brackets'],
            [/@symbols/, {
                cases: {
                    '@operators': 'operator',
                    '@default': ''
                }
            }]
        ],
        
        string_double: [
            [/[^\\"]+/, 'string'],
            [/\\./, 'string.escape'],
            [/"/, 'string', '@pop']
        ],
        
        string_single: [
            [/[^\\']+/, 'string'],
            [/\\./, 'string.escape'],
            [/'/, 'string', '@pop']
        ]
    }
};

// Quantum-Net Language Definition
const quantumNetLanguage = {
    id: 'quantum-net',
    extensions: ['.qn', '.qnet'],
    aliases: ['QuantumNet', 'quantum-net', 'Quantum-Net'],
    mimetypes: ['text/x-quantumnet'],
    
    keywords: [
        'network', 'node', 'connection', 'protocol', 'channel',
        'teleport', 'distribute', 'entangle', 'communicate', 'sync',
        'if', 'else', 'for', 'while', 'return', 'async', 'await',
        'import', 'from', 'as', 'def', 'class', 'print'
    ],
    
    networkTypes: [
        'quantum', 'classical', 'hybrid', 'entangled',
        'star', 'ring', 'mesh', 'tree', 'bus'
    ],
    
    operators: [
        '=', '==', '!=', '<', '>', '<=', '>=',
        '->', '<-', '<->', '=>', '->>'
    ],
    
    symbols: /[=><!~?:&|+\-*\/\^%]+/,
    
    tokenizer: {
        root: [
            // Network definitions
            [/network\s+\w+\s*{/, 'network.definition'],
            [/node\s+\w+/, 'network.node'],
            [/protocol\s+\w+/, 'network.protocol'],
            
            // Connection syntax
            [/->|<-|<->|=>|--/, 'network.connection'],
            
            // Keywords
            [/\b(network|node|connection|protocol|channel)\b/, 'keyword.network'],
            [/\b(teleport|distribute|entangle|communicate|sync)\b/, 'keyword.operation'],
            
            // Identifiers and keywords
            [/[a-z_$][\w$]*/, {
                cases: {
                    '@keywords': 'keyword',
                    '@networkTypes': 'type.network',
                    '@default': 'identifier'
                }
            }],
            
            // IP addresses and ports
            [/\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b/, 'network.ip'],
            [/:[0-9]+/, 'network.port'],
            
            // Numbers
            [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
            [/\d+/, 'number'],
            
            // Strings
            [/"([^"\\]|\\.)*$/, 'string.invalid'],
            [/'([^'\\]|\\.)*$/, 'string.invalid'],
            [/"/, 'string', '@string_double'],
            [/'/, 'string', '@string_single'],
            
            // Comments
            [/\/\/.*$/, 'comment'],
            [/#.*$/, 'comment'],
            
            // Delimiters and operators
            [/[{}()\[\]]/, '@brackets'],
            [/@symbols/, {
                cases: {
                    '@operators': 'operator',
                    '@default': ''
                }
            }]
        ],
        
        string_double: [
            [/[^\\"]+/, 'string'],
            [/\\./, 'string.escape'],
            [/"/, 'string', '@pop']
        ],
        
        string_single: [
            [/[^\\']+/, 'string'],
            [/\\./, 'string.escape'],
            [/'/, 'string', '@pop']
        ]
    }
};

// Register languages with Monaco Editor
function registerLanguages() {
    // Register Synapse
    monaco.languages.register({
        id: synapseLanguage.id,
        extensions: synapseLanguage.extensions,
        aliases: synapseLanguage.aliases
    });
    
    monaco.languages.setMonarchTokensProvider('synapse', {
        keywords: synapseLanguage.keywords,
        typeKeywords: synapseLanguage.typeKeywords,
        operators: synapseLanguage.operators,
        symbols: synapseLanguage.symbols,
        tokenizer: synapseLanguage.tokenizer
    });
    
    // Register Qubit-Flow
    monaco.languages.register({
        id: qubitFlowLanguage.id,
        extensions: qubitFlowLanguage.extensions,
        aliases: qubitFlowLanguage.aliases
    });
    
    monaco.languages.setMonarchTokensProvider('qubit-flow', {
        keywords: qubitFlowLanguage.keywords,
        gates: qubitFlowLanguage.gates,
        operators: qubitFlowLanguage.operators,
        symbols: qubitFlowLanguage.symbols,
        tokenizer: qubitFlowLanguage.tokenizer
    });
    
    // Register Quantum-Net
    monaco.languages.register({
        id: quantumNetLanguage.id,
        extensions: quantumNetLanguage.extensions,
        aliases: quantumNetLanguage.aliases
    });
    
    monaco.languages.setMonarchTokensProvider('quantum-net', {
        keywords: quantumNetLanguage.keywords,
        networkTypes: quantumNetLanguage.networkTypes,
        operators: quantumNetLanguage.operators,
        symbols: quantumNetLanguage.symbols,
        tokenizer: quantumNetLanguage.tokenizer
    });
}

// Auto-completion providers
function registerCompletionProviders() {
    // Synapse completions
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
    
    // Qubit-Flow completions
    monaco.languages.registerCompletionItemProvider('qubit-flow', {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: 'qubit',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'qubit ${1:q} = |${2:0}⟩',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Initialize a qubit'
                },
                {
                    label: 'H',
                    kind: monaco.languages.CompletionItemKind.Function,
                    insertText: 'H[${1:qubit}]',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Apply Hadamard gate'
                },
                {
                    label: 'CNOT',
                    kind: monaco.languages.CompletionItemKind.Function,
                    insertText: 'CNOT[${1:control}, ${2:target}]',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Apply CNOT gate'
                },
                {
                    label: 'measure',
                    kind: monaco.languages.CompletionItemKind.Function,
                    insertText: 'measure(${1:qubit})',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Measure qubit state'
                }
            ];
            return { suggestions };
        }
    });
    
    // Quantum-Net completions
    monaco.languages.registerCompletionItemProvider('quantum-net', {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: 'network',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'network ${1:name} {\n    nodes: [${2}],\n    connections: [${3}]\n}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a quantum network'
                },
                {
                    label: 'protocol',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'protocol ${1:name} {\n    ${2:// protocol steps}\n}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a network protocol'
                },
                {
                    label: 'entangle',
                    kind: monaco.languages.CompletionItemKind.Function,
                    insertText: 'entangle(${1:node1}, ${2:node2})',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Create entanglement between nodes'
                }
            ];
            return { suggestions };
        }
    });
}

// Export functions for use in playground
window.LanguageDefinitions = {
    registerLanguages,
    registerCompletionProviders,
    synapseLanguage,
    qubitFlowLanguage,
    quantumNetLanguage
};