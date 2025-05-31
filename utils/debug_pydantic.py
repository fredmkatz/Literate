from pydantic.dataclasses import dataclass, Field
field = Field
def debug_dataclass_creation(cls):
    print(f"Processing class: {cls.__name__}")
    for name, annotation in cls.__annotations__.items():
        print(f"  Field: {name} -> {annotation}")
        if hasattr(cls, name):
            default_val = getattr(cls, name)
            print(f"    Default: {default_val} (type: {type(default_val)})")
    
    try:
        return dataclass(cls)
    except Exception as e:
        print(f"ERROR in {cls.__name__}: {e}")
        raise

