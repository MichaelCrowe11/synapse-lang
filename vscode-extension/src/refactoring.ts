import * as vscode from 'vscode';

export class SynapseRefactoringProvider implements vscode.CodeActionProvider {
    public static readonly providedCodeActionKinds = [
        vscode.CodeActionKind.RefactorExtract,
        vscode.CodeActionKind.RefactorInline,
        vscode.CodeActionKind.RefactorRewrite,
        vscode.CodeActionKind.Refactor
    ];
    
    async provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range | vscode.Selection,
        context: vscode.CodeActionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.CodeAction[]> {
        const actions: vscode.CodeAction[] = [];
        
        // Extract function
        if (this.canExtractFunction(document, range)) {
            actions.push(this.createExtractFunctionAction(document, range));
        }
        
        // Extract variable
        if (this.canExtractVariable(document, range)) {
            actions.push(this.createExtractVariableAction(document, range));
        }
        
        // Extract parallel block
        if (this.canExtractParallelBlock(document, range)) {
            actions.push(this.createExtractParallelBlockAction(document, range));
        }
        
        // Convert to quantum circuit
        if (this.canConvertToQuantumCircuit(document, range)) {
            actions.push(this.createConvertToQuantumCircuitAction(document, range));
        }
        
        // Rename symbol
        if (this.canRenameSymbol(document, range)) {
            actions.push(this.createRenameSymbolAction(document, range));
        }
        
        // Inline variable
        if (this.canInlineVariable(document, range)) {
            actions.push(this.createInlineVariableAction(document, range));
        }
        
        // Add uncertainty
        if (this.canAddUncertainty(document, range)) {
            actions.push(this.createAddUncertaintyAction(document, range));
        }
        
        // Optimize tensor operations
        if (this.canOptimizeTensorOps(document, range)) {
            actions.push(this.createOptimizeTensorOpsAction(document, range));
        }
        
        return actions;
    }
    
    private canExtractFunction(document: vscode.TextDocument, range: vscode.Range): boolean {
        // Check if selection contains complete statements
        const text = document.getText(range);
        return text.length > 0 && !range.isSingleLine;
    }
    
