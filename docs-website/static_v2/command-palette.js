// Command Palette Module for Synapse
(function() {
    'use strict';

    class CommandPalette {
        constructor() {
            this.isOpen = false;
            this.commands = [
                { name: 'Go to Playground', action: () => window.location.href = '/playground', keys: 'P' },
                { name: 'View Documentation', action: () => window.location.href = '/docs', keys: 'D' },
                { name: 'Analytics Dashboard', action: () => window.location.href = '/dashboard', keys: 'A' },
                { name: 'GitHub Repository', action: () => window.open('https://github.com/michaelcrowe11/synapse-lang'), keys: 'G' },
                { name: 'Copy Install Command', action: () => this.copyInstallCommand(), keys: 'I' },
                { name: 'Toggle Theme', action: () => this.toggleTheme(), keys: 'T' },
                { name: 'Search Documentation', action: () => this.searchDocs(), keys: 'S' },
                { name: 'Report Issue', action: () => window.open('https://github.com/michaelcrowe11/synapse-lang/issues'), keys: 'R' }
            ];
            this.init();
        }

        init() {
            // Add keyboard listener
            document.addEventListener('keydown', (e) => {
                // Ctrl/Cmd + K to open
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                    e.preventDefault();
                    this.toggle();
                }

                // Escape to close
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });

            // Add styles
            this.injectStyles();
        }

        injectStyles() {
            const style = document.createElement('style');
            style.textContent = `
                .command-palette-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.5);
                    z-index: 99999;
                    display: none;
                    animation: fadeIn 0.2s ease;
                }

                .command-palette-overlay.open {
                    display: block;
                }

                .command-palette {
                    position: fixed;
                    top: 20%;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 90%;
                    max-width: 600px;
                    background: #fff;
                    border-radius: 12px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                    animation: slideDown 0.3s ease;
                }

                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }

                @keyframes slideDown {
                    from {
                        opacity: 0;
                        transform: translateX(-50%) translateY(-20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateX(-50%) translateY(0);
                    }
                }

                .command-palette-input {
                    width: 100%;
                    padding: 20px;
                    font-size: 18px;
                    border: none;
                    border-bottom: 2px solid #f0f0f0;
                    outline: none;
                    font-family: system-ui, -apple-system, sans-serif;
                }

                .command-palette-results {
                    max-height: 400px;
                    overflow-y: auto;
                }

                .command-palette-item {
                    padding: 15px 20px;
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    transition: background 0.1s ease;
                }

                .command-palette-item:hover,
                .command-palette-item.selected {
                    background: #f5f5f5;
                }

                .command-palette-item-name {
                    font-size: 14px;
                    font-weight: 500;
                    color: #333;
                }

                .command-palette-item-key {
                    font-size: 12px;
                    padding: 2px 6px;
                    background: #e0e0e0;
                    border-radius: 4px;
                    font-weight: 600;
                    color: #666;
                }

                .command-palette-footer {
                    padding: 10px 20px;
                    background: #f9f9f9;
                    border-top: 1px solid #e0e0e0;
                    font-size: 12px;
                    color: #666;
                    text-align: center;
                }

                /* Dark mode support */
                [data-theme="dark"] .command-palette {
                    background: #1a1a1a;
                    color: #fff;
                }

                [data-theme="dark"] .command-palette-input {
                    background: #1a1a1a;
                    color: #fff;
                    border-bottom-color: #333;
                }

                [data-theme="dark"] .command-palette-item:hover,
                [data-theme="dark"] .command-palette-item.selected {
                    background: #2a2a2a;
                }

                [data-theme="dark"] .command-palette-item-name {
                    color: #fff;
                }

                [data-theme="dark"] .command-palette-item-key {
                    background: #333;
                    color: #aaa;
                }

                [data-theme="dark"] .command-palette-footer {
                    background: #111;
                    border-top-color: #333;
                    color: #888;
                }
            `;
            document.head.appendChild(style);
        }

        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }

        open() {
            if (this.isOpen) return;

            // Create overlay
            const overlay = document.createElement('div');
            overlay.className = 'command-palette-overlay';
            overlay.onclick = () => this.close();

            // Create palette
            const palette = document.createElement('div');
            palette.className = 'command-palette';
            palette.onclick = (e) => e.stopPropagation();

            // Create input
            const input = document.createElement('input');
            input.className = 'command-palette-input';
            input.type = 'text';
            input.placeholder = 'Type a command or search...';
            input.autofocus = true;

            // Create results container
            const results = document.createElement('div');
            results.className = 'command-palette-results';

            // Create footer
            const footer = document.createElement('div');
            footer.className = 'command-palette-footer';
            footer.innerHTML = 'Press <kbd>↑</kbd> <kbd>↓</kbd> to navigate, <kbd>Enter</kbd> to select, <kbd>Esc</kbd> to close';

            // Populate results
            this.renderCommands(results, this.commands);

            // Add input listener
            let selectedIndex = 0;
            input.addEventListener('input', (e) => {
                const query = e.target.value.toLowerCase();
                const filtered = this.commands.filter(cmd =>
                    cmd.name.toLowerCase().includes(query)
                );
                this.renderCommands(results, filtered);
                selectedIndex = 0;
                this.updateSelection(results, selectedIndex);
            });

            // Add keyboard navigation
            input.addEventListener('keydown', (e) => {
                const items = results.querySelectorAll('.command-palette-item');

                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                    this.updateSelection(results, selectedIndex);
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    selectedIndex = Math.max(selectedIndex - 1, 0);
                    this.updateSelection(results, selectedIndex);
                } else if (e.key === 'Enter') {
                    e.preventDefault();
                    const selected = items[selectedIndex];
                    if (selected) {
                        const index = parseInt(selected.dataset.index);
                        this.executeCommand(this.commands[index]);
                    }
                }
            });

            // Assemble palette
            palette.appendChild(input);
            palette.appendChild(results);
            palette.appendChild(footer);
            overlay.appendChild(palette);

            // Add to DOM
            document.body.appendChild(overlay);

            // Show with animation
            setTimeout(() => {
                overlay.classList.add('open');
                input.focus();
            }, 10);

            this.isOpen = true;
            this.currentOverlay = overlay;
        }

        close() {
            if (!this.isOpen || !this.currentOverlay) return;

            this.currentOverlay.classList.remove('open');
            setTimeout(() => {
                if (this.currentOverlay && this.currentOverlay.parentNode) {
                    this.currentOverlay.parentNode.removeChild(this.currentOverlay);
                }
                this.currentOverlay = null;
            }, 200);

            this.isOpen = false;
        }

        renderCommands(container, commands) {
            container.innerHTML = '';
            commands.forEach((cmd, index) => {
                const item = document.createElement('div');
                item.className = 'command-palette-item';
                item.dataset.index = this.commands.indexOf(cmd);
                item.innerHTML = `
                    <span class="command-palette-item-name">${cmd.name}</span>
                    <span class="command-palette-item-key">${cmd.keys}</span>
                `;
                item.onclick = () => this.executeCommand(cmd);
                container.appendChild(item);
            });

            // Select first item by default
            if (container.firstChild) {
                container.firstChild.classList.add('selected');
            }
        }

        updateSelection(container, index) {
            const items = container.querySelectorAll('.command-palette-item');
            items.forEach((item, i) => {
                if (i === index) {
                    item.classList.add('selected');
                    item.scrollIntoView({ block: 'nearest' });
                } else {
                    item.classList.remove('selected');
                }
            });
        }

        executeCommand(command) {
            this.close();
            setTimeout(() => {
                command.action();
            }, 100);
        }

        copyInstallCommand() {
            const commands = [
                'pip install synapse_lang',
                'npm install synapse-lang-core',
                'docker pull michaelcrowe11/synapse-lang'
            ];
            const command = commands[Math.floor(Math.random() * commands.length)];
            navigator.clipboard.writeText(command).then(() => {
                this.showNotification(`Copied: ${command}`);
            });
        }

        toggleTheme() {
            const currentTheme = document.body.dataset.theme || 'light';
            const newTheme = currentTheme === 'light' ? 'dark' : 'light';
            document.body.dataset.theme = newTheme;
            localStorage.setItem('theme', newTheme);
            this.showNotification(`Theme: ${newTheme}`);
        }

        searchDocs() {
            const query = prompt('Search documentation:');
            if (query) {
                window.location.href = `/docs?search=${encodeURIComponent(query)}`;
            }
        }

        showNotification(message) {
            const notification = document.createElement('div');
            notification.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: #5B47E0;
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                z-index: 100000;
                animation: slideUp 0.3s ease;
            `;
            notification.textContent = message;
            document.body.appendChild(notification);

            setTimeout(() => {
                notification.style.animation = 'slideDown 0.3s ease';
                setTimeout(() => {
                    document.body.removeChild(notification);
                }, 300);
            }, 2000);
        }
    }

    // Auto-initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            window.commandPalette = new CommandPalette();
        });
    } else {
        window.commandPalette = new CommandPalette();
    }
})();