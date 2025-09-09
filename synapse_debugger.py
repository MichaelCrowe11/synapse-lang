"""
Synapse Language - Advanced Debugger and Profiler
Interactive debugging, profiling, and performance analysis tools
"""

import sys
import time
import traceback
import inspect
import cProfile
import pstats
import io
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import threading
import psutil
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
import ast

console = Console()

@dataclass
class Breakpoint:
    """Represents a breakpoint in the code"""
    file: str
    line: int
    condition: Optional[str] = None
    hit_count: int = 0
    enabled: bool = True
    temporary: bool = False

@dataclass
class WatchVariable:
    """Variable to watch during execution"""
    name: str
    expression: str
    value: Any = None
    history: List[Any] = field(default_factory=list)
    
@dataclass
class StackFrame:
    """Represents a stack frame"""
    function: str
    file: str
    line: int
    locals: Dict[str, Any]
    globals: Dict[str, Any]

class SynapseDebugger:
    """Advanced debugger for Synapse Language"""
    
    def __init__(self, interpreter=None):
        self.interpreter = interpreter
        self.breakpoints: Dict[Tuple[str, int], Breakpoint] = {}
        self.watch_vars: List[WatchVariable] = []
        self.call_stack: List[StackFrame] = []
        self.execution_history: deque = deque(maxlen=1000)
        self.current_frame: Optional[StackFrame] = None
        self.stepping = False
        self.step_over = False
        self.console = Console()
        self.profiler = None
        
    def set_breakpoint(self, file: str, line: int, condition: Optional[str] = None):
        """Set a breakpoint at specified location"""
        bp = Breakpoint(file, line, condition)
        self.breakpoints[(file, line)] = bp
        self.console.print(f"[green]Breakpoint set at {file}:{line}[/green]")
        
    def remove_breakpoint(self, file: str, line: int):
        """Remove a breakpoint"""
        if (file, line) in self.breakpoints:
            del self.breakpoints[(file, line)]
            self.console.print(f"[red]Breakpoint removed from {file}:{line}[/red]")
            
    def add_watch(self, expression: str):
        """Add a watch expression"""
        watch = WatchVariable(name=expression.split('=')[0].strip() if '=' in expression else expression,
                            expression=expression)
        self.watch_vars.append(watch)
        self.console.print(f"[cyan]Watch added: {expression}[/cyan]")
        
    def should_break(self, file: str, line: int, frame: StackFrame) -> bool:
        """Check if execution should break at current location"""
        if self.stepping:
            return True
            
        if (file, line) in self.breakpoints:
            bp = self.breakpoints[(file, line)]
            if bp.enabled:
                bp.hit_count += 1
                
                # Check condition if specified
                if bp.condition:
                    try:
                        result = eval(bp.condition, frame.globals, frame.locals)
                        if not result:
                            return False
                    except:
                        self.console.print(f"[red]Invalid breakpoint condition: {bp.condition}[/red]")
                        return False
                
                # Remove temporary breakpoint
                if bp.temporary:
                    del self.breakpoints[(file, line)]
                    
                return True
        
        return False
    
    def update_watches(self, frame: StackFrame):
        """Update watch variable values"""
        for watch in self.watch_vars:
            try:
                value = eval(watch.expression, frame.globals, frame.locals)
                watch.value = value
                watch.history.append(value)
            except:
                watch.value = "<Error evaluating expression>"
    
    def display_debug_info(self):
        """Display comprehensive debug information"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=10)
        )
        
        # Header
        header = Panel("[bold cyan]Synapse Debugger[/bold cyan]", style="cyan")
        layout["header"].update(header)
        
        # Main area split
        layout["main"].split_row(
            Layout(name="code", ratio=2),
            Layout(name="info", ratio=1)
        )
        
        # Code display
        if self.current_frame:
            code_display = self._format_code_context(
                self.current_frame.file,
                self.current_frame.line
            )
            layout["code"].update(Panel(code_display, title="Code", border_style="green"))
        
        # Info panel split
        layout["info"].split_column(
            Layout(name="stack"),
            Layout(name="watches"),
            Layout(name="locals")
        )
        
        # Stack trace
        stack_table = self._format_stack_trace()
        layout["stack"].update(Panel(stack_table, title="Call Stack", border_style="blue"))
        
        # Watch variables
        watch_table = self._format_watches()
        layout["watches"].update(Panel(watch_table, title="Watches", border_style="yellow"))
        
        # Local variables
        if self.current_frame:
            locals_table = self._format_locals(self.current_frame.locals)
            layout["locals"].update(Panel(locals_table, title="Local Variables", border_style="magenta"))
        
        # Footer with commands
        footer = Panel(
            "[bold]Commands:[/bold] (s)tep | (n)ext | (c)ontinue | (l)ist | (p)rint <expr> | (w)atch <expr> | (b)reak <line> | (q)uit",
            style="dim"
        )
        layout["footer"].update(footer)
        
        self.console.print(layout)
    
    def _format_code_context(self, file: str, line: int, context: int = 5) -> str:
        """Format code with context around current line"""
        try:
            with open(file, 'r') as f:
                lines = f.readlines()
            
            start = max(0, line - context - 1)
            end = min(len(lines), line + context)
            
            formatted = []
            for i in range(start, end):
                line_num = i + 1
                is_current = line_num == line
                has_breakpoint = (file, line_num) in self.breakpoints
                
                prefix = ""
                if is_current:
                    prefix = "→ "
                elif has_breakpoint:
                    prefix = "● "
                else:
                    prefix = "  "
                
                line_text = f"{prefix}{line_num:4d} | {lines[i].rstrip()}"
                
                if is_current:
                    formatted.append(f"[bold yellow]{line_text}[/bold yellow]")
                elif has_breakpoint:
                    formatted.append(f"[red]{line_text}[/red]")
                else:
                    formatted.append(line_text)
            
            return "\n".join(formatted)
        except:
            return f"Unable to read file: {file}"
    
    def _format_stack_trace(self) -> Table:
        """Format call stack as a table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Level", style="cyan", width=6)
        table.add_column("Function", style="green")
        table.add_column("Location", style="yellow")
        
        for i, frame in enumerate(reversed(self.call_stack)):
            table.add_row(
                str(i),
                frame.function,
                f"{frame.file}:{frame.line}"
            )
        
        return table
    
    def _format_watches(self) -> Table:
        """Format watch variables as a table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Expression", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Type", style="yellow")
        
        for watch in self.watch_vars:
            value_str = str(watch.value)[:50]  # Truncate long values
            type_str = type(watch.value).__name__ if watch.value is not None else "None"
            table.add_row(watch.expression, value_str, type_str)
        
        return table
    
    def _format_locals(self, locals_dict: Dict[str, Any]) -> Table:
        """Format local variables as a table"""
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Variable", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Type", style="yellow")
        
        for name, value in locals_dict.items():
            if not name.startswith('__'):  # Skip special variables
                value_str = str(value)[:50]  # Truncate long values
                type_str = type(value).__name__
                table.add_row(name, value_str, type_str)
        
        return table
    
    def interactive_debug(self):
        """Enter interactive debugging mode"""
        self.display_debug_info()
        
        while True:
            try:
                command = self.console.input("[bold cyan]debug>[/bold cyan] ").strip()
                
                if not command:
                    continue
                
                parts = command.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""
                
                if cmd in ('s', 'step'):
                    self.stepping = True
                    break
                elif cmd in ('n', 'next'):
                    self.step_over = True
                    break
                elif cmd in ('c', 'continue'):
                    self.stepping = False
                    break
                elif cmd in ('l', 'list'):
                    self.display_debug_info()
                elif cmd in ('p', 'print'):
                    self._print_expression(args)
                elif cmd in ('w', 'watch'):
                    self.add_watch(args)
                elif cmd in ('b', 'break'):
                    self._handle_breakpoint_command(args)
                elif cmd in ('q', 'quit'):
                    sys.exit(0)
                elif cmd == 'help':
                    self._show_help()
                else:
                    self.console.print(f"[red]Unknown command: {cmd}[/red]")
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'quit' to exit debugger[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def _print_expression(self, expr: str):
        """Evaluate and print an expression"""
        if not expr:
            self.console.print("[red]Usage: print <expression>[/red]")
            return
        
        try:
            if self.current_frame:
                result = eval(expr, self.current_frame.globals, self.current_frame.locals)
                self.console.print(f"{expr} = {result}")
            else:
                self.console.print("[red]No active frame[/red]")
        except Exception as e:
            self.console.print(f"[red]Error evaluating expression: {e}[/red]")
    
    def _handle_breakpoint_command(self, args: str):
        """Handle breakpoint commands"""
        if not args:
            # List all breakpoints
            if self.breakpoints:
                table = Table(title="Breakpoints")
                table.add_column("Location", style="cyan")
                table.add_column("Condition", style="yellow")
                table.add_column("Hits", style="green")
                
                for (file, line), bp in self.breakpoints.items():
                    table.add_row(
                        f"{file}:{line}",
                        bp.condition or "",
                        str(bp.hit_count)
                    )
                
                self.console.print(table)
            else:
                self.console.print("[yellow]No breakpoints set[/yellow]")
        else:
            # Set a breakpoint
            try:
                line = int(args)
                if self.current_frame:
                    self.set_breakpoint(self.current_frame.file, line)
                else:
                    self.console.print("[red]No active file[/red]")
            except ValueError:
                self.console.print("[red]Invalid line number[/red]")
    
    def _show_help(self):
        """Show help information"""
        help_text = """
