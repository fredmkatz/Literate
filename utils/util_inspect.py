from pydantic.dataclasses import dataclass
import dataclasses
import inspect

import utils.util_all_fmk as fmk

def get_classes_in_module(module):
    return [obj for name, obj in inspect.getmembers(module) if inspect.isclass(obj)]

def inspect_module(module, outfile_name, outfile_dir):
    all_classes =  get_classes_in_module(module)
    class_dict = {}
    for cls in all_classes:
        name = cls.__name__
        qualified = str(cls)
        mro = [c.__name__ for c in cls.__mro__]
        # fields =  [f.name for f in fields(cls)]
        
        cdict = {}
        cdict["name"] = name
        cdict["qualified"] = qualified
        cdict["mro"] = str(mro)
        cdict["rmro"] = str(mro[::-1])
        
        class_dict[name] = cdict
        
        # print(cls.__name__, " Qualified: ", qualified)
        # print(cls.__name__, " MRO: ",  mro)
        # print(cls.__name__, " to_typed_dict: ", cls.to_typed_dict)
        # if dataclasses.is_dataclass(cls):
            # print(cls.__name__, " fields: ", [f.name for f in cls.__fields__])
        # print(cls.__name__, " to_typed_dict: ", cls.vars())
    fmk.write_yaml(class_dict, f"{outfile_dir}/{outfile_name}")
    

