import inspect
from dataclasses import MISSING

class PydanticMixin:
    _type: str = ""

    def shared_post_init(self):
        """Override this for shared post-init logic. Use super().shared_post_init()."""
        pass

    def __post_init__(self):
        """Called by standard dataclasses after __init__"""
        self._type = type(self).__name__
        if USING_PYDANTIC:
            return
        self.shared_post_init()

    @model_validator(mode='after')
    def validate_and_process(self):
        """Called by Pydantic v2 after initialization"""
        self._type = type(self).__name__
        if not USING_PYDANTIC:
            print(f"!! For {self._type}: @model_validator() was called in standard mode!")
            return self
        self.shared_post_init()
        return self

    def get_field_order(self):
        fieldnames = getattr(self, "__field_order__", list(self.__dict__.keys()))
        exclusions = ['all_classes_p', 'all_class_names_p', 'class_index_p', 'plural_index_p', 'full_class_index_p', "container"]
        pruned_fieldnames = [item for item in fieldnames if item not in exclusions]
        return pruned_fieldnames

    def __repr__(self):
        fields = {name: getattr(self, name, None) for name in self.get_field_order()}
        field_str = ", ".join(f"{k}={repr(v)}" for k, v in fields.items())
        return f"{type(self).__name__}({field_str})"

    def to_typed_dict(self):
        def convert(val):
            if isinstance(val, PydanticMixin):
                return val.to_typed_dict()
            elif isinstance(val, list):
                return [convert(v) for v in val]
            elif isinstance(val, dict):
                return {k: convert(v) for k, v in val.items()}
            return val

        field_names = self.get_field_order()
        output = {"_type": getattr(self, "_type", type(self).__name__)}
        output.update({
            k: convert(getattr(self, k, None)) for k in self.get_field_order()
        })
        return output

    def run_post_init_if_needed(self):
        """Ensure that both __post_init__ and shared_post_init are called."""
        if hasattr(self, "__post_init__"):
            self.__post_init__()
        if hasattr(self, "shared_post_init"):
            self.shared_post_init()

    @classmethod
    def from_typed_dict(cls, data):
        """
        Recursively deserialize a _type-annotated dict into a dataclass instance.
        Uses the module context of the calling class to resolve types consistently.
        """
        # Get the module where the calling class is defined
        caller_module = inspect.getmodule(cls)
        
        def convert(value):
            if isinstance(value, dict) and "_type" in value:
                type_name = value["_type"]
                
                # First try: look for the class in the caller's module
                target_class = getattr(caller_module, type_name, None)
                
                if target_class is None:
                    # Fallback: try the global TYPE_REGISTRY
                    target_class = TYPE_REGISTRY.get(type_name)
                
                if target_class is None:
                    # Last resort: try to find it in any module that has the same class name
                    for registered_cls in TYPE_REGISTRY.values():
                        if registered_cls.__name__ == type_name:
                            target_class = registered_cls
                            break
                
                if target_class:
                    return target_class.from_typed_dict(value)
                else:
                    raise ValueError(f"Cannot resolve type '{type_name}' in module {caller_module.__name__}")
                    
            elif isinstance(value, list):
                return [convert(v) for v in value]
            return value

        intype = "??"
        if isinstance(data, dict):
            intype = data.get("_type", "NoneSpecified")
        
        converted_data = {k: convert(v) for k, v in data.items() if k != "_type"}
        
        if USING_PYDANTIC:
            instance = object.__new__(cls)
            for field in cls.__dataclass_fields__.values():
                name = field.name
                value = converted_data.get(name, field.default if field.default is not MISSING else None)
                setattr(instance, name, value)
            instance.run_post_init_if_needed()
            
            # Mark objects as created from typed dict to suppress warnings
            instance._creation_context = "from_typed_dict"
            
            outtype = getattr(instance, "_type", "NO_TYPE")
            if outtype in watching:
                print(outtype, " INSTANCE IS\n***\n", repr(instance))
                print("***")
            return instance
        else:
            result = cls(**converted_data)
            
            # Mark objects as created from typed dict to suppress warnings
            result._creation_context = "from_typed_dict"
            
            outtype = getattr(result, "_type", "NO_TYPE")
            if outtype in watching:
                print(outtype, " RESULT IS\n***\n ", repr(result))
                print("***")
            return result

    @classmethod
    def model_json_schema(cls):
        return TypeAdapter(cls).json_schema()


