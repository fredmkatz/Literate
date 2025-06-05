from typing import Dict, Any, List, Union, Optional, get_type_hints
from dataclasses import is_dataclass, fields
import inspect
import logging

# from utils.util_flogging import flogger
import pprint


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ObjectCreator")
from utils.util_json import as_json, as_yaml


class GenericObjectCreator:
    """
    Generic object creator that transforms dictionaries into dataclass instances.

    This class handles the conversion of dictionary structures into the
    appropriate dataclass instances based on the _type field in the dictionary,
    without any domain-specific handling.
    """

    def __init__(self, model_module):
        """
        Initialize the object creator with a model module.

        Args:
            model_module: Module containing the model class definitions
        """
        self.model_module = model_module
        self.class_map = self._build_class_map()

    def _build_class_map(self) -> Dict[str, Any]:
        """
        Build a map of type names to class objects from the model module.

        Returns:
            Dictionary mapping type names to class objects
        """
        print(f"Building class map for module: {self.model_module.__name__}")
        logger.info(f"Building class map for module: {self.model_module.__name__}")
        class_map = {}

        # Find all dataclasses in the module
        for name, obj in inspect.getmembers(self.model_module):
            if inspect.isclass(obj) and is_dataclass(obj):
                # Use class name as the default type key
                class_map[name] = obj

                # Also use _type field default if available
                if is_dataclass(obj):
                    for field_obj in fields(obj):
                        if field_obj.name == "_type" and field_obj.default is not None:
                            type_name = field_obj.default
                            class_map[type_name] = obj
        print("Class map is")
        pretty_string = pprint.pformat(class_map, indent=4)
        print(pretty_string)

        return class_map

    from utils.util_flogging import trace_method, flogger

    # @trace_method
    def create(self, data_dict: Dict[str, Any]) -> Any:
        """
        Create an object from a dictionary representation.

        Args:
            data_dict: Dictionary containing object data with a _type field

        Returns:
            Instantiated object of the specified type or the original dictionary if creation fails
        """

        tracing = [
            "LiterateModel",
            "BaseDataType",
            "DataType",
            "ClassName",
            "AttributeName",
            "SubjectName",
            "Class",
        ]
        tracing = ["Class", "CodeType", "ValueType"]
        tracing = ["OneLiner", "BaseDataType"]
        tracing = ["Class"]
        tracing = ["Attribute"]

        # Handle None or empty dictionary case
        if data_dict is None or not data_dict:
            logger.warning("Empty or None dictionary provided")
            return None

        # Get type from data
        type_name = data_dict.get("_type")
        oname = data_dict.get("name", "Unnamed")

        # print(f"ObjectCreator Creating object of type: {type_name} - named {oname}")
        if not type_name:
            logger.warning(f"CREATOR No _type specified in dictionary: {data_dict}")
            return data_dict

        # Get the class for this type
        cls = self.class_map.get(type_name)
        if not cls:
            logger.warning(
                f"CREATOR Unknown type: {type_name}. Available types: {list(self.class_map.keys())}"
            )
            return data_dict
        if type_name in tracing:
            print(
                f"CREATOR Tracing {type_name} - type is {type(data_dict)} to {cls},\n dict = {as_yaml(data_dict)} "
            )

        # Create kwargs for instantiation
        kwargs = self._prepare_kwargs(cls, data_dict)

        if type_name in tracing:
            string = as_json(kwargs)
            # print(f"\n\nKWARGS are {kwargs}\n{string}")
        # Create the object
        try:
            the_obj = cls(**kwargs)
            finaltype = getattr(the_obj, "_type", "NoType")

            if type_name in tracing or finaltype != type_name:
                print(f"CREATOR ...Created object of type: {the_obj.__class__.__name__}")
                print(f"CREATOR ... str= {the_obj}")
                print("CREATOR ... model_dump= \n",  as_yaml(the_obj.model_dump()))
                print("CREATOR type() is ", type(the_obj))
                ostring = as_yaml(the_obj, warnings=True)
                print("final object is...\n ", ostring)
                
                print("CREATOR _type = ", finaltype)
                print("\n")

            return the_obj
        except Exception as e:  # todo - fix as_entered and revive this code
            logger.error(f"CREATOR: Error creating {type_name}: {str(e)}", exc_info=True)
            print("Source is ", data_dict)
            logger.error(f"CREATOR: Using kwargs: {list(kwargs.keys())}")
            return data_dict

    def _prepare_kwargs(self, cls: Any, data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare keyword arguments for class instantiation.

        Args:
            cls: Class to instantiate
            data_dict: Dictionary containing the data

        Returns:
            Dictionary of processed keyword arguments
        """
        kwargs = {}

        # Get type hints for the class
        hints = get_type_hints(cls)

        # Process each field in the data dictionary
        for field_name, field_value in data_dict.items():
            # Skip _type field since it's used for type determination
            if field_name == "_type":
                continue

            # Process the field if it exists in the class
            if field_name in hints:
                expected_type = hints[field_name]
                processed_value = self._process_value(field_value, expected_type)
                kwargs[field_name] = processed_value
            else:
                logger.warning(f"Field {field_name} not found in class {cls.__name__}")

        return kwargs

    def _process_value(self, value: Any, expected_type: Any) -> Any:
        """
        Process a value based on its expected type.

        Args:
            value: Value to process
            expected_type: Expected type for the value

        Returns:
            Processed value appropriate for the expected type
        """
        # Handle None
        if value is None:
            return None

        # Handle string literal type hints (forward references)
        if isinstance(expected_type, str):
            # Try to find the type in the module
            if hasattr(self.model_module, expected_type):
                expected_type = getattr(self.model_module, expected_type)
            else:
                logger.warning(
                    f"Type hint is a string literal, but not found in module: {expected_type}"
                )
                return value

        # Check if this is a list type
        origin = getattr(expected_type, "__origin__", None)
        if origin is list or origin is List:
            # Handle lists by processing each element
            if not isinstance(value, list):
                logger.warning(f"Expected list but got {type(value)}")
                return []

            element_type = expected_type.__args__[0]
            return [self._process_value(item, element_type) for item in value]

        # Check if this is an Optional type
        elif origin is Union and type(None) in expected_type.__args__:
            # Extract the non-None type
            for arg in expected_type.__args__:
                if arg is not type(None):
                    return self._process_value(value, arg)
            return None

        # Handle dictionary value that should be converted to an object
        elif isinstance(value, dict) and "_type" in value:
            # Recursively create objects for nested dictionaries
            return self.create(value)

        # Handle simple value types (including dataclass instances)
        elif isinstance(value, (str, int, float, bool)):
            # No special handling for primitive types
            return value

        # Return the value as-is for other cases
        return value
