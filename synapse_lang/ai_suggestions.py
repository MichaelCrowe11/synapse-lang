"""AI-Powered Code Suggestions for Synapse Language
Provides intelligent code completion, error detection, and optimization suggestions
"""

import re
import ast
import json
import hashlib
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum, auto
import time
import difflib


class SuggestionType(Enum):
    """Types of AI suggestions"""
    COMPLETION = auto()
    ERROR_FIX = auto()
    OPTIMIZATION = auto()
    REFACTORING = auto()
    PATTERN = auto()
    IMPORT = auto()
    DOCUMENTATION = auto()
    TEST = auto()


class Confidence(Enum):
    """Confidence levels for suggestions"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


@dataclass
class CodeSuggestion:
    """AI-generated code suggestion"""
    id: str = field(default_factory=lambda: hashlib.sha256(str(time.time()).encode()).hexdigest()[:8])
    type: SuggestionType = SuggestionType.COMPLETION
    title: str = ""
    description: str = ""
    original_code: str = ""
    suggested_code: str = ""
    position: Tuple[int, int] = (0, 0)  # (line, column)
    confidence: Confidence = Confidence.MEDIUM
    reasoning: str = ""
    benefits: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.type.name,
            'title': self.title,
            'description': self.description,
            'original_code': self.original_code,
            'suggested_code': self.suggested_code,
            'position': self.position,
            'confidence': self.confidence.name,
            'reasoning': self.reasoning,
            'benefits': self.benefits,
            'keywords': self.keywords
        }


class SynapsePatterns:
    """Common Synapse language patterns and templates"""

    @staticmethod
    def get_patterns() -> Dict[str, Dict[str, Any]]:
        return {
            "uncertainty_propagation": {
                "trigger": ["uncertain", "±", "error"],
                "template": "let {var} = {value} ± {error}",
                "description": "Create uncertain value with error bounds",
                "example": "let measurement = 10.5 ± 0.3"
            },
            "parallel_execution": {
                "trigger": ["parallel", "async", "concurrent"],
                "template": "parallel {\n    {statements}\n}",
                "description": "Execute statements in parallel",
                "example": "parallel {\n    let a = compute_heavy()\n    let b = compute_other()\n}"
            },
            "hypothesis_testing": {
                "trigger": ["hypothesis", "test", "validate"],
                "template": "hypothesis \"{name}\" {\n    assume {assumption}\n    when {condition}\n    then {expectation}\n}",
                "description": "Define scientific hypothesis",
                "example": "hypothesis \"conservation\" {\n    assume energy_before\n    when collision_occurs\n    then energy_after == energy_before\n}"
            },
            "quantum_circuit": {
                "trigger": ["quantum", "qubit", "H", "CNOT"],
                "template": "quantum[{qubits}] {\n    {operations}\n}",
                "description": "Define quantum circuit",
                "example": "quantum[2] {\n    H(q0)\n    CNOT(q0, q1)\n    measure(q0, q1)\n}"
            },
            "matrix_operations": {
                "trigger": ["matrix", "tensor", "@", "matmul"],
                "template": "let {result} = {matrix1} @ {matrix2}",
                "description": "Matrix multiplication",
                "example": "let result = A @ B"
            },
            "error_handling": {
                "trigger": ["try", "catch", "error", "exception"],
                "template": "try {\n    {code}\n} catch {error_type} {\n    {handler}\n}",
                "description": "Error handling block",
                "example": "try {\n    let result = risky_operation()\n} catch ComputationError {\n    fallback_value\n}"
            }
        }


class CodeAnalyzer:
    """Analyzes Synapse code for patterns and issues"""

    def __init__(self):
        self.patterns = SynapsePatterns.get_patterns()
        self.syntax_rules = self._load_syntax_rules()

    def _load_syntax_rules(self) -> Dict[str, Any]:
        """Load Synapse syntax rules"""
        return {
            "variable_naming": r"^[a-z][a-z0-9_]*$",
            "function_naming": r"^[a-z][a-z0-9_]*$",
            "constant_naming": r"^[A-Z][A-Z0-9_]*$",
            "keywords": [
                "let", "def", "if", "then", "else", "for", "in", "while",
                "parallel", "quantum", "hypothesis", "assume", "when", "then",
                "measure", "uncertain", "try", "catch", "import", "export"
            ]
        }

    def analyze_code(self, code: str) -> List[CodeSuggestion]:
        """Analyze code and generate suggestions"""
        suggestions = []
        lines = code.split('\n')

        for i, line in enumerate(lines):
            # Check for completion opportunities
            suggestions.extend(self._suggest_completions(line, i))

            # Check for common patterns
            suggestions.extend(self._suggest_patterns(line, i))

            # Check for potential errors
            suggestions.extend(self._suggest_error_fixes(line, i))

            # Check for optimizations
            suggestions.extend(self._suggest_optimizations(line, i))

        return suggestions

    def _suggest_completions(self, line: str, line_num: int) -> List[CodeSuggestion]:
        """Suggest code completions"""
        suggestions = []

        # Incomplete let statement
        if line.strip().startswith("let ") and "=" not in line:
            suggestions.append(CodeSuggestion(
                type=SuggestionType.COMPLETION,
                title="Complete variable declaration",
                description="Add assignment to variable declaration",
                original_code=line,
                suggested_code=line + " = ",
                position=(line_num, len(line)),
                confidence=Confidence.HIGH,
                reasoning="Variable declaration without assignment"
            ))

        # Incomplete function definition
        if line.strip().startswith("def ") and ":" not in line:
            suggestions.append(CodeSuggestion(
                type=SuggestionType.COMPLETION,
                title="Complete function definition",
                description="Add colon to function definition",
                original_code=line,
                suggested_code=line + ":",
                position=(line_num, len(line)),
                confidence=Confidence.HIGH,
                reasoning="Function definition without colon"
            ))

        # Incomplete uncertain value
        if "±" in line and not re.search(r"\d+\.?\d*\s*±\s*\d+\.?\d*", line):
            suggestions.append(CodeSuggestion(
                type=SuggestionType.COMPLETION,
                title="Complete uncertain value",
                description="Add error value to uncertain expression",
                original_code=line,
                suggested_code=line.replace("±", "± 0.1"),
                position=(line_num, line.find("±") + 1),
                confidence=Confidence.MEDIUM,
                reasoning="Uncertain value missing error term"
            ))

        return suggestions

    def _suggest_patterns(self, line: str, line_num: int) -> List[CodeSuggestion]:
        """Suggest common patterns"""
        suggestions = []

        for pattern_name, pattern in self.patterns.items():
            for trigger in pattern["trigger"]:
                if trigger in line.lower():
                    suggestions.append(CodeSuggestion(
                        type=SuggestionType.PATTERN,
                        title=f"Apply {pattern_name} pattern",
                        description=pattern["description"],
                        original_code=line,
                        suggested_code=pattern["example"],
                        position=(line_num, 0),
                        confidence=Confidence.MEDIUM,
                        reasoning=f"Detected {trigger} keyword, suggesting {pattern_name} pattern",
                        keywords=[trigger]
                    ))

        return suggestions

    def _suggest_error_fixes(self, line: str, line_num: int) -> List[CodeSuggestion]:
        """Suggest fixes for potential errors"""
        suggestions = []

        # Missing semicolon (if required)
        if line.strip() and not line.strip().endswith((':', '{', '}')):
            if any(keyword in line for keyword in ["let", "return"]):
                # Only for statements that might need semicolons
                pass  # Synapse doesn't require semicolons

        # Incorrect variable naming
        var_match = re.search(r"let\s+([A-Z][A-Za-z0-9_]*)\s*=", line)
        if var_match:
            var_name = var_match.group(1)
            suggested_name = var_name.lower()
            suggestions.append(CodeSuggestion(
                type=SuggestionType.ERROR_FIX,
                title="Fix variable naming convention",
                description="Variables should start with lowercase",
                original_code=line,
                suggested_code=line.replace(var_name, suggested_name),
                position=(line_num, var_match.start(1)),
                confidence=Confidence.HIGH,
                reasoning="Variable names should follow camelCase convention",
                benefits=["Improves code readability", "Follows language conventions"]
            ))

        # Missing imports for quantum operations
        if any(op in line for op in ["H(", "CNOT(", "measure("]):
            if "import quantum" not in line:
                suggestions.append(CodeSuggestion(
                    type=SuggestionType.IMPORT,
                    title="Add quantum import",
                    description="Import quantum operations module",
                    original_code="",
                    suggested_code="import quantum",
                    position=(0, 0),
                    confidence=Confidence.HIGH,
                    reasoning="Quantum operations require quantum module import"
                ))

        return suggestions

    def _suggest_optimizations(self, line: str, line_num: int) -> List[CodeSuggestion]:
        """Suggest performance optimizations"""
        suggestions = []

        # Suggest parallel execution for independent operations
        if line.count("let ") > 1 and "parallel" not in line:
            suggestions.append(CodeSuggestion(
                type=SuggestionType.OPTIMIZATION,
                title="Consider parallel execution",
                description="Multiple assignments can be parallelized",
                original_code=line,
                suggested_code=f"parallel {{\n    {line}\n}}",
                position=(line_num, 0),
                confidence=Confidence.MEDIUM,
                reasoning="Independent assignments can benefit from parallelization",
                benefits=["Improved performance", "Better resource utilization"]
            ))

        # Suggest uncertainty propagation
        if re.search(r"\+\s*\-\s*\*\s*/", line) and "±" not in line:
            suggestions.append(CodeSuggestion(
                type=SuggestionType.OPTIMIZATION,
                title="Consider uncertainty propagation",
                description="Arithmetic operations may benefit from uncertainty tracking",
                original_code=line,
                suggested_code=line + "  # Consider using uncertain values",
                position=(line_num, len(line)),
                confidence=Confidence.LOW,
                reasoning="Arithmetic operations in scientific code often involve uncertainty"
            ))

        return suggestions


class SmartCompletion:
    """Smart code completion engine"""

    def __init__(self):
        self.completions = self._build_completion_database()
        self.context_history = []

    def _build_completion_database(self) -> Dict[str, List[str]]:
        """Build database of completions"""
        return {
            "let": ["let variable = value", "let result = calculation()"],
            "def": ["def function_name():", "def calculate(x, y):"],
            "if": ["if condition:", "if x > 0:"],
            "for": ["for item in collection:", "for i in range(n):"],
            "while": ["while condition:", "while x < limit:"],
            "parallel": ["parallel { statements }", "parallel { task1; task2 }"],
            "quantum": ["quantum[2] { H(q0); CNOT(q0, q1) }", "quantum[n] { circuit }"],
            "hypothesis": ["hypothesis \"name\" { assume; when; then }", "hypothesis \"test\" { }"],
            "uncertain": ["uncertain_value ± error", "10.5 ± 0.3"],
            "import": ["import module", "import quantum", "import math"],
            "measure": ["measure(qubit)", "measure(q0, q1)"],
            "H": ["H(qubit)", "H(q0)"],
            "CNOT": ["CNOT(control, target)", "CNOT(q0, q1)"]
        }

    def get_completions(self, partial_code: str, cursor_pos: int) -> List[CodeSuggestion]:
        """Get smart completions for partial code"""
        suggestions = []

        # Extract word at cursor
        word_start = cursor_pos
        while word_start > 0 and partial_code[word_start - 1].isalnum():
            word_start -= 1

        current_word = partial_code[word_start:cursor_pos]

        # Find matching completions
        for keyword, completions in self.completions.items():
            if keyword.startswith(current_word.lower()):
                for completion in completions:
                    suggestions.append(CodeSuggestion(
                        type=SuggestionType.COMPLETION,
                        title=f"Complete {keyword}",
                        description=f"Complete {keyword} statement",
                        original_code=current_word,
                        suggested_code=completion,
                        position=(0, word_start),
                        confidence=Confidence.HIGH,
                        reasoning=f"Keyword completion for {keyword}"
                    ))

        return suggestions


class AICodeAssistant:
    """Main AI assistant for Synapse code"""

    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.completion = SmartCompletion()
        self.session_history = []

    def analyze_and_suggest(self, code: str, cursor_pos: Optional[int] = None) -> List[CodeSuggestion]:
        """Analyze code and provide suggestions"""
        suggestions = []

        # Code analysis suggestions
        suggestions.extend(self.analyzer.analyze_code(code))

        # Smart completions if cursor position provided
        if cursor_pos is not None:
            suggestions.extend(self.completion.get_completions(code, cursor_pos))

        # Remove duplicates and sort by confidence
        unique_suggestions = self._deduplicate(suggestions)
        return sorted(unique_suggestions, key=lambda s: s.confidence.value, reverse=True)

    def _deduplicate(self, suggestions: List[CodeSuggestion]) -> List[CodeSuggestion]:
        """Remove duplicate suggestions"""
        seen = set()
        unique = []

        for suggestion in suggestions:
            key = (suggestion.type, suggestion.title, suggestion.suggested_code)
            if key not in seen:
                seen.add(key)
                unique.append(suggestion)

        return unique

    def get_documentation_suggestion(self, function_name: str) -> Optional[CodeSuggestion]:
        """Suggest documentation for function"""
        doc_templates = {
            "calculate": "Calculate and return the result of mathematical operation",
            "measure": "Measure quantum state and return classical result",
            "optimize": "Optimize the given function using specified algorithm",
            "parallel": "Execute operations in parallel for improved performance"
        }

        template = doc_templates.get(function_name,
                                   f"Brief description of {function_name} function")

        return CodeSuggestion(
            type=SuggestionType.DOCUMENTATION,
            title=f"Add documentation for {function_name}",
            description="Add function documentation",
            suggested_code=f'"""{template}"""',
            confidence=Confidence.MEDIUM,
            reasoning="Function lacks documentation"
        )

    def suggest_tests(self, function_code: str) -> List[CodeSuggestion]:
        """Suggest test cases for function"""
        suggestions = []

        # Extract function name
        func_match = re.search(r"def\s+(\w+)", function_code)
        if func_match:
            func_name = func_match.group(1)

            test_code = f"""
