#!/usr/bin/env python3
"""
Synapse Language - Main Runner
Execute Synapse programs from command line
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path for development
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synapse_lang import __version__, execute
from synapse_lang.synapse_interpreter import SynapseInterpreter


def run_file(filepath: str, verbose: bool = False):
    """Run a Synapse program from file."""
    path = Path(filepath)

    if not path.exists():
        print(f"Error: File '{filepath}' not found")
        return 1

    if path.suffix not in [".syn", ".synapse"]:
        print("Warning: File extension should be .syn or .synapse")

    print(f"Running Synapse program: {path.name}")
    print("-" * 50)

    try:
        with open(path, encoding="utf-8") as f:
            code = f.read()

        # Execute the code
        result = execute(code, optimized=True)

        if result is not None:
            print(f"\nResult: {result}")

        print("-" * 50)
        print("Program executed successfully!")
        return 0

    except Exception as e:
        print(f"Error: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def run_interactive():
    """Run interactive REPL."""
    print(f"Synapse Language v{__version__} - Interactive Mode")
    print("Type 'exit()' or press Ctrl+C to quit")
    print("-" * 50)

    interpreter = SynapseInterpreter()

    while True:
        try:
            # Get input
            code = input("synapse> ")

            if code.strip() in ["exit()", "quit()", "exit", "quit"]:
                break

            if not code.strip():
                continue

            # Execute
            result = interpreter.execute(code)

            if result is not None:
                print(f"=> {result}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")


def run_demo(demo_name: str = "quantum"):
    """Run a demo program."""
    demos = {
        "quantum": "examples/quantum_demo.py",
        "uncertainty": "examples/uncertainty_demo.syn",
        "parallel": "examples/parallel_demo.syn",
        "hello": "examples/hello_world.syn"
    }

    if demo_name not in demos:
        print(f"Available demos: {', '.join(demos.keys())}")
        return 1

    demo_path = Path(__file__).parent / demos[demo_name]

    if demo_path.suffix == ".py":
        # Run Python demo
        print(f"Running Python demo: {demo_name}")
        print("-" * 50)
        import subprocess
        result = subprocess.run([sys.executable, str(demo_path)])
        return result.returncode
    else:
        # Run Synapse demo
        return run_file(str(demo_path))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Synapse Language Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run a Synapse program
  python run_synapse.py program.syn

  # Interactive REPL
  python run_synapse.py -i

  # Run demo
  python run_synapse.py --demo quantum

  # Show version
  python run_synapse.py --version
        """
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Synapse program file to run (.syn or .synapse)"
    )

    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive REPL"
    )

    parser.add_argument(
        "--demo",
        choices=["quantum", "uncertainty", "parallel", "hello"],
        help="Run a demo program"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output with stack traces"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"Synapse Language v{__version__}"
    )

    args = parser.parse_args()

    # Determine what to run
    if args.demo:
        return run_demo(args.demo)
    elif args.interactive or (not args.file and not args.demo):
        return run_interactive()
    elif args.file:
        return run_file(args.file, verbose=args.verbose)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
