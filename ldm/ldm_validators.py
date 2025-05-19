# ldm_validators.py
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field

from typing import Any, get_type_hints, get_origin, get_args, Optional, Union, Literal, Callable
from dataclasses import fields, is_dataclass

import ldm.Literate_01 as Literate_01
from ldm.Literate_01 import Diagnostic

    
def createError(obj, message) -> Diagnostic:
    return createDiagnostic(obj, message, severity = "Error")

def createWarning(obj, message) -> Diagnostic:
    return createDiagnostic(obj, message, severity = "Warning")

def createDiagnostic(obj, message, severity = "Error") -> Diagnostic:
    oname = ""
    oname = getattr(obj, "name", "anon")
    d = Diagnostic(severity = severity, message = message, object_type = obj._type, object_name = oname)
    obj.diagnostics.append(d)
    # print(d)
    return d
    

def validate_references(model) -> List[str]:
    """Validate all references within a model."""
    return []
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
    # if not one_liner:
    #     All_Errors.append(
    #         createError(component, "Missing oneLiner")
    #     )
    if one_liner and len(str(one_liner)) > 90:
        All_Errors.append(
            createWarning(component, f"oneLiner is too long. ({len(str(one_liner))} chars).")
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

def validate_data_type_clause(dtc):
    validate_presence(dtc, "data_type")

def validate_formula(formula):
    
    one_liner = getattr(formula, "one_liner", "")
    if len(str(one_liner)) > 90:
        All_Errors.append(
            createError(formula, f"Formula one_liner is too long ({len(str(one_liner))} chars)")
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
Literate_01.DataTypeClause.validate = validate_data_type_clause
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
        
    # But in all cases, do deep field valiation
    validate_fields(obj)

from validate_fields import all_validation_errors
def create_error(obj, message):
    """
    Helper function to log or handle validation errors.
    """
    e = f"Validation Error in {getattr(obj, '_type', 'Unknown Type')}: {message}"
    # global all_validation_errors
    all_validation_errors.append(e)

def validate_fields(obj: Any):
    """
    Validate whether the values of fields in the object have the proper types,
    including deep type checking for generics like List[X].
    """
    if not obj:
        print("Null object in validate_object")
        return

    otype = getattr(obj, "_type", "No type?")
    oname = getattr(obj, "name", "NoName?")
    # print(f"Validating object: {otype} - {oname}")

    # Get the class of the object
    cls = obj.__class__

    # Ensure the object is a dataclass
    if not is_dataclass(cls):
        create_error(obj, "Object is not a dataclass")
        return

    # Get the list of fields in the class
    flds = fields(cls)

    for fld in flds:
        # Get the value of the field in the object
        value = getattr(obj, fld.name, None)

        # Get the expected type of the field
        field_type = get_type_hints(cls).get(fld.name, None)

        # Check if the field is optional
        is_optional = is_optional_type(field_type)
        # if not is_optional:
        #     print("Required field?", fld)
        

        # If the value is None and the field is not optional, create an error
        if value is None:
            if not is_optional:
                create_error(obj, f"Required field '{fld.name}' is missing")
            continue

        # Perform deep type checking
        if not check_type(value, field_type):
            # print("check_type(value) - value is ", value)
            create_error(
                obj,
                f"For field '{fld.name}' - expected {field_type}, but got {type(value)}"
            )
def is_optional_type(field_type):
    """
    Check if a field type is Optional (i.e., Union[..., None]).
    """
    origin = get_origin(field_type)
    args = get_args(field_type)
    return origin is Union and type(None) in args

def check_type(value: Any, expected_type: Any) -> bool:
    """
    Recursively check if the value matches the expected type, including generics.
    """
    # print(f"Checking value: {value}, Expected type: {expected_type}")

    if expected_type is None:
        return True

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # If no origin, it's a simple type
    if origin is None:
        return isinstance(value, expected_type)

    # Handle Optional (Union[..., None])
    if origin is Union and type(None) in args:
        # Allow None or validate against the other type in the Union
        non_none_args = [arg for arg in args if arg is not type(None)]
        return value is None or any(check_type(value, arg) for arg in non_none_args)

    # Handle generic types
    if origin in {list, set}:
        if not isinstance(value, origin):
            return False
        if args:
            # Validate all elements in the list or set
            return all(check_type(item, args[0]) for item in value)

    if origin is dict:
        if not isinstance(value, dict):
            return False
        if args:
            key_type, value_type = args
            # Validate all keys and values in the dictionary
            return all(
                check_type(k, key_type) and check_type(v, value_type)
                for k, v in value.items()
            )

    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if len(args) == 2 and args[1] is Ellipsis:  # Tuple[X, ...]
            # Validate all elements in the tuple
            return all(check_type(item, args[0]) for item in value)
        # Validate fixed-length tuples
        return len(value) == len(args) and all(check_type(item, arg) for item, arg in zip(value, args))

    if origin is Callable:
        return callable(value)

    if expected_type is Any:
        return True

    # Add more cases for other generic types if needed
    return isinstance(value, expected_type)

# Helper function to validate entire model
def validate_model(model):
    """Validate an entire LDM model."""
    validate_component(model)
    validate_each(model.subjects)

    return All_Errors