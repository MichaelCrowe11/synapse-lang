#!/usr/bin/env python3
"""
Synapse Language REPL (Read-Eval-Print-Loop)
Interactive shell for scientific reasoning and parallel computation
"""

import sys
import os
import atexit
import traceback
from pathlib import Path
from typing import Optional
import time
from colorama import init, Fore, Style

# Handle readline import for cross-platform compatibility
try:
    import readline
except ImportError:
    try:
        # Windows alternative
        import pyreadline3 as readline
    except ImportError:
        # Fallback if no readline available
        readline = None

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synapse_interpreter import SynapseInterpreter, Lexer, UncertainValue

# Initialize colorama for cross-platform colored output
init(autoreset=True)

class SynapseREPL:
    def __init__(self):
        self.interpreter = SynapseInterpreter()
        self.history_file = Path.home() / '.synapse_history'
        self.multiline_buffer = []
        self.in_multiline = False
        self.block_depth = 0
        
        # Setup readline for better input handling
        self.setup_readline()
        
        # REPL configuration
        self.config = {
            'show_tokens': False,
            'show_timing': False,
            'parallel_workers': 8,
            'auto_save': True
        }
        
        # Welcome banner
        self.print_banner()
    
    def setup_readline(self):
        """Configure readline for history and tab completion"""
        if readline is None:
            # Readline not available, skip setup
            return
            
        # Enable tab completion
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.completer)
        
        # Load history if it exists
        if self.history_file.exists():
            try:
                readline and readline.read_history_file(str(self.history_file))
            except Exception:
                pass  # Ignore history file errors
        
        # Save history on exit
        def save_history():
            if readline is not None:
                try:
                    readline.write_history_file(str(self.history_file))
                except Exception:
                    pass
        atexit.register(save_history)
        
        # Set history length
        readline and readline.set_history_length(1000)
    
    def completer(self, text: str, state: int) -> Optional[str]:
        """Tab completion for variables and keywords"""
        keywords = [
            'hypothesis', 'experiment', 'parallel', 'branch', 'stream',
            'reason', 'chain', 'premise', 'derive', 'conclude',
            'uncertain', 'observe', 'propagate', 'constrain', 'evolve',
            'pipeline', 'stage', 'fork', 'path', 'merge', 'explore',
            'try', 'fallback', 'accept', 'reject', 'symbolic',
            'let', 'solve', 'prove'
        ]
        
        # Get all possible completions
        options = keywords + list(self.interpreter.variables.keys())
        
        # Filter matching options
        matches = [opt for opt in options if opt.startswith(text)]
        
        if state < len(matches):
            return matches[state]
        return None
    
    def print_banner(self):
        """Print welcome banner"""
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}       Synapse Language Interactive Shell v0.2.0")
        print(f"{Fore.CYAN}  Scientific Reasoning & Parallel Thought Processing")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.GREEN}Type 'help' for commands, 'exit' to quit")
        print(f"{Fore.GREEN}Use Ctrl+D to exit multiline mode")
        print()
    
    def print_help(self):
        """Print help information"""
        help_text = """
{title}Available Commands:{reset}
  {cmd}help{reset}          - Show this help message
  {cmd}exit/quit{reset}     - Exit the REPL
  {cmd}clear{reset}         - Clear screen
  {cmd}vars{reset}          - Show all variables
  {cmd}reset{reset}         - Reset interpreter state
  {cmd}save <file>{reset}   - Save session to file
  {cmd}load <file>{reset}   - Load and run file
  {cmd}config{reset}        - Show configuration
  {cmd}tokens on/off{reset} - Toggle token display
  {cmd}timing on/off{reset} - Toggle execution timing

{title}Language Features:{reset}
  {kw}uncertain{reset} x = 10 ± 0.5     - Uncertain values
  {kw}parallel{reset} {{ ... }}          - Parallel execution
  {kw}hypothesis{reset} H {{ ... }}      - Hypothesis testing
  {kw}experiment{reset} E {{ ... }}      - Experiment definition
  {kw}reason chain{reset} C {{ ... }}    - Reasoning chains

{title}Examples:{reset}
  > uncertain mass = 10.5 ± 0.2
  > uncertain velocity = 25.3 ± 0.5
  > parallel {{
      branch A: test_1
      branch B: test_2
    }}
        """.format(
            title=f"{Fore.YELLOW}{Style.BRIGHT}",
            cmd=f"{Fore.CYAN}",
            kw=f"{Fore.MAGENTA}",
            reset=Style.RESET_ALL
        )
        print(help_text)
    
    def is_multiline_start(self, line: str) -> bool:
        """Check if line starts a multiline block"""
        multiline_keywords = [
            'hypothesis', 'experiment', 'parallel', 'reason', 
            'pipeline', 'explore', 'symbolic', 'stream'
        ]
        return any(line.strip().startswith(kw) for kw in multiline_keywords)
    
    def count_braces(self, line: str) -> int:
        """Count brace depth change in line"""
        return line.count('{') - line.count('}')
    
    def execute_line(self, line: str):
        """Execute a single line of Synapse code"""
        # Check for REPL commands
        stripped = line.strip()
        
        if not stripped:
            return
        
        if stripped == 'help':
            self.print_help()
            return
        
        if stripped in ['exit', 'quit']:
            print(f"{Fore.YELLOW}Goodbye!")
            sys.exit(0)
        
        if stripped == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        
        if stripped == 'vars':
            self.show_variables()
            return
        
        if stripped == 'reset':
            self.interpreter = SynapseInterpreter()
            print(f"{Fore.GREEN}Interpreter reset")
            return
        
        if stripped == 'config':
            self.show_config()
            return
        
        if stripped.startswith('tokens '):
            self.toggle_tokens(stripped.split()[1])
            return
        
        if stripped.startswith('timing '):
            self.toggle_timing(stripped.split()[1])
            return
        
        if stripped.startswith('save '):
            self.save_session(stripped.split()[1])
            return
        
        if stripped.startswith('load '):
            self.load_file(stripped.split()[1])
            return
        
        # Execute Synapse code
        try:
            # Show tokens if enabled
            if self.config['show_tokens']:
                lexer = Lexer(line)
                tokens = lexer.tokenize()
                print(f"{Fore.BLUE}Tokens: {[f'{t.type.value}:{t.value}' for t in tokens]}")
            
            # Time execution if enabled
            start_time = time.time() if self.config['show_timing'] else None
            
            # Execute code
            results = self.interpreter.execute(line)
            
            # Show timing
            if self.config['show_timing']:
                elapsed = time.time() - start_time
                print(f"{Fore.BLUE}Execution time: {elapsed:.4f}s")
            
            # Display results
            for result in results:
                if result is not None:
                    if isinstance(result, UncertainValue):
                        print(f"{Fore.GREEN}→ {result}")
                    elif isinstance(result, dict):
                        self.pretty_print_dict(result)
                    else:
                        print(f"{Fore.GREEN}→ {result}")
        
        except Exception as e:
            print(f"{Fore.RED}Error: {e}")
            if os.getenv('SYNAPSE_DEBUG'):
                traceback.print_exc()
    
    def execute_multiline(self, code: str):
        """Execute multiline block of code"""
        try:
            if self.config['show_tokens']:
                lexer = Lexer(code)
                tokens = lexer.tokenize()
                print(f"{Fore.BLUE}Tokens: {len(tokens)} total")
            
            start_time = time.time() if self.config['show_timing'] else None
            
            results = self.interpreter.execute(code)
            
            if self.config['show_timing']:
                elapsed = time.time() - start_time
                print(f"{Fore.BLUE}Execution time: {elapsed:.4f}s")
            
            for result in results:
                if result is not None:
                    if isinstance(result, dict):
                        self.pretty_print_dict(result)
                    else:
                        print(f"{Fore.GREEN}→ {result}")
        
        except Exception as e:
            print(f"{Fore.RED}Error: {e}")
            if os.getenv('SYNAPSE_DEBUG'):
                traceback.print_exc()
    
    def pretty_print_dict(self, d: dict, indent: int = 0):
        """Pretty print dictionary results"""
        spaces = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                print(f"{spaces}{Fore.CYAN}{key}:")
                self.pretty_print_dict(value, indent + 1)
            else:
                print(f"{spaces}{Fore.CYAN}{key}: {Fore.GREEN}{value}")
    
    def show_variables(self):
        """Display all variables in the interpreter"""
        if not self.interpreter.variables:
            print(f"{Fore.YELLOW}No variables defined")
            return
        
        print(f"{Fore.YELLOW}Variables:")
        for name, value in self.interpreter.variables.items():
            if isinstance(value, UncertainValue):
                print(f"  {Fore.CYAN}{name}: {Fore.GREEN}{value}")
            else:
                print(f"  {Fore.CYAN}{name}: {Fore.GREEN}{value}")
    
    def show_config(self):
        """Display current configuration"""
        print(f"{Fore.YELLOW}Configuration:")
        for key, value in self.config.items():
            print(f"  {Fore.CYAN}{key}: {Fore.GREEN}{value}")
    
    def toggle_tokens(self, state: str):
        """Toggle token display"""
        self.config['show_tokens'] = state.lower() == 'on'
        print(f"{Fore.GREEN}Token display: {self.config['show_tokens']}")
    
    def toggle_timing(self, state: str):
        """Toggle timing display"""
        self.config['show_timing'] = state.lower() == 'on'
        print(f"{Fore.GREEN}Timing display: {self.config['show_timing']}")
    
    def save_session(self, filename: str):
        """Save current session variables to file"""
        try:
            with open(filename, 'w') as f:
                for name, value in self.interpreter.variables.items():
                    if isinstance(value, UncertainValue):
                        f.write(f"uncertain {name} = {value.value} ± {value.uncertainty}\n")
                    elif isinstance(value, (int, float)):
                        f.write(f"{name} = {value}\n")
                    elif isinstance(value, str):
                        f.write(f'{name} = "{value}"\n')
            print(f"{Fore.GREEN}Session saved to {filename}")
        except Exception as e:
            print(f"{Fore.RED}Error saving session: {e}")
    
    def load_file(self, filename: str):
        """Load and execute a Synapse file"""
        try:
            with open(filename, 'r') as f:
                code = f.read()
            
            print(f"{Fore.YELLOW}Loading {filename}...")
            results = self.interpreter.execute(code)
            
            for result in results:
                if result is not None:
                    print(f"{Fore.GREEN}→ {result}")
            
            print(f"{Fore.GREEN}File loaded successfully")
        except FileNotFoundError:
            print(f"{Fore.RED}File not found: {filename}")
        except Exception as e:
            print(f"{Fore.RED}Error loading file: {e}")
    
    def run(self):
        """Main REPL loop"""
        while True:
            try:
                # Get prompt
                if self.in_multiline:
                    prompt = f"{Fore.YELLOW}... "
                else:
                    prompt = f"{Fore.GREEN}synapse> "
                
                # Read input
                line = input(prompt)
                
                # Check for multiline mode
                if not self.in_multiline and self.is_multiline_start(line):
                    self.in_multiline = True
                    self.multiline_buffer = [line]
                    self.block_depth = self.count_braces(line)
                
                elif self.in_multiline:
                    if line.strip() == '' and self.block_depth == 0:
                        # Execute multiline buffer
                        code = '\n'.join(self.multiline_buffer)
                        self.execute_multiline(code)
                        self.multiline_buffer = []
                        self.in_multiline = False
                        self.block_depth = 0
                    else:
                        self.multiline_buffer.append(line)
                        self.block_depth += self.count_braces(line)
                        
                        if self.block_depth == 0:
                            # Block complete, execute
                            code = '\n'.join(self.multiline_buffer)
                            self.execute_multiline(code)
                            self.multiline_buffer = []
                            self.in_multiline = False
                
                else:
                    # Single line execution
                    self.execute_line(line)
            
            except KeyboardInterrupt:
                if self.in_multiline:
                    print(f"\n{Fore.YELLOW}Multiline input cancelled")
                    self.multiline_buffer = []
                    self.in_multiline = False
                    self.block_depth = 0
                else:
                    print(f"\n{Fore.YELLOW}Use 'exit' or Ctrl+D to quit")
            
            except EOFError:
                print(f"\n{Fore.YELLOW}Goodbye!")
                break
            
            except Exception as e:
                print(f"{Fore.RED}REPL Error: {e}")
                if os.getenv('SYNAPSE_DEBUG'):
                    traceback.print_exc()

def main():
    """Entry point for the REPL"""
    repl = SynapseREPL()
    repl.run()

if __name__ == "__main__":
    main()