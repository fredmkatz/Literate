from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Type, Union, ClassVar, Set
from abc import ABC, abstractmethod


from utils_pom.util_flogging import flogger
from utils_pom.util_flogging import trace_decorator

class FieldType(ABC):
    """
    Abstract base class representing a field type with analysis capabilities.
    Handles parsing and analyzing type strings like 'Optional[List[str]]'.
    added comments to test github actions
    """
    # Class registry for factory method
    _type_registry: ClassVar[Dict[str, Type[FieldType]]] = {}
    
    
    def __init__(self, raw_string: str, is_optional: bool = False):
        """
        Initialize the base field type.
        
        Args:
            raw_string: String representation of the field type
            is_optional: Whether this type is optional (can be None)
        """
        self.raw_string = raw_string
        self.is_optional = is_optional
    
    @classmethod
    def register(cls, operator: str = None):
        """
        Register a subclass in the type registry.
        
        Args:
            operator: The operator string this class handles (e.g., 'List', 'Dict')
        """
        def decorator(subclass):
            if operator:
                cls._type_registry[operator] = subclass
            return subclass
        return decorator
    
    @classmethod
    # @trace_decorator
    def create(cls, field_type_string: str) -> FieldType:
        """
        Factory method to create the appropriate FieldType subclass.
        
        Args:
            field_type_string: String representation of the field type
            
        Returns:
            Appropriate FieldType subclass instance
        """
        # Clean the string
        field_type_str = str(field_type_string).strip("'\"")
        
        # Check for Optional
        is_optional = False
        
        # Check for container types with brackets
        bracket_pos = field_type_str.find('[')
        if bracket_pos > 0:
            operator = field_type_str[:bracket_pos]
            content, _ = cls._parse_brackets(field_type_str, bracket_pos + 1)
            
            # Handle Optional specially
            if operator == 'Optional':
                is_optional = True
                # Recursively create the contained type
                if content:
                    inner_type = cls.create(content[0])
                    inner_type.is_optional = True
                    return inner_type
            
            # Handle Union specially (could be Optional)
            elif operator == 'Union':
                # Check if one of types is None (making it Optional)
                has_none = any(item.strip() == 'None' for item in content)
                non_none_types = [item for item in content if item.strip() != 'None']
                
                if has_none and len(non_none_types) == 1:
                    # It's effectively Optional[X]
                    inner_type = cls.create(non_none_types[0])
                    inner_type.is_optional = True
                    return inner_type
                else:
                    # It's a true Union
                    element_types = [cls.create(item) for item in content if item.strip() != 'None']
                    return UnionType(field_type_str, is_optional=has_none, element_types=element_types)
            
            # Use the registry to create the appropriate subclass
            if operator in cls._type_registry:
                return cls._type_registry[operator].from_content(field_type_str, content, is_optional)
            
            # Unknown operator, treat as simple type
            return SimpleType(field_type_str, is_optional)
        
        # No brackets, it's a simple type (primitive or class)
        return SimpleType(field_type_str, is_optional)
    
    @classmethod
    def _parse_brackets(cls, s: str, start_pos: int) -> tuple[list[str], int]:
        """
        Parse content within brackets, handling nested brackets.
        
        Args:
            s: String to parse
            start_pos: Starting position after the opening bracket
            
        Returns:
            Tuple of (parsed_content, end_position)
        """
        result = []
        current = ""
        level = 0
        i = start_pos
        
        while i < len(s):
            char = s[i]
            
            if char == '[':
                # Opening bracket
                current += char
                level += 1
            elif char == ']':
                # Closing bracket
                if level == 0:
                    # End of our top-level bracket - don't add to current
                    result.append(current.strip())
                    return result, i + 1
                else:
                    # This is a nested closing bracket, include it
                    current += char
                    level -= 1
            elif char == ',' and level == 0:
                # Top-level separator
                result.append(current.strip())
                current = ""
            else:
                # Any other character
                current += char
            
            i += 1
        
        # Add the last item if there is one
        if current:
            result.append(current.strip())
        
        return result, i
    
    # @abstractmethod
    def suffix(self) -> str:
        """Get a suffix identifying the type."""
        return "SuffixTBD"
    
    # @abstractmethod
    @trace_decorator
    def value_phrase(self, metadata: dict) -> str:
        """Generate a grammar rule phrase for this type."""
        return "ValuePhraseTBD"
    
    def get_base_types(self) -> List[str]:
        """Get the base types for this field type."""
        return []
    
    def is_primitive_type(self) -> bool:
        """Check if this is a primitive type."""
        return False
    
    def is_class_type(self) -> bool:
        """Check if this is a class type (not primitive)."""
        return False
    
    def is_list(self) -> bool:
        """Check if this is a List type."""
        return False
    
    def is_set(self) -> bool:
        """Check if this is a Set type."""
        return False
    
    def is_dict(self) -> bool:
        """Check if this is a Dict type."""
        return False
    
    def is_tuple(self) -> bool:
        """Check if this is a Tuple type."""
        return False
    
    def is_union(self) -> bool:
        """Check if this is a Union type."""
        return False
    
    def is_simple_type(self) -> bool:
        """Check if this is a simple type (no operators)."""
        return False
    
    def __str__(self) -> str:
        """String representation of the field type."""
        return self.raw_string
    
    def display(self, indent: int = 0) -> str:
        """
        Display the field type analysis in a readable format.
        
        Args:
            indent: Number of spaces to indent (for nested display)
            
        Returns:
            String representation of the field type analysis
        """
        indent_str = ' ' * indent
        lines = [f"{indent_str}Field Type: {self.raw_string} ({self.__class__.__name__})"]
        lines.append(f"{indent_str}  Is Optional: {self.is_optional}")
        
        # Add additional properties specific to each subclass
        self._add_display_properties(lines, indent_str)
        
        return "\n".join(lines)
    
    def _add_display_properties(self, lines: List[str], indent_str: str):
        """Add subclass-specific properties to the display output."""
        pass


