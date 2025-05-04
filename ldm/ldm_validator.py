# ldm_validator.py
from typing import List, Any, Dict

class LDMValidator:
    """Validator for Literate models"""
    
    def validate(self, obj: Any) -> List[str]:
        """
        Validate an object based on its type.
        This is the main entry point for validation.
        """
        obj_type = getattr(obj, "_type", None)
        errors = []
        
        print(f"Validating object of type: {obj_type}")
        
        # Dispatch to specific validation methods based on object type
        if obj_type == "LDM":
            errors.extend(self._validate_ldm(obj))
            # Validate references for LDM types
            errors.extend(self._validate_references(obj))
        elif obj_type == "Class":
            errors.extend(self._validate_class(obj))
        elif obj_type == "Attribute":
            errors.extend(self._validate_attribute(obj))
        else:
            errors.append(f"Unsupported type: {obj_type}")
        
        # Add test error to verify validation is working
        errors.append("TEST VALIDATION MESSAGE - validation is working")
        
        return errors