"""
Test models for use in the POM test suite.

This module defines simple dataclass models for testing the grammar generator,
visitor, and parser.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class SimpleClass:
    """Simple test class with primitive fields."""
    
    name: str
    value: int = 0
    
    class Meta:
        presentable_header = "simple_class {name}"

@dataclass
class ComplexClass:
    """Complex test class with nested fields."""
    
    name: str
    items: List[str] = field(default_factory=list)
    is_active: bool = False
    nested: Optional['NestedClass'] = None
    
    class Meta:
        presentable_header = "complex_class {name} {#if is_active}(active){/if}"

@dataclass
class NestedClass:
    """Nested class for testing nested structures."""
    
    id: str
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BaseClass:
    """Base class for testing inheritance."""
    
    id: str
    name: str

@dataclass
class ChildClass(BaseClass):
    """Child class for testing inheritance."""
    
    description: str
    value: int = 0

@dataclass
class BooleanTestClass:
    """Class for testing boolean field handling."""
    
    is_active: bool = field(
        default=False,
        metadata={
            "presentable_true": "ACTIVE",
            "presentable_false": "INACTIVE",
            "explicit": True
        }
    )
    
    is_optional: bool = field(
        default=False,
        metadata={
            "presentable_true": "optional",
            "presentable_false": "required",
            "explicit": False
        }
    )

@dataclass
class ListTestClass:
    """Class for testing list field handling."""
    
    items: List[str] = field(
        default_factory=list,
        metadata={
            "list_format": {
                "opener": "[",
                "closer": "]",
                "separator": ",",
                "whitespace": True
            }
        }
    )
    
    nested_items: List['NestedClass'] = field(default_factory=list)

@dataclass
class ModelWithTemplate:
    """Class for testing template-based rules."""
    
    name: str
    description: str
    
    class Meta:
        presentable_template = "model {name} - {description}"
        presentable_header = "# Model {name}"
