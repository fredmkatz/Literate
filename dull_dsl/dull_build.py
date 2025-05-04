from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable, Any
from abc import ABC
import re
from dict_to_html import create_dict_html

import os
from utils_pom.util_fmk_pom import write_text, write_yaml
from utils_pom.util_json_pom import as_json
from utils_pom.util_fmk_pom import create_fresh_directory


# from utils_pom.util_json_pom import as_json
# from utils_pom.util_fmk_pom import as_yaml
import ldm.ldm_renderers as ldm_renderers

from dull_dsl.dull_parser import parse_model_doc
from new_dict_lib import model_to_json, model_to_yaml, model_to_json_file, model_to_yaml_file


from ldm_object_creator import GenericObjectCreator
import ldm.Literate_01 as Literate_01



all_clauses_by_priority = None
part_plurals = None
part_parts = None

def build_dull_dsl(dull_specs: Dict):
    
    model_dir = dull_specs["dirpath"]
    model_doc = dull_specs["model_doc"]
    model_name =   os.path.splitext(model_doc)[0]
    model_doc_path = f"{model_dir}/{model_doc}"
    
    model_module = dull_specs["model_module"]
    model_module_path = f"{model_dir}/{model_module}"
    results_dir = f"{model_dir}/{model_name}_results"
    
    
    # print("Dull specs: ", as_json(dull_specs))
   
    print("Model dir: ", model_dir)
    print("Model doc: ", model_doc)
    print("Model name: ", model_name)
    print("Model doc path: ", model_doc_path)
    print("Model module: ", model_module)
    print("Model module path: ", model_module_path)
    print("Results dir: ", results_dir)
    

    create_fresh_directory(results_dir)
    doc_part = parse_model_doc(dull_specs, model_doc_path)
    displayed = doc_part.displayed()


    write_text(f"{results_dir}/{model_name}.parsed.txt", displayed)
    the_dict = doc_part.derive_dict_for_document(dull_specs)
    ldms = the_dict.get("LDMs", [])
    if not ldms:
        print("No LDMs found in the dictionary")
        return
    the_ldm_dict = ldms[0]

    print("Returned from dict creation")
    write_text(f"{results_dir}/{model_name}.dict.json", as_json(the_ldm_dict))
    write_yaml(the_ldm_dict, f"{results_dir}/{model_name}.dict.yaml")



    
    
    creator = GenericObjectCreator(Literate_01) 
    # print(f"Creating model from dictionary: {the_ldm_dict}")
    the_ldm_model = creator.create(the_ldm_dict)
    print(f"Created model: {the_ldm_model.__class__}")
    # print("Repr for model is", repr(the_ldm_model))
    
    # test_ldm_model(the_ldm_model)
            
    
    # Serialize it to files
    json_sample = model_to_json_file(the_ldm_model, f"{results_dir}/{model_name}.model.json")
    yaml_sample = model_to_yaml_file(the_ldm_model, f"{results_dir}/{model_name}.model.yaml")
    print("Created model JSON and YAML files")
    
    validate_model(the_ldm_model)

    print("Rendering....")    # Render
    # Render
    render_path2 = f"{results_dir}/{model_name}.rendered.md"
    rendering = render_to_markdown(the_ldm_model)
    write_text(render_path2, rendering)
    
    # Create HTML
    html_path = f"{results_dir}/{model_name}.html"

    create_dict_html(the_ldm_dict, html_path)

def validate_model(the_model) -> List[str]:
    
    import ldm.ldm_validators as ldm_validators
    # Validate the model
    print("Validating model...")
    errors = ldm_validators.validate_model(the_model)
    print("Validating references...")
    errors += ldm_validators.validate_references(the_model)
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")
    else:
        print("No validation errors found.") 



def render_to_markdown(the_model):
    markdown_output = ldm_renderers.render_markdown_ldm(the_model)
    return markdown_output



def create_ldm_html(results_dir, model_name, the_ldm_dict, html_path):
    html_path = f"{results_dir}/{model_name}.dict.html"
    create_dict_html(the_ldm_dict, html_path)
    exit(0)
    # from ldm_object_creator import GenericObjectCreator

def test_ldm_model(the_model):
    model_name = the_model.show_name()
    print("Model name is ", model_name)
    # print("type of name is , model_name.name._type")
    print(f"Created model: {the_model}")
    print(f"Created model: {the_model.__class__}")
    print(f"Created model: {the_model.__dict__}")
    

    for subject in the_model.subjects:
        print(subject.show_name())
        for class_ in subject.classes:
            print("\t", class_.show_name())
            print("type of class, name is " , type(class_),  type(class_.name))

