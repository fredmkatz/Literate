# Presentable Model Visitor Specification (Continued)

## 6. Model Visitor (Continued)

```python
    def _get_location(self, node):
        """
        Get source location from a parse tree node.
        
        Args:
            node: Parse tree node
            
        Returns:
            SourceLocation object, or None if not available
        """
        if hasattr(node, 'meta'):
            line = getattr(node.meta, 'line', None)
            column = getattr(node.meta, 'column', None)
            if line is not None and column is not None:
                return SourceLocation(
                    line=line,
                    column=column,
                    length=len(str(node)) if hasattr(node, '__str__') else None
                )
        return None
    
    def _to_snake_case(self, name):
        """
        Convert a CamelCase name to snake_case.
        
        Args:
            name: Name to convert
            
        Returns:
            Converted name
        """
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
    
    def _to_class_name(self, snake_case_name):
        """
        Convert a snake_case name to CamelCase.
        
        Args:
            snake_case_name: Name to convert
            
        Returns:
            Converted name
        """
        # Split by underscore and capitalize each part
        parts = snake_case_name.split('_')
        return ''.join(p.capitalize() for p in parts)
```

### 6.2 Specialized Visitor Methods

The visitor includes specialized methods for handling different value types:

```python
class PomVisitor(PomVisitor):  # Continued
    
    def visit_boolean_value(self, tree):
        """
        Process boolean values with metadata-based representation.
        
        Args:
            tree: Parse tree node
            
        Returns:
            Boolean value
        """
        # Get the token text
        if not tree.children:
            return False
            
        token_text = str(tree.children[0]).lower()
        
        # Get current field metadata if available
        class_name, field_name = self._parse_value_node_name(tree.data)
        target_obj = self.context.get_object(class_name)
        
        if target_obj and hasattr(target_obj.__class__, '__dataclass_fields__'):
            field = target_obj.__class__.__dataclass_fields__.get(field_name)
            if field and field.metadata:
                metadata = field.metadata
                
                # Check for presentable_true/false values
                if 'presentable_true' in metadata and token_text == metadata['presentable_true'].lower():
                    return True
                if 'presentable_false' in metadata and token_text == metadata['presentable_false'].lower():
                    return False
        
        # Default handling
        return token_text in ('true', 'yes', '1', 't', 'y')
    
    def visit_list_value(self, tree):
        """
        Process list values by collecting child values.
        
        Args:
            tree: Parse tree node
            
        Returns:
            List of values
        """
        elements = []
        
        # Process each child that isn't a delimiter
        for child in tree.children:
            # Skip delimiters like '[', ']', ','
            if isinstance(child, Token) and child.value in ('', '[', ']', ','):
                continue
                
            # Process the child value
            value = self.visit(child)
            if value is not None:  # Skip None values
                elements.append(value)
        
        return elements
    
    def visit_camel_case_value(self, tree):
        """
        Process camel case values from multiple identifiers.
        
        Args:
            tree: Parse tree node
            
        Returns:
            CamelCase string
        """
        # Collect identifier tokens
        identifiers = []
        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                identifiers.append(child.value)
            elif isinstance(child, Tree):
                # Recursively visit sub-trees
                result = self.visit(child)
                if isinstance(result, str):
                    identifiers.append(result)
        
        # Now combine into camelCase
        return self._combine_to_camel_case(identifiers, upper_first=False)
    
    def visit_upper_camel_value(self, tree):
        """
        Process upper camel case values from multiple identifiers.
        
        Args:
            tree: Parse tree node
            
        Returns:
            UpperCamelCase string
        """
        # Similar to camel_case but with uppercase first letter
        identifiers = []
        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                identifiers.append(child.value)
            elif isinstance(child, Tree):
                result = self.visit(child)
                if isinstance(result, str):
                    identifiers.append(result)
        
        return self._combine_to_camel_case(identifiers, upper_first=True)
    
    def visit_lower_camel_value(self, tree):
        """
        Process lower camel case values from multiple identifiers.
        
        Args:
            tree: Parse tree node
            
        Returns:
            lowerCamelCase string
        """
        # Same as camel_case_value
        return self.visit_camel_case_value(tree)
    
    def _combine_to_camel_case(self, identifiers, upper_first=False):
        """
        Combine identifiers into a camel case string.
        
        Args:
            identifiers: List of identifier strings
            upper_first: Whether to capitalize the first part
            
        Returns:
            Camel case string
        """
        if not identifiers:
            return ""
            
        # Process the first part
        if upper_first:
            result = identifiers[0].capitalize()
        else:
            result = identifiers[0].lower()
            
        # Capitalize the rest
        for ident in identifiers[1:]:
            result += ident.capitalize()
            
        return result
```

## 7. Complete System Integration

