from pydantic.dataclasses import dataclass
from pydantic import TypeAdapter

class PydanticMixin:
    def model_dump(self, **kwargs):
        # Use TypeAdapter for serialization
        adapter = TypeAdapter(type(self))
        return adapter.dump_python(self, **kwargs)
    
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