def test_{func_name}():
    # Test basic functionality
    result = {func_name}()
    assert result is not None

    # Test edge cases
    # Add specific test cases here
"""

            suggestions.append(CodeSuggestion(
                type=SuggestionType.TEST,
                title=f"Generate tests for {func_name}",
                description="Create comprehensive test suite",
                suggested_code=test_code.strip(),
                confidence=Confidence.MEDIUM,
                reasoning="Function should have corresponding tests",
                benefits=["Improves code reliability", "Enables refactoring confidence"]
            ))

        return suggestions


# Example usage and testing
if __name__ == "__main__":
    print("Synapse AI Code Suggestions")
    print("=" * 40)

    # Create AI assistant
    assistant = AICodeAssistant()

    # Test code samples
    test_codes = [
        "let X = 10",  # Naming convention issue
        "let value = 10.5 ± ",  # Incomplete uncertain value
        "def calculate(",  # Incomplete function
        "quantum[2] { H(q0) }",  # Missing import
        "let a = x + y\nlet b = x * z",  # Could be parallelized
    ]

    for i, code in enumerate(test_codes):
        print(f"\n--- Test {i+1}: {code} ---")
        suggestions = assistant.analyze_and_suggest(code)

        for suggestion in suggestions[:3]:  # Show top 3 suggestions
            print(f"• {suggestion.title}")
            print(f"  Type: {suggestion.type.name}")
            print(f"  Confidence: {suggestion.confidence.name}")
            print(f"  Suggestion: {suggestion.suggested_code}")
            print(f"  Reasoning: {suggestion.reasoning}")

    # Test smart completion
    print("\n--- Smart Completion Test ---")
    partial_code = "let result = uncertain"
    completions = assistant.completion.get_completions(partial_code, len(partial_code))

    print(f"Completions for '{partial_code}':")
    for completion in completions[:3]:
        print(f"• {completion.suggested_code}")

    # Test documentation suggestion
    print("\n--- Documentation Suggestion ---")
    doc_suggestion = assistant.get_documentation_suggestion("calculate_uncertainty")
    if doc_suggestion:
        print(f"• {doc_suggestion.title}")
        print(f"  {doc_suggestion.suggested_code}")

    # Test pattern suggestions
    print("\n--- Pattern Suggestions ---")
    pattern_code = "I need to test a hypothesis about quantum"
    pattern_suggestions = assistant.analyzer._suggest_patterns(pattern_code, 0)

    for suggestion in pattern_suggestions[:2]:
        print(f"• {suggestion.title}")
        print(f"  {suggestion.suggested_code}")

    print("\n✅ AI-powered code suggestions implemented!")