    private createExtractFunctionAction(document: vscode.TextDocument, range: vscode.Range): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Extract Function',
            vscode.CodeActionKind.RefactorExtract
        );
        
        const selectedText = document.getText(range);
        const functionName = 'extracted_function';
        
        // Analyze the selected code for parameters and return values
        const params = this.extractParameters(selectedText);
        const returnType = this.inferReturnType(selectedText);
        
        // Create function definition
        const functionDef = `
procedure ${functionName}(${params.join(', ')}) {
${this.indentText(selectedText)}
    return result
}`;
        
        // Create function call
        const functionCall = `${functionName}(${params.join(', ')})`;
        
        const edit = new vscode.WorkspaceEdit();
        
        // Insert function definition before current function
        const insertPosition = this.findFunctionInsertPosition(document, range.start);
        edit.insert(document.uri, insertPosition, functionDef + '\n\n');
        
        // Replace selected text with function call
        edit.replace(document.uri, range, functionCall);
        
        action.edit = edit;
        return action;
    }
    
    private canExtractVariable(document: vscode.TextDocument, range: vscode.Range): boolean {
        const text = document.getText(range);
        // Check if selection is an expression
        return text.length > 0 && range.isSingleLine && !text.includes('\n');
    }
    
    private createExtractVariableAction(document: vscode.TextDocument, range: vscode.Range): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Extract Variable',
            vscode.CodeActionKind.RefactorExtract
        );
        
        const selectedText = document.getText(range);
        const variableName = this.suggestVariableName(selectedText);
        
        const edit = new vscode.WorkspaceEdit();
        
        // Insert variable declaration
        const line = range.start.line;
        const lineStart = new vscode.Position(line, 0);
        edit.insert(document.uri, lineStart, `let ${variableName} = ${selectedText}\n`);
        
        // Replace expression with variable
        edit.replace(document.uri, range, variableName);
        
        action.edit = edit;
        return action;
    }
    
    private canExtractParallelBlock(document: vscode.TextDocument, range: vscode.Range): boolean {
        const text = document.getText(range);
        return text.includes('branch') || text.split('\n').length > 3;
    }
    
    private createExtractParallelBlockAction(document: vscode.TextDocument, range: vscode.Range): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Extract to Parallel Block',
            vscode.CodeActionKind.RefactorExtract
        );
        
        const selectedText = document.getText(range);
        const lines = selectedText.split('\n').filter(l => l.trim());
        
        // Create parallel block
        const parallelBlock = `
parallel {
${lines.map((line, i) => `    branch ${String.fromCharCode(65 + i)}: ${line.trim()}`).join('\n')}
}`;
        
        const edit = new vscode.WorkspaceEdit();
        edit.replace(document.uri, range, parallelBlock);
        
        action.edit = edit;
        return action;
    }
    
    private canConvertToQuantumCircuit(document: vscode.TextDocument, range: vscode.Range): boolean {
        const text = document.getText(range);
        return text.includes('qubit') || text.includes('gate') || text.includes('measure');
    }
    
    private createConvertToQuantumCircuitAction(document: vscode.TextDocument, range: vscode.Range): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Convert to Quantum Circuit',
            vscode.CodeActionKind.RefactorRewrite
        );
        
        const selectedText = document.getText(range);
        
        // Parse and convert to quantum circuit syntax
        const circuitDef = `
quantum circuit converted_circuit {
    input: |0⟩ ⊗ |0⟩
    gates: [
        H(0),
        CNOT(0, 1),
        measure_all()
    ]
    output: entangled_state
}`;
        
        const edit = new vscode.WorkspaceEdit();
        edit.replace(document.uri, range, circuitDef);
        
        action.edit = edit;
        return action;
    }
    
    private canRenameSymbol(document: vscode.TextDocument, range: vscode.Range): boolean {
        const text = document.getText(range);
        return /^[a-zA-Z_]\w*$/.test(text.trim());
    }
    
    private createRenameSymbolAction(document: vscode.TextDocument, range: vscode.Range): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Rename Symbol',
            vscode.CodeActionKind.Refactor
        );
        
        action.command = {
            command: 'editor.action.rename',
            title: 'Rename Symbol'
        };
        
        return action;
    }
    
    private canInlineVariable(document: vscode.TextDocument, range: vscode.Range): boolean {
        const line = document.lineAt(range.start.line).text;
        return line.includes('let ') || line.includes('const ');
    }
    
    private createInlineVariableAction(document: vscode.TextDocument, range: vscode.Range): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Inline Variable',
            vscode.CodeActionKind.RefactorInline
        );
        
        const line = document.lineAt(range.start.line).text;
        const match = line.match(/(?:let|const)\s+(\w+)\s*=\s*(.+)/);
        
        if (match) {
            const [, variableName, value] = match;
            const edit = new vscode.WorkspaceEdit();
            
            // Remove variable declaration
            const lineRange = document.lineAt(range.start.line).rangeIncludingLineBreak;
            edit.delete(document.uri, lineRange);
            
            // Find and replace all occurrences
            const text = document.getText();
            const regex = new RegExp(`\\b${variableName}\\b`, 'g');
            let match;
            
            while ((match = regex.exec(text)) !== null) {
                const pos = document.positionAt(match.index);
                if (pos.line > range.start.line) {
                    const replaceRange = new vscode.Range(
                        pos,
                        pos.translate(0, variableName.length)
                    );
                    edit.replace(document.uri, replaceRange, `(${value})`);
                }
            }
            
            action.edit = edit;
        }
        
        return action;
    }
    
    private canAddUncertainty(document: vscode.TextDocument, range: vscode.Range): boolean {
        const text = document.getText(range);
        return /\d+(\.\d+)?/.test(text) && !text.includes('±');
    }
    
    private createAddUncertaintyAction(document: vscode.TextDocument, range: vscode.Range): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Add Uncertainty',
            vscode.CodeActionKind.Refactor
        );
        
        const selectedText = document.getText(range);
        const value = parseFloat(selectedText);
        const uncertainty = (value * 0.05).toFixed(2); // 5% uncertainty
        
        const edit = new vscode.WorkspaceEdit();
        edit.replace(document.uri, range, `${selectedText} ± ${uncertainty}`);
        
        action.edit = edit;
        return action;
    }
    
    private canOptimizeTensorOps(document: vscode.TextDocument, range: vscode.Range): boolean {
        const text = document.getText(range);
        return text.includes('tensor') || text.includes('contract') || text.includes('einsum');
    }
    
    private createOptimizeTensorOpsAction(document: vscode.TextDocument, range: vscode.Range): vscode.CodeAction {
        const action = new vscode.CodeAction(
            'Optimize Tensor Operations',
            vscode.CodeActionKind.RefactorRewrite
        );
        
        const selectedText = document.getText(range);
        
        // Simple optimization: combine consecutive operations
        const optimized = selectedText
            .replace(/\.contract\([^)]+\)\.contract\([^)]+\)/, '.contract_multi($1, $2)')
            .replace(/\.transpose\(\)\.transpose\(\)/, '')
            .replace(/\.normalize\(\)\.normalize\(\)/, '.normalize()');
        
        const edit = new vscode.WorkspaceEdit();
        edit.replace(document.uri, range, optimized);
        
        action.edit = edit;
        return action;
    }
    
    // Helper methods
    private extractParameters(code: string): string[] {
        const params: Set<string> = new Set();
        const variablePattern = /\b([a-zA-Z_]\w*)\b/g;
        let match;
        
        while ((match = variablePattern.exec(code)) !== null) {
            const variable = match[1];
            // Filter out keywords and function names
            if (!this.isKeyword(variable)) {
                params.add(variable);
            }
        }
        
        return Array.from(params).slice(0, 3); // Limit to 3 parameters
    }
    
    private inferReturnType(code: string): string {
        if (code.includes('quantum')) return 'QuantumState';
        if (code.includes('tensor')) return 'Tensor';
        if (code.includes('uncertain')) return 'UncertainValue';
        return 'Any';
    }
    
    private indentText(text: string, spaces: number = 4): string {
        const indent = ' '.repeat(spaces);
        return text.split('\n').map(line => indent + line).join('\n');
    }
    
    private findFunctionInsertPosition(document: vscode.TextDocument, currentPosition: vscode.Position): vscode.Position {
        // Find the start of the current function/procedure
        for (let i = currentPosition.line - 1; i >= 0; i--) {
            const line = document.lineAt(i).text;
            if (line.includes('procedure') || line.includes('function') || line.includes('experiment')) {
                return new vscode.Position(i, 0);
            }
        }
        return new vscode.Position(0, 0);
    }
    
    private suggestVariableName(expression: string): string {
        if (expression.includes('tensor')) return 'tensor_result';
        if (expression.includes('quantum')) return 'quantum_state';
        if (expression.includes('parallel')) return 'parallel_result';
        if (expression.includes('uncertain')) return 'uncertain_value';
        return 'extracted_value';
    }
    
    private isKeyword(word: string): boolean {
        const keywords = [
            'hypothesis', 'experiment', 'parallel', 'branch', 'quantum',
            'tensor', 'uncertain', 'let', 'const', 'if', 'else', 'for',
            'while', 'return', 'procedure', 'function'
        ];
        return keywords.includes(word);
    }
}