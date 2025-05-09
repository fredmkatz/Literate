# ldm_validators.py
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field


import ldm.Literate_01 as Literate_01
from Literate_01 import Diagnostic

    
def createError(obj, message) -> Diagnostic:
    return createDiagnostic(obj, message, severity = "Error")

def createWarning(obj, message) -> Diagnostic:
    return createDiagnostic(obj, message, severity = "Warning")

def createDiagnostic(obj, message, severity = "Error") -> Diagnostic:
    oname = ""
    oname = getattr(obj, "name", "anon")
    d = Diagnostic(severity = severity, message = message, object_type = obj._type, object_name = oname)
    obj.diagnostics.append(d)
    print(d)
    return d
    

def validate_references(model) -> List[str]:
    """Validate all references within a model."""
    class_names = set()
    
    # First pass: collect all class names
    for subject in model.subjects:
        for cls in subject.classes:
            if cls.name in class_names:
                All_Errors.append(
                    createError(model, f"Duplicate class name: {cls.name}")
                )
            class_names.add(cls.name)
    
    # Second pass: validate references
    for subject in model.subjects:
        for cls in subject.classes:
            # Check subtype_of references
            for ref in cls.subtype_of or []:
                if ref not in class_names:
                    All_Errors.append(
                        createError(cls, f"Invalid reference to '{ref}' in subtype_of")
                    )
                                    
            # Check based_on references
            for ref in cls.based_on or []:
                if ref not in class_names:
                    All_Errors.append(
                        createError(cls, f"Invalid reference to '{ref}' in based_on")
                    )
    return All_Errors
    

def validate_component(component) -> List[str]:
    """Base validation for all Components."""
    
    component_type = component._type
    name = component.name
    if not name:
        d = createError(component, "Name is missing")
        All_Errors.append(d)
    
    one_liner = component.one_liner
    if not one_liner:
        All_Errors.append(
            createError(component, "Missing oneLiner")
        )
    elif len(one_liner) > 50:
        All_Errors.append(
            createWarning(component, f"oneLiner is too long  in {component_type} ({len(one_liner)} chars")
        )

    

def validate_subject(self) -> List[str]:
    validate_component(self)
    
    validate_each(self.classes)
    validate_each(self.subjects)
    
def validate_attribute_section(self) -> List[str]:
    """Validate AttributeSection instances."""
    validate_component(self)
    
    # Check that the attributes list is present
    if not hasattr(self, "attributes") or self.attributes is None:
        All_Errors.append(
            createError(self, "Missing list of Attributes", severity="ERROR")
        )
    
    # Validate each attribute
    validate_each(self.attributes)
    

def validate_class(self) -> List[str]:
    """Validate Class instances."""
    
    validate_component(self)
    
    # Class-specific validations
    # ...
    validate_each(self.constraints)

    # Validate attributes and attribute sections
    validate_each(self.attributes)
    validate_each(self.attribute_sections)
    

def validate_attribute(attrib):
    validate_component(attrib)
    
    validate_presence(attrib, "data_type_clause")
    validate_object(attrib.data_type_clause)
    validate_object(attrib.derivation)
    validate_object(attrib.default)
    validate_each(attrib.constraints)

def validate_formula(formula):
    
    as_entered = getattr(formula, "as_entered", "")
    if len(as_entered) > 50:
        All_Errors.append(
            createError(formula, f"as_entered is too long ({len(as_entered)} chars)")
        )
    
    validate_presence(formula, "code")

def validate_constraint(constraint):
    validate_formula(constraint)

# Then attach the methods to the classes
Literate_01.Component.validate = validate_component
Literate_01.Subject.validate = validate_subject
Literate_01.Class.validate = validate_class

Literate_01.AttributeSection.validate = validate_attribute_section
Literate_01.Attribute.validate = validate_attribute
Literate_01.Formula.validate = validate_formula
Literate_01.Constraint.validate = validate_constraint
# ... and so on for other classes

All_Errors = []

def validate_presence(obj, attname):
    value = getattr(obj, attname, None)
    if value == None:
        All_Errors.append(
            createError(obj, f"No value for {attname}")
        )

def validate_each(objects: List):
    for obj in objects:
        validate_object(obj)
        
def validate_object(obj: Any):
    if not obj:
        # print("Null object in validate_object")
        return

    otype = getattr(obj, "_type", "No type?")
    oname = getattr(obj, "name", "NoName?")
    # print(f"Validating object: {otype} - {oname}")
    if hasattr(obj, "validate"):
        # print(f"... found validate method! - {obj.validate.__name__}")

        obj.validate()
    else:
        print(f"... no validate method attached for {otype} {oname}")

# Helper function to validate entire model
def validate_model(model):
    """Validate an entire LDM model."""
    validate_component(model)
    validate_each(model.subjects)

    return All_Errors