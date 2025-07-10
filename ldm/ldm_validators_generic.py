from dataclasses import dataclass, field, fields, is_dataclass

import typing
from typing import (
    Any,
    Tuple,
    get_type_hints,
    get_origin,
    get_args,
    Optional,
    Union,
    Literal,
    Callable,
)

def create_field_error(obj, category, message):
    """
    Helper function to log or handle validation errors.
    """
    
    from ldm.ldm_validators_v3 import createBug
    createBug(obj, category,  message)


def check_type(value: Any, expected_type: Any) -> bool:
    """
    Recursively check if the value matches the expected type, including generics.
    Fixed to handle module import issues.
    """
    # print(f"Checking value: {value}, Expected type: {expected_type}")

    if expected_type is None:
        return True

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # If no origin, it's a simple type
    if origin is None:
        return check_simple_type(value, expected_type)

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
        return len(value) == len(args) and all(
            check_type(item, arg) for item, arg in zip(value, args)
        )

    if origin is Callable:
        return callable(value)

    if expected_type is Any:
        return True

    # Add more cases for other generic types if needed
    return check_simple_type(value, expected_type)


def check_simple_type(value: Any, expected_type: Any) -> bool:
    """
    Check simple (non-generic) types, handling module import issues.
    """
    
    if expected_type == typing.Any:
        return True

    # Direct isinstance check
    if isinstance(value, expected_type):
        return True
    
    # If that fails, check if it's the same class name from different modules
    if hasattr(expected_type, '__name__') and hasattr(value, '__class__'):
        expected_name = expected_type.__name__
        actual_name = value.__class__.__name__
        
        if expected_name == actual_name:
            # Same class name - probably same class from different imports
            # print(f"Type name match: {expected_name} == {actual_name} (different modules)")
            return True
        
        # Check if it's a subclass relationship
        try:
            if issubclass(value.__class__, expected_type):
                return True
        except TypeError:
            # expected_type might not be a class
            pass
    
    return False


def validate_fields(obj: Any):
    """
    Improved field validation that's more forgiving of module import issues.
    """
    if not obj:
        print("Null object in validate_object")
        return

    otype = getattr(obj, "_type", "No type?")
    oname = getattr(obj, "name", "NoName?")

    # Get the class of the object
    cls = obj.__class__

    # Ensure the object is a dataclass
    if not is_dataclass(cls):
        create_field_error(obj, "Non DataClass", "Object is not a dataclass")
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

        # If the value is None and the field is not optional, create an error
        if value is None:
            if not is_optional:
                create_field_error(obj, "MissingValue", f"Required field '{fld.name}' is missing")
            continue

        # Skip validation for certain problematic fields temporarily
        if should_skip_field_validation(fld.name, field_type, value):
            continue

        # Perform deep type checking
        if not check_type(value, field_type):
            create_field_error(
                obj, "InvalidFieldType",
                f"For field '{fld.name}' - expected {field_type}, but got {type(value)}"
            )


def should_skip_field_validation(field_name: str, field_type: Any, value: Any) -> bool:
    """
    Determine if we should skip validation for certain problematic fields.
    """
    # Skip diagnostics field if it's a plain list - we know this is usually correct
    if field_name == 'diagnostics' and isinstance(value, list):
        # Could add more sophisticated checking here
        return False  # Don't skip - let it validate properly
    
    # Skip other known problematic fields temporarily
    # Add more conditions here as needed
    
    return False



def is_optional_type(field_type):
    """
    Check if a field type is Optional (i.e., Union[..., None]).
    """
    origin = get_origin(field_type)
    args = get_args(field_type)
    return origin is Union and type(None) in args

def check_basic_type_compatibility(value: Any, expected_type: Any) -> bool:
    """Check only basic type compatibility, ignoring complex generic details."""
    origin = get_origin(expected_type)
    
    # Handle Optional
    if origin is Union and type(None) in get_args(expected_type):
        non_none_args = [arg for arg in get_args(expected_type) if arg is not type(None)]
        expected_type = non_none_args[0] if non_none_args else Any
        origin = get_origin(expected_type)
    
    # Check basic container types
    if origin is list and not isinstance(value, list):
        return False
    if origin is dict and not isinstance(value, dict):
        return False
    if origin is tuple and not isinstance(value, tuple):
        return False
    
    # For non-generic types, be lenient about class names
    if origin is None:
        return check_simple_type(value, expected_type)
    
    return True  # Be lenient about everything else