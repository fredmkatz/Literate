from typing import Any, get_type_hints, get_origin, get_args, Optional, Union, Literal, Callable
from dataclasses import fields, is_dataclass

all_validation_errors = []
def create_error(obj, message):
    """
    Helper function to log or handle validation errors.
    """
    error = f"Field Validation Error in {getattr(obj, '_type', 'Unknown Type')}: {message}"
    print(error)
    all_validation_errors.append(error)
    

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
    print(f"Validating object: {otype} - {oname}")

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
        if not is_optional:
            print("Required field?", fld)
        

        # If the value is None and the field is not optional, create an error
        if value is None:
            if not is_optional:
                create_error(obj, f"Required field '{fld.name}' is missing")
            continue

        # Perform deep type checking
        if not check_type(value, field_type):
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
    if expected_type is None:
        return True

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    # If no origin, it's a simple type
    if origin is None:
        return isinstance(value, expected_type)

    # Handle generic types
    if origin in {list, tuple, set}:
        if not isinstance(value, origin):
            return False
        if args:
            return all(check_type(item, args[0]) for item in value)

    if origin is dict:
        if not isinstance(value, dict):
            return False
        if args:
            key_type, value_type = args
            return all(
                check_type(k, key_type) and check_type(v, value_type)
                for k, v in value.items()
            )

    if origin is Union:
        return any(check_type(value, arg) for arg in args)

    if origin is Literal:
        return value in args

    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if len(args) == 2 and args[1] is Ellipsis:  # Tuple[X, ...]
            return all(check_type(item, args[0]) for item in value)
        return len(value) == len(args) and all(check_type(item, arg) for item, arg in zip(value, args))

    if origin is Callable:
        return callable(value)

    if origin is deque:
        if not isinstance(value, deque):
            return False
        if args:
            return all(check_type(item, args[0]) for item in value)

    if expected_type is Any:
        return True

    if origin is type:
        return isinstance(value, type) and issubclass(value, args[0])

    # Add more cases for other generic types if needed
    return False