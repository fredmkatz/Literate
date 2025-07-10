from jsonschema import validate
from jsonschema import Draft7Validator
import utils.util_all_fmk as fmk
from typing import Any

def read_object(object_path) -> Any:
    if object_path.endswith(".yaml"):
        obj = fmk.read_yaml_file(object_path)
        return obj
    if object_path.endswith(".json"):
        obj = fmk.read_json_file(object_path)
        return obj
    print("read_object requires a .json path or a .yaml path")
    return {}
    

def validate_to_schema(schema_path = "", object_path = "") -> bool:
    schema = read_object(schema_path)
    print("Schema path is: ", schema_path)
    # print("SCHEMA is")
    # print(schema)

    print("Object  path is: ", object_path)

    obj = read_object(object_path)

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(obj), key=lambda e: e.path)
    if errors:
        print(len(errors), " validation errors found!")
        for error in errors:
            print(f"Error at path: {list(error.path)},\nMessage: {error.message}")
            print()
        print(len(errors), " validation errors found!")

    else:
        print("Validation successful!")    # validate(instance=obj, schema=schema)
    # print("Object is")
    # print(obj)
    

if __name__ == "__main__":
    model_name = "Literate"
    model_path = f"ldm/ldm_models/{model_name}"
    schema_name = "LiterateMetaModel_01_PD_schema.yaml"
    schema_path = f"{model_path}/{model_name}_results/{model_name}Meta/{schema_name}"
    
    object_name = "Literate_PD_03.model.yaml"
    object_name = "Literate_PD_04.v_model.json"
    
    object_path = f"{model_path}/{model_name}_results/{object_name}"
    

    validate_to_schema(schema_path=schema_path, object_path=object_path)
    
    
    import yaml
    import json
    from ldm.Literate_01 import Cardinality

    # Test direct serialization
    test_data = {"cardinality": Cardinality.ONE_ONE}
    yaml_output = yaml.dump(test_data)
    print(yaml_output)
    print(repr(yaml_output))
    
    print("\nand now in json")
    json_output = json.dumps(test_data)
    print(json_output)
