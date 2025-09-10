const vscode = require('vscode');
const { LanguageClient, TransportKind } = require('vscode-languageclient/node');
const path = require('path');

let client;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('Synapse Language Support is now active!');
    
    // Register the show info command
    let disposable = vscode.commands.registerCommand('synapse.showInfo', function () {
        vscode.window.showInformationMessage(
            'Synapse Language Support - A language for scientific reasoning and parallel thought processing. Visit https://github.com/MichaelCrowe11/synapse-lang for more information.'
        );
    });
    context.subscriptions.push(disposable);
    
    // Register format command
    let formatCommand = vscode.commands.registerCommand('synapse.format', async () => {
        const editor = vscode.window.activeTextEditor;
        if (editor && editor.document.languageId === 'synapse') {
            await vscode.commands.executeCommand('editor.action.formatDocument');
        }
    });
    context.subscriptions.push(formatCommand);
    
    // Register run command
    let runCommand = vscode.commands.registerCommand('synapse.run', () => {
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
        terminal.sendText(`python -m synapse_interpreter "${editor.document.fileName}"`);
    });
    context.subscriptions.push(runCommand);
    
    // Start the language server
    const serverModule = context.asAbsolutePath(path.join('server.js'));
    const debugOptions = { execArgv: ['--nolazy', '--inspect=6009'] };
    
    const serverOptions = {
        run: { module: serverModule, transport: TransportKind.ipc },
        debug: {
            module: serverModule,
            transport: TransportKind.ipc,
            options: debugOptions
        }
    };
    
    const clientOptions = {
        documentSelector: [{ scheme: 'file', language: 'synapse' }],
        synchronize: {
            fileEvents: vscode.workspace.createFileSystemWatcher('**/.syn', '**/.synapse')
        }
    };
    
    // Create and start the language client
    client = new LanguageClient(
        'synapseLanguageServer',
        'Synapse Language Server',
        serverOptions,
        clientOptions
    );
    
    // Start the client
    client.start();
    
    // Status bar item showing Synapse version
    const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(beaker) Synapse 0.1.0';
    statusBarItem.tooltip = 'Synapse Language Support Active';
    statusBarItem.command = 'synapse.showInfo';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

function deactivate() {
    console.log('Synapse Language Support deactivated');
    if (client) {
        return client.stop();
    }
}

module.exports = {
    activate,
    deactivate
}