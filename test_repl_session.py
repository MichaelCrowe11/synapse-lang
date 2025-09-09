#!/usr/bin/env python3
"""
Automated test of REPL functionality
Simulates an interactive session
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from synapse_interpreter_enhanced import SynapseInterpreterEnhanced

def test_repl_session():
    """Test REPL with a series of commands"""
    interpreter = SynapseInterpreterEnhanced()
    
    print("="*60)
    print("SYNAPSE LANGUAGE - REPL SESSION DEMO")
    print("="*60)
    
    # Test commands
    commands = [
        ("Basic arithmetic", "x = 42"),
        ("Variable usage", "y = x * 2"),
        ("Display result", "y"),
        
        ("Create experiment", """experiment Demo {
            setup: 100
            synthesize: "Analysis complete"
        }"""),
        
        ("Create pipeline", """pipeline DataFlow {
            stage Input {
                size: 1000
            }
            stage Output {
                processed: 2000
            }
        }"""),
        
        ("Hypothesis testing", """hypothesis H1 {
            assume: 1 > 0
            predict: "valid"
            validate: 1
        }"""),
        
        ("Show variables", "vars"),
    ]
    
    for description, command in commands:
        print(f"\n[{description}]")
        print(f"synapse> {command}")
        
        try:
            if command == "vars":
                interpreter.show_variables()
            else:
                result = interpreter.execute(command)
                if result:
                    if isinstance(result, list):
                        for r in result:
                            if r is not None:
                                interpreter.display_result(r)
                    else:
                        interpreter.display_result(result)
        except Exception as e:
            print(f"Error: {e}")
    
    print("\n" + "="*60)
    print("SESSION COMPLETE")
    print("="*60)
    
    # Verify some results
    assert interpreter.current_context.get('x') == 42
    assert interpreter.current_context.get('y') == 84
    assert 'Demo' in interpreter.experiments
    assert 'DataFlow' in interpreter.pipelines
    
    print("\nAll assertions passed!")
    return True

if __name__ == "__main__":
    success = test_repl_session()
    sys.exit(0 if success else 1)