# Enhanced robust instance checker that respects creation context
def is_robust_instance(obj, ctype) -> bool:
    """
    Check if obj is an instance of ctype, handling module import differences.
    Suppresses warnings for objects created via from_typed_dict.
    """
    # First try the standard isinstance check
    if isinstance(obj, ctype):
        return True
    
    # If that fails, check for module path differences
    obj_class = type(obj)
    target_name = ctype.__name__
    
    # Check direct class name match
    if obj_class.__name__ == target_name:
        # Check if this object was created from typed dict
        suppress_warnings = getattr(obj, '_creation_context', None) == 'from_typed_dict'
        
        if not suppress_warnings:
            # Warn about module path mismatch
            obj_module = getattr(obj_class, '__module__', 'unknown')
            ctype_module = getattr(ctype, '__module__', 'unknown')
            
            if obj_module != ctype_module:
                import warnings
                warnings.warn(
                    f"Module path mismatch detected: "
                    f"object class {obj_class.__name__} from '{obj_module}' "
                    f"vs expected class from '{ctype_module}'. "
                    f"This suggests inconsistent imports.",
                    UserWarning,
                    stacklevel=2
                )
        
        return True
    
    # Check inheritance chain for name matches
    for base in obj_class.__mro__:
        if base.__name__ == target_name:
            return True
    
    return False


# Modified containing method for Container class
def containing(self, ctype):
    """Find the nearest container of the specified type."""
    if not self.container:
        return None
    
    if is_robust_instance(self.container, ctype):
        return self.container
    
    return self.container.containing(ctype)


# Alternative approach: Module-aware TYPE_REGISTRY
class ModuleAwareRegistry:
    """Registry that can resolve types from different module contexts."""
    
    def __init__(self):
        self.by_name = {}  # class_name -> list of classes
        self.by_module_and_name = {}  # (module_name, class_name) -> class
    
    def register(self, cls):
        """Register a class in the registry."""
        class_name = cls.__name__
        module_name = getattr(cls, '__module__', 'unknown')
        
        # Store by name
        if class_name not in self.by_name:
            self.by_name[class_name] = []
        self.by_name[class_name].append(cls)
        
        # Store by module and name
        self.by_module_and_name[(module_name, class_name)] = cls
    
    def get(self, class_name, context_module=None):
        """Get a class by name, preferring the context module."""
        if context_module:
            module_name = getattr(context_module, '__name__', str(context_module))
            key = (module_name, class_name)
            if key in self.by_module_and_name:
                return self.by_module_and_name[key]
        
        # Fallback to any class with that name
        classes = self.by_name.get(class_name, [])
        return classes[0] if classes else None


# Replace the global TYPE_REGISTRY with the module-aware one
TYPE_REGISTRY_NEW = ModuleAwareRegistry()

# Modified dataclass decorator to use new registry
def dataclass(*args, **kwargs):
    def wrapper(cls):
        if USING_PYDANTIC:
            config = kwargs.get("config", {})
            config.setdefault("repr", False)
            kwargs["config"] = config
        else:
            kwargs.setdefault("repr", False)

        cls = base_dataclass(**kwargs)(cls)
        
        # Register in both old and new registries for compatibility
        TYPE_REGISTRY[cls.__name__] = cls
        TYPE_REGISTRY_NEW.register(cls)
        
        return cls

    return wrapper(args[0]) if args else wrapper