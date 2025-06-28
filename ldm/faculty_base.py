# faculty_base_v4.py
from typing import Dict, Callable, Any, Type
import sys
from functools import wraps
import utils.util_all_fmk as fmk

All_Patches_ByName = {}

def patch_on(target_class: Type):
    """Decorator to immediately patch a method onto a specific class."""
    def decorator(func):
        # Immediately patch the target class
        method_name = "validate"  # Fixed method name for validation
        
        # Create a proper method
        def create_method(original_func):
            def method(instance_self):
                return original_func(instance_self)
            method.__name__ = method_name
            method.__doc__ = original_func.__doc__
            return method
        
        patched_method = create_method(func)
        setattr(target_class, method_name, patched_method)
        All_Patches_ByName[target_class.__name__] = func
        
        print(f"Immediately patched {method_name} onto {target_class.__name__}")
        
        # Still mark it for tracking (optional)
        func._patch_target = target_class
        return func
    return decorator

def show_patches(patches):
    print("Patches are...")
    for target, func in patches.items():
        print(f"Function {func} patched to target {target}")
        
def faculty_class(cls):
    """Class decorator to set up a Faculty class."""
    # The patching is now done immediately by @patch_on decorators
    # This decorator can just add any utility methods if needed
    
    print(f"Faculty class {cls.__name__} created - methods patched immediately")
    print("returning from faculty class: All Patches By Name...")
    cls.all_patches = All_Patches_ByName
    print(All_Patches_ByName)
    return cls


def resolve_patched_method(faculty, obj, current_class_name = None):
    otype = getattr(obj, "_type", "No type?")
    oname = getattr(obj, "name", "NoName?")
    actual_type = type(obj).__name__
    # print(f"Resolving method for : {otype} == {oname} (actual type: {actual_type})")

    cls = type(obj)
    mro = [c.__name__ for c in cls.__mro__]
    
    # Note: MRO begins with type of object
    # print("\tmro for object is: ", mro)
    patched_func = None
    
    current_index = -1
    if current_class_name:
        try:
            current_index = mro.index(current_class_name)
        except ValueError:
            print(f"Warning: {current_class_name} not found in MRO: {mro}")

    # Look for next class in MRO that has a validator
    for next_class_name in mro[current_index + 1:]:
        patched_func = faculty.all_patches.get(next_class_name, None)
        if patched_func:
            print(f"..... found patched fn: {patched_func} on class: {next_class_name}")

            return patched_func
        if current_class_name:
            print(f"resolve_patched_method - no parent fn found after {current_class_name}")
            
        else:
            print(f"resolve_patched_method - No method found for {actual_type}")

    
