import warnings
from typing import Any, Type, List, Optional
from utils.util_pydantic import PydanticMixin,  dataclass, field
from utils.util_fmk import id_for, ids_for

@dataclass 
class Container():
    container: Optional["Container"]  = None
    # container: Optional["Container"] = field(default=None, kw_only=True)
    
    def shared_post_init(self):
        self.container = None

    def containees(self) -> List["Container"]:
        return []
    
    def clean_containees(self) -> List['Container']:
        
        containees0 = self.containees()
    
        cleaned = [c for c in containees0 if c and is_robust_instance(c, Container)]
        return cleaned
    
    def set_containees_back(self, parents = [], verbose = False):
        if not self:
            print("CBUG: None parent in set_containees back; skipping set-backs")
            return
        if not is_robust_instance(self, Container):
            print("CBUG: NonContainer parent in set_containees back; skipping set-backs")
            print(f"\t{type(self)} [{self}]")
            return 
        for c in self.clean_containees():
            if not c:
                print(f"CBUG: Null containee inside {type(self)}")
                continue
            if not is_robust_instance(c, Container):
                print(f"CBUG: Containee {type(c)} for {type(self)} is not a Container")
                print("***   ", self, "   ***")
                continue
            if c in parents:
                parents_list = [id_for(p) for p in parents]
                print(f"CBUG: ContainmentCycle: !!! Can't contain {c} in {self}; it's among the parents: {parents_list}")
                continue
            if verbose:
                print(f"Setting container of {id_for(c)} to {id_for(self)}")
            c.container = self
            c.set_containees_back(parents + [self], verbose=verbose)
        
    
    # Updated containing method using the robust checker
    def containing(self, ctype: Type) -> 'Container':
        """Find the nearest container of the specified type."""
        if not self.container:
            return None
        
        if is_robust_instance(self.container, ctype):
            return self.container
        # print("Trying selfcontainer: a ...", type(self), " contained in ", type(self.container))
        if type(self.container).__name__ == "FieldInfo":
            print(f"BUG: Seeking {ctype} above {id_for(self)}. has container = {id_for(self.container)},\n\tbut that has type  fieldinfo returning none")
            return None
        return self.container.containing(ctype)
    
    def all_contained(self, ctype: Type) -> List["Container"]:
        the_list = []
        
        for c in self.clean_containees():
            if not c:
                continue
            
            if is_robust_instance(c, ctype):
                the_list.append(c)
            the_list.extend(c.all_contained(ctype))
        return the_list

    def up_chain(self):
        chain = id_for(self)
        parent = self.container
        if not parent:
            return chain
        
        if "FieldInfo" in str(parent) :
            return chain + " -> " + "FieldInfo?" + id_for(parent)
        if not is_robust_instance(parent, Container):
            return chain + " -> " + "NonContainer: " + id_for(parent)
        
        return  chain + " -> " + parent.up_chain()

def show_containers(container: Container, indent = ""):
    for c in container.clean_containees():
        if not c:
            continue
        print(f"{indent}{id_for(container)} contains {id_for(c)}")
        show_containers(c, indent + "\t")

def is_robust_instance(obj: Any, ctype: Type) -> bool:
    """
    Check if obj is an instance of ctype, handling module import differences.
    
    Args:
        obj: The object to check
        ctype: The class/type to check against
        
    Returns:
        bool: True if obj is an instance of ctype (or equivalent class)
        
    Warns:
        If module path differences are detected and fallback matching is used
    """
    # First try the standard isinstance check
    if isinstance(obj, ctype):
        return True
    
    # If that fails, check for module path differences
    obj_class = type(obj)
    target_name = ctype.__name__
    
    # Check direct class name match
    if obj_class.__name__ == target_name:
        # Warn about module path mismatch
        obj_module = getattr(obj_class, '__module__', 'unknown')
        ctype_module = getattr(ctype, '__module__', 'unknown')
        
        if obj_module != ctype_module and False:
            warnings.warn(
                f"Module path mismatch detected: "
                f"object class {obj_class.__name__} from '{obj_module}' "
                f"vs expected class from '{ctype_module}'. "
                f"This suggests inconsistent imports. "
                f"Consider standardizing your import statements.",
                UserWarning,
                stacklevel=2
            )
        
        return True
    
    # Check inheritance chain for name matches
    for base in obj_class.__mro__:
        if base.__name__ == target_name:
            # Warn about module path mismatch in inheritance
            base_module = getattr(base, '__module__', 'unknown')
            ctype_module = getattr(ctype, '__module__', 'unknown')
            
            # if base_module != ctype_module:
            #     warnings.warn(
            #         f"Module path mismatch in inheritance: "
            #         f"object inherits from {base.__name__} in '{base_module}' "
            #         f"vs expected class from '{ctype_module}'. "
            #         f"This suggests inconsistent imports.",
            #         UserWarning,
            #         stacklevel=2
            #     )
            
            return True
    
    return False
# Optional: Helper function to detect and report all import inconsistencies
def check_import_consistency(*classes):
    """
    Check for import inconsistencies between classes.
    Useful for debugging import issues across your codebase.
    """
    class_info = []
    for cls in classes:
        if hasattr(cls, '__name__') and hasattr(cls, '__module__'):
            class_info.append({
                'name': cls.__name__,
                'module': cls.__module__,
                'class': cls
            })
    
    # Group by class name
    by_name = {}
    for info in class_info:
        name = info['name']
        if name not in by_name:
            by_name[name] = []
        by_name[name].append(info)
    
    # Report inconsistencies
    inconsistencies = []
    for name, infos in by_name.items():
        if len(infos) > 1:
            modules = [info['module'] for info in infos]
            if len(set(modules)) > 1:  # Different modules for same class name
                inconsistencies.append({
                    'class_name': name,
                    'modules': modules,
                    'classes': [info['class'] for info in infos]
                })
    
    if inconsistencies:
        print("Import inconsistencies detected:")
        for inc in inconsistencies:
            print(f"  Class '{inc['class_name']}' imported from: {inc['modules']}")
            print(f"    Classes are {'the same' if len(set(inc['classes'])) == 1 else 'different'} objects")
    else:
        print("No import inconsistencies detected.")
    
    return inconsistencies