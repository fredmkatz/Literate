"""
Diagnostic system for Presentable Object Model (POM) package.

This module provides classes for tracking and reporting errors,
warnings, and other diagnostics during parsing and object construction.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Any, Dict
import weakref

class DiagnosticSeverity(Enum):
    """Severity levels for diagnostics."""
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    HINT = 'hint'

@dataclass
class SourceLocation:
    """Location in source code."""
    line: int
    column: int
    length: Optional[int] = None
    file_path: Optional[str] = None
    
    def __str__(self):
        """String representation of location."""
        loc = f"{self.file_path or 'input'}:{self.line}:{self.column}"
        if self.length:
            loc += f"-{self.column + self.length}"
        return loc

@dataclass
class Diagnostic:
    """Diagnostic message with location and severity."""
    message: str
    severity: DiagnosticSeverity
    location: Optional[SourceLocation] = None
    source: str = "pom"
    code: Optional[str] = None
    related_locations: List[SourceLocation] = field(default_factory=list)
    
    # We don't store the model element directly to avoid reference cycles
    # It will be maintained externally
    
    def __str__(self):
        """String representation of diagnostic."""
        code_str = f"[{self.code}] " if self.code else ""
        loc = f" at {self.location}" if self.location else ""
        return f"{self.severity.value.upper()}: {code_str}{self.message}{loc}"

class DiagnosticRegistry:
    """Registry that maps model elements to their diagnostics."""
    
    def __init__(self):
        """Initialize the registry."""
        self._diagnostics = []
        self._element_map = weakref.WeakKeyDictionary()
    
    def add(self, diagnostic: Diagnostic, element: Any = None):
        """
        Add a diagnostic with optional element association.
        
        Args:
            diagnostic: The diagnostic to add
            element: Optional model element to associate with
        """
        self._diagnostics.append(diagnostic)
        
        if element is not None:
            if element not in self._element_map:
                self._element_map[element] = []
            self._element_map[element].append(diagnostic)
    
    def add_error(self, message: str, location: Optional[SourceLocation] = None,
                 element: Any = None, code: Optional[str] = None):
        """
        Helper to quickly add an error diagnostic.
        
        Args:
            message: Error message
            location: Optional source location
            element: Optional model element to associate with
            code: Optional error code
            
        Returns:
            The created diagnostic
        """
        diagnostic = Diagnostic(
            message=message,
            severity=DiagnosticSeverity.ERROR,
            location=location,
            code=code
        )
        self.add(diagnostic, element)
        return diagnostic
    
    def add_warning(self, message: str, location: Optional[SourceLocation] = None,
                   element: Any = None, code: Optional[str] = None):
        """
        Helper to quickly add a warning diagnostic.
        
        Args:
            message: Warning message
            location: Optional source location
            element: Optional model element to associate with
            code: Optional warning code
            
        Returns:
            The created diagnostic
        """
        diagnostic = Diagnostic(
            message=message,
            severity=DiagnosticSeverity.WARNING,
            location=location,
            code=code
        )
        self.add(diagnostic, element)
        return diagnostic
    
    def add_info(self, message: str, location: Optional[SourceLocation] = None,
                element: Any = None, code: Optional[str] = None):
        """
        Helper to quickly add an info diagnostic.
        
        Args:
            message: Info message
            location: Optional source location
            element: Optional model element to associate with
            code: Optional info code
            
        Returns:
            The created diagnostic
        """
        diagnostic = Diagnostic(
            message=message,
            severity=DiagnosticSeverity.INFO,
            location=location,
            code=code
        )
        self.add(diagnostic, element)
        return diagnostic
    
    def add_hint(self, message: str, location: Optional[SourceLocation] = None,
                element: Any = None, code: Optional[str] = None):
        """
        Helper to quickly add a hint diagnostic.
        
        Args:
            message: Hint message
            location: Optional source location
            element: Optional model element to associate with
            code: Optional hint code
            
        Returns:
            The created diagnostic
        """
        diagnostic = Diagnostic(
            message=message,
            severity=DiagnosticSeverity.HINT,
            location=location,
            code=code
        )
        self.add(diagnostic, element)
        return diagnostic
    
    def has_errors(self) -> bool:
        """
        Check if the registry contains any errors.
        
        Returns:
            True if there are any error-severity diagnostics
        """
        return any(d.severity == DiagnosticSeverity.ERROR 
                  for d in self._diagnostics)
    
    def get_all(self) -> List[Diagnostic]:
        """
        Get all diagnostics.
        
        Returns:
            List of all diagnostics
        """
        return self._diagnostics
    
    def get_for_element(self, element: Any) -> List[Diagnostic]:
        """
        Get all diagnostics for a specific model element.
        
        Args:
            element: Model element to get diagnostics for
            
        Returns:
            List of diagnostics for the element
        """
        return self._element_map.get(element, [])
    
    def get_for_location(self, line: int, 
                        column: Optional[int] = None) -> List[Diagnostic]:
        """
        Get all diagnostics for a specific source location.
        
        Args:
            line: Line number
            column: Optional column number
            
        Returns:
            List of diagnostics for the location
        """
        return [d for d in self._diagnostics 
                if d.location and d.location.line == line and
                (column is None or d.location.column == column)]
    
    def get_by_severity(self, severity: DiagnosticSeverity) -> List[Diagnostic]:
        """
        Get all diagnostics with a specific severity.
        
        Args:
            severity: Severity level to filter by
            
        Returns:
            List of diagnostics with matching severity
        """
        return [d for d in self._diagnostics if d.severity == severity]
    
    def get_errors(self) -> List[Diagnostic]:
        """
        Get all error diagnostics.
        
        Returns:
            List of error diagnostics
        """
        return self.get_by_severity(DiagnosticSeverity.ERROR)
    
    def get_warnings(self) -> List[Diagnostic]:
        """
        Get all warning diagnostics.
        
        Returns:
            List of warning diagnostics
        """
        return self.get_by_severity(DiagnosticSeverity.WARNING)
    
    def clear(self):
        """Clear all diagnostics."""
        self._diagnostics.clear()
        self._element_map.clear()
    
    def __str__(self):
        """String representation of all diagnostics."""
        if not self._diagnostics:
            return "No diagnostics"
        
        return "\n".join(str(d) for d in self._diagnostics)
    
    def __len__(self):
        """Number of diagnostics."""
        return len(self._diagnostics)
    
    def output_for_ide(self, format: str = "vscode") -> str:
        """
        Output diagnostics in a format suitable for IDEs.
        
        Args:
            format: Output format ('vscode', 'json', etc.)
            
        Returns:
            Formatted diagnostic output
        """
        if format == "vscode":
            import json
            problems = []
            
            for diag in self._diagnostics:
                if not diag.location:
                    continue
                    
                problem = {
                    "file": diag.location.file_path or "input.txt",
                    "line": diag.location.line,
                    "column": diag.location.column,
                    "severity": diag.severity.value,
                    "message": diag.message,
                    "code": diag.code or "POM000"
                }
                problems.append(problem)
                
            return json.dumps(problems)
        
        # Default to string representation
        return str(self)
