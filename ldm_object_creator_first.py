from typing import Dict, Any, List, Union, Optional, get_type_hints
from dataclasses import dataclass, field, is_dataclass, fields
import inspect
from utils_pom.util_json_pom import as_json
from utils_pom.util_flogging import trace_method
class ObjectCreator:
    """
    Creates objects from dictionary representations using a model module.
    
    This class handles the conversion of dictionary structures into the 
    appropriate dataclass instances based on the _type field in the dictionary.
    """
    
    def __init__(self, model_module):
        """
        Initialize the ObjectCreator with a model module.
        
        Args:
            model_module: Module containing the model class definitions
        """
        self.model_module = model_module
        self.class_map = self._build_class_map(model_module)
        print("CLASS MAP|n", self.class_map)
        
    def _build_class_map(self, model_module) -> Dict[str, Any]:
        """
        Build a map of type names to class objects from the model module.
        
        Args:
            model_module: Module containing model classes
            
        Returns:
            Dictionary mapping type names to class objects
        """
        class_map = {}
        
        # Check if there's a convenience list of all classes
        if hasattr(model_module, 'AllLDMClasses'):
            for cls in model_module.AllLDMClasses:
                if not inspect.isclass(cls):
                    continue
                    
                # Use class name by default
                class_map[cls.__name__] = cls
                
                # Check for _type field default in class definition
                if is_dataclass(cls):
                    for field_obj in fields(cls):
                        if field_obj.name == '_type' and field_obj.default is not None:
                            type_name = field_obj.default
                            class_map[type_name] = cls
                            break
        else:
            # Fallback to inspecting the module for dataclasses
            for name, obj in inspect.getmembers(model_module):
                if inspect.isclass(obj) and is_dataclass(obj):
                    # Use class name by default
                    class_map[name] = obj
                    
                    # Check for _type field default in class
                    for field_obj in fields(obj):
                        if field_obj.name == '_type' and field_obj.default is not None:
                            type_name = field_obj.default
                            class_map[type_name] = obj
                            break
        
        # # Add special handling for section types
        # class_map['Section2'] = model_module.SubjectB
        # class_map['Section3'] = model_module.SubjectC
        # class_map['Section4'] = model_module.SubjectD
        # class_map['Section5'] = model_module.SubjectE
        
        return class_map
    
    def create(self, data_dict: Dict[str, Any]) -> Any:
        """
        Create an object from a dictionary representation.
        
        Args:
            data_dict: Dictionary containing object data with a _type field
            
        Returns:
            Instantiated object of the specified type
        """
        # Handle None case
        if data_dict is None:
            return None
            
        # Get type from data
        type_name = data_dict.get('_type')
        if not type_name:
            print(f"MappingError: No _type specified in dictionary: {data_dict}")
            # If no _type is specified, try to guess based on dictionary keys
            type_name = self._guess_type(data_dict)
            
            if not type_name:
                raise ValueError(f"Cannot determine type for dictionary: {data_dict}")
        
        # Get the class for this type
        cls = self.class_map.get(type_name)
        if not cls:
            print(f"MappingError: Unknown type: {type_name}. Available types: {list(self.class_map.keys())}")
            # We'll just return the dictionary in this case
            return data_dict
        # print(f"FOUND THE TYPE. Creating {type_name} from dictionary: {data_dict}")
        # Create kwargs for instantiation
        kwargs = self._prepare_kwargs(cls, data_dict)
        
        # Create the object
        try:
            return cls(**kwargs)
        except Exception as e:
            print(f"MappingError: creating {type_name}: {str(e)}")
            print(f"With kwargs: {list(kwargs.keys())}")
            # Return the raw dictionary in case of error
            return data_dict
    
    @trace_method
    def _guess_type(self, data_dict: Dict[str, Any]) -> Optional[str]:
        """
        Attempt to guess the type based on dictionary keys.
        
        Args:
            data_dict: Dictionary to analyze
            
        Returns:
            Guessed type name or None if unable to determine
        """
        print("MappingError: Guessing type for dictionary:", data_dict)

        # Subject guessing based on prefix
        if 'prefix' in data_dict:
            prefix = data_dict.get('prefix')
            if prefix == '#':
                return 'LDM'
            elif prefix == '##':
                return 'SubjectB'
            elif prefix == '###':
                return 'SubjectC'
            elif prefix == '####':
                return 'SubjectD'
            elif prefix == '#####':
                return 'SubjectE'
            elif prefix == '_':
                return 'Class'
            elif prefix == '-':
                return 'Attribute'
            elif prefix == '__':
                return 'AttributeSection'
                
        # Look for type-distinctive fields
        if 'derivation' in data_dict:
            return 'Derivation'
        if 'constraint' in data_dict:
            return 'Constraint'
        if 'default' in data_dict and isinstance(data_dict['default'], str):
            return 'Default'
            
        return None
        
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
        
        
        import pprint
        # Get type hints for the class to determine expected types
        hints = get_type_hints(cls)
        # print(f"Type hints for {cls.__name__}: {pprint.pformat(hints)}")
        # Handle special cases for certain fields
        
        # Special handling for name field that may be in a different format
        if ('name' in data_dict and 'name' in hints and 
            data_dict['name'] and data_dict['name'] != ''):
            if isinstance(data_dict['name'], str):
                # Class with "ValueType: " prefix in name
                if data_dict['name'].startswith('ValueType: '):
                    data_dict['is_value_type'] = True
                    data_dict['name'] = data_dict['name'][10:]
                elif ':' in data_dict['name']:
                    # Split the name at the colon
                    parts = data_dict['name'].split(':', 1)
                    data_dict['name'] = parts[0].strip()
                    if len(parts) > 1 and parts[1].strip():
                        # If there's text after the colon, use it as the one_liner
                        if 'one_liner' not in data_dict or not data_dict['one_liner']:
                            data_dict['one_liner'] = parts[1].strip()
        
        # Process each field that appears in the data dictionary
        for field_name, field_value in data_dict.items():
            # Skip _type field since it's used for type determination, not as a parameter
            if field_name == '_type':
                continue
                
            # Special handling for certain fields
            if field_name == 'sectionS':
                # Map to the appropriate subjects field
                field_name = 'subjects'
                
            # Process the field based on its type
            # print(f"Processing field - getting kwarg: {field_name} with value: {field_value}")
            if field_name in hints:
                expected_type = hints[field_name]
                processed_value = self._process_value(field_value, expected_type)
                kwargs[field_name] = processed_value
            else:
                print(f"MappingError: dict field {field_name} has no matching model field for {cls.__name__}")
        
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
        # print(f"Processing  expected type: {expected_type} for value: {value}")
        # Check if we need to look at the string literal name for a forward reference
        if isinstance(expected_type, str):
            # Try to find the type in the module
            if hasattr(self.model_module, expected_type):
                expected_type = getattr(self.model_module, expected_type)
            else:
                print(f"MappingError: expected type is a string, but not found in module - {expected_type}")
                # Just return the value as-is if we can't resolve the type
                return value
            
        # Check if this is a list type
        origin = getattr(expected_type, '__origin__', None)
        if origin is list or origin is List:
            # Handle lists by processing each element
            if not isinstance(value, list):
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
            
        # Handle complex types (dictionaries that need to be converted to objects)
        elif isinstance(value, dict):
            # Special handling for TypedLine objects
            # if 'type_label' in value:
                # print(f"Checking for creation {value['type_label']}")

            if ('type_label' in value and 'content' in value and 
                hasattr(self.model_module, 'OneLiner')):
                # Create a OneLiner or Paragraph based on the type
                print(f"MappingError: Need special processing. Checking for creation {value['type_label']} from dictionary: {value}")
                if value['type_label'] == 'ELABORATION':
                    # Process the content as a list of paragraphs
                    print(f"Creating paragraphs for {value['type_label']}")
                    paragraphs = []
                    if isinstance(value['content'], list):
                        for item in value['content']:
                            if item.get('type_label') == 'PARAGRAPH':
                                # Process paragraph content
                                if 'content' in item and isinstance(item['content'], list):
                                    para_text = ' '.join([c.get('content', '') for c in item['content']])
                                    paragraphs.append(self.model_module.Paragraph(para_text))
                                elif 'content' in item:
                                    paragraphs.append(self.model_module.Paragraph(str(item['content'])))
                    print(f"Created {len(paragraphs)} paragraphs")
                    print(f"Paragraphs: {paragraphs}")
                    return paragraphs
                elif 'content' in value:
                    return self.model_module.OneLiner(str(value['content']))
                
            # If the value has a _type, recursively create the object
            if '_type' in value:
                return self.create(value)
                
            # If the expected type is a dataclass, try to instantiate it
            if (inspect.isclass(expected_type) and is_dataclass(expected_type) and 
                expected_type.__name__ in self.class_map):
                # Prepare kwargs for the dataclass
                kwargs = {}
                for field in fields(expected_type):
                    if field.name in value:
                        field_hint = get_type_hints(expected_type).get(field.name)
                        kwargs[field.name] = self._process_value(value[field.name], field_hint)
                
                # Create the object
                try:
                    return expected_type(**kwargs)
                except Exception as e:
                    print(f"MappingError: failed creating {expected_type.__name__}: {str(e)}")
                    return value
            
            # Just return the dictionary as-is if we can't match it to a class
            print(f"MappingError: NoClass for dictionary: {value}")
            return value
            
        # Handle simple types that don't need conversion
        elif isinstance(value, (str, int, float, bool)):
            # Special handling for CamelCase classes
            print(f"Checking for Camel simple type: {expected_type} for value: {value}")
            if (inspect.isclass(expected_type) and 
                expected_type.__name__ in ('UpperCamel', 'LowerCamel', 'CamelCase')):
                # Create the camel case instance
                # print("Creating CamelCase instance")
                try:
                    result =  expected_type(value)
                    # print(f"Created CamelCase instance: {result}")
                    # print(f"Created CamelCase instance - repr is : {repr(result)}")
                    return str(result)
                except:
                    print(f"MappingError: creating CamelCase instance for {value}")
                    return value
            return value
            
        # Fallback for other types
        return value