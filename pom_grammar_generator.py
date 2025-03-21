"""
Grammar generator for Presentable Object Models.

This module provides classes for generating Lark grammars from dataclass-based
model definitions, with support for inheritance, templates, and specialized types.
"""

import inspect
import re
from dataclasses import is_dataclass, fields
from typing import Dict, List, Set, Any, Optional, Type, Union, get_type_hints, get_origin, get_args
from .pom_utils import to_snake_case, to_upper_camel

# Make the generator compatible with the Grammar base class if available
try:
    from class_grammar import Grammar
    grammar_base = Grammar
except ImportError:
    # Fallback to a simple base class
    class Grammar:
        def __init__(self, name="Grammar"):
            self.name = name
            self._lark_grammar = ""
    
    grammar_base = Grammar

class PomGrammarGenerator(grammar_base):
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
    
    def _analyze_model(self, model_module):
        """
        Analyze the model to build class hierarchy and identify complex types.
        
        Args:
            model_module: Module containing dataclass definitions
        """
        # Find all dataclasses in the module
        classes = {}
        for name, obj in inspect.getmembers(model_module):
            if inspect.isclass(obj) and is_dataclass(obj):
                classes[name] = obj
        
        # Build class hierarchy
        for name, cls in classes.items():
            # Get direct base classes
            bases = [base.__name__ for base in cls.__bases__ 
                    if base.__name__ in classes and base.__name__ != 'object']
            
            # Create entry for this class
            self.class_hierarchy[name] = {
                'class': cls,
                'bases': bases,
                'subtypes': [],
                'attributes': {}
            }
        
        # Add subtype references
        for name, info in self.class_hierarchy.items():
            for base in info['bases']:
                if base in self.class_hierarchy:
                    self.class_hierarchy[base]['subtypes'].append(name)
        
        # Process classes in a suitable order
        self._process_classes_in_order()
    
    def _process_classes_in_order(self):
        """
        Process classes in an order that respects dependencies.
        Generate rules for each class.
        """
        # Process base classes first
        while len(self.processed_classes) < len(self.class_hierarchy):
            progress = False
            
            for class_name, info in sorted(self.class_hierarchy.items()):
                if class_name in self.processed_classes:
                    continue
                
                # Check if all base classes have been processed
                if all(base in self.processed_classes for base in info['bases']):
                    self._generate_class_rules(class_name, info['class'])
                    progress = True
            
            if not progress:
                # Circular dependency or some other issue
                # Process remaining classes in any order
                for class_name, info in sorted(self.class_hierarchy.items()):
                    if class_name not in self.processed_classes:
                        self._generate_class_rules(class_name, info['class'])
                break
    
    def _generate_class_rules(self, class_name, cls):
        """
        Generate grammar rules for a specific class.
        
        Args:
            class_name: Name of the class
            cls: Class object
        """
        if class_name in self.processed_classes:
            return
            
        self.processed_classes.add(class_name)
        
        # Add comment indicating the class rules
        self.rules.append(f"// ========== {class_name.upper()} ==========")
        
        # Get class metadata (from both in-code Meta and external config)
        metadata = self._get_class_metadata(cls, class_name)
        
        # Check if this is an abstract class that shouldn't generate direct rules
        if metadata.get('is_abstract', False):
            # Only generate type hierarchy rule
            self._generate_type_hierarchy_rule(class_name)
            return
            
        # Generate the header rule if template exists
        if metadata.get('presentable_header'):
            self._generate_header_rule(class_name, cls, metadata['presentable_header'])
        
        # Generate field clause rules
        self._generate_field_clauses(class_name, cls)
        
        # Generate the class body rule
        self._generate_body_rule(class_name, cls)
        
        # Generate the type hierarchy rule
        self._generate_type_hierarchy_rule(class_name)
        
        # Add empty line for readability
        self.rules.append("")
    
    def _generate_header_rule(self, class_name, cls, template):
        """
        Generate a header rule for a class based on a template.
        
        Args:
            class_name: Name of the class
            cls: Class object
            template: Header template
        """
        # Convert template to grammar rule
        rule_name = to_snake_case(class_name) + "_header"
        rule_parts = self._template_to_grammar_parts(template, class_name)
        
        # Create the header rule
        rule = f"{rule_name}: {' '.join(rule_parts)}"
        self.rules.append(rule)
        self.rule_names.add(rule_name)
        
        # Create the class rule that includes the header and body
        class_rule_name = to_snake_case(class_name)
        body_rule_name = class_rule_name + "_body"
        class_rule = f"{class_rule_name}: {rule_name} {body_rule_name}"
        self.rules.append(class_rule)
        self.rule_names.add(class_rule_name)
    
    def _template_to_grammar_parts(self, template, class_name):
        """
        Convert a template string to grammar rule parts.
        
        Args:
            template: Template string
            class_name: Name of the class for field references
            
        Returns:
            List of grammar rule parts
        """
        # Pattern to match field references like {name}
        field_pattern = r'\{([^{}#>/]+)\}'
        
        # Pattern to match conditionals like {{#if field}}...{{/if}}
        conditional_pattern = r'\{\{#if ([^}]+)\}\}(.*?)\{\{/if\}\}'
        
        # Pattern to match partials like {{> partial}}
        partial_pattern = r'\{\{> ([^}]+)\}\}'
        
        # First replace conditionals with optional parts
        template = re.sub(conditional_pattern, 
                         lambda m: f"[{m.group(2)}]", 
                         template)
        
        # Replace partials with rule references
        template = re.sub(partial_pattern,
                         lambda m: f"{to_snake_case(m.group(1))}", 
                         template)
        
        # Replace field references with rule references
        template = re.sub(field_pattern,
                         lambda m: f"{class_name}_{m.group(1)}_value", 
                         template)
        
        # Process special tokens
        special_tokens = self.config.get('special_tokens', {
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
        })
        
        for char, token in special_tokens.items():
            template = template.replace(char, f" {token} ")
            self.terminals.add(token)
        
        # Split into tokens and clean up
        parts = template.split()
        result = []
        
        for part in parts:
            if part.startswith(class_name) and part.endswith("_value"):
                # Field value reference
                result.append(part)
                
                # Make sure we add a rule for this value if it doesn't exist
                self.rule_names.add(part)
            elif part in self.terminals:
                # Terminal token
                result.append(part)
            elif part.strip():
                # Non-empty part - convert to terminal
                if part.isupper():
                    # Already a terminal name
                    self.terminals.add(part)
                    result.append(part)
                else:
                    # Abstract class - only subtypes
                    rule = f"{rule_name}: {subtype_rules}"
            
            self.rules.append(rule)
            self.rule_names.add(rule_name)
    
    def _generate_body_rule(self, class_name, cls):
        """
        Generate a body rule for a class.
        
        Args:
            class_name: Name of the class
            cls: Class object
        """
        # Rule name
        rule_name = f"{to_snake_case(class_name)}_body"
        
        # Get all field clause rules for this class
        field_clauses = self._get_all_field_clauses(class_name)
        
        # Create the rule text
        if field_clauses:
            rule_text = f"({' | '.join(field_clauses)})*"
            rule = f"{rule_name}: {rule_text}"
        else:
            rule = f"{rule_name}: /* No fields */"
        
        self.rules.append(rule)
        self.rule_names.add(rule_name)
    
    def _get_all_field_clauses(self, class_name):
        """
        Get all field clause rule names for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            List of field clause rule names
        """
        return [rule for rule in self.rule_names 
                if rule.startswith(f"{class_name}_") and rule.endswith("_clause")]
    
    def _get_class_metadata(self, cls, class_name):
        """
        Get metadata for a class, combining in-code Meta with external config.
        
        Args:
            cls: Class object
            class_name: Name of the class
            
        Returns:
            Dictionary of metadata
        """
        # Start with defaults
        metadata = {
            "presentable_header": None,
            "presentable_template": None,
            "is_abstract": False
        }
        
        # Check for in-code Meta class
        if hasattr(cls, 'Meta'):
            if hasattr(cls.Meta, 'presentable_header'):
                metadata['presentable_header'] = cls.Meta.presentable_header
            if hasattr(cls.Meta, 'presentable_template'):
                metadata['presentable_template'] = cls.Meta.presentable_template
            if hasattr(cls.Meta, 'is_abstract'):
                metadata['is_abstract'] = cls.Meta.is_abstract
        
        # Override with external metadata from config
        external_metadata = self.config.get_class_metadata(class_name)
        metadata.update(external_metadata)
        
        return metadata
    
    def _get_field_metadata(self, field_obj, class_name, field_name):
        """
        Get metadata for a field, combining field metadata with external config.
        
        Args:
            field_obj: Field object
            class_name: Name of the class
            field_name: Name of the field
            
        Returns:
            Dictionary of metadata
        """
        # Start with defaults
        metadata = {
            "required": True,
            "presentable_true": None,
            "presentable_false": None,
            "explicit": False,
            "list_format": None
        }
        
        # Check for field-level metadata
        if hasattr(field_obj, 'metadata'):
            metadata.update(field_obj.metadata)
        
        # Override with external metadata from config
        external_metadata = self.config.get_field_metadata(class_name, field_name)
        metadata.update(external_metadata)
        
        return metadata
    
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
                
            return to_snake_case(class_name)
            
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
    
    def _is_primitive_type(self, field_type):
        """Check if a type is a primitive type."""
        return field_type in (str, int, float, bool)
    
    def _is_list_type(self, field_type):
        """Check if a type is a list or similar container."""
        origin = get_origin(field_type)
        return origin is list or str(origin) == "<class 'list'>"
    
    def _is_optional_type(self, field_type):
        """Check if a type is Optional."""
        origin = get_origin(field_type)
        if origin is Union or str(origin) == "<class 'typing.Union'>":
            args = get_args(field_type)
            return type(None) in args or 'NoneType' in str(args)
        return False
    
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
            if arg is not type(None) and str(arg) != "<class 'NoneType'>":
                return arg
        return Any  # Default if can't determine
    
    def _to_terminal_name(self, text):
        """Convert a string to a terminal name."""
        if text.isalnum():
            return text.upper()
        else:
            # Special character or token
            special_tokens = {
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
            }
            
            if text in special_tokens:
                token_name = special_tokens[text]
                self.terminals.add(token_name)
                return token_name
            
            return f"TOKEN_{ord(text[0])}"
    
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
                start_rules = " | ".join(to_snake_case(c) for c in root_classes)
                grammar_parts.append(f"start: {start_rules}")
                grammar_parts.append("")
        
        # Add all terminals
        grammar_parts.append("// ===== Terminal definitions =====")
        
        # Special tokens
        special_tokens = {
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
        }
        
        for name, value in special_tokens.items():
            if name in self.terminals:
                grammar_parts.append(f"{name}: {value}")
        
        # Field name terminals
        case_insensitive = "i" if not self.config.get('case_sensitive', False) else ""
        for terminal in sorted(self.terminals):
            if terminal not in special_tokens and terminal not in {
                'STRING', 'NUMBER', 'BOOLEAN', 'NEWLINE', 'INDENT', 'DEDENT'
            }:
                grammar_parts.append(f"{terminal}: \"{terminal.lower()}\"{case_insensitive}")
        
        # Standard value types
        grammar_parts.append("")
        grammar_parts.append("// ===== Value types =====")
        grammar_parts.append(f"STRING: {self.config.get('terminals', {}).get('string_format', '\"\\\"\" /[^\\\"]*/ \"\\\"\"')}")
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
                    # Convert to terminal
                    term_name = part.upper()
                    self.terminals.add(term_name)
                    result.append(term_name)
        
        return result
    
    def _generate_field_clauses(self, class_name, cls):
        """
        Generate field clause rules for a class, handling inheritance and specialization.
        
        Args:
            class_name: Name of the class
            cls: Class object
        """
        # Get specialized fields (fields redefined in this class)
        specialized_fields = self._get_specialized_fields(cls)
        
        # Track processed fields to avoid duplicates
        processed_fields = set()
        
        # Process fields defined in this class
        for field_obj in fields(cls):
            # Skip private fields
            if field_obj.name.startswith('_'):
                continue
                
            # Generate field clause and value rules
            self._generate_field_rules(class_name, field_obj.name, field_obj)
            processed_fields.add(field_obj.name)
        
        # Process inherited fields that aren't overridden
        for base_name in self.class_hierarchy[class_name]['bases']:
            if base_name not in self.class_hierarchy:
                continue
                
            base_cls = self.class_hierarchy[base_name]['class']
            
            for field_obj in fields(base_cls):
                # Skip private fields and already processed fields
                if field_obj.name.startswith('_') or field_obj.name in processed_fields:
                    continue
                    
                # Skip fields that are specialized in this class
                if field_obj.name in specialized_fields:
                    continue
                    
                # Generate field clause and value rules
                self._generate_field_rules(class_name, field_obj.name, field_obj)
                processed_fields.add(field_obj.name)
    
    def _get_specialized_fields(self, cls):
        """
        Get fields that are specialized (redefined) in this class.
        
        Args:
            cls: Class to analyze
            
        Returns:
            Set of field names that are specialized
        """
        specialized = set()
        
        # Get base classes
        bases = [base for base in cls.__bases__ 
                if is_dataclass(base) and base.__name__ in self.class_hierarchy]
        
        # Get fields in this class
        cls_fields = {f.name: f.type for f in fields(cls)}
        
        # Check each base class
        for base in bases:
            base_fields = {f.name: f.type for f in fields(base)}
            
            # Find fields with the same name but different types
            for name, type_hint in cls_fields.items():
                if name in base_fields and type_hint != base_fields[name]:
                    specialized.add(name)
        
        return specialized
    
    def _generate_field_rules(self, class_name, field_name, field_obj):
        """
        Generate rules for a field clause and value.
        
        Args:
            class_name: Name of the class
            field_name: Name of the field
            field_obj: Field object
        """
        # Generate field clause rule
        self._generate_field_clause_rule(class_name, field_name, field_obj)
        
        # Generate field value rule based on type
        self._generate_field_value_rule(class_name, field_name, field_obj)
    
    def _generate_field_clause_rule(self, class_name, field_name, field_obj):
        """
        Generate a rule for a field clause.
        
        Args:
            class_name: Name of the class
            field_name: Name of the field
            field_obj: Field object
        """
        # Get the field clause template
        template = self.config.get('field_clause_template', '{field_name}: {field_value}')
        
        # Get field metadata
        metadata = self._get_field_metadata(field_obj, class_name, field_name)
        
        # Check if field has its own template
        if 'field_clause_template' in metadata:
            template = metadata['field_clause_template']
        
        # Replace placeholders with actual values
        rule_text = template.replace('{field_name}', field_name.upper())
        rule_text = rule_text.replace('{field_value}', f"{class_name}_{field_name}_value")
        
        # Create the rule
        rule_name = f"{class_name}_{field_name}_clause"
        rule = f"{rule_name}: {rule_text}"
        
        self.rules.append(rule)
        self.rule_names.add(rule_name)
        
        # Add the field name to terminals
        self.terminals.add(field_name.upper())
    
    def _generate_field_value_rule(self, class_name, field_name, field_obj):
        """
        Generate a rule for a field value based on its type.
        
        Args:
            class_name: Name of the class
            field_name: Name of the field
            field_obj: Field object
        """
        # Get field type and metadata
        field_type = field_obj.type
        metadata = self._get_field_metadata(field_obj, class_name, field_name)
        
        # Rule name
        rule_name = f"{class_name}_{field_name}_value"
        
        # Handle custom template if specified
        if 'presentable_template' in metadata:
            template_parts = self._template_to_grammar_parts(
                metadata['presentable_template'], class_name)
            self.rules.append(f"{rule_name}: {' '.join(template_parts)}")
            self.rule_names.add(rule_name)
            return
        
        # Handle different field types
        if self._is_primitive_type(field_type):
            # Primitive type (str, int, bool)
            self._generate_primitive_value_rule(rule_name, field_type, metadata)
        elif self._is_list_type(field_type):
            # List type
            self._generate_list_value_rule(rule_name, field_type, metadata)
        elif self._is_optional_type(field_type):
            # Optional type - handle the underlying type
            element_type = self._get_optional_element_type(field_type)
            self._generate_field_value_rule_for_type(rule_name, element_type, metadata)
        elif self._is_class_type(field_type):
            # Class type - reference the class rule
            self._generate_class_value_rule(rule_name, field_type)
        else:
            # Default case - generic value
            self.rules.append(f"{rule_name}: value")
        
        self.rule_names.add(rule_name)
    
    def _generate_primitive_value_rule(self, rule_name, field_type, metadata):
        """
        Generate a rule for a primitive value.
        
        Args:
            rule_name: Name of the rule
            field_type: Field type
            metadata: Field metadata
        """
        if field_type == str:
            # String type
            terminal = self.config.get('terminals', {}).get('string_format', 'STRING')
            self.rules.append(f"{rule_name}: {terminal}")
            
        elif field_type == bool:
            # Boolean type with possible special representation
            if 'presentable_true' in metadata and 'presentable_false' in metadata:
                true_val = metadata['presentable_true'].upper()
                false_val = metadata['presentable_false'].upper()
                
                # Add terminals
                self.terminals.add(true_val)
                self.terminals.add(false_val)
                
                # Create rule
                if metadata.get('explicit', True):
                    self.rules.append(f"{rule_name}: {true_val} | {false_val}")
                else:
                    # Only required value is included if not explicit
                    if metadata.get('default', False):
                        self.rules.append(f"{rule_name}: [{true_val}]")
                    else:
                        self.rules.append(f"{rule_name}: [{false_val}]")
            else:
                # Default boolean
                self.rules.append(f"{rule_name}: {self.config.get('terminals', {}).get('boolean_format', 'BOOLEAN')}")
                
        elif field_type in (int, float):
            # Numeric type
            self.rules.append(f"{rule_name}: {self.config.get('terminals', {}).get('number_format', 'NUMBER')}")
            
        else:
            # Other primitive type - fallback to generic value
            self.rules.append(f"{rule_name}: value")
    
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
                rule = f"{self._to_terminal_name(opener)} [{element_rule} ({self._to_terminal_name(separator)} {element_rule})*] {self._to_terminal_name(closer)}"
            else:
                # Simple separated list
                rule = f"{element_rule} ({self._to_terminal_name(separator)} {element_rule})*"
        
        # Add the rule
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
        class_rule = to_snake_case(class_name)
        self.rules.append(f"{rule_name}: {class_rule}")
    
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
    
    def _generate_type_hierarchy_rule(self, class_name):
        """
        Generate a rule for type hierarchy (parent class with subtypes).
        
        Args:
            class_name: Name of the class
        """
        # Get subtypes of this class
        subtypes = self.class_hierarchy[class_name].get('subtypes', [])
        
        # If this class has subtypes, create a rule for the hierarchy
        if subtypes:
            rule_name = to_snake_case(class_name)
            subtype_rules = " | ".join(to_snake_case(st) for st in subtypes)
            
            # Add class's own rule if not abstract
            metadata = self._get_class_metadata(
                self.class_hierarchy[class_name]['class'], class_name)
            
            if not metadata.get('is_abstract', False):
                # Include the class's own body rule
                body_rule = f"{rule_name}_body"
                if subtype_rules:
                    rule = f"{rule_name}: {subtype_rules} | {body_rule}"
                else:
                    rule = f"{rule_name}: {body_rule}"
            else: