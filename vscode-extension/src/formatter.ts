import { FormattingOptions } from 'vscode-languageserver/node';

export class SynapseFormatter {
    format(text: string, options: FormattingOptions): string {
        const lines = text.split('\n');
        const formatted: string[] = [];
        let indentLevel = 0;
        const indent = options.insertSpaces ? ' '.repeat(options.tabSize) : '\t';
        
        for (const line of lines) {
            const trimmed = line.trim();
            
            // Decrease indent for closing braces
            if (trimmed.startsWith('}') || trimmed.startsWith(']') || trimmed.startsWith(')')) {
                indentLevel = Math.max(0, indentLevel - 1);
            }
            
            // Apply indentation
            if (trimmed) {
                formatted.push(indent.repeat(indentLevel) + trimmed);
            } else {
                formatted.push('');
            }
            
            // Increase indent for opening braces
            if (trimmed.endsWith('{') || trimmed.endsWith('[') || trimmed.endsWith('(')) {
                indentLevel++;
            }
            
            // Handle single-line blocks
            if (trimmed.includes('{') && trimmed.includes('}')) {
                // Don't change indent for single-line blocks
            }
        }
        
        return formatted.join('\n');
    }
}