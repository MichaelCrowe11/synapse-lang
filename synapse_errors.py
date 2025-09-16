"""
Synapse Language - Enhanced Error Handling
Comprehensive error reporting with line numbers and context
"""

import traceback
from dataclasses import dataclass
from enum import Enum


class ErrorType(Enum):
    """Types of errors in Synapse"""
    SYNTAX_ERROR = "Syntax Error"
    RUNTIME_ERROR = "Runtime Error"
    TYPE_ERROR = "Type Error"
    NAME_ERROR = "Name Error"
    VALUE_ERROR = "Value Error"
    PARALLEL_ERROR = "Parallel Execution Error"
    TENSOR_ERROR = "Tensor Operation Error"
    SYMBOLIC_ERROR = "Symbolic Computation Error"
    REASONING_ERROR = "Reasoning Chain Error"
    PIPELINE_ERROR = "Pipeline Error"

@dataclass
class ErrorLocation:
    """Location information for an error"""
    line: int
    column: int
    filename: str | None = None
    source_line: str | None = None

    def __str__(self):
        loc = f"line {self.line}, column {self.column}"
        if self.filename:
            loc = f"{self.filename}:{loc}"
        return loc

@dataclass
class ErrorContext:
    """Context information for debugging"""
    variables: dict
    call_stack: list[str]
    parallel_branch: str | None = None
    pipeline_stage: str | None = None

class SynapseError(Exception):
    """Base exception for Synapse language errors"""

    def __init__(self,
                 message: str,
                 error_type: ErrorType,
                 location: ErrorLocation | None = None,
                 context: ErrorContext | None = None,
                 suggestion: str | None = None):
        self.message = message
        self.error_type = error_type
        self.location = location
        self.context = context
        self.suggestion = suggestion
        super().__init__(self.format_error())

    def format_error(self) -> str:
        """Format error message with all details"""
        lines = [f"\n{self.error_type.value}: {self.message}"]

        if self.location:
            lines.append(f"  at {self.location}")
            if self.location.source_line:
                lines.append(f"\n    {self.location.source_line}")
                if self.location.column > 0:
                    lines.append("    " + " " * (self.location.column - 1) + "^")

        if self.suggestion:
            lines.append(f"\nSuggestion: {self.suggestion}")

        if self.context:
            if self.context.parallel_branch:
                lines.append(f"\nIn parallel branch: {self.context.parallel_branch}")
            if self.context.pipeline_stage:
                lines.append(f"In pipeline stage: {self.context.pipeline_stage}")
            if self.context.call_stack:
                lines.append("\nCall stack:")
                for frame in self.context.call_stack[-5:]:  # Show last 5 frames
                    lines.append(f"  - {frame}")

        return "\n".join(lines)

class SyntaxError(SynapseError):
    """Syntax error in Synapse code"""

    def __init__(self, message: str, location: ErrorLocation, suggestion: str | None = None):
        super().__init__(message, ErrorType.SYNTAX_ERROR, location, suggestion=suggestion)

class RuntimeError(SynapseError):
    """Runtime error during execution"""

    def __init__(self, message: str, location: ErrorLocation | None = None,
                 context: ErrorContext | None = None):
        super().__init__(message, ErrorType.RUNTIME_ERROR, location, context)

class TypeError(SynapseError):
    """Type mismatch error"""

    def __init__(self, message: str, expected: str, got: str,
                 location: ErrorLocation | None = None):
        suggestion = f"Expected {expected}, but got {got}"
        super().__init__(message, ErrorType.TYPE_ERROR, location, suggestion=suggestion)

class NameError(SynapseError):
    """Undefined variable or function"""

    def __init__(self, name: str, location: ErrorLocation | None = None,
                 similar_names: list[str] | None = None):
        message = f"'{name}' is not defined"
        suggestion = None
        if similar_names:
            suggestion = f"Did you mean: {', '.join(similar_names[:3])}?"
        super().__init__(message, ErrorType.NAME_ERROR, location, suggestion=suggestion)

class ParallelExecutionError(SynapseError):
    """Error in parallel branch execution"""

    def __init__(self, branch_name: str, original_error: Exception,
                 location: ErrorLocation | None = None):
        message = f"Error in parallel branch '{branch_name}': {str(original_error)}"
        context = ErrorContext(
            variables={},
            call_stack=[],
            parallel_branch=branch_name
        )
        super().__init__(message, ErrorType.PARALLEL_ERROR, location, context)

class TensorOperationError(SynapseError):
    """Error in tensor operation"""

    def __init__(self, operation: str, message: str,
                 shapes: tuple | None = None,
                 location: ErrorLocation | None = None):
        full_message = f"Tensor operation '{operation}' failed: {message}"
        suggestion = None
        if shapes:
            suggestion = f"Tensor shapes involved: {shapes}"
        super().__init__(full_message, ErrorType.TENSOR_ERROR, location, suggestion=suggestion)

