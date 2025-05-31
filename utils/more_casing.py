"""
Utility functions for Presentable Object Model (POM) package.

This module provides utility functions for naming conventions, string
manipulation, and other common operations used by the POM package.
"""

import re
from typing import List, Dict, Any, Optional

def to_snake_case(name: str) -> str:
    """
    Convert a CamelCase name to snake_case.
    
    Args:
        name: Name to convert
        
    Returns:
        Converted snake_case name
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

def to_upper_camel(name: str) -> str:
    """
    Convert a snake_case or space-separated name to UpperCamelCase.
    
    Args:
        name: Name to convert
        
    Returns:
        Converted UpperCamelCase name
    """
    # Split on underscores, spaces, and dashes
    parts = re.split(r'[_\s-]+', name)
    
    # Capitalize each part
    return ''.join(p.capitalize() for p in parts if p)

def to_lower_camel(name: str) -> str:
    """
    Convert a snake_case or space-separated name to lowerCamelCase.
    
    Args:
        name: Name to convert
        
    Returns:
        Converted lowerCamelCase name
    """
    camel = to_upper_camel(name)
    if not camel:
        return ''
    
    # Lowercase the first character
    return camel[0].lower() + camel[1:]

def split_camel_case(text: str) -> List[str]:
    """
    Split a camel case string into words.
    
    Args:
        text: CamelCase text to split
        
    Returns:
        List of words
    """
    # First remove any brackets and trim
    text = text.strip("[] \t\n\r")

    # Handle empty or single char strings
    if len(text) <= 1:
        return [text] if text else []

    # Add word boundary before each capital letter
    words = []
    current_word = text[0]

    for c in text[1:]:
        if c.isupper() and current_word[-1].islower():
            # New word starts at uppercase after lowercase
            words.append(current_word)
            current_word = c
        else:
            current_word += c

    # Add the last word
    words.append(current_word)
    return words

def join_camel_case(words: List[str], upper_first: bool = True) -> str:
    """
    Join words into a camel case string.
    
    Args:
        words: List of words to join
        upper_first: Whether to capitalize the first word
        
    Returns:
        Camel case string
    """
    if not words:
        return ""
        
    # Process the first word
    if upper_first:
        result = words[0].capitalize()
    else:
        result = words[0].lower()
        
    # Capitalize the rest
    for word in words[1:]:
        result += word.capitalize()
        
    return result

def clean_string(text: str) -> str:
    """
    Clean and normalize a string.
    
    Args:
        text: String to clean
        
    Returns:
        Cleaned string
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Handle quoted strings
    if text and text[0] == '"' and text[-1] == '"':
        text = text[1:-1]
    
    return text

def extract_field_name(node_name: str) -> str:
    """
    Extract the field name from a node name.
    
    Args:
        node_name: Node name like "class_name_field_name_suffix"
        
    Returns:
        Field name
    """
    # Split by underscore
    parts = node_name.split('_')
    
    # If there are at least two parts, return the last part
    if len(parts) >= 2:
        return parts[-1]
    
    return node_name

def extract_class_name(node_name: str) -> str:
    """
    Extract the class name from a node name.
    
    Args:
        node_name: Node name like "class_name_field_name_suffix"
        
    Returns:
        Class name
    """
    # Split by underscore
    parts = node_name.split('_')
    
    # If there are at least three parts, return all but the last two parts joined
    if len(parts) >= 3:
        return '_'.join(parts[:-2])
    
    return node_name

def to_class_reference(class_name: str) -> str:
    """
    Convert a class name to a reference suitable for grammar rules.
    
    Args:
        class_name: Class name
        
    Returns:
        Class reference
    """
    return to_snake_case(class_name)

def is_primitive_type(type_name: str) -> bool:
    """
    Check if a type name represents a primitive type.
    
    Args:
        type_name: Type name
        
    Returns:
        True if primitive type
    """
    primitives = {
        'str', 'string', 'int', 'integer', 'float', 'double',
        'bool', 'boolean', 'none', 'any'
    }
    return type_name.lower() in primitives


def normalize_name(name: str, case: str = 'snake') -> str:
    """
    Normalize a name to the requested case.
    
    Args:
        name: Name to normalize
        case: Target case ('snake', 'upper_camel', 'lower_camel')
        
    Returns:
        Normalized name
    """
    if case == 'snake':
        return to_snake_case(name)
    elif case == 'upper_camel':
        return to_upper_camel(name)
    elif case == 'lower_camel':
        return to_lower_camel(name)
    else:
        return name