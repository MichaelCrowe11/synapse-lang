"""
Comprehensive error handling system for Synapse Language.

This module provides a hierarchical error system with detailed error information,
recovery mechanisms, and debugging support.
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
import traceback
import sys


class ErrorSeverity(Enum):
    """Error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Categories of errors in Synapse."""
    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    RUNTIME = "runtime"
    TYPE = "type"
    QUANTUM = "quantum"
    PARALLEL = "parallel"
    UNCERTAINTY = "uncertainty"
    SECURITY = "security"
    RESOURCE = "resource"
    IO = "io"


@dataclass
class SourceLocation:
    """Represents a location in source code."""
    filename: Optional[str] = None
    line: int = -1
    column: int = -1
    length: int = 0

    def __str__(self) -> str:
        if self.filename:
            return f"{self.filename}:{self.line}:{self.column}"
        return f"{self.line}:{self.column}"


@dataclass
class ErrorContext:
    """Additional context for error reporting."""
    variables: Dict[str, Any] = None
    call_stack: List[str] = None
    quantum_state: Optional[str] = None
    parallel_context: Optional[str] = None

    def __post_init__(self):
        if self.variables is None:
            self.variables = {}
        if self.call_stack is None:
            self.call_stack = []


class SynapseError(Exception):
    """Base exception class for all Synapse errors."""

    def __init__(
        self,
        message: str,
        location: Optional[SourceLocation] = None,
        category: ErrorCategory = ErrorCategory.RUNTIME,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        context: Optional[ErrorContext] = None,
        cause: Optional[Exception] = None,
        suggestions: Optional[List[str]] = None
    ):
        super().__init__(message)
        self.message = message
        self.location = location
        self.category = category
        self.severity = severity
        self.context = context or ErrorContext()
        self.cause = cause
        self.suggestions = suggestions or []

    def __str__(self) -> str:
        """Format error message with context."""
        parts = []

        # Add severity and category
        parts.append(f"[{self.severity.value.upper()}:{self.category.value.upper()}]")

        # Add location if available
        if self.location and self.location.line > 0:
            parts.append(f"at {self.location}")

        # Add main message
        parts.append(self.message)

        # Add suggestions if available
        if self.suggestions:
            parts.append("\nSuggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                parts.append(f"  {i}. {suggestion}")

        return " ".join(parts)

    def format_detailed(self) -> str:
        """Generate detailed error report."""
        lines = [str(self)]

        # Add context information
        if self.context.variables:
            lines.append("\nVariable context:")
            for name, value in self.context.variables.items():
                lines.append(f"  {name} = {value}")

        if self.context.call_stack:
            lines.append("\nCall stack:")
            for i, frame in enumerate(self.context.call_stack):
                lines.append(f"  {i}: {frame}")

        if self.context.quantum_state:
            lines.append(f"\nQuantum state: {self.context.quantum_state}")

        if self.context.parallel_context:
            lines.append(f"\nParallel context: {self.context.parallel_context}")

        # Add cause if available
        if self.cause:
            lines.append(f"\nCaused by: {self.cause}")

        return "\n".join(lines)


# Specific error types

class SyntaxError(SynapseError):
    """Syntax errors during parsing."""

    def __init__(self, message: str, location: Optional[SourceLocation] = None, **kwargs):
        super().__init__(
            message,
            location=location,
            category=ErrorCategory.SYNTAX,
            **kwargs
        )


class SemanticError(SynapseError):
    """Semantic analysis errors."""

    def __init__(self, message: str, location: Optional[SourceLocation] = None, **kwargs):
        super().__init__(
            message,
            location=location,
            category=ErrorCategory.SEMANTIC,
            **kwargs
        )


class TypeError(SynapseError):
    """Type system errors."""

    def __init__(self, message: str, expected_type: str = None, actual_type: str = None, **kwargs):
        if expected_type and actual_type:
            message = f"{message} (expected {expected_type}, got {actual_type})"
        super().__init__(
            message,
            category=ErrorCategory.TYPE,
            **kwargs
        )
        self.expected_type = expected_type
        self.actual_type = actual_type


class RuntimeError(SynapseError):
    """Runtime execution errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RUNTIME,
            **kwargs
        )


class QuantumError(SynapseError):
    """Quantum computing related errors."""

    def __init__(self, message: str, circuit_state: str = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.QUANTUM,
            **kwargs
        )
        if circuit_state and self.context:
            self.context.quantum_state = circuit_state


class ParallelError(SynapseError):
    """Parallel execution errors."""

    def __init__(self, message: str, thread_id: str = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.PARALLEL,
            **kwargs
        )
        if thread_id and self.context:
            self.context.parallel_context = f"Thread {thread_id}"


class UncertaintyError(SynapseError):
    """Uncertainty computation errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.UNCERTAINTY,
            **kwargs
        )


class SecurityError(SynapseError):
    """Security sandbox violations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.SECURITY,
            severity=ErrorSeverity.CRITICAL,
            **kwargs
        )


