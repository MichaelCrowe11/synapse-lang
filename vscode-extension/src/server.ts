import {
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
    Position,
    DocumentFormattingParams,
    TextEdit,
    Hover,
    MarkupContent,
    DefinitionParams,
    Location,
    ReferenceParams,
    CodeAction,
    CodeActionKind,
    CodeActionParams,
    WorkspaceEdit
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';
import { SynapseAnalyzer } from './analyzer';
import { SynapseFormatter } from './formatter';

const connection = createConnection(ProposedFeatures.all);
const documents: TextDocuments<TextDocument> = new TextDocuments(TextDocument);
const analyzer = new SynapseAnalyzer();
const formatter = new SynapseFormatter();

let hasConfigurationCapability = false;
let hasWorkspaceFolderCapability = false;
let hasDiagnosticRelatedInformationCapability = false;

connection.onInitialize((params: InitializeParams) => {
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

    const result: InitializeResult = {
        capabilities: {
            textDocumentSync: TextDocumentSyncKind.Incremental,
            completionProvider: {
                resolveProvider: true,
                triggerCharacters: ['.', ':', '(', '{', '[', ' ', '@']
            },
            hoverProvider: true,
            definitionProvider: true,
            referencesProvider: true,
            documentFormattingProvider: true,
            documentRangeFormattingProvider: true,
            codeActionProvider: {
                codeActionKinds: [
                    CodeActionKind.QuickFix,
                    CodeActionKind.Refactor,
                    CodeActionKind.RefactorExtract,
                    CodeActionKind.RefactorInline,
                    CodeActionKind.RefactorRewrite
                ]
            },
            renameProvider: {
                prepareProvider: true
            },
            documentSymbolProvider: true,
            workspaceSymbolProvider: true,
            foldingRangeProvider: true,
            semanticTokensProvider: {
                legend: {
                    tokenTypes: [
                        'namespace', 'class', 'enum', 'interface', 'struct',
                        'typeParameter', 'type', 'parameter', 'variable', 'property',
                        'enumMember', 'decorator', 'function', 'method', 'macro',
                        'keyword', 'modifier', 'comment', 'string', 'number', 'regexp', 'operator'
                    ],
                    tokenModifiers: [
                        'declaration', 'definition', 'readonly', 'static', 'deprecated',
                        'abstract', 'async', 'modification', 'documentation', 'defaultLibrary'
                    ]
                },
                full: true,
                range: true
            }
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
});

// Enhanced completion with context awareness
connection.onCompletion((params: TextDocumentPositionParams): CompletionItem[] => {
    const document = documents.get(params.textDocument.uri);
    if (!document) return [];
    
    const text = document.getText();
    const offset = document.offsetAt(params.position);
    const context = analyzer.getContextAt(text, offset);
    
    return analyzer.getCompletions(context);
});

connection.onCompletionResolve((item: CompletionItem): CompletionItem => {
    return analyzer.resolveCompletion(item);
});

// Enhanced hover with detailed documentation
connection.onHover((params: TextDocumentPositionParams): Hover | null => {
    const document = documents.get(params.textDocument.uri);
    if (!document) return null;
    
    const hover = analyzer.getHover(document, params.position);
    return hover;
});

// Go to definition
connection.onDefinition((params: DefinitionParams): Location | Location[] | null => {
    const document = documents.get(params.textDocument.uri);
    if (!document) return null;
    
    return analyzer.getDefinition(document, params.position);
});

// Find references
connection.onReferences((params: ReferenceParams): Location[] | null => {
    const document = documents.get(params.textDocument.uri);
    if (!document) return null;
    
    return analyzer.getReferences(document, params.position, params.context.includeDeclaration);
});

// Code actions (quick fixes and refactorings)
connection.onCodeAction((params: CodeActionParams): CodeAction[] => {
    const document = documents.get(params.textDocument.uri);
    if (!document) return [];
    
    const codeActions: CodeAction[] = [];
    
    // Quick fixes for diagnostics
    for (const diagnostic of params.context.diagnostics) {
        const quickFix = analyzer.getQuickFix(document, diagnostic);
        if (quickFix) {
            codeActions.push(quickFix);
        }
    }
    
    // Refactoring actions
    const refactorings = analyzer.getRefactorings(document, params.range);
    codeActions.push(...refactorings);
    
    return codeActions;
});

// Document formatting
connection.onDocumentFormatting((params: DocumentFormattingParams): TextEdit[] => {
    const document = documents.get(params.textDocument.uri);
    if (!document) return [];
    
    const formatted = formatter.format(document.getText(), params.options);
    
    return [{
        range: {
            start: { line: 0, character: 0 },
            end: document.positionAt(document.getText().length)
        },
        newText: formatted
    }];
});

// Document validation
async function validateTextDocument(textDocument: TextDocument): Promise<void> {
    const diagnostics = await analyzer.analyze(textDocument);
    connection.sendDiagnostics({ uri: textDocument.uri, diagnostics });
}

// Document change handling
documents.onDidChangeContent(change => {
    validateTextDocument(change.document);
});

documents.onDidOpen(change => {
    validateTextDocument(change.document);
});

// Listen for configuration changes
connection.onDidChangeConfiguration(change => {
    documents.all().forEach(validateTextDocument);
});

documents.listen(connection);
connection.listen();