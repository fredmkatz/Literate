"""
Pydantic-compatible dataclass utilities.

This file allows you to write code that works identically with either:
- Python standard dataclasses, or
- Pydantic v2 dataclasses

---------------------------------------------------
🔧 Usage:

1. In your model files, do:

    from util_pydantic import dataclass, field, PydanticMixin

2. Use:
    @dataclass        # provided by this module (not standard!)
    field(...)        # not Field
    class MyClass(PydanticMixin, ...): ...

3. Inside your class, override:
    def shared_post_init(self):
        super().shared_post_init()
        ... # your logic here

Avoid defining your own __post_init__ or @model_validator. This mixin reroutes both.

---------------------------------------------------
🛠 Features:
- Automatically selects Pydantic or standard dataclass based on USING_PYDANTIC.
- Automatically sets the `_type` field to the class name.
- Unified `model_dump`, `model_validate`, `model_json_schema`.
- Supports clean __repr__() and field ordering.
- Deserialization dispatcher based on `_type`.

"""

import json
from pydantic import TypeAdapter, model_validator
from dataclasses import MISSING



# Optional dependency, used in gen_schema
import utils.util_all_fmk as fmk


# 🔁 Toggle this to switch between standard and Pydantic behavior

USING_PYDANTIC = False
USING_PYDANTIC = True
USING_PYDANTIC = True
USING_PYDANTIC = False

print("### USING_PYDANTIC =", USING_PYDANTIC)

# 🔁 Dynamically choose which dataclass/field to use
if USING_PYDANTIC:
    from pydantic.dataclasses import dataclass as base_dataclass
    from pydantic import Field as base_field
else:
    from dataclasses import dataclass as base_dataclass, field as base_field

# 🧠 Registry for polymorphic deserialization
TYPE_REGISTRY = {}

def typing_of(x):
    xtype = type(x)
    x_type = ""
    if isinstance(x, dict):
        x_type = x.get("_type", "no_type")
    else:
        x_type = getattr(x, "_type", "No_Type")
    return f"{xtype} : {x_type}"

# 🧠 Unified @dataclass decorator with auto-registration
def dataclass(*args, **kwargs):
    def wrapper(cls):
        # 👇 Make sure mixin __repr__ is not overridden
        if USING_PYDANTIC:
            config = kwargs.get("config", {})
            config.setdefault("repr", False)
            kwargs["config"] = config
        else:
            kwargs.setdefault("repr", False)

        cls = base_dataclass(**kwargs)(cls)
        TYPE_REGISTRY[cls.__name__] = cls
        return cls

    return wrapper(args[0]) if args else wrapper

# 🔁 Compatible field() alias
field = base_field


# =============================================================================
# 📦 Main Mixin for compatibility
# =============================================================================
watching = ["Attribute", "Class"]
watching = []
def using():
    if USING_PYDANTIC:
        return "UsingPydantic - "
    return "NOT UsingPydantic - "
