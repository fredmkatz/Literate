from typing import List, Any
from collections import defaultdict

from faculty_base_v3 import Faculty, faculty_class, patch_on, show_patches
from ldm.Literate_01 import *

from utils.util_flogging import trace_decorator

Reserved_Words = [
    "Class",
]

All_Trivials = [
    'Decimal', 
    'CamelName', 
    'CodeExpression', 
    'DateTime', 
    'PrimitiveType', 
    'Time', 
    'Emoji', 
    'Boolean', 
    'ValueTypeRichText', 
    'String', 
    'Date', 
    'Message', 
    'SimpleDataTypeSubtpeOfDataType', 
    'AggregatingOperator', 
    'OneLiner', 
    'QualifiedCamel', 
    'LowerCamel', 
    'UpperCamel', 
    'Integer'
]

The_Model: LiterateModel = None

@faculty_class
class Extractors(Faculty):
    """Faculty for adding validation methods to LDM classes."""
    
    def object_extract(self, obj: Any, method_name: str = "as_extract"):
        """Create an extract for object using the appropriate patched method."""
        if not obj:
            return None

        patched_func = self.resolve_patched_method(obj, method_name)
        if patched_func:
            return patched_func(obj)
        return None
    
    # the ultimate fallback
    @patch_on(object, "as_extract")
    def any_extract(self):
        name = getattr(self, "name", "Anon")
        if not isinstance(name, str):
            name = name.content
            if name in Reserved_Words:
                name = name + "_"
        otype = type(self).__name__
        extract = { "_type": otype, "name": name}
        return extract

    def call_super_extract(self, obj, current_class_name: str = None):
        """Helper to call super().as_extractl() equivalent."""
        return self.call_super_method(obj, "as_extract", current_class_name)

    @patch_on(LiterateModel, "as_extract")
    def model_extract(model):
        global The_Model
        
        The_Model = model
        the_extract = _extract_faculty.call_super_extract(model, 'LiterateModel')
        class_extracts = []
        for cls in model.all_classes:
            cname = cls.name.content
            # print("cls is ", cls, type(cls), "MRO: ", cls.__mro__)
            # print("Trival  is ", Trivial)
                  
            # if issubclass(cls, Trivial):
            #     print(f"Extract skipping trivial class (by Trivial mixin) {cname}")
            #     continue

            if cname in All_Trivials:
                print(f"Extract skipping trivial class (by adhoc list) {cname}")
                continue
            print("extracting ", cls)
            cls_extract = object_extract(cls)
            print("Extract is ", cls_extract)
            class_extracts.append(cls_extract)
        the_extract['classes'] = class_extracts
        return the_extract

    @patch_on(Class, "as_extract")
    def class_extract(cls: Class):
        the_extract = _extract_faculty.call_super_extract(cls, 'Class')
        edges = []
        for subtype_by in cls.subtype_of:
            subtyping = subtype_by.subtyping_name
            class_ref = subtype_by.class_name
            edge = create_edge("subtype_of", class_ref.content, "1:1")
            
            edges.append(edge)
        for base_ref in cls.based_on:
            edge = create_edge("based_on", base_ref.content, "M:1")
            edges.append(edge)
        
        for attribute in cls.attributes:
            att_name = attribute.name.content
            (target_type, card) = core_type(attribute)
            if target_type in All_Trivials:
                print(f"extract skipping attribute - {att_name} - target type {target_type} is trivial")
                continue
            if not target_type in The_Model.all_class_names:
                print(f"extract skipping attribute - {att_name} - target type {target_type} is not in all class names")
                continue
            
            edge = create_edge(att_name, target_type, card)
            edges.append(edge)

        the_extract["edges"] = edges
        return the_extract


# Create the htmlers instance
_extract_faculty = Extractors()
print("Created Extractprs() = ", _extract_faculty)
show_patches(_extract_faculty.all_patches)

def core_type(attribute: Attribute):
    dtc = attribute.data_type_clause
    dt = dtc.data_type
    core = dt_core(dt)
    card = dtc.cardinality
    return (core, card)

def dt_core(datatype: DataType):
    base_types = datatype.base_type_names()
    print(f"Base type names for {datatype} are {base_types}")
    return base_types[0]

def create_edge(relation, target_name, cardinality = "missing!"):
    print(f"Cardinality is {repr(cardinality)}")
    if not cardinality:
        cardinality = "blank!"
    if isinstance(cardinality, list):
        cardinality = "1:1"
    if isinstance(cardinality, set):
        cardinality = "1:1b"
    if not isinstance(cardinality, str):
        cardinality = "1:1c"
    cardinality = str(cardinality)
    
    if target_name in Reserved_Words:
        target_name = target_name + "_"
    edge = { 
            "relation": relation,
            "to": target_name,
            "cardinality": cardinality
            }
    return edge

def object_extract(the_object):
    object_x = _extract_faculty.object_extract(the_object)
    return object_x



def create_model_extract_with_faculty(the_model, extract_path):

    # Note extract file is in
    #  ldm/ldm_models/MODEL/MODEL_results/Model.extract.yaml
    
    extract = object_extract(the_model)
    print("And the extract is....")
    print(extract)
    fmk.write_yaml(extract, extract_path)




