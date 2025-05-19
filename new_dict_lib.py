import json
import dataclasses
import inspect
import yaml
from typing import Any, Dict, List, Optional, Set, Union, get_type_hints

def object_to_dict(obj, max_depth=20, current_depth=0, visited=None):
    """
    Convert an object to a dictionary recursively with proper depth tracking.
    
    Args:
        obj: Object to convert
        max_depth: Maximum recursion depth to prevent infinite loops
        current_depth: Current recursion depth
        visited: Set of already visited object ids to prevent cycles
        
    Returns:
        Dictionary representation of the object
    """
    # Initialize visited set if not provided
    if visited is None:
        visited = set()
        
    # Check recursion depth
    if current_depth > max_depth:
        return "...[max depth reached]"
        
    # Handle None
    if obj is None:
        return None
        
    # Handle basic types
    if isinstance(obj, (str, int, float, bool)):
        return obj
        
    # Check for cycles (for objects that can be hashed)
    obj_id = id(obj)
    if obj_id in visited:
        return f"...[cycle detected: {type(obj).__name__}]"
    
    try:
        visited.add(obj_id)
    except:
        # Some objects might not be hashable, just continue
        pass
        
    # Handle lists
    if isinstance(obj, list):
        return [object_to_dict(item, max_depth, current_depth + 1, visited) 
                for item in obj]
        
    # Handle special LDM types - add specific handling for TypedLine objects
    if hasattr(obj, 'type_label') and hasattr(obj, 'content'):
        result = {
            "type": obj.type_label
        }
        if isinstance(obj.content, list):
            result["content"] = object_to_dict(obj.content, max_depth, current_depth + 1, visited)
        else:
            result["content"] = obj.content
        
        if hasattr(obj, 'extra_text') and obj.extra_text:
            result["extra_text"] = obj.extra_text
            
        return result
        
    # Handle dataclasses
    if dataclasses.is_dataclass(obj):
        result = {}
        
        # Add type information
        if hasattr(obj, '_type'):
            result['_type'] = obj._type
            
        # Convert all fields
        for field in dataclasses.fields(obj):
            # Skip internal fields (optional)
            if field.name.startswith('_') and field.name != '_type':
                continue
                
            value = getattr(obj, field.name)
            
            # Skip empty collections and None values
            if (isinstance(value, list) and not value) or value is None:
                continue
                
            # Process the field value
            result[field.name] = object_to_dict(
                value, max_depth, current_depth + 1, visited
            )
                
        return result
        
    # Handle dictionaries
    if isinstance(obj, dict):
        return {key: object_to_dict(value, max_depth, current_depth + 1, visited) 
                for key, value in obj.items()}
    
    # Handle custom string representation for other types
    try:
        return str(obj)
    except:
        return f"[Unserializable object of type {type(obj).__name__}]"


def model_to_json(model, indent=2, max_depth=20):
    """
    Convert a model object to a JSON string with proper depth handling.
    
    Args:
        model: Model object to convert
        indent: Indentation level for pretty printing
        max_depth: Maximum recursion depth
        
    Returns:
        JSON string representation
    """
    return json.dumps(
        object_to_dict(model, max_depth=max_depth),
        indent=indent,
        ensure_ascii=False
    )


def model_to_yaml(model, max_depth=20):
    """
    Convert a model object to YAML with proper depth handling.
    
    Args:
        model: Model object to convert
        max_depth: Maximum recursion depth
        
    Returns:
        YAML string representation
    """
    import yaml
    
    # Define a custom representer for sets
    def set_representer(dumper, data):
        return dumper.represent_sequence('tag:yaml.org,2002:seq', list(data))
    
    # Add the custom representer to the yaml dumper
    yaml.add_representer(set, set_representer)
    
    # Convert the object to a dictionary and then to YAML
    return yaml.dump(
        object_to_dict(model, max_depth=max_depth),
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True
    )
    

def serialize_model(obj, max_depth=20):
    """
    Serialize a model object to a dictionary, handling circular references and deep nesting.
    
    Args:
        obj: The model object to serialize
        max_depth: Maximum recursion depth
        
    Returns:
        A dictionary representation of the object
    """
    visited = set()
    
import json
import dataclasses
import inspect
from typing import Any, Dict, List, Optional, Set, Union, get_type_hints
from utils_pom.util_json_pom import clean_dict

def serialize_model(obj, max_depth=20):
    """
    Serialize a model object to a dictionary, handling circular references and deep nesting.
    
    Args:
        obj: The model object to serialize
        max_depth: Maximum recursion depth
        
    Returns:
        A dictionary representation of the object
    """
    visited = set()
    
    def _serialize(obj, depth=0):
        """Recursive helper function."""
        # Check recursion depth
        if depth > max_depth:
            return "[max depth reached]"
            
        # Handle None
        if obj is None:
            return None
            
        # Handle basic types
        if isinstance(obj, (str, int, float, bool)):
            return obj
            
        # Handle cycles using object ID
        obj_id = id(obj)
        if obj_id in visited:
            return f"[circular reference to {type(obj).__name__}]"
            
        visited.add(obj_id)
        
        # Handle lists
        if isinstance(obj, list):
            result = []
            for item in obj:
                result.append(_serialize(item, depth + 1))
            return result
            
        # Handle dataclasses
        if dataclasses.is_dataclass(obj):
            result = {}
            
            # Add type information
            if hasattr(obj, "_type"):
                result["_type"] = obj._type
                
            # Add all fields
            for field in dataclasses.fields(obj):
                # Skip private fields except _type
                if field.name.startswith("_") and field.name != "_type":
                    continue
                    
                value = getattr(obj, field.name)
                
                # Skip empty collections and None values for cleaner output
                if value is None or (isinstance(value, list) and len(value) == 0):
                    continue
                    
                result[field.name] = _serialize(value, depth + 1)
                
            return result
            
        # Handle dictionaries
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                result[key] = _serialize(value, depth + 1)
            return result

        if hasattr(obj, '__json__'):
            return obj.__json__()

        # Handle any other object type by using its string representation
        return str(obj)
            
    # Start the serialization
    return _serialize(obj)

def model_to_dict(model) -> dict:
    
    serialized = serialize_model(model)
    cleaned = clean_dict(serialized)
    return cleaned

def model_to_json_file(model, filename, indent=2):
    """
    Serialize a model to a JSON file.
    
    Args:
        model: The model object to serialize
        filename: The output filename
        indent: JSON indentation level
    """
    serialized = model_to_dict(model)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(serialized, f, indent=indent, ensure_ascii=False)
    print(f"Model serialized to {filename}")
    
    # Return a sample of the JSON for display
    json_str = json.dumps(serialized, indent=indent, ensure_ascii=False)
    return json_str[:200] + "..." if len(json_str) > 200 else json_str

def model_to_yaml_file(model, filename):
    """
    Serialize a model to a YAML file.
    
    Args:
        model: The model object to serialize
        filename: The output filename
    """
    serialized = model_to_dict(model)
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(serialized, f, sort_keys=False, default_flow_style=False)
    print(f"Model serialized to {filename}")
    
    # Return a sample of the YAML for display
    yaml_str = yaml.dump(serialized, sort_keys=False, default_flow_style=False)
    return yaml_str[:200] + "..." if len(yaml_str) > 200 else yaml_str