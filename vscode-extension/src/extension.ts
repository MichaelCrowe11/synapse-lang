import * as vscode from 'vscode';
import * as path from 'path';
import { LanguageClient, LanguageClientOptions, ServerOptions, TransportKind } from 'vscode-languageclient/node';
import { SynapseDebugAdapterFactory } from './debugAdapter';
import { SynapseTestProvider } from './testProvider';
import { SynapseRefactoringProvider } from './refactoring';
import { SynapseDocumentationGenerator } from './docGenerator';
import { SynapseCloudIntegration } from './cloudIntegration';

let client: LanguageClient;

export function activate(context: vscode.ExtensionContext) {
    console.log('Synapse Language Support v0.3.0 is now active!');
    
    // Initialize status bar
    const statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBar.text = '$(beaker) Synapse 0.3.0';
    statusBar.tooltip = 'Synapse Language Support Active';
    statusBar.command = 'synapse.showInfo';
    statusBar.show();
    context.subscriptions.push(statusBar);
    
    // Register commands
    registerCommands(context);
    
    // Start language server
    startLanguageServer(context);
    
    // Initialize debug adapter
    const debugAdapterFactory = new SynapseDebugAdapterFactory();
    context.subscriptions.push(
        vscode.debug.registerDebugAdapterDescriptorFactory('synapse', debugAdapterFactory)
    );
    
    // Initialize test provider
    const testProvider = new SynapseTestProvider();
    context.subscriptions.push(
        vscode.tests.createTestController('synapseTests', 'Synapse Tests')
    );
    
    // Initialize refactoring provider
    const refactoringProvider = new SynapseRefactoringProvider();
    context.subscriptions.push(
        vscode.languages.registerCodeActionsProvider('synapse', refactoringProvider)
    );
    
    // Initialize documentation generator
    const docGenerator = new SynapseDocumentationGenerator();
    context.subscriptions.push(
        vscode.commands.registerCommand('synapse.generateDocs', () => docGenerator.generate())
    );
    
    // Initialize cloud integration
    const cloudIntegration = new SynapseCloudIntegration(context);
    cloudIntegration.initialize();
}

function registerCommands(context: vscode.ExtensionContext) {
    // Show info command
    context.subscriptions.push(
        vscode.commands.registerCommand('synapse.showInfo', () => {
            vscode.window.showInformationMessage(
                'Synapse Language Support v0.3.0 - Advanced scientific computing language',
                'Documentation',
                'Cloud Portal'
            ).then(selection => {
                if (selection === 'Documentation') {
                    vscode.env.openExternal(vscode.Uri.parse('https://github.com/MichaelCrowe11/synapse-lang'));
                } else if (selection === 'Cloud Portal') {
                    vscode.env.openExternal(vscode.Uri.parse('https://synapse-lang.com'));
                }
            });
        })
    );
    
    // Format document command
    context.subscriptions.push(
        vscode.commands.registerCommand('synapse.format', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor && editor.document.languageId === 'synapse') {
                await vscode.commands.executeCommand('editor.action.formatDocument');
            }
        })
    );
    
    // Run file command
    context.subscriptions.push(
        vscode.commands.registerCommand('synapse.run', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage('No active editor');
                return;
            }
            
            if (editor.document.languageId !== 'synapse') {
                vscode.window.showErrorMessage('Current file is not a Synapse file');
                return;
            }
            
            const terminal = vscode.window.createTerminal('Synapse');
            terminal.show();
            const config = vscode.workspace.getConfiguration('synapse');
            const pythonPath = config.get<string>('pythonPath', 'python');
            terminal.sendText(`${pythonPath} -m synapse_interpreter "${editor.document.fileName}"`);
        })
    );
    
    // Debug file command
    context.subscriptions.push(
        vscode.commands.registerCommand('synapse.debug', () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;
            
            vscode.debug.startDebugging(undefined, {
                type: 'synapse',
                name: 'Debug Synapse File',
                request: 'launch',
                program: editor.document.fileName
            });
        })
    );
    
    // Run tests command
    context.subscriptions.push(
        vscode.commands.registerCommand('synapse.runTests', () => {
            vscode.commands.executeCommand('testing.runAll');
        })
    );
    
    // Refactor command
    context.subscriptions.push(
        vscode.commands.registerCommand('synapse.refactor', () => {
            vscode.commands.executeCommand('editor.action.quickFix');
        })
    );
    
    // Cloud sync command
    context.subscriptions.push(
        vscode.commands.registerCommand('synapse.cloudSync', async () => {
            const cloudIntegration = new SynapseCloudIntegration(context);
            await cloudIntegration.sync();
        })
    );
}

function startLanguageServer(context: vscode.ExtensionContext) {
    const serverModule = context.asAbsolutePath(path.join('dist', 'server.js'));
    const debugOptions = { execArgv: ['--nolazy', '--inspect=6009'] };
    
    const serverOptions: ServerOptions = {
        run: { module: serverModule, transport: TransportKind.ipc },
        debug: {
            module: serverModule,
            transport: TransportKind.ipc,
            options: debugOptions
        }
    };
    
    const clientOptions: LanguageClientOptions = {
        documentSelector: [{ scheme: 'file', language: 'synapse' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/*.{syn,synapse}')
        },
        middleware: {
            provideCompletionItem: async (document, position, context, token, next) => {
                const result = await next(document, position, context, token);
                // Add cloud-based suggestions
                return result;
            }
        }
    };
    
    client = new LanguageClient(
        'synapseLanguageServer',
        'Synapse Language Server',
        serverOptions,
        clientOptions
    );
    
    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}