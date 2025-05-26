import ldm.Literate_01
import dataclasses
from dataclasses import dataclass, fields
from typing import Optional, List
from typing import get_args, get_origin, Tuple, Union, List


reference_types = {
    "SubjectB",
    "SubjectC",
    "SubjectD",
    "SubjectE",           
    "Class",
    "AttributeSection",
    "Attribute",
    "LDM",

}
def do_graph():
    
    classes = ldm.Literate_01.AllLDMClasses
    # for cls in classes:
    #     print(cls.__name__)
    triples = []
    for cls in classes:
        triples.extend(class_triples(cls))
    for x in triples:
        print(x)

def class_triples(cls):
    triples = []


    class_name = cls.__name__
    if not class_name in reference_types:
        return []
    bases = cls.__bases__

    for base in bases:
        triple = [class_name, "subtype_of", base.__name__]
        triples.append(triple)
    class_dict = get_fields_with_types(cls)
    for field_name, value in class_dict.items():
        triples.append([class_name, field_name, value])
    return triples

def get_fields_with_types(cls):
    if dataclasses.is_dataclass(cls) :
    
        field_types = {field.name: extract_inner_type(field.type) for field in fields(cls)}
    else: 
        print(f"{cls} is not a dataclass")
        field_types = {}
    return field_types

def extract_inner_type(tp):
    origin = get_origin(tp)
    if origin is Union:
        args = [arg for arg in get_args(tp) if arg is not type(None)]
        if len(args) == 1:
            return extract_inner_type(args[0])
        return tuple(extract_inner_type(arg) for arg in args)
    elif origin in (list, List):
        return extract_inner_type(get_args(tp)[0])
    elif origin is tuple or origin is Tuple:
        # Return a tuple of inner types for each element
        return tuple(extract_inner_type(arg) for arg in get_args(tp))
    else:
        return tp



if __name__ == "__main__":
    do_graph()
    