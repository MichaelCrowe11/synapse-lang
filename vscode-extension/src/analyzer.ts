import { TextDocument, Position, CompletionItem, CompletionItemKind, Hover, Location, CodeAction, CodeActionKind, Diagnostic, DiagnosticSeverity, Range } from 'vscode-languageserver/node';

export class SynapseAnalyzer {
    private keywords = [
        'hypothesis', 'experiment', 'parallel', 'branch', 'quantum', 'tensor',
        'uncertain', 'pipeline', 'procedure', 'function', 'let', 'const'
    ];
    
    private functions = [
        'create_tensor', 'differentiate', 'integrate', 'measure_all',
        'normalize', 'contract', 'parallel_map', 'parallel_reduce'
    ];
    
    private quantumGates = [
        'H', 'X', 'Y', 'Z', 'CNOT', 'CZ', 'SWAP', 'Toffoli'
    ];
    
    getContextAt(text: string, offset: number): string {
        // Simple context detection
        const before = text.substring(Math.max(0, offset - 100), offset);
        if (before.includes('quantum')) return 'quantum';
        if (before.includes('tensor')) return 'tensor';
        if (before.includes('parallel')) return 'parallel';
        return 'general';
    }
    
    getCompletions(context: string): CompletionItem[] {
        const items: CompletionItem[] = [];
        
        // Add keywords
        this.keywords.forEach(keyword => {
            items.push({
                label: keyword,
                kind: CompletionItemKind.Keyword,
                detail: `Synapse keyword: ${keyword}`
            });
        });
        
        // Add context-specific completions
        if (context === 'quantum') {
            this.quantumGates.forEach(gate => {
                items.push({
                    label: gate,
                    kind: CompletionItemKind.Method,
                    detail: `Quantum gate: ${gate}`
                });
            });
        }
        
        // Add functions
        this.functions.forEach(func => {
            items.push({
                label: func,
                kind: CompletionItemKind.Function,
                detail: `Function: ${func}`,
                insertText: `${func}($1)`,
                insertTextFormat: 2
            });
        });
        
        return items;
    }
    
    resolveCompletion(item: CompletionItem): CompletionItem {
        // Add documentation
        item.documentation = `Documentation for ${item.label}`;
        return item;
    }
    
    getHover(document: TextDocument, position: Position): Hover | null {
        const text = document.getText();
        const offset = document.offsetAt(position);
        
        // Find word at position
        const wordPattern = /[a-zA-Z_]\w*/g;
        let match;
        
        while ((match = wordPattern.exec(text)) !== null) {
            if (match.index <= offset && offset <= match.index + match[0].length) {
                const word = match[0];
                
                if (this.keywords.includes(word)) {
                    return {
                        contents: {
                            kind: 'markdown',
                            value: `**${word}** - Synapse keyword\n\nUsed for ${word} operations.`
                        }
                    };
                }
                
                if (this.functions.includes(word)) {
                    return {
                        contents: {
                            kind: 'markdown',
                            value: `**${word}()** - Built-in function\n\nPerforms ${word} operation.`
                        }
                    };
                }
                
                break;
            }
        }
        
        return null;
    }
    
    getDefinition(document: TextDocument, position: Position): Location | null {
        // Simple definition finding
        const text = document.getText();
        const line = position.line;
        const lines = text.split('\n');
        const currentLine = lines[line];
        
        // Find variable/function name at position
        const match = currentLine.match(/\b(\w+)\b/);
        if (match) {
            const name = match[1];
            
            // Search for definition
            for (let i = 0; i < lines.length; i++) {
                if (lines[i].includes(`let ${name}`) || 
                    lines[i].includes(`const ${name}`) ||
                    lines[i].includes(`procedure ${name}`) ||
                    lines[i].includes(`function ${name}`)) {
                    return {
                        uri: document.uri,
                        range: {
                            start: { line: i, character: 0 },
                            end: { line: i, character: lines[i].length }
                        }
                    };
                }
            }
        }
        
        return null;
    }
    
    getReferences(document: TextDocument, position: Position, includeDeclaration: boolean): Location[] {
        const locations: Location[] = [];
        const text = document.getText();
        const lines = text.split('\n');
        const line = lines[position.line];
        
        // Find word at position
        const match = line.match(/\b(\w+)\b/);
        if (!match) return locations;
        
        const word = match[1];
        const regex = new RegExp(`\\b${word}\\b`, 'g');
        
        // Find all occurrences
        lines.forEach((line, lineNumber) => {
            let match;
            while ((match = regex.exec(line)) !== null) {
                locations.push({
                    uri: document.uri,
                    range: {
                        start: { line: lineNumber, character: match.index },
                        end: { line: lineNumber, character: match.index + word.length }
                    }
                });
            }
        });
        
        return locations;
    }
    
    getQuickFix(document: TextDocument, diagnostic: Diagnostic): CodeAction | null {
        if (diagnostic.message.includes('Unmatched brackets')) {
            const action: CodeAction = {
                title: 'Add missing bracket',
                kind: CodeActionKind.QuickFix,
                diagnostics: [diagnostic],
                edit: {
                    changes: {
                        [document.uri]: [{
                            range: diagnostic.range,
                            newText: document.getText(diagnostic.range) + '}'
                        }]
                    }
                }
            };
            return action;
        }
        
        return null;
    }
    
    getRefactorings(document: TextDocument, range: Range): CodeAction[] {
        const actions: CodeAction[] = [];
        const text = document.getText(range);
        
        if (text.length > 0) {
            actions.push({
                title: 'Extract to function',
                kind: CodeActionKind.RefactorExtract,
                command: {
                    title: 'Extract to function',
                    command: 'synapse.extractFunction'
                }
            });
            
            if (range.start.line === range.end.line) {
                actions.push({
                    title: 'Extract to variable',
                    kind: CodeActionKind.RefactorExtract,
                    command: {
                        title: 'Extract to variable',
                        command: 'synapse.extractVariable'
                    }
                });
            }
        }
        
        return actions;
    }
    
    async analyze(document: TextDocument): Promise<Diagnostic[]> {
        const diagnostics: Diagnostic[] = [];
        const text = document.getText();
        const lines = text.split('\n');
        
        lines.forEach((line, i) => {
            // Check for unmatched brackets
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
            
            // Check for missing uncertainty
            if (line.includes('uncertain') && !line.includes('±')) {
                diagnostics.push({
                    severity: DiagnosticSeverity.Warning,
                    range: {
                        start: { line: i, character: 0 },
                        end: { line: i, character: line.length }
                    },
                    message: 'Uncertain value should specify uncertainty using ±',
                    source: 'synapse'
                });
            }
        });
        
        return diagnostics;
    }
}