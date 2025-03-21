### 4.2 Rule Generation (Continued)

```python
def _generate_list_value_rule(self, rule_name, field_type, metadata):
    """
    Generate a rule for a list value.
    
    Args:
        rule_name: Name of the rule
        field_type: Field type (list or similar)
        metadata: Field metadata
    """
    # Get element type
    element_type = self._get_list_element_type(field_type)
    
    # Get list format
    list_format = metadata.get('list_format', self.config.get('list_format', {
        'opener': '[',
        'closer': ']',
        'separator': ',',
        'whitespace': True
    }))
    
    # Create terminals for delimiters if needed
    opener = list_format.get('opener', '[')
    closer = list_format.get('closer', ']')
    separator = list_format.get('separator', ',')
    
    # Add whitespace if configured
    sep_with_space = f" {separator} " if list_format.get('whitespace', True) else separator
    
    # Generate element type rule if needed
    element_rule = self._get_rule_for_type(element_type)
    
    # Create the list rule
    if list_format.get('indent', False):
        # Indented list (YAML style)
        rule = f"NEWLINE INDENT ({separator} {element_rule})+ DEDENT"
        # Make sure we have these terminals
        self.terminals.add("NEWLINE")
        self.terminals.add("INDENT")
        self.terminals.add("DEDENT")
    else:
        # Standard delimited list
        if opener and closer:
            rule = f"{opener} [{element_rule} ({sep_with_space} {element_rule})*] {closer}"
        else:
            # Simple separated list
            rule = f"{element_rule} ({sep_with_space} {element_rule})*"
    
    # Add opener/closer to terminals if needed
    if opener and not opener.isalnum():
        opener_term = self._to_terminal_name(opener)
        self.rules.append(f"{rule_name}: {rule.replace(opener, opener_term)}")
        self.terminals.add(opener_term)
    elif closer and not closer.isalnum():
        closer_term = self._to_terminal_name(closer)
        self.rules.append(f"{rule_name}: {rule.replace(closer, closer_term)}")
        self.terminals.add(closer_term)
    else:
        self.rules.append(f"{rule_name}: {rule}")

def _generate_class_value_rule(self, rule_name, field_type):
    """
    Generate a rule for a class type value.
    
    Args:
        rule_name: Name of the rule
        field_type: Field type (a class)
    """
    # Get the class name
    if isinstance(field_type, str):
        # Handle forward reference as string
        class_name = field_type.strip("'")
    else:
        class_name = field_type.__name__
    
    # Reference the class rule
    class_rule = self._to_snake_case(class_name)
    self.rules.append(f"{rule_name}: {class_rule}")

def _get_rule_for_type(self, type_):
    """
    Get a rule name for a given type.
    
    Args:
        type_: A type (class, primitive, etc.)
        
    Returns:
        Rule name for that type
    """
    if self._is_primitive_type(type_):
        # Primitive type
        if type_ == str:
            return "STRING"
        elif type_ == bool:
            return "BOOLEAN"
        elif type_ in (int, float):
            return "NUMBER"
        else:
            return "value"
            
    elif self._is_class_type(type_):
        # Class type
        if isinstance(type_, str):
            # Handle forward reference as string
            class_name = type_.strip("'")
        else:
            class_name = type_.__name__
            
        return self._to_snake_case(class_name)
        
    elif self._is_list_type(type_):
        # List type - create a generic list rule
        element_type = self._get_list_element_type(type_)
        element_rule = self._get_rule_for_type(element_type)
        return f"list_{element_rule}"
        
    elif self._is_optional_type(type_):
        # Optional type - use the underlying type
        element_type = self._get_optional_element_type(type_)
        return self._get_rule_for_type(element_type)
        
    else:
        # Default
        return "value"

def _generate_field_value_rule_for_type(self, rule_name, type_, metadata):
    """
    Generate a field value rule for a given type.
    
    Args:
        rule_name: Name of the rule
        type_: The type to generate a rule for
        metadata: Field metadata
    """
    if self._is_primitive_type(type_):
        self._generate_primitive_value_rule(rule_name, type_, metadata)
    elif self._is_list_type(type_):
        self._generate_list_value_rule(rule_name, type_, metadata)
    elif self._is_class_type(type_):
        self._generate_class_value_rule(rule_name, type_)
    else:
        # Default
        self.rules.append(f"{rule_name}: value")
```

### 4.4 Type Detection Utilities

The grammar generator needs utility methods to identify different types:

```python
def _is_primitive_type(self, field_type):
    """Check if a type is a primitive type."""
    return field_type in (str, int, float, bool)

def _is_list_type(self, field_type):
    """Check if a type is a list or similar container."""
    origin = get_origin(field_type)
    return origin is list or origin is List

def _is_optional_type(self, field_type):
    """Check if a type is Optional."""
    origin = get_origin(field_type)
    return origin is Union and type(None) in get_args(field_type)

def _is_class_type(self, field_type):
    """Check if a type is a custom class type."""
    # Handle forward references in string form
    if isinstance(field_type, str):
        class_name = field_type.strip("'")
        return class_name in self.class_hierarchy
    
    # Handle actual class types
    return (isinstance(field_type, type) and 
            field_type.__name__ in self.class_hierarchy)

def _get_list_element_type(self, field_type):
    """Get the element type of a list."""
    args = get_args(field_type)
    if args:
        return args[0]
    return Any  # Default if can't determine

def _get_optional_element_type(self, field_type):
    """Get the underlying type of an Optional."""
    args = get_args(field_type)
    # Find the non-None type
    for arg in args:
        if arg is not type(None):
            return arg
    return Any  # Default if can't determine
```

### 4.5 Grammar Generation Utilities

The grammar generator needs some utility methods for naming and formatting:

```python
def _to_snake_case(self, name):
    """Convert a CamelCase name to snake_case."""
    # Handle empty or single character names
    if len(name) <= 1:
        return name.lower()
    
    # Insert underscore before capital letters and convert to lowercase
    result = name[0]
    for c in name[1:]:
        if c.isupper():
            result += '_' + c.lower()
        else:
            result += c
    
    return result.lower()

def _to_terminal_name(self, text):
    """Convert a string to a terminal name."""
    if text.isalnum():
        return text.upper()
    else:
        # Special character or token
        return {
            '#': 'HASH',
            '*': 'ASTERISK',
            '_': 'UNDERSCORE',
            '-': 'DASH',
            '(': 'LPAREN',
            ')': 'RPAREN',
            '[': 'LBRACK',
            ']': 'RBRACK',
            '{': 'LBRACE',
            '}': 'RBRACE',
            ',': 'COMMA',
            ':': 'COLON',
            '.': 'DOT'
        }.get(text, f"TOKEN_{ord(text[0])}")

def _generate_grammar_text(self):
    """Generate the complete grammar text."""
    grammar_parts = []
    
    # Add header
    grammar_parts.append("// Generated Lark grammar for Presentable Object Model")
    grammar_parts.append(f"// Generator: {self.__class__.__name__}")
    grammar_parts.append("")
    
    # Add all rules
    grammar_parts.extend(self.rules)
    grammar_parts.append("")
    
    # Add start rule if not already added
    if "start" not in self.rule_names:
        # Find the likely root class
        root_classes = [name for name, info in self.class_hierarchy.items()
                        if not info['bases']]
        if root_classes:
            start_rules = " | ".join(self._to_snake_case(c) for c in root_classes)
            grammar_parts.append(f"start: {start_rules}")
            grammar_parts.append("")
    
    # Add all terminals
    grammar_parts.append("// ===== Terminal definitions =====")
    
    # Special tokens
    for name, value in {
        'HASH': '"#"',
        'ASTERISK': '"*"',
        'UNDERSCORE': '"_"',
        'DASH': '"-"',
        'LPAREN': '"("',
        'RPAREN': '")"',
        'LBRACK': '"["',
        'RBRACK': '"]"',
        'LBRACE': '"{"',
        'RBRACE': '"}"',
        'COMMA': '","',
        'COLON': '":"',
        'DOT': '"."'
    }.items():
        if name in self.terminals:
            grammar_parts.append(f"{name}: {value}")
    
    # Field name terminals
    case_insensitive = "i" if not self.config.get('case_sensitive', False) else ""
    for terminal in sorted(self.terminals):
        if not terminal in {'HASH', 'ASTERISK', 'UNDERSCORE', 'DASH', 
                           'LPAREN', 'RPAREN', 'LBRACK', 'RBRACK', 
                           'LBRACE', 'RBRACE', 'COMMA', 'COLON', 'DOT',
                           'STRING', 'NUMBER', 'BOOLEAN'}:
            grammar_parts.append(f"{terminal}: \"{terminal.lower()}\"{case_insensitive}")
    
    # Standard value types
    grammar_parts.append("")
    grammar_parts.append("// ===== Value types =====")
    grammar_parts.append(f"STRING: {self.config.get('terminals', {}).get('string_format', '\"[^\"]*\"')}")
    grammar_parts.append(f"NUMBER: {self.config.get('terminals', {}).get('number_format', '/[0-9]+(\\.[0-9]+)?/')}")
    grammar_parts.append(f"BOOLEAN: {self.config.get('terminals', {}).get('boolean_format', '\"true\" | \"false\"')}")
    grammar_parts.append("IDENTIFIER: /[a-zA-Z][a-zA-Z0-9_]*/")
    grammar_parts.append("")
    
    # Generic value rule
    grammar_parts.append("// Generic value (fallback)")
    grammar_parts.append("value: STRING | NUMBER | BOOLEAN | IDENTIFIER")
    grammar_parts.append("")
    
    # Add whitespace handling
    grammar_parts.append("// Whitespace handling")
    grammar_parts.append("WHITESPACE: /[ \\t\\n\\r]+/")
    grammar_parts.append("COMMENT: \"//\" /[^\\n]*/ \"\\n\"")
    grammar_parts.append("%ignore WHITESPACE")
    grammar_parts.append("%ignore COMMENT")
    
    return "\n".join(grammar_parts)
```

## 5. Diagnostic System

### 5.1 Diagnostic Data Structures

```python
# pom_diagnostics.py
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Any, Dict
import weakref

class DiagnosticSeverity(Enum):
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
        loc = f" at {self.location}" if self.location else ""
        return f"{self.severity.value.upper()}{self.code or ''}: {self.message}{loc}"
```

### 5.2 Diagnostic Registry

```python
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
        """Helper to quickly add an error."""
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
        """Helper to quickly add a warning."""
        diagnostic = Diagnostic(
            message=message,
            severity=DiagnosticSeverity.WARNING,
            location=location,
            code=code
        )
        self.add(diagnostic, element)
        return diagnostic
    
    def has_errors(self) -> bool:
        """Check if the registry contains any errors."""
        return any(d.severity == DiagnosticSeverity.ERROR 
                  for d in self._diagnostics)
    
    def get_all(self) -> List[Diagnostic]:
        """Get all diagnostics."""
        return self._diagnostics
    
    def get_for_element(self, element: Any) -> List[Diagnostic]:
        """Get all diagnostics for a specific model element."""
        return self._element_map.get(element, [])
    
    def get_for_location(self, line: int, 
                        column: Optional[int] = None) -> List[Diagnostic]:
        """Get all diagnostics for a specific source location."""
        return [d for d in self._diagnostics 
                if d.location and d.location.line == line and
                (column is None or d.location.column == column)]
    
    def __str__(self):
        """String representation of all diagnostics."""
        return "\n".join(str(d) for d in self._diagnostics)
    
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
```