[bold cyan]Debugger Commands:[/bold cyan]

[yellow]Execution Control:[/yellow]
  s, step     - Step into next line
  n, next     - Step over next line
  c, continue - Continue execution
  q, quit     - Quit debugger

[yellow]Inspection:[/yellow]
  l, list     - Show current code context
  p <expr>    - Print expression value
  w <expr>    - Add watch expression

[yellow]Breakpoints:[/yellow]
  b           - List all breakpoints
  b <line>    - Set breakpoint at line
  
[yellow]Help:[/yellow]
  help        - Show this help message
"""
        self.console.print(Panel(help_text, title="Help", border_style="green"))


class SynapseProfiler:
    """Performance profiler for Synapse Language"""
    
    def __init__(self):
        self.profiler = cProfile.Profile()
        self.stats = None
        self.memory_snapshots = []
        self.execution_times = defaultdict(list)
        self.console = Console()
        
    def start_profiling(self):
        """Start profiling execution"""
        self.profiler.enable()
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
    def stop_profiling(self):
        """Stop profiling and collect statistics"""
        self.profiler.disable()
        self.end_time = time.time()
        self.end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Create stats object
        s = io.StringIO()
        self.stats = pstats.Stats(self.profiler, stream=s)
        
    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile a specific function"""
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            result = func(*args, **kwargs)
            
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024
            
            self.execution_times[func.__name__].append({
                'time': end_time - start_time,
                'memory': end_memory - start_memory
            })
            
            return result
        
        return wrapper
    
    def display_profile_report(self, top_n: int = 20):
        """Display comprehensive profiling report"""
        if not self.stats:
            self.console.print("[red]No profiling data available[/red]")
            return
        
        # Time statistics
        self.console.print("\n[bold cyan]═══ Performance Profile Report ═══[/bold cyan]\n")
        
        # Overall statistics
        total_time = self.end_time - self.start_time
        memory_delta = self.end_memory - self.start_memory
        
        stats_table = Table(title="Overall Statistics", show_header=False)
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("Total Execution Time", f"{total_time:.4f} seconds")
        stats_table.add_row("Memory Usage Delta", f"{memory_delta:+.2f} MB")
        stats_table.add_row("Peak Memory", f"{self.end_memory:.2f} MB")
        
        self.console.print(stats_table)
        
        # Function statistics
        self.console.print("\n[bold]Top Functions by Time:[/bold]")
        func_table = Table(show_header=True, header_style="bold magenta")
        func_table.add_column("Function", style="cyan")
        func_table.add_column("Calls", style="yellow")
        func_table.add_column("Total Time", style="green")
        func_table.add_column("Per Call", style="green")
        func_table.add_column("Cumulative", style="blue")
        
        # Sort by cumulative time
        self.stats.sort_stats('cumulative')
        
        # Get top functions
        stats_str = io.StringIO()
        self.stats.stream = stats_str
        self.stats.print_stats(top_n)
        
        # Parse stats output
        lines = stats_str.getvalue().split('\n')
        for line in lines:
            if line and not line.startswith(' ') and '{' in line:
                parts = line.split()
                if len(parts) >= 6:
                    func_name = parts[-1].split('/')[-1]  # Get just the function name
                    func_table.add_row(
                        func_name[:50],  # Truncate long names
                        parts[0],
                        f"{float(parts[2]):.4f}",
                        f"{float(parts[3]):.6f}",
                        f"{float(parts[4]):.4f}"
                    )
        
        self.console.print(func_table)
        
        # Memory hotspots
        if self.execution_times:
            self.console.print("\n[bold]Memory Hotspots:[/bold]")
            memory_table = Table(show_header=True, header_style="bold magenta")
            memory_table.add_column("Function", style="cyan")
            memory_table.add_column("Avg Memory Delta", style="yellow")
            memory_table.add_column("Max Memory Delta", style="red")
            memory_table.add_column("Calls", style="green")
            
            for func_name, measurements in self.execution_times.items():
                memory_deltas = [m['memory'] for m in measurements]
                if memory_deltas:
                    memory_table.add_row(
                        func_name,
                        f"{np.mean(memory_deltas):.2f} MB",
                        f"{np.max(memory_deltas):.2f} MB",
                        str(len(measurements))
                    )
            
            self.console.print(memory_table)
        
        # Bottleneck analysis
        self.console.print("\n[bold]Bottleneck Analysis:[/bold]")
        self._analyze_bottlenecks()
        
        # Optimization suggestions
        self.console.print("\n[bold]Optimization Suggestions:[/bold]")
        self._suggest_optimizations()
    
    def _analyze_bottlenecks(self):
        """Analyze and identify performance bottlenecks"""
        bottlenecks = []
        
        # Analyze function times
        if self.execution_times:
            for func_name, measurements in self.execution_times.items():
                times = [m['time'] for m in measurements]
                if times and np.mean(times) > 0.1:  # Functions taking > 100ms
                    bottlenecks.append({
                        'type': 'Slow Function',
                        'name': func_name,
                        'avg_time': np.mean(times),
                        'suggestion': 'Consider optimization or caching'
                    })
        
        # Display bottlenecks
        if bottlenecks:
            for b in bottlenecks:
                self.console.print(f"  • [yellow]{b['type']}[/yellow]: {b['name']} "
                                 f"(avg: {b['avg_time']:.3f}s)")
                self.console.print(f"    [dim]{b['suggestion']}[/dim]")
        else:
            self.console.print("  [green]No significant bottlenecks detected[/green]")
    
    def _suggest_optimizations(self):
        """Provide optimization suggestions based on profiling data"""
        suggestions = []
        
        # Check for high memory usage
        if hasattr(self, 'end_memory') and self.end_memory > 1000:  # > 1GB
            suggestions.append("• High memory usage detected. Consider using generators or chunking large datasets.")
        
        # Check for repeated computations
        if self.execution_times:
            for func_name, measurements in self.execution_times.items():
                if len(measurements) > 100:
                    suggestions.append(f"• Function '{func_name}' called {len(measurements)} times. Consider memoization.")
        
        # Display suggestions
        if suggestions:
            for suggestion in suggestions:
                self.console.print(f"  {suggestion}")
        else:
            self.console.print("  [green]Performance looks good! No immediate optimizations needed.[/green]")
    
    def export_profile_data(self, filename: str = "profile_report.html"):
        """Export profiling data to HTML report"""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Synapse Language - Profiling Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #1a1a2e; color: #eee; }}
        h1 {{ color: #9333EA; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #444; padding: 8px; text-align: left; }}
        th {{ background: #2d2d44; color: #C084FC; }}
        .metric {{ color: #F0ABFC; }}
    </style>
</head>
<body>
    <h1>Synapse Language - Performance Profile Report</h1>
    <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2>Overall Statistics</h2>
    <table>
        <tr><td class="metric">Total Time</td><td>{self.end_time - self.start_time:.4f} seconds</td></tr>
        <tr><td class="metric">Memory Delta</td><td>{self.end_memory - self.start_memory:+.2f} MB</td></tr>
        <tr><td class="metric">Peak Memory</td><td>{self.end_memory:.2f} MB</td></tr>
    </table>
    
    <!-- Add more detailed statistics here -->
</body>
</html>
"""
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        self.console.print(f"[green]Profile report exported to {filename}[/green]")


# Example usage
if __name__ == "__main__":
    # Example debugging session
    debugger = SynapseDebugger()
    debugger.set_breakpoint("example.syn", 10)
    debugger.add_watch("temperature_rise")
    
    # Example profiling
    profiler = SynapseProfiler()
    
    @profiler.profile_function
    def example_function():
        time.sleep(0.1)
        return sum(range(1000000))
    
    profiler.start_profiling()
    result = example_function()
    profiler.stop_profiling()
    profiler.display_profile_report()