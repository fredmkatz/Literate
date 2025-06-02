""" Usage notes:
    This file provides a way to develop with dataclasses or Pydantic dataclasses

    -   In the file defining dataclasses, first 
        from util_pydantic import PydanticMixin, dataclass, field
        
    - use @dataclass to announce your dataclasses
    - use "field", not "Field" to introduce fields for the dataclass
    - use the PydanticMixin, so:
            MyClass(PydanticMixin, ... other supertypes ...)


    Aside from aliasing dataclass to normal or Pydantic data classes, the mixin
    handles the following fact:
    -   In normal dataclasses, there's a __post_init__ method, called after
        __init__() has finished its work.
    -   In Pydantic dataclasses, __post_init__() is not called, instead a
        method marked as @model_validator will be called

    The mixin handles this by rerouting calls to __post_init__() or to
    the @modelvalidator to a method, shared_post_init().  So
    -  do not use post_init() or @model_validator in your code.
    Always use shared_post_init() instead of either
    And, as with __post_init__s, remmember to start off with a call
    to super, as in
    
        def shared_post_init(self):
            super().shared_post_init()
    
    Flag in util_pydantic_compat, USING_PYDANTIC controls which flavor
    of dataclass to use
    
    Also _type introduced in Pydantic Mixin


"""
from pydantic import TypeAdapter, model_validator

USING_PYDANTIC = False
USING_PYDANTIC = True

print("### USING_PYDANTIC = ", USING_PYDANTIC)

if USING_PYDANTIC:
    from pydantic.dataclasses import dataclass as base_dataclass
    from pydantic import Field as base_field
else:
    from dataclasses import dataclass as base_dataclass, field as base_field

def dataclass(*args, **kwargs):
    if USING_PYDANTIC:
        config = kwargs.get("config", {})
        config.setdefault("repr", False)
        kwargs["config"] = config
    else:
        kwargs.setdefault("repr", False)
    return base_dataclass(*args, **kwargs)

dataclass = dataclass
field = base_field



class PydanticMixin:

    _type: str #= field(init=False)

    def shared_post_init(self):
        pass  # override in subclasses as needed
    
    def __post_init__(self):    # will only be used for normal dataclasses
        the_type_name = type(self).__name__
        self._type = type(self).__name__
        print("PostInit assigning type: ", self._type)

        if USING_PYDANTIC:
            print(f"!!\tFor {the_type_name}: Using PYDANTIC, but post_init was called")
            return
        # self.using_normal = True
        self.shared_post_init()


    @model_validator(mode='after')  # will only be used by Pydantic
    def validate_and_process(self):
        the_type_name = type(self).__name__
        self._type = type(self).__name__
        print("Pydantic assigning type: ", self._type)

        if not USING_PYDANTIC:
            print(f"!!\tFor {the_type_name}, Not Using PYDANTIC, but @model_validator was called")
            return

        # self.using_pydantic = True
        
        self.shared_post_init()

        return self


    def get_field_order(self):
        return getattr(self, "__field_order__", list(self.__dict__.keys()))


    def __repr__(self):
        # print("Called __repr__ in PyCompat")
        fields = {name: getattr(self, name, None) for name in self.get_field_order()}
        field_str = ", ".join(f"{k}={repr(v)}" for k, v in fields.items())
        return f"{type(self).__name__}({field_str})"
    
    def repr(self):
        return self.__repr__()
    def model_dump(self):
        return {k: getattr(self, k, None) for k in self.get_field_order()}


    # def model_dump(self, **kwargs):
    #     # Use TypeAdapter for serialization
    #     adapter = TypeAdapter(type(self))
    #     return adapter.dump_python(self, **kwargs)
    
    def model_dump_json(self, **kwargs):
        adapter = TypeAdapter(type(self))
        return adapter.dump_json(self, **kwargs)
    
    @classmethod
    def model_validate(cls, data):
        adapter = TypeAdapter(cls)
        return adapter.validate_python(data)
    
    @classmethod 
    def model_validate_json(cls, json_data):
        adapter = TypeAdapter(cls)
        return adapter.validate_json(json_data)

    @classmethod 
    def model_json_schema(cls):
        adapter = TypeAdapter(cls)
        return adapter.json_schema()


import json

import utils.util_all_fmk as fmk

def gen_schema(the_model, model_name, schema_dir):
    print("Generate schema")
    class_schema = the_model.model_json_schema()
    schema_json = json.dumps(class_schema, indent=2)
    schema_yaml = fmk.as_yaml(class_schema)
    # print(schema_json)

    json_schema_path = f"{schema_dir}/{model_name}_schema.json"
    yaml_schema_path = f"{schema_dir}/{model_name}_schema.yaml"
    fmk.write_text(json_schema_path, schema_json)
    fmk.write_text(yaml_schema_path, schema_yaml)

# if __name__ == "__main__":
    # from ldm.Literate_01 import LiterateModel

#     gen_schema( LiterateModel, "Literate", "trials")

if __name__ == "__main__":
    @dataclass
    class User(PydanticMixin):
        name: str
        age: int

    # Test it
    user = User(name="Alice", age=30)

    # Let's see what pydantic-related attributes are available
    pydantic_attrs = [attr for attr in dir(user) if 'pydantic' in attr.lower()]
    print("\nPydantic attributes:", pydantic_attrs)

    # Also check the class
    class_pydantic_attrs = [attr for attr in dir(User) if 'pydantic' in attr.lower()]
    print("\nClass pydantic attributes:", class_pydantic_attrs)

    print("\n.test dump")

    user_dict = user.model_dump()
    print(user_dict)  # Should work now

    print("\n.test dump to json")

    user_dict = user.model_dump_json(indent = 4)
    print(user_dict)  # Should work now

    print("\n.test validation")
    # Also test validation
    new_user = User.model_validate({"name": "Bob", "age": 25})
    print(new_user)

    print("\n.test validation for false")
    # # Also test validation
    # new_user = User.model_validate({"name": 23, "age": 25})
    # print(new_user)


    # Now works as expected:
    user_dict = user.model_dump()
    
    
