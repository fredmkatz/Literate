from typing import Dict, Callable, Any, Type
import sys
from functools import wraps
import inspect

All_Patches_ByName = {}

def patch_on(target_class: Type, method_name: str = None):
    """Decorator to register a method for patching onto a specific class.
    
    Args:
        target_class: The class to patch the method onto
        method_name: Optional method name. If not provided, uses the decorated function's name
    """
    def decorator(func):
        # Use provided method name or function name
        actual_method_name = method_name or func.__name__
        
        # Store in registry with class name as key
        if target_class.__name__ not in All_Patches_ByName:
            All_Patches_ByName[target_class.__name__] = {}
        
        All_Patches_ByName[target_class.__name__][actual_method_name] = func
        
        print(f"Registered {actual_method_name} for {target_class.__name__}")
        
        # Mark the function for tracking
        func._patch_target = target_class
        func._patch_method_name = actual_method_name
        return func
    return decorator

def show_patches(patches):
    print("Patches are...")
    for target, methods in patches.items():
        for method_name, func in methods.items():
            print(f"Function {func.__name__} registered as {method_name} for target {target}")

class Faculty:
    """Base class for faculty objects that manage method patching."""
    
    def __init__(self):
        # Set up patches from global registry when instance is created
        self.all_patches = {}
        
        # Copy the global patches to this instance's structure
        for class_name, methods in All_Patches_ByName.items():
            if class_name not in self.all_patches:
                self.all_patches[class_name] = {}
            self.all_patches[class_name].update(methods)
        
        print("Faculty patches setup:")
        for target, methods in self.all_patches.items():
            for method_name, func in methods.items():
                print(f"  {target}.{method_name} -> {func.__name__}")
        
    def resolve_patched_method(self, obj, method_name: str, current_class_name: str = None):
        """Resolve the appropriate patched method for an object.
        
        Args:
            obj: The object to find a method for
            method_name: Name of the method to find
            current_class_name: Optional current class name for super() calls
        """
        otype = getattr(obj, "_type", "No type?")
        oname = getattr(obj, "name", "NoName?")
        actual_type = type(obj).__name__
        
        cls = type(obj)
        mro = [c.__name__ for c in cls.__mro__]
        
        current_index = -1
        if current_class_name:
            try:
                current_index = mro.index(current_class_name)
                # print(f"Looking for super method after {current_class_name} in MRO: {mro}")
            except ValueError:
                print(f"Warning: {current_class_name} not found in MRO: {mro}")

        # Look for method in MRO order (starting after current class if specified)
        for class_name in mro[current_index + 1:]:
            class_methods = self.all_patches.get(class_name, {})
            patched_func = class_methods.get(method_name, None)
            if patched_func:
                # print(f"Found {method_name} method: {patched_func} on class: {class_name}")
                return patched_func
        
        if current_class_name:
            print(f"No parent {method_name} method found after {current_class_name}")
        else:
            print(f"No {method_name} method found for {actual_type}")
        
        return None
    
    def call_super_method(self, obj, method_name: str, current_class_name: str = None):
        """Helper to call the next method in the MRO.
        
        Args:
            obj: The object to call the method on
            method_name: Name of the method to call
            current_class_name: Current class name (auto-detected if not provided)
        """
        # Auto-detect current class name if not provided
        if current_class_name is None:
            # Get the calling frame to determine current class
            frame = inspect.currentframe().f_back
            # Look for the method name in the frame's local variables or code
            current_class_name = self._detect_current_class(frame, obj)
        
        patched_func = self.resolve_patched_method(obj, method_name, current_class_name)
        if patched_func:
            return patched_func(obj)
        return None
    
    def _detect_current_class(self, frame, obj):
        """Attempt to detect the current class from the call stack."""
        # This is a bit tricky - we'll use the MRO and try to match against registered methods
        cls = type(obj)
        mro = [c.__name__ for c in cls.__mro__]
        
        # Get the function name from the frame
        func_code = frame.f_code
        func_name = func_code.co_name
        
        # Look through MRO to find which class this function belongs to
        for class_name in mro:
            class_methods = self.all_patches.get(class_name, {})
            if func_name in [f.__name__ for f in class_methods.values()]:
                print(f"Auto-detected current class: {class_name}")
                return class_name
        
        print(f"Could not auto-detect current class for {func_name}")
        return None

def faculty_class(cls):
    """Class decorator to set up a Faculty subclass."""
    
    # Make sure it inherits from Faculty
    if not issubclass(cls, Faculty):
        # Create a new class that inherits from both Faculty and the original class
        class_dict = dict(cls.__dict__)
        class_dict.pop('__dict__', None)  # Remove __dict__ descriptor
        class_dict.pop('__weakref__', None)  # Remove __weakref__ descriptor
        
        # Create new class inheriting from Faculty
        new_cls = type(cls.__name__, (Faculty,) + cls.__bases__, class_dict)
        
        # Copy over the patching setup
        _setup_faculty_patches(new_cls)
        
        print(f"Faculty class {new_cls.__name__} created inheriting from Faculty")
        return new_cls
    else:
        _setup_faculty_patches(cls)
        print(f"Faculty class {cls.__name__} created")
        return cls

def _setup_faculty_patches(cls):
    """Set up the patches dictionary for a faculty class."""
    # The patches will be set up in __init__ when the instance is created
    # This allows all @patch_on decorators to complete first
    pass