class ResourceError(SynapseError):
    """Resource exhaustion or allocation errors."""

    def __init__(self, message: str, resource_type: str = None, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RESOURCE,
            **kwargs
        )
        self.resource_type = resource_type


class IOError(SynapseError):
    """Input/Output errors."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.IO,
            **kwargs
        )


class ErrorCollector:
    """Collects and manages multiple errors during compilation/execution."""

    def __init__(self, max_errors: int = 100):
        self.errors: List[SynapseError] = []
        self.warnings: List[SynapseError] = []
        self.max_errors = max_errors

    def add_error(self, error: SynapseError):
        """Add an error to the collection."""
        if error.severity in (ErrorSeverity.ERROR, ErrorSeverity.CRITICAL):
            self.errors.append(error)
            if len(self.errors) > self.max_errors:
                raise RuntimeError(f"Too many errors (>{self.max_errors})")
        else:
            self.warnings.append(error)

    def has_errors(self) -> bool:
        """Check if any errors have been collected."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if any warnings have been collected."""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """Get summary of all errors and warnings."""
        lines = []

        if self.errors:
            lines.append(f"Errors ({len(self.errors)}):")
            for error in self.errors:
                lines.append(f"  • {error}")

        if self.warnings:
            lines.append(f"Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                lines.append(f"  • {warning}")

        return "\n".join(lines)

    def raise_if_errors(self):
        """Raise exception if any errors were collected."""
        if self.has_errors():
            if len(self.errors) == 1:
                raise self.errors[0]
            else:
                raise RuntimeError(f"Multiple errors occurred:\n{self.get_summary()}")


class ErrorRecovery:
    """Provides error recovery mechanisms."""

    @staticmethod
    def suggest_fixes(error: SynapseError) -> List[str]:
        """Generate fix suggestions for common errors."""
        suggestions = []

        if isinstance(error, SyntaxError):
            if "expected" in error.message.lower():
                suggestions.append("Check for missing punctuation or keywords")
            if "unexpected" in error.message.lower():
                suggestions.append("Remove or replace the unexpected token")

        elif isinstance(error, TypeError):
            suggestions.append("Check variable types and function signatures")
            if error.expected_type and error.actual_type:
                suggestions.append(f"Convert {error.actual_type} to {error.expected_type}")

        elif isinstance(error, QuantumError):
            suggestions.append("Verify quantum circuit construction")
            suggestions.append("Check qubit indices and gate parameters")

        elif isinstance(error, ParallelError):
            suggestions.append("Check for race conditions in parallel code")
            suggestions.append("Verify shared variable access patterns")

        return suggestions

    @staticmethod
    def attempt_recovery(error: SynapseError, context: Dict[str, Any]) -> Optional[Any]:
        """Attempt to recover from specific error types."""
        if isinstance(error, TypeError) and "division by zero" in error.message:
            # Return infinity for division by zero
            return float('inf')

        if isinstance(error, UncertaintyError) and "negative uncertainty" in error.message:
            # Use absolute value for uncertainty
            return abs(context.get('uncertainty_value', 0))

        # No recovery possible
        return None


def format_traceback(error: Exception, context: Dict[str, Any] = None) -> str:
    """Format enhanced traceback with Synapse context."""
    lines = []

    # Standard Python traceback
    lines.append("Python Traceback:")
    lines.extend(traceback.format_exception(type(error), error, error.__traceback__))

    # Add Synapse-specific context
    if isinstance(error, SynapseError):
        lines.append("\nSynapse Context:")
        lines.append(error.format_detailed())

    if context:
        lines.append("\nExecution Context:")
        for key, value in context.items():
            lines.append(f"  {key}: {value}")

    return "\n".join(lines)


def handle_error(error: Exception, context: Dict[str, Any] = None, debug: bool = False) -> str:
    """Central error handling function."""
    if isinstance(error, SynapseError):
        # Add suggestions if not already present
        if not error.suggestions:
            error.suggestions = ErrorRecovery.suggest_fixes(error)

        if debug:
            return format_traceback(error, context)
        else:
            return str(error)
    else:
        # Wrap non-Synapse errors
        wrapped = RuntimeError(
            f"Internal error: {error}",
            cause=error,
            context=ErrorContext(variables=context or {})
        )

        if debug:
            return format_traceback(wrapped, context)
        else:
            return str(wrapped)


# Export main components
__all__ = [
    # Base classes
    'SynapseError', 'ErrorSeverity', 'ErrorCategory',
    'SourceLocation', 'ErrorContext',

    # Specific error types
    'SyntaxError', 'SemanticError', 'TypeError', 'RuntimeError',
    'QuantumError', 'ParallelError', 'UncertaintyError',
    'SecurityError', 'ResourceError', 'IOError',

    # Utilities
    'ErrorCollector', 'ErrorRecovery',
    'format_traceback', 'handle_error'
]