class PydanticMixin:
    _type: str = ""  # auto-set to class name

    def shared_post_init(self):
        """Override this for shared post-init logic. Use super().shared_post_init()."""
        pass

    def __post_init__(self):
        """Called by standard dataclasses after __init__"""
        self._type = type(self).__name__
        if USING_PYDANTIC:
            # print(f"!! For {self._type}: post_init() was called under Pydantic!")
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
        # print("get_field_order for ", self)   ## TODO - Causes look
        return getattr(self, "__field_order__", list(self.__dict__.keys()))

    def __repr__(self):
        fields = {name: getattr(self, name, None) for name in self.get_field_order()}
        field_str = ", ".join(f"{k}={repr(v)}" for k, v in fields.items())
        return f"{type(self).__name__}({field_str})"

    def repr(self):
        return self.__repr__()

    
    def to_typed_dict(self):
        def convert(val):
            if isinstance(val, PydanticMixin):
                return val.to_typed_dict()
            elif isinstance(val, list):
                return [convert(v) for v in val]
            elif isinstance(val, dict):
                return {k: convert(v) for k, v in val.items()}
            return val
        # print(f"{using()} to_typed_dict: {typing_of(self)}")
        field_names = self.get_field_order()
        # print(f"\t{typing_of(self)} field names are: ", field_names)

        output = {"_type": getattr(self, "_type", type(self).__name__)}
        
        output.update({
            k: convert(getattr(self, k, None)) for k in self.get_field_order()
        })
        return output

    
    def run_post_init_if_needed(instance):
        """Ensure that both __post_init__ and shared_post_init are called.
        This mimics dataclass lifecycle behavior when bypassing __init__ (e.g., via object.__new__).
        """
        if hasattr(instance, "__post_init__"):
            instance.__post_init__()
        if hasattr(instance, "shared_post_init"):
            instance.shared_post_init()


    @classmethod
    def from_typed_dict(cls, data):
        """Recursively deserialize a _type-annotated dict into a dataclass instance.
        If USING_PYDANTIC, bypass validation by manually constructing the object.
        """
        def convert(value):
            if isinstance(value, dict) and "_type" in value:
                subcls = TYPE_REGISTRY.get(value["_type"])
                if subcls:
                    return subcls.from_typed_dict(value)
            elif isinstance(value, list):
                return [convert(v) for v in value]
            return value

        intype = "??"
        # print(f"{using()} from_type_dict: converting: ", cls.__name__)
        if isinstance(data, dict):
            intype = data.get("_type", "NoneSpecified")
            # print('\tincoming type is ', typing_of(data))
        converted_data = {k: convert(v) for k, v in data.items() if k != "_type"}
        # converted_data = {k: convert(v) for k, v in data.items() }
        
        if USING_PYDANTIC:
            instance = object.__new__(cls)
            for field in cls.__dataclass_fields__.values():
                name = field.name
                value = converted_data.get(name, field.default if field.default is not MISSING else None)
                setattr(instance, name, value)
            instance.run_post_init_if_needed()
            outtype = getattr(instance, "_type", "NO_TYPE")
            # print(f'\tOutgoing type for {intype} instance is... ', typing_of(instance))
            if outtype in watching:
                print(outtype, " INSTANCE IS\n***\n", repr(instance))
                print("***")

            return instance

        else:
            result =  cls(**converted_data)
            outtype = getattr(result, "_type",  "NO_TYPE")
            # print(f'\tOutgoing type for {intype} result is... ', typing_of(result))
            if outtype in watching:
                print(outtype, " RESULT IS\n***\n ", repr(result))
                print("***")

            return result



    @classmethod
    def model_json_schema(cls):
        return TypeAdapter(cls).json_schema()


# =============================================================================
# 🔁 Deserialize from dict with _type-dispatching
# =============================================================================
def object_from_typed_dict(data):
    if not isinstance(data, dict) or "_type" not in data:
        raise ValueError("Expected a dict with a '_type' field")
    cls = TYPE_REGISTRY.get(data["_type"])
    if cls is None:
        raise ValueError(f"Unknown type: {data['_type']}")
    return cls.from_typed_dict(data)




# =============================================================================
# 📤 Optional: Generate a JSON/YAML schema for a model
# =============================================================================

def gen_schema(the_model, model_name, schema_dir):
    print("Generate schema...")
    class_schema = the_model.model_json_schema()
    schema_yaml = fmk.as_yaml(class_schema, warnings=False)
    fmk.write_text(f"{schema_dir}/{model_name}_schema.yaml", schema_yaml)


# =============================================================================
# 🧪 Example / Test
# =============================================================================

if __name__ == "__main__":
    @dataclass
    class User(PydanticMixin):
        name: str
        age: int

    user = User(name="Alice", age=30)
    print("\nPydantic attributes:", [a for a in dir(user) if 'pydantic' in a.lower()])
    print("Class attributes:", [a for a in dir(User) if 'pydantic' in a.lower()])

    print("\n.model_dump:")
    print(user.model_dump())

    print("\n.model_dump_json:")
    print(user.model_dump_json(indent=4))

    print("\n.model_validate:")
    new_user = User.model_validate({"name": "Bob", "age": 25})
    print(new_user)
