# ldm_validators.py
import ldm.Literate_01 as Literate_01
from typing import List, Dict, Any, Tuple

def validate_references(model) -> List[str]:
    """Validate all references within a model."""
    errors = []
    class_names = set()
    
    # First pass: collect all class names
    for subject in model.subjects:
        for cls in subject.classes:
            if cls.name in class_names:
                errors.append(f"Duplicate class name: {cls.name}")
            class_names.add(cls.name)
    
    # Second pass: validate references
    for subject in model.subjects:
        for cls in subject.classes:
            # Check subtype_of references
            for ref in cls.subtype_of or []:
                if ref not in class_names:
                    errors.append(f"Class '{cls.name}': Invalid reference to '{ref}' in subtype_of")
            
            # Check based_on references
            for ref in cls.based_on or []:
                if ref not in class_names:
                    errors.append(f"Class '{cls.name}': Invalid reference to '{ref}' in based_on")
    
    return errors

def validate_component(self) -> List[str]:
    """Base validation for all Components."""
    errors = []
    
    if not self.name:
        errors.append(f"{self._type}: Missing name")
        
    return errors

def validate_attribute_section(self) -> List[str]:
    """Validate AttributeSection instances."""
    errors = validate_component(self)
    
    # Check that the attributes list is present
    if not hasattr(self, "attributes") or self.attributes is None:
        errors.append(f"AttributeSection '{self.name}': Missing attributes list")
    
    # Validate each attribute
    for attr in self.attributes:
        if hasattr(attr, "validate"):
            attr_errors = attr.validate()
            for error in attr_errors:
                errors.append(f"AttributeSection '{self.name}': {error}")
    
    return errors

def validate_class(self) -> List[str]:
    """Validate Class instances."""
    errors = validate_component(self)
    
    # Class-specific validations
    # ...
    
    # Validate attributes and attribute sections
    for attr in self.attributes:
        if hasattr(attr, "validate"):
            attr_errors = attr.validate()
            for error in attr_errors:
                errors.append(f"Class '{self.name}': {error}")
    
    for section in self.attribute_sections:
        if hasattr(section, "validate"):
            section_errors = section.validate()
            for error in section_errors:
                errors.append(f"Class '{self.name}': {error}")
    
    return errors

# Then attach the methods to the classes
Literate_01.Component.validate = validate_component
Literate_01.AttributeSection.validate = validate_attribute_section
Literate_01.Class.validate = validate_class
# ... and so on for other classes

# Helper function to validate entire model
def validate_model(model):
    """Validate an entire LDM model."""
    all_errors = []
    
    if hasattr(model, "validate"):
        model_errors = model.validate()
        all_errors.extend(model_errors)
    
    return all_errors