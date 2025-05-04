from typing import Dict, Any, List, Union

    


def create_model_from_dict(metamodel, metaclasses, model_dict: Dict) -> Any:
    print("Creating model from dict")
    # print(as_json(model_dict))
    # print("Model dict is: ", model_dict)
    # print("Model is: ", model)
    # print("Model dict is: ", model_dict)
    # print("Model dict is: ", model_dict)
    
    print(f"model is {metamodel}")
    print(f"classes are {metaclasses}")
    metas_by_name = {x.__name__: x for x in metaclasses}
    print("Metas by name: ", metas_by_name)   
    
    the_object = create_obect_for_class_named("LDM", metas_by_name)
    if not the_object:
        print(f"ERROR: No class found for LDM")
        return None
    the_object.name = "The NAME"
    print("The object is ", the_object)   
    return None
    # return model(**model_dict)  # type: ignore
    
def create_obect_for_class_named(class_name: str, metas_by_name: Dict) -> Any:
    # print("Creating object for class named")
    # print(f"Class name is {class_name}")
    # print(f"Meta by name is {metas_by_name}")
    the_class = metas_by_name.get(class_name, None)
    if not the_class:
        print(f"ERROR: No class found for {class_name}")
        return None
    # print("The class is ", the_class)
    return the_class()