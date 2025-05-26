class Faculty:
    """Base class for functionality providers (renderers, validators, etc.)"""
    
    # Class variables to track registered methods
    _registries = {}  # Maps faculty_type -> {(target_class, format) -> method}
    _common_handlers = {}  # Maps faculty_type -> {base_class -> common_handler}
    
    def __init__(self, faculty_type, model_module=None, classes=None):
        """Initialize a faculty instance."""
        self.faculty_type = faculty_type
        
        # Import model classes
        self.classes = {}
        if model_module:
            self.classes = self.import_model(model_module, classes)
        
        # Ensure registry exists
        self._ensure_registry(faculty_type)
    
    @classmethod
    def _ensure_registry(cls, faculty_type):
        """Ensure registry exists for the faculty type"""
        if faculty_type not in cls._registries:
            cls._registries[faculty_type] = {}
        if faculty_type not in cls._common_handlers:
            cls._common_handlers[faculty_type] = {}
        return cls._registries[faculty_type]
    
    def register_common_handler(self, base_class, handler):
        """Register a common handler method for a base class"""
        if self.faculty_type not in self._common_handlers:
            self._common_handlers[self.faculty_type] = {}
        self._common_handlers[self.faculty_type][base_class] = handler
    
    def register(self, target_class=None, format_name="default"):
        """Register a method for this faculty type, class, and format."""
        registry = self._ensure_registry(self.faculty_type)
        
        def decorator(method):
            # If no target class specified, try to infer from method annotation
            nonlocal target_class
            if target_class is None:
                # Try to infer from method annotation
                if hasattr(method, "__annotations__") and "self" in method.__annotations__:
                    target_class = method.__annotations__["self"]
            
            # If we still don't have a target class, use the method name
            if target_class is None:
                # Extract class name from method name (e.g., render_ldm -> LDM)
                method_name = method.__name__
                if "_" in method_name:
                    class_name = method_name.split("_")[-1].capitalize()
                    if class_name in self.classes:
                        target_class = self.classes[class_name]
            
            if target_class:
                registry[(target_class, format_name)] = method
                
                # Wrap method to automatically handle parent calls
                def wrapped_method(self):
                    result = method(self)
                    return result
                
                # Add parent handler attribute to method
                wrapped_method._handles_parent = True
                
                return wrapped_method
            return method
        return decorator
    
    def call_parent_method(self, obj):
        """Call parent method for an object"""
        method_found = False
        result = ""
        
        # Look through parent classes
        for parent_class in obj.__class__.__bases__:
            # Check if parent has a registered method
            parent_method = self._registries[self.faculty_type].get((parent_class, "default"))
            if parent_method:
                result += parent_method(obj)
                method_found = True
                break
            
            # Check if parent has a common handler
            if parent_class in self._common_handlers.get(self.faculty_type, {}):
                handler = self._common_handlers[self.faculty_type][parent_class]
                result += handler(obj)
                method_found = True
                break
        
        if not method_found:
            # Try with grandparents if needed
            for parent_class in obj.__class__.__bases__:
                for grandparent in parent_class.__bases__:
                    if grandparent in self._common_handlers.get(self.faculty_type, {}):
                        handler = self._common_handlers[self.faculty_type][grandparent]
                        result += handler(obj)
                        method_found = True
                        break
                if method_found:
                    break
        
        return result
    
    def apply(self, format_name="default", method_name=None):
        """Apply all registered methods for this faculty type and format."""
        registry = self._registries.get(self.faculty_type, {})
        
        # Default method name if not provided
        if method_name is None:
            if format_name == "default":
                method_name = f"{self.faculty_type}"
            else:
                method_name = f"{self.faculty_type}_{format_name}"
        
        # Apply all registered methods
        for (target_class, fmt), method in registry.items():
            if fmt == format_name:
                # Create wrapper that automatically calls parent
                def create_wrapper(method):
                    def wrapper(self):
                        # First call parent handler
                        result = self.faculty.call_parent_method(self)
                        # Then call our method
                        result += method(self)
                        return result
                    return wrapper
                
                # Only wrap if method doesn't already handle parent calls
                if not hasattr(method, "_handles_parent"):
                    wrapped = create_wrapper(method)
                    wrapped.faculty = self  # Store faculty reference
                    print(f"Applying method {method.__name__} to {target_class.__name__} with format {fmt}")
                    setattr(target_class, method_name, wrapped)
                else:
                    # Method already handles parents
                    print(f"Method {method.__name__} already handles parent calls, skipping wrapping.")
                    setattr(target_class, method_name, method)
    
    @staticmethod
    # First, let's modify the Faculty's import_model method to handle both module objects and strings
    def import_model(module_or_name, classes=None):
        """Import classes from a model module."""
        import importlib
        import inspect
        from dataclasses import is_dataclass
        
        # Check if we have a module object or a string
        if inspect.ismodule(module_or_name):
            module = module_or_name
        else:
            # It's a string, import it
            try:
                module = importlib.import_module(module_or_name)
            except ImportError as e:
                print(f"Error importing {module_or_name}: {e}")
                return {}
        
        # If no specific classes requested, import all
        if classes is None:
            result = {}
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and is_dataclass(obj):
                    result[name] = obj
            return result
        
        # Import specific classes
        imported = {}
        for name in classes:
            if hasattr(module, name):
                imported[name] = getattr(module, name)
        return imported