@FieldType.register()
class SimpleType(FieldType):
    """Represents a simple type without operators (primitive or class name)."""
    
    def __init__(self, raw_string: str, is_optional: bool = False):
        super().__init__(raw_string, is_optional)
        # Determine if it's a primitive type
        self._is_primitive = raw_string in {'str', 'int', 'float', 'bool', 'None', 'Any'}
        self.raw_string = raw_string
    
    @classmethod
    def from_content(cls, raw_string: str, content: List[str], is_optional: bool = False) -> SimpleType:
        """Create from parsed content - not applicable for SimpleType."""
        return cls(raw_string, is_optional)
    
    def suffix(self) -> str:
        if  self.raw_string in {'str', 'int', 'float', 'bool'}:
            return self.raw_string
        return "simple"
    
    def value_phrase(self, metadata: dict) -> str:
        from class_casing import NTCase

        if self.is_primitive_type():
            return self._primitive_phrase(metadata)
        # if self.raw_string.lower() == "camelcase":
        #     return "CAMEL_CASE"
        return str(NTCase(self.raw_string))  # Class name for non-primitives
    
    def _primitive_phrase(self, metadata: dict) -> str:
        """Generate a phrase for primitive types."""
        if self.raw_string == "str":
            return "STRING"
        
        elif self.raw_string == "bool":
            return "BOOLEAN"
            
        elif self.raw_string in ("int", "float"):
            return "NUMBER"
            
        return "value"  # Fallback
    
    def get_base_types(self) -> List[str]:
        return [self.raw_string]
    
    def is_primitive_type(self) -> bool:
        return self._is_primitive
    
    def is_class_type(self) -> bool:
        return not self._is_primitive
    
    def is_simple_type(self) -> bool:
        return True
    
    def _add_display_properties(self, lines: List[str], indent_str: str):
        lines.append(f"{indent_str}  Is Primitive: {self._is_primitive}")
        lines.append(f"{indent_str}  Base Type: {self.raw_string}")


@FieldType.register("List")
class ListType(FieldType):
    """Represents a List[X] type."""
    
    def __init__(self, raw_string: str, element_type: FieldType, is_optional: bool = False):
        super().__init__(raw_string, is_optional)
        self.element_type = element_type
    
    @classmethod
    def from_content(cls, raw_string: str, content: List[str], is_optional: bool = False) -> ListType:
        if content:
            element_type = FieldType.create(content[0])
            return cls(raw_string, element_type, is_optional)
        return cls(raw_string, SimpleType("Any"), is_optional)
    
    def suffix(self) -> str:
        return "list"
    
    def value_phrase(self, metadata: dict) -> str:
        
        # Generate element type rule
        element_phrase = self.element_type.value_phrase(metadata)
        
        # Create list rule template
        list_template = metadata.get("list", "{element} ( ',+ ' {element} )+")
        
        # Fill in the template
        rule = list_template.replace("{element}", element_phrase)
        # flogger.infof(f"List meta: {metadata}")
        # flogger.infof(f"List rule: {rule}")
        return rule
    
    def get_base_types(self) -> List[str]:
        return self.element_type.get_base_types()
    
    def get_element_type(self) -> FieldType:
        return self.element_type
    
    def get_element_type_string(self) -> str:
        return str(self.element_type)
    
    def is_list(self) -> bool:
        return True
    
    def _add_display_properties(self, lines: List[str], indent_str: str):
        lines.append(f"{indent_str}  Element Type:")
        lines.append(self.element_type.display(indent=indent_str.count(' ') + 4))