### 7.1 Parser Integration

The final step is to integrate the grammar generator and visitor with the parser:

```python
# pom_parser.py
from lark import Lark
from typing import Optional, Any, Dict, Tuple

from pom_grammar_generator import PomGrammarGenerator
from pom_visitor import PomVisitor
from pom_config import PomConfig
from pom_diagnostics import DiagnosticRegistry, SourceLocation, Diagnostic, DiagnosticSeverity

class PomParser:
    """
    Parser for Presentable Object Models.
    Combines grammar generation, parsing, and visiting.
    """
    
    def __init__(self, model_module, config=None, format_name=None):
        """
        Initialize the parser.
        
        Args:
            model_module: Module containing model classes
            config: Optional configuration (uses default if None)
            format_name: Optional format name to load
        """
        self.model_module = model_module
        self.config = config or PomConfig()
        
        # Load format if specified
        if format_name:
            self.config.load_format(format_name)
        
        # Load model metadata
        if hasattr(model_module, '__name__'):
            self.config.load_model_metadata(model_module.__name__)
        
        # Initialize diagnostics
        self.diagnostics = DiagnosticRegistry()
        
        # Create the grammar generator
        self.grammar_generator = PomGrammarGenerator(self.config, "PomGrammar")
        
        # Generate the grammar
        self.grammar = self.grammar_generator.generate_grammar(model_module)
        
        # Create the parser (deferred until needed)
        self._parser = None
    
    def _get_parser(self, start_rule=None):
        """
        Get the parser, creating it if necessary.
        
        Args:
            start_rule: Optional start rule for the parser
            
        Returns:
            Lark parser
        """
        if self._parser is None or start_rule:
            # Create parser with appropriate configuration
            self._parser = Lark(
                self.grammar, 
                start=start_rule or 'start',
                parser='earley'  # Most flexible parser
            )
        return self._parser
    
    def parse(self, input_text, start_rule=None, file_path=None):
        """
        Parse input text to create a model object.
        
        Args:
            input_text: Input text to parse
            start_rule: Optional start rule for the parser
            file_path: Optional file path for error reporting
            
        Returns:
            Tuple of (model_object, success)
        """
        # Clear previous diagnostics
        self.diagnostics = DiagnosticRegistry()
        
        try:
            # Get the parser
            parser = self._get_parser(start_rule)
            
            # Parse the input
            parse_tree = parser.parse(input_text)
            
            # Create and configure visitor
            visitor = PomVisitor(self.model_module, self.diagnostics)
            
            # Visit the parse tree to build the model
            model = visitor.visit(parse_tree)
            
            return model, True
            
        except Exception as e:
            # Handle parsing errors
            self._handle_parse_error(e, input_text, file_path)
            return None, False
    
    def _handle_parse_error(self, error, input_text, file_path=None):
        """
        Handle a parsing error by creating appropriate diagnostics.
        
        Args:
            error: The exception that occurred
            input_text: The input text that was being parsed
            file_path: Optional file path for error reporting
        """
        # Create a diagnostic for the error
        if hasattr(error, 'line') and hasattr(error, 'column'):
            # Error with location information
            location = SourceLocation(
                line=error.line,
                column=error.column,
                file_path=file_path
            )
            
            # Get context lines for better error reporting
            context = self._get_error_context(input_text, error)
            
            self.diagnostics.add_error(
                f"Syntax error: {str(error)}\n{context}",
                location,
                code="SYNTAX_ERROR"
            )
        else:
            # Generic error without location
            self.diagnostics.add_error(
                f"Error during parsing: {str(error)}",
                code="PARSE_ERROR"
            )
    
    def _get_error_context(self, input_text, error, context_lines=2):
        """
        Get context lines around an error for better error reporting.
        
        Args:
            input_text: Input text
            error: Error with line/column attributes
            context_lines: Number of context lines to include
            
        Returns:
            String with context lines
        """
        if not hasattr(error, 'line'):
            return ""
            
        # Split input into lines
        lines = input_text.splitlines()
        if not lines:
            return ""
            
        # Calculate line range
        start_line = max(0, error.line - 1 - context_lines)
        end_line = min(len(lines) - 1, error.line - 1 + context_lines)
        
        # Build context
        context = []
        for i in range(start_line, end_line + 1):
            line_num = i + 1  # 1-based line numbers
            prefix = "-> " if line_num == error.line else "   "
            context.append(f"{prefix}{line_num}: {lines[i]}")
            
            # Add error marker
            if line_num == error.line and hasattr(error, 'column'):
                context.append("   " + " " * error.column + "^")
        
        return "\n".join(context)
```

### 7.2 Grammar Generator Integration with Base Grammar Class