class ErrorHandler:
    """Central error handling and reporting"""

    def __init__(self, source_code: str | None = None):
        self.source_code = source_code
        self.source_lines = source_code.split("\n") if source_code else []
        self.errors: list[SynapseError] = []
        self.warnings: list[str] = []

    def add_location_info(self, error: Exception, line: int, column: int) -> SynapseError:
        """Add location information to an error"""
        source_line = self.source_lines[line - 1] if line <= len(self.source_lines) else None
        location = ErrorLocation(line, column, source_line=source_line)

        if isinstance(error, SynapseError):
            error.location = location
            return error
        else:
            # Convert standard exception to SynapseError
            return RuntimeError(str(error), location)

    def handle_error(self, error: Exception, context: dict | None = None) -> None:
        """Handle and record an error"""
        if isinstance(error, SynapseError):
            self.errors.append(error)
        else:
            # Convert to SynapseError
            synapse_error = RuntimeError(str(error))
            if context:
                synapse_error.context = ErrorContext(
                    variables=context.get("variables", {}),
                    call_stack=self._extract_call_stack()
                )
            self.errors.append(synapse_error)

    def _extract_call_stack(self) -> list[str]:
        """Extract call stack from current execution"""
        stack = []
        for frame_info in traceback.extract_stack()[:-2]:  # Skip this function and caller
            stack.append(f"{frame_info.filename}:{frame_info.lineno} in {frame_info.name}")
        return stack

    def add_warning(self, message: str, line: int | None = None) -> None:
        """Add a warning message"""
        if line:
            message = f"Line {line}: {message}"
        self.warnings.append(message)

    def has_errors(self) -> bool:
        """Check if there are any errors"""
        return len(self.errors) > 0

    def get_report(self) -> str:
        """Get formatted error report"""
        lines = []

        if self.errors:
            lines.append("=" * 60)
            lines.append(f"Found {len(self.errors)} error(s):")
            lines.append("=" * 60)
            for i, error in enumerate(self.errors, 1):
                lines.append(f"\n{i}. {error}")

        if self.warnings:
            lines.append("\n" + "=" * 60)
            lines.append(f"Warnings ({len(self.warnings)}):")
            lines.append("=" * 60)
            for warning in self.warnings:
                lines.append(f"  ⚠ {warning}")

        return "\n".join(lines)

    def clear(self) -> None:
        """Clear all errors and warnings"""
        self.errors.clear()
        self.warnings.clear()

class ErrorRecovery:
    """Error recovery strategies for parser"""

    @staticmethod
    def find_similar_names(name: str, available_names: list[str], threshold: float = 0.7) -> list[str]:
        """Find similar variable/function names for suggestions"""
        from difflib import SequenceMatcher

        similar = []
        for available in available_names:
            ratio = SequenceMatcher(None, name.lower(), available.lower()).ratio()
            if ratio >= threshold:
                similar.append((available, ratio))

        # Sort by similarity
        similar.sort(key=lambda x: x[1], reverse=True)
        return [name for name, _ in similar[:3]]

    @staticmethod
    def suggest_fix(error_type: str, context: dict) -> str | None:
        """Suggest a fix for common errors"""
        suggestions = {
            "missing_semicolon": "Add a semicolon ';' at the end of the statement",
            "unclosed_brace": "Add a closing brace '}' to match the opening brace",
            "unclosed_paren": "Add a closing parenthesis ')' to match the opening one",
            "invalid_operator": "Use a valid operator (+, -, *, /, **, ==, !=, <, >, <=, >=)",
            "missing_colon": "Add a colon ':' after the condition or declaration",
        }
        return suggestions.get(error_type)

    @staticmethod
    def synchronize_tokens(tokens: list, current_index: int) -> int:
        """Find next synchronization point after error"""
        # Skip to next statement boundary
        sync_tokens = {";", "}", "\n", "parallel", "experiment", "hypothesis", "pipeline"}

        while current_index < len(tokens):
            if tokens[current_index].value in sync_tokens:
                return current_index + 1
            current_index += 1

        return current_index

def create_error_from_exception(exc: Exception, line: int = 0, column: int = 0) -> SynapseError:
    """Create a SynapseError from a standard exception"""
    location = ErrorLocation(line, column) if line > 0 else None

    if isinstance(exc, KeyError):
        return NameError(str(exc), location)
    elif isinstance(exc, ValueError):
        return SynapseError(str(exc), ErrorType.VALUE_ERROR, location)
    elif isinstance(exc, TypeError):
        return SynapseError(str(exc), ErrorType.TYPE_ERROR, location)
    else:
        return RuntimeError(str(exc), location)

# Global error handler instance
_global_error_handler = None

def get_error_handler(source_code: str | None = None) -> ErrorHandler:
    """Get or create global error handler"""
    global _global_error_handler
    if _global_error_handler is None or source_code:
        _global_error_handler = ErrorHandler(source_code)
    return _global_error_handler

def reset_error_handler():
    """Reset global error handler"""
    global _global_error_handler
    _global_error_handler = None