@FieldType.register("Set")
class SetType(FieldType):
    """Represents a Set[X] type."""
    
    def __init__(self, raw_string: str, element_type: FieldType, is_optional: bool = False):
        super().__init__(raw_string, is_optional)
        self.element_type = element_type
    
    @classmethod
    def from_content(cls, raw_string: str, content: List[str], is_optional: bool = False) -> SetType:
        if content:
            element_type = FieldType.create(content[0])
            return cls(raw_string, element_type, is_optional)
        return cls(raw_string, SimpleType("Any"), is_optional)
    
    def suffix(self) -> str:
        return "set"
    
    def value_phrase(self, metadata: dict) -> str:
        # Generate element type rule
        element_phrase = self.element_type.value_phrase(metadata)
        
        # Create set rule
        set_template = "{element_phrase} ( ',' {element_phrase} )*"
        rule = set_template.replace("{element_phrase}", element_phrase)
        
        # flogger.infof(f"Set rule: {rule}")
        return rule
    
    def get_base_types(self) -> List[str]:
        return self.element_type.get_base_types()
    
    def get_element_type(self) -> FieldType:
        return self.element_type
    
    def get_element_type_string(self) -> str:
        return str(self.element_type)
    
    def is_set(self) -> bool:
        return True
    
    def _add_display_properties(self, lines: List[str], indent_str: str):
        lines.append(f"{indent_str}  Element Type:")
        lines.append(self.element_type.display(indent=indent_str.count(' ') + 4))


@FieldType.register("Dict")
class DictType(FieldType):
    """Represents a Dict[K, V] type."""
    
    def __init__(self, raw_string: str, key_type: FieldType, value_type: FieldType, is_optional: bool = False):
        super().__init__(raw_string, is_optional)
        self.key_type = key_type
        self.value_type = value_type
    
    @classmethod
    def from_content(cls, raw_string: str, content: List[str], is_optional: bool = False) -> DictType:
        key_type = FieldType.create(content[0] if content else "Any")
        value_type = FieldType.create(content[1] if len(content) > 1 else "Any")
        return cls(raw_string, key_type, value_type, is_optional)
    
    def suffix(self) -> str:
        return "dict"
    
    def value_phrase(self, metadata: dict) -> str:
        key_phrase = self.key_type.value_phrase(metadata)
        value_phrase = self.value_type.value_phrase(metadata)
        
        # Create dictionary rule
        dict_template = "'{' ({key_phrase} ':' {value_phrase}) (',' {key_phrase} ':' {value_phrase})* '}'"
        rule = dict_template.replace("{key_phrase}", key_phrase).replace("{value_phrase}", value_phrase)
        
        # flogger.infof(f"Dict rule: {rule}")
        return rule
    
    def get_base_types(self) -> List[str]:
        return self.key_type.get_base_types() + self.value_type.get_base_types()
    
    def get_key_type(self) -> FieldType:
        return self.key_type
    
    def get_value_type(self) -> FieldType:
        return self.value_type
    
    def is_dict(self) -> bool:
        return True
    
    def _add_display_properties(self, lines: List[str], indent_str: str):
        lines.append(f"{indent_str}  Key Type:")
        lines.append(self.key_type.display(indent=indent_str.count(' ') + 4))
        lines.append(f"{indent_str}  Value Type:")
        lines.append(self.value_type.display(indent=indent_str.count(' ') + 4))


