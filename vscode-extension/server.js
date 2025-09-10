const {
    createConnection,
    TextDocuments,
    ProposedFeatures,
    InitializeParams,
    DidChangeConfigurationNotification,
    CompletionItem,
    CompletionItemKind,
    TextDocumentPositionParams,
    TextDocumentSyncKind,
    InitializeResult,
    Diagnostic,
    DiagnosticSeverity,
    Range,
    Position
} = require('vscode-languageserver/node');

const { TextDocument } = require('vscode-languageserver-textdocument');

// Create a connection for the server
const connection = createConnection(ProposedFeatures.all);

// Create a simple text document manager
const documents = new TextDocuments(TextDocument);

let hasConfigurationCapability = false;
let hasWorkspaceFolderCapability = false;
let hasDiagnosticRelatedInformationCapability = false;

connection.onInitialize((params) => {
    const capabilities = params.capabilities;

    hasConfigurationCapability = !!(
        capabilities.workspace && !!capabilities.workspace.configuration
    );
    hasWorkspaceFolderCapability = !!(
        capabilities.workspace && !!capabilities.workspace.workspaceFolders
    );
    hasDiagnosticRelatedInformationCapability = !!(
        capabilities.textDocument &&
        capabilities.textDocument.publishDiagnostics &&
        capabilities.textDocument.publishDiagnostics.relatedInformation
    );

    const result = {
        capabilities: {
            textDocumentSync: TextDocumentSyncKind.Incremental,
            completionProvider: {
                resolveProvider: true,
                triggerCharacters: ['.', ':', '(', '{', '[', ' ']
            },
            hoverProvider: true,
            definitionProvider: true,
            documentFormattingProvider: true,
            documentRangeFormattingProvider: true
        }
    };
    
    if (hasWorkspaceFolderCapability) {
        result.capabilities.workspace = {
            workspaceFolders: {
                supported: true
            }
        };
    }
    
    return result;
});

connection.onInitialized(() => {
    if (hasConfigurationCapability) {
        connection.client.register(DidChangeConfigurationNotification.type, undefined);
    }
    if (hasWorkspaceFolderCapability) {
        connection.workspace.onDidChangeWorkspaceFolders(_event => {
            connection.console.log('Workspace folder change event received.');
        });
    }
});

// Synapse language keywords for completion
const synapseKeywords = [
    'hypothesis', 'experiment', 'parallel', 'branch', 'stream', 'reason', 'chain',
    'premise', 'derive', 'conclude', 'uncertain', 'observe', 'propagate', 'constrain',
    'evolve', 'pipeline', 'stage', 'fork', 'path', 'merge', 'explore', 'try',
    'fallback', 'accept', 'reject', 'symbolic', 'let', 'solve', 'prove', 'synthesize',
    'validate', 'assume', 'predict', 'setup', 'procedure', 'analysis', 'from', 'when',
    'through', 'where', 'for', 'all', 'exists', 'in', 'with', 'at', 'synchronize',
    'async', 'await', 'channel', 'quantum', 'circuit', 'tensor', 'measure'
];

// Built-in functions
const synapseFunctions = [
    'create_tensor', 'differentiate', 'integrate', 'solve_equation', 'optimize',
    'measure_all', 'entangle', 'superposition', 'collapse', 'normalize',
    'contract', 'transform', 'reduce', 'map', 'filter', 'fold', 'zip',
    'parallel_map', 'parallel_reduce', 'async_execute', 'await_result'
];

// Quantum gates
const quantumGates = [
    'H', 'X', 'Y', 'Z', 'CNOT', 'CZ', 'SWAP', 'Toffoli', 'Fredkin',
    'RX', 'RY', 'RZ', 'Phase', 'T', 'S', 'measure'
];

// Provide completion items
connection.onCompletion((textDocumentPosition) => {
    const completionItems = [];
    
    // Add keywords
    synapseKeywords.forEach(keyword => {
        completionItems.push({
            label: keyword,
            kind: CompletionItemKind.Keyword,
            detail: 'Synapse keyword',
            documentation: `Keyword: ${keyword}`
        });
    });
    
    // Add functions
    synapseFunctions.forEach(func => {
        completionItems.push({
            label: func,
            kind: CompletionItemKind.Function,
            detail: 'Built-in function',
            documentation: `Function: ${func}()`,
            insertText: `${func}($1)`,
            insertTextFormat: 2 // Snippet format
        });
    });
    
    // Add quantum gates
    quantumGates.forEach(gate => {
        completionItems.push({
            label: gate,
            kind: CompletionItemKind.Method,
            detail: 'Quantum gate',
            documentation: `Quantum gate: ${gate}`,
            insertText: `${gate}($1)`,
            insertTextFormat: 2
        });
    });
    
    return completionItems;
});

// Provide hover information
connection.onHover((params) => {
    const document = documents.get(params.textDocument.uri);
    if (!document) return null;
    
    const text = document.getText();
    const offset = document.offsetAt(params.position);
    
    // Find the word at the current position
    const wordPattern = /[a-zA-Z_][a-zA-Z0-9_]*/g;
    let match;
    while ((match = wordPattern.exec(text)) !== null) {
        if (match.index <= offset && offset <= match.index + match[0].length) {
            const word = match[0];
            
            // Provide documentation for keywords
            if (synapseKeywords.includes(word)) {
                return {
                    contents: {
                        kind: 'markdown',
                        value: getKeywordDocumentation(word)
                    }
                };
            }
            
            // Provide documentation for functions
            if (synapseFunctions.includes(word)) {
                return {
                    contents: {
                        kind: 'markdown',
                        value: getFunctionDocumentation(word)
                    }
                };
            }
            
            break;
        }
    }
    
    return null;
});

// Document diagnostics (error checking)
async function validateTextDocument(textDocument) {
    const text = textDocument.getText();
    const diagnostics = [];
    
    // Check for common syntax errors
    const lines = text.split(/\r?\n/);
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Check for unclosed brackets
        const openBrackets = (line.match(/\{/g) || []).length;
        const closeBrackets = (line.match(/\}/g) || []).length;
        if (openBrackets !== closeBrackets) {
            diagnostics.push({
                severity: DiagnosticSeverity.Error,
                range: {
                    start: { line: i, character: 0 },
                    end: { line: i, character: line.length }
                },
                message: 'Unmatched brackets',
                source: 'synapse'
            });
        }
        
        // Check for missing semicolons (if required)
        if (line.trim() && !line.trim().endsWith('{') && !line.trim().endsWith('}') 
            && !line.trim().endsWith(';') && !line.trim().startsWith('//')) {
            // This is a simple heuristic - adjust based on actual language rules
        }
        
        // Check for undefined symbols (simplified)
        const uncertainPattern = /uncertain\s+(\w+)\s*=/g;
        let match;
        while ((match = uncertainPattern.exec(line)) !== null) {
            const varName = match[1];
            // Check if uncertainty is specified
            if (!line.includes('±')) {
                diagnostics.push({
                    severity: DiagnosticSeverity.Warning,
                    range: {
                        start: { line: i, character: match.index },
                        end: { line: i, character: match.index + match[0].length }
                    },
                    message: `Uncertain variable '${varName}' should specify uncertainty using ±`,
                    source: 'synapse'
                });
            }
        }
    }
    
    connection.sendDiagnostics({ uri: textDocument.uri, diagnostics });
}

// Documentation helpers
function getKeywordDocumentation(keyword) {
    const docs = {
        'hypothesis': '**hypothesis** - Defines a scientific hypothesis with assumptions, predictions, and validation criteria',
        'experiment': '**experiment** - Creates an experimental setup with parallel testing branches',
        'parallel': '**parallel** - Executes multiple computations simultaneously',
        'uncertain': '**uncertain** - Declares a value with associated uncertainty (± notation)',
        'quantum': '**quantum** - Defines quantum circuits and operations',
        'tensor': '**tensor** - Creates and manipulates multi-dimensional arrays',
        'pipeline': '**pipeline** - Defines a data processing pipeline with stages',
        'symbolic': '**symbolic** - Enables symbolic mathematics and equation solving'
    };
    
    return docs[keyword] || `**${keyword}** - Synapse keyword`;
}

function getFunctionDocumentation(func) {
    const docs = {
        'create_tensor': '**create_tensor(dimensions)** - Creates a new tensor with specified dimensions',
        'differentiate': '**differentiate(expression, variable)** - Computes the derivative of an expression',
        'measure_all': '**measure_all()** - Measures all qubits in a quantum circuit',
        'normalize': '**normalize()** - Normalizes a tensor or quantum state',
        'parallel_map': '**parallel_map(function, collection)** - Applies a function to each element in parallel'
    };
    
    return docs[func] || `**${func}()** - Built-in Synapse function`;
}

// Document formatting
connection.onDocumentFormatting((params) => {
    const document = documents.get(params.textDocument.uri);
    if (!document) return [];
    
    const text = document.getText();
    const formatted = formatSynapseCode(text);
    
    return [{
        range: {
            start: { line: 0, character: 0 },
            end: document.positionAt(text.length)
        },
        newText: formatted
    }];
});

function formatSynapseCode(code) {
    // Simple formatter - indent blocks
    const lines = code.split(/\r?\n/);
    const formatted = [];
    let indentLevel = 0;
    const indentString = '\t';
    
    for (const line of lines) {
        const trimmed = line.trim();
        
        // Decrease indent for closing braces
        if (trimmed.startsWith('}')) {
            indentLevel = Math.max(0, indentLevel - 1);
        }
        
        // Apply indentation
        if (trimmed) {
            formatted.push(indentString.repeat(indentLevel) + trimmed);
        } else {
            formatted.push('');
        }
        
        // Increase indent for opening braces
        if (trimmed.endsWith('{')) {
            indentLevel++;
        }
    }
    
    return formatted.join('\n');
}

// Listen for document changes
documents.onDidChangeContent(change => {
    validateTextDocument(change.document);
});

// Make the text document manager listen on the connection
documents.listen(connection);

// Listen on the connection
connection.listen();