```python
# Modified PomGrammarGenerator to inherit from Grammar
from class_grammar import Grammar
import inspect
from dataclasses import is_dataclass, fields
from typing import Dict, List, Any, Optional, Type, Union, get_type_hints

class PomGrammarGenerator(Grammar):
    """
    Grammar generator for Presentable Object Models.
    Creates Lark grammar from dataclass definitions.
    """
    
    def __init__(self, config, name="PresentableGrammar"):
        """
        Initialize the grammar generator.
        
        Args:
            config: Configuration for grammar generation
            name: Name of the grammar
        """
        super().__init__(name)
        self.config = config
        self.processed_classes = set()
        self.class_hierarchy = {}
        self.rules = []
        self.terminals = set()
        self.rule_names = set()
    
    def generate_grammar(self, model_module) -> str:
        """
        Generate a complete Lark grammar for the given model module.
        
        Args:
            model_module: Module containing dataclass definitions
            
        Returns:
            Complete Lark grammar as a string
        """
        # Reset state
        self.processed_classes.clear()
        self.class_hierarchy.clear()
        self.rules.clear()
        self.terminals.clear()
        self.rule_names.clear()
        
        # Analyze the model
        self._analyze_model(model_module)
        
        # Generate grammar components
        grammar_text = self._generate_grammar_text()
        
        # Store the generated grammar
        self._lark_grammar = grammar_text
        
        return grammar_text
    
    # ... Additional methods from previous specification ...
```

## 8. Usage Examples

### 8.1 Basic Usage

```python
# Import the model module
import literate_model

# Create a parser for the model
from pom_parser import PomParser
parser = PomParser(literate_model)

# Parse an input string
input_text = """
# **MyModel**

## **MySubject**

_ **MyClass** - A class for testing
    name: "TestClass"
    is_value_type: true
    attributes: [
        - **firstAttr** - First attribute (required String)
            derivation:
                english: "Computed from name"
                code: "return 'attr_' + this.name;"
    ]
"""

# Parse the input
model, success = parser.parse(input_text)

# Check for success
if success:
    print(f"Successfully parsed model: {model.name}")
    # Use the model object
else:
    # Handle errors
    print("Parsing failed:")
    print(parser.diagnostics)
```

### 8.2 Custom Format Example

```python
# Load a custom JSON format
from pom_config import PomConfig
config = PomConfig()
config.load_format("json")

# Create parser with the custom format
parser = PomParser(literate_model, config)

# Parse JSON input
json_input = """
{
  "type": "model",
  "name": "MyModel",
  "subjects": [
    {
      "type": "subject",
      "name": "MySubject",
      "classes": [
        {
          "type": "class",
          "name": "MyClass",
          "one_liner": "A class for testing",
          "is_value_type": true,
          "attributes": [
            {
              "type": "attribute",
              "name": "firstAttr",
              "one_liner": "First attribute",
              "data_type_clause": {
                "data_type": {
                  "type": "base-data-type",
                  "class_": "String"
                }
              }
            }
          ]
        }
      ]
    }
  ]
}
"""

# Parse the input
model, success = parser.parse(json_input)
```

### 8.3 External Metadata Example

```yaml
# literate_model_grammar.yaml - External metadata for literate_model
classes:
  Class:
    presentable_header: "_ **{name}**{{#if one_liner}} - {one_liner}{{/if}}"
    
    fields:
      attributes:
        list_format:
          opener: "["
          closer: "]"
          separator: ","
      is_value_type:
        presentable_true: "ValueType"
        presentable_false: "ReferenceType"
        explicit: true

  Attribute:
    presentable_header: "- **{name}**{{#if one_liner}} - {one_liner}{{/if}} {data_type_clause}"
```

```python
# The metadata will be loaded automatically when the model is specified
parser = PomParser(literate_model)

# With explicit format override
parser = PomParser(literate_model, format_name="json")
```

## 9. Implementation Notes

1. **Code Organization**:
   - Separate logical components into their own modules
   - Make extensive use of comments to explain implementation details
   - Reference this specification in comments for traceability

2. **Error Handling**:
   - Use diagnostics rather than exceptions for semantic errors
   - Wrap all external library calls in try/except blocks
   - Provide detailed error messages with context

3. **Performance Considerations**:
   - Cache generated grammars where possible
   - Use weakref for diagnostic registry to avoid memory leaks
   - Implement efficient parse tree traversal

4. **Extension Points**:
   - Allow for custom visitor methods via registration
   - Support pluggable type handlers
   - Provide hooks for preprocessing and postprocessing

5. **Testing Strategy**:
   - Unit tests for individual components
   - Integration tests for the complete pipeline
   - Test with various input formats and model configurations
   - Include error case testing

The implementation should strike a balance between flexibility and simplicity, making it easy to use for common cases while allowing for customization when needed.