@FieldType.register("Tuple")
class TupleType(FieldType):
    """Represents a Tuple[X, Y, Z, ...] type."""
    
    def __init__(self, raw_string: str, element_types: List[FieldType], is_optional: bool = False):
        super().__init__(raw_string, is_optional)
        self.element_types = element_types
    
    @classmethod
    def from_content(cls, raw_string: str, content: List[str], is_optional: bool = False) -> TupleType:
        element_types = [FieldType.create(item) for item in content]
        return cls(raw_string, element_types, is_optional)
    
    def suffix(self) -> str:
        return "tuple"
    
    def value_phrase(self, metadata: dict) -> str:
        # Generate element type rules
        element_phrases = [et.value_phrase(metadata) for et in self.element_types]
        
        # Create tuple rule
        if element_phrases:
            elements_str = ", ".join(element_phrases)
            tuple_template = "'(' {elements} ')'"
            rule = tuple_template.replace("{elements}", elements_str)
        else:
            rule = "'(' ')'"
        
        # flogger.infof(f"Tuple rule: {rule}")
        return rule
    
    def get_base_types(self) -> List[str]:
        base_types = []
        for et in self.element_types:
            base_types.extend(et.get_base_types())
        return base_types
    
    def get_element_types(self) -> List[FieldType]:
        return self.element_types
    
    def is_tuple(self) -> bool:
        return True
    
    def _add_display_properties(self, lines: List[str], indent_str: str):
        lines.append(f"{indent_str}  Element Types:")
        for i, et in enumerate(self.element_types):
            lines.append(f"{indent_str}    [{i}]:")
            lines.append(et.display(indent=indent_str.count(' ') + 6))


@FieldType.register("Union")
class UnionType(FieldType):
    """Represents a Union[X, Y, Z, ...] type."""
    
    def __init__(self, raw_string: str, element_types: List[FieldType], is_optional: bool = False):
        super().__init__(raw_string, is_optional)
        self.element_types = element_types
    
    @classmethod
    def from_content(cls, raw_string: str, content: List[str], is_optional: bool = False) -> UnionType:
        element_types = [FieldType.create(item) for item in content if item.strip() != 'None']
        return cls(raw_string, element_types, is_optional=is_optional)
    
    def suffix(self) -> str:
        return "union"
    
    def value_phrase(self, metadata: dict) -> str:
        # Generate element type rules
        element_phrases = [et.value_phrase(metadata) for et in self.element_types]
        
        # Create union rule (using | operator)
        if element_phrases:
            rule = " | ".join(element_phrases)
        else:
            rule = "value"  # Default fallback
        
        # flogger.infof(f"Union rule: {rule}")
        return rule
    
    def get_base_types(self) -> List[str]:
        base_types = []
        for et in self.element_types:
            base_types.extend(et.get_base_types())
        return base_types
    
    def get_element_types(self) -> List[FieldType]:
        return self.element_types
    
    def is_union(self) -> bool:
        return True
    
    def _add_display_properties(self, lines: List[str], indent_str: str):
        lines.append(f"{indent_str}  Union Types:")
        for i, et in enumerate(self.element_types):
            lines.append(f"{indent_str}    [{i}]:")
            lines.append(et.display(indent=indent_str.count(' ') + 6))


# Utility functions

# Global field terminals set
field_terminals = set()
field_name_literals = set()
punctuation_terminals = set()

def add_field_terminal(terminal: str):
    """Add a terminal to the global field terminals set."""
    field_terminals.add(terminal)

def create_field_type(field_type_string: str) -> FieldType:
    """
    Factory function to create an appropriate FieldType instance.
    
    Args:
        field_type_string: String representation of the field type
        
    Returns:
        Appropriate FieldType subclass instance
    """
    return FieldType.create(field_type_string)

def get_field_terminals() -> Set[str]:
    """Get the global set of field terminals."""
    return field_terminals

def to_terminal_name(text: str) -> str:
    """Convert a string to a terminal name."""
    from pom_config import named_pmarks, pmark_named
    
    if text.isalnum():
        return text.upper()
    
    # Check if it's a named punctuation mark
    token_name = None
    if text in named_pmarks or text in pmark_named:
        token_name = named_pmarks[text]
        punctuation_terminals.add(token_name)
    elif f"'{text}'" in named_pmarks:   
        token_name = named_pmarks[f"'{text}'"]
        
    if token_name:
        flogger.infof(f"Adding {token_name} to field_terminals")
        # Add to terminals set
        add_field_terminal(token_name)
        return token_name
    
    token_name = f"TOKEN_{ord(text[0])}"
    flogger.infof(f"Named pmark not found for {text}. Adding {token_name} to terminals")
    return token_name

