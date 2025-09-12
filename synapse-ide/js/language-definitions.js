/**
 * Language Definitions for Synapse IDE
 * Supports Synapse, Qubit-Flow, Quantum-Net, Flux, and Crowe languages
 */

// Synapse Language Definition
const synapseLanguage = {
    id: 'synapse',
    extensions: ['.syn', '.synapse'],
    aliases: ['Synapse', 'synapse'],
    mimetypes: ['text/x-synapse'],
    
    // Language configuration
    configuration: {
        comments: {
            lineComment: '//',
            blockComment: ['/*', '*/']
        },
        brackets: [
            ['{', '}'],
            ['[', ']'],
            ['(', ')']
        ],
        autoClosingPairs: [
            { open: '{', close: '}' },
            { open: '[', close: ']' },
            { open: '(', close: ')' },
            { open: '"', close: '"' },
            { open: "'", close: "'" }
        ],
        surroundingPairs: [
            { open: '{', close: '}' },
            { open: '[', close: ']' },
            { open: '(', close: ')' },
            { open: '"', close: '"' },
            { open: "'", close: "'" }
        ]
    },
    
    // Tokenizer
    tokenizer: {
        root: [
            // Comments
            [/\/\/.*$/, 'comment'],
            [/\/\*/, 'comment', '@comment'],
            
            // Keywords
            [/\b(uncertain|parallel|monte_carlo|correlation|experiment|hypothesis|reason|chain|premise|derive|conclude|synthesize|fork|branch|stage|pipeline)\b/, 'keyword'],
            
            // Scientific operators
            [/[±∈∼⊗∇∂]/, 'operator.scientific'],
            
            // Standard operators
            [/[=+\-*/%<>!&|^~?:]/, 'operator'],
            
            // Numbers with uncertainty
            [/\d+(\.\d+)?\s*±\s*\d+(\.\d+)?/, 'number.uncertainty'],
            
            // Regular numbers
            [/\d+(\.\d+)?([eE][-+]?\d+)?/, 'number'],
            
            // Strings
            [/"([^"\\]|\\.)*$/, 'string.invalid'],
            [/"/, 'string', '@string'],
            [/'([^'\\]|\\.)*$/, 'string.invalid'],
            [/'/, 'string', '@string_single'],
            
            // Identifiers
            [/[a-zA-Z_]\w*/, 'identifier'],
            
            // Delimiters
            [/[{}()\[\]]/, 'delimiter'],
            [/[,;]/, 'delimiter'],
            
            // Whitespace
            [/\s+/, 'white']
        ],
        
        comment: [
            [/[^\/*]+/, 'comment'],
            [/\/\*/, 'comment', '@push'],
            ["\\*/", 'comment', '@pop'],
            [/[\/*]/, 'comment']
        ],
        
        string: [
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
    aliases: ['Qubit-Flow', 'qubit-flow'],
    mimetypes: ['text/x-qubit-flow'],
    
    configuration: {
        comments: {
            lineComment: '#',
            blockComment: ['/*', '*/']
        },
        brackets: [
            ['{', '}'],
            ['[', ']'],
            ['(', ')'],
            ['|', '⟩']
        ],
        autoClosingPairs: [
            { open: '{', close: '}' },
            { open: '[', close: ']' },
            { open: '(', close: ')' },
            { open: '|', close: '⟩' }
        ]
    },
    
    tokenizer: {
        root: [
            // Comments
            [/#.*$/, 'comment'],
            [/\/\*/, 'comment', '@comment'],
            
            // Keywords
            [/\b(qubit|gate|circuit|measure|entangle|superposition|hadamard|pauli|cnot|teleport|swap|phase|rotation)\b/, 'keyword'],
            
            // Quantum states
            [/\|[01+\-ijkl]*⟩/, 'string.quantum-state'],
            
            // Gates
            [/\b[HXYZISCNOT]+\b/, 'type.gate'],
            
            // Operators
            [/[⊗⊕≈→↔⟷]/, 'operator.quantum'],
            [/[=+\-*/%<>!&|^~?:]/, 'operator'],
            
            // Numbers
            [/\d+(\.\d+)?([eE][-+]?\d+)?/, 'number'],
            
            // Strings
            [/"([^"\\]|\\.)*"/, 'string'],
            [/'([^'\\]|\\.)*'/, 'string'],
            
            // Identifiers
            [/[a-zA-Z_]\w*/, 'identifier'],
            
            // Delimiters
            [/[{}()\[\]]/, 'delimiter'],
            [/[,;]/, 'delimiter']
        ],
        
        comment: [
            [/[^\/*]+/, 'comment'],
            [/\/\*/, 'comment', '@push'],
            ["\\*/", 'comment', '@pop'],
            [/[\/*]/, 'comment']
        ]
    }
};

// Quantum-Net Language Definition
const quantumNetLanguage = {
    id: 'quantum-net',
    extensions: ['.qn', '.qnet'],
    aliases: ['Quantum-Net', 'quantum-net'],
    mimetypes: ['text/x-quantum-net'],
    
    configuration: {
        comments: {
            lineComment: '//',
            blockComment: ['/*', '*/']
        },
        brackets: [
            ['{', '}'],
            ['[', ']'],
            ['(', ')']
        ]
    },
    
    tokenizer: {
        root: [
            // Comments
            [/\/\/.*$/, 'comment'],
            [/\/\*/, 'comment', '@comment'],
            
            // Keywords
            [/\b(node|quantum_link|entanglement|protocol|teleport|distribute|network|topology|routing|security)\b/, 'keyword'],
            
            // Network operators
            [/[⊗⊕≈→↔⟷]/, 'operator.network'],
            [/[=+\-*/%<>!&|^~?:]/, 'operator'],
            
            // Coordinates
            [/\(\s*\d+(\.\d+)?\s*,\s*\d+(\.\d+)?\s*\)/, 'number.coordinate'],
            
            // Numbers
            [/\d+(\.\d+)?([eE][-+]?\d+)?/, 'number'],
            
            // Strings
            [/"([^"\\]|\\.)*"/, 'string'],
            [/'([^'\\]|\\.)*'/, 'string'],
            
            // Identifiers
            [/[a-zA-Z_]\w*/, 'identifier'],
            
            // Delimiters
            [/[{}()\[\]]/, 'delimiter'],
            [/[,;]/, 'delimiter']
        ],
        
        comment: [
            [/[^\/*]+/, 'comment'],
            [/\/\*/, 'comment', '@push'],
            ["\\*/", 'comment', '@pop'],
            [/[\/*]/, 'comment']
        ]
    }
};

// Flux Language Definition
const fluxLanguage = {
    id: 'flux',
    extensions: ['.flux', '.fl'],
    aliases: ['Flux', 'flux'],
    mimetypes: ['text/x-flux'],
    
    configuration: {
        comments: {
            lineComment: '//',
            blockComment: ['/*', '*/']
        },
        brackets: [
            ['{', '}'],
            ['[', ']'],
            ['(', ')']
        ]
    },
    
    tokenizer: {
        root: [
            // Comments
            [/\/\/.*$/, 'comment'],
            [/\/\*/, 'comment', '@comment'],
            
            // Keywords
            [/\b(flow|stream|transform|filter|map|reduce|emit|collect|pipeline|async|await|parallel|sequential)\b/, 'keyword'],
            
            // Flow operators
            [/[→←↔↕⇒⇔⟹⟷]/, 'operator.flow'],
            [/[=+\-*/%<>!&|^~?:]/, 'operator'],
            
            // Numbers
            [/\d+(\.\d+)?([eE][-+]?\d+)?/, 'number'],
            
            // Strings
            [/"([^"\\]|\\.)*"/, 'string'],
            [/'([^'\\]|\\.)*'/, 'string'],
            
            // Identifiers
            [/[a-zA-Z_]\w*/, 'identifier'],
            
            // Delimiters
            [/[{}()\[\]]/, 'delimiter'],
            [/[,;]/, 'delimiter']
        ],
        
        comment: [
            [/[^\/*]+/, 'comment'],
            [/\/\*/, 'comment', '@push'],
            ["\\*/", 'comment', '@pop'],
            [/[\/*]/, 'comment']
        ]
    }
};

// Crowe Language Definition
const croweLanguage = {
    id: 'crowe',
    extensions: ['.crowe', '.cr'],
    aliases: ['Crowe', 'crowe'],
    mimetypes: ['text/x-crowe'],
    
    configuration: {
        comments: {
            lineComment: '//',
            blockComment: ['/*', '*/']
        },
        brackets: [
            ['{', '}'],
            ['[', ']'],
            ['(', ')']
        ]
    },
    
    tokenizer: {
        root: [
            // Comments
            [/\/\/.*$/, 'comment'],
            [/\/\*/, 'comment', '@comment'],
            
            // Keywords
            [/\b(define|function|module|import|export|class|interface|type|struct|enum|trait|impl|match|case|if|else|for|while|loop|break|continue|return|yield)\b/, 'keyword'],
            
            // Built-in types
            [/\b(int|float|string|bool|array|map|set|option|result)\b/, 'type'],
            
            // Operators
            [/[=+\-*/%<>!&|^~?:]/, 'operator'],
            
            // Numbers
            [/\d+(\.\d+)?([eE][-+]?\d+)?/, 'number'],
            
            // Strings
            [/"([^"\\]|\\.)*"/, 'string'],
            [/'([^'\\]|\\.)*'/, 'string'],
            
            // Identifiers
            [/[a-zA-Z_]\w*/, 'identifier'],
            
            // Delimiters
            [/[{}()\[\]]/, 'delimiter'],
            [/[,;]/, 'delimiter']
        ],
        
        comment: [
            [/[^\/*]+/, 'comment'],
            [/\/\*/, 'comment', '@push'],
            ["\\*/", 'comment', '@pop'],
            [/[\/*]/, 'comment']
        ]
    }
};

// Color themes for each language
const languageThemes = {
    'synapse-dark': {
        base: 'vs-dark',
        inherit: true,
        rules: [
            { token: 'keyword', foreground: '7A5CFF', fontStyle: 'bold' },
            { token: 'operator.scientific', foreground: '43E5FF', fontStyle: 'bold' },
            { token: 'number.uncertainty', foreground: 'F39C12', fontStyle: 'bold' },
            { token: 'string', foreground: '27AE60' },
            { token: 'comment', foreground: '6C7B7F', fontStyle: 'italic' },
            { token: 'identifier', foreground: 'E6E8EB' }
        ],
        colors: {
            'editor.background': '#0B0F14',
            'editor.foreground': '#E6E8EB',
            'editorCursor.foreground': '#43E5FF',
            'editor.lineHighlightBackground': '#1A1E23',
            'editorLineNumber.foreground': '#6C7B7F',
            'editor.selectionBackground': '#7A5CFF33'
        }
    },
    
    'quantum-dark': {
        base: 'vs-dark',
        inherit: true,
        rules: [
            { token: 'keyword', foreground: '00D4AA', fontStyle: 'bold' },
            { token: 'operator.quantum', foreground: 'FF6B9D', fontStyle: 'bold' },
            { token: 'string.quantum-state', foreground: 'FFD93D', fontStyle: 'bold' },
            { token: 'type.gate', foreground: 'A8E6CF', fontStyle: 'bold' },
            { token: 'comment', foreground: '7B68EE', fontStyle: 'italic' }
        ],
        colors: {
            'editor.background': '#0D1B2A',
            'editor.foreground': '#F0F8FF',
            'editorCursor.foreground': '#FF6B9D',
            'editor.lineHighlightBackground': '#1B263B'
        }
    }
};

// Completion providers for each language
const completionProviders = {
    synapse: {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: 'uncertain',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'uncertain ${1:variable} = ${2:value} ± ${3:error}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Declare an uncertain value with error bounds'
                },
                {
                    label: 'parallel',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'parallel {\n    branch ${1:A}: ${2:computation}\n    branch ${3:B}: ${4:computation}\n}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Execute computations in parallel branches'
                },
                {
                    label: 'experiment',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'experiment ${1:ExperimentName} {\n    ${2:setup}\n    ${3:execution}\n    ${4:analysis}\n}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a scientific experiment'
                }
            ];
            return { suggestions };
        }
    },
    
    'qubit-flow': {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: 'qubit',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'qubit ${1:name} = |${2:0}⟩',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Declare a quantum bit'
                },
                {
                    label: 'circuit',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'circuit ${1:CircuitName} {\n    ${2:gates}\n    measure ${3:qubits}\n}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a quantum circuit'
                },
                {
                    label: 'hadamard',
                    kind: monaco.languages.CompletionItemKind.Function,
                    insertText: 'hadamard(${1:qubit})',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Apply Hadamard gate'
                }
            ];
            return { suggestions };
        }
    },
    
    'quantum-net': {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: 'node',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'node ${1:NodeName} at (${2:x}, ${3:y})',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a network node'
                },
                {
                    label: 'quantum_link',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'quantum_link ${1:node1} ↔ ${2:node2}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Create quantum entanglement link'
                }
            ];
            return { suggestions };
        }
    },
    
    flux: {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: 'flow',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'flow ${1:name} {\n    ${2:operations}\n}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a data flow'
                },
                {
                    label: 'transform',
                    kind: monaco.languages.CompletionItemKind.Function,
                    insertText: 'transform(${1:data} → ${2:result})',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Transform data'
                }
            ];
            return { suggestions };
        }
    },
    
    crowe: {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: 'function',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'function ${1:name}(${2:params}) -> ${3:ReturnType} {\n    ${4:body}\n}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a function'
                },
                {
                    label: 'module',
                    kind: monaco.languages.CompletionItemKind.Keyword,
                    insertText: 'module ${1:ModuleName} {\n    ${2:content}\n}',
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    documentation: 'Define a module'
                }
            ];
            return { suggestions };
        }
    }
};

// Function to register all languages
function registerLanguages() {
    // Register language definitions
    monaco.languages.register({ id: 'synapse' });
    monaco.languages.register({ id: 'qubit-flow' });
    monaco.languages.register({ id: 'quantum-net' });
    monaco.languages.register({ id: 'flux' });
    monaco.languages.register({ id: 'crowe' });
    
    // Set language configurations
    monaco.languages.setLanguageConfiguration('synapse', synapseLanguage.configuration);
    monaco.languages.setLanguageConfiguration('qubit-flow', qubitFlowLanguage.configuration);
    monaco.languages.setLanguageConfiguration('quantum-net', quantumNetLanguage.configuration);
    monaco.languages.setLanguageConfiguration('flux', fluxLanguage.configuration);
    monaco.languages.setLanguageConfiguration('crowe', croweLanguage.configuration);
    
    // Set tokenizers
    monaco.languages.setMonarchTokensProvider('synapse', synapseLanguage);
    monaco.languages.setMonarchTokensProvider('qubit-flow', qubitFlowLanguage);
    monaco.languages.setMonarchTokensProvider('quantum-net', quantumNetLanguage);
    monaco.languages.setMonarchTokensProvider('flux', fluxLanguage);
    monaco.languages.setMonarchTokensProvider('crowe', croweLanguage);
    
    // Register completion providers
    Object.keys(completionProviders).forEach(languageId => {
        monaco.languages.registerCompletionItemProvider(languageId, completionProviders[languageId]);
    });
    
    // Define themes
    Object.keys(languageThemes).forEach(themeName => {
        monaco.editor.defineTheme(themeName, languageThemes[themeName]);
    });
    
    console.log('All languages registered successfully');
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.registerLanguages = registerLanguages;
    window.languageDefinitions = {
        synapse: synapseLanguage,
        'qubit-flow': qubitFlowLanguage,
        'quantum-net': quantumNetLanguage,
        flux: fluxLanguage,
        crowe: croweLanguage
    };
}