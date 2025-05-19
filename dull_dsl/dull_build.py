from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Callable, Any
from abc import ABC
import re

import os
import sys
from utils_pom.util_fmk_pom import write_text, write_yaml
from utils_pom.util_json_pom import as_json
from utils_pom.util_fmk_pom import create_fresh_directory
import weasy_pdf as weasy
from dict_to_html import create_dict_html

from pdf2md import convert_pdf2md
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
    create_fresh_directory(results_dir)

    trace_path = f"{model_dir}/{model_name}_trace.txt"
    print("Rediirecting to: ", trace_path)
    sys.stdout = open(trace_path, "w", encoding="utf-8")

    
    # print("Dull specs: ", as_json(dull_specs))
    show_phase("Warming up")
    print("Model dir: ", model_dir)
    print("Model doc: ", model_doc)
    print("Model name: ", model_name)
    print("Model doc path: ", model_doc_path)
    print("Model module: ", model_module)
    print("Model module path: ", model_module_path)
    print("Results dir: ", results_dir)
    

    show_phase(r"Parsing model: {model_doc_path}")
    doc_part = parse_model_doc(dull_specs, model_doc_path)
    displayed = doc_part.displayed()


    write_text(f"{results_dir}/{model_name}.parsed.txt", displayed)
    
    show_phase("Deriving dict for model")
    the_dict = doc_part.derive_dict_for_document(dull_specs)
    yaml_dict_file = f"{results_dir}/{model_name}.dict.yaml"
    json_dict_file = f"{results_dir}/{model_name}.dict.json"
    write_text(json_dict_file, as_json(the_dict))
    write_yaml(the_dict, yaml_dict_file)
    print(f".. full dict saved  in {yaml_dict_file} and {json_dict_file}")

    ldms = the_dict.get("literate_models", [])
    if not ldms:
        print("No LiterateModels found in the dictionary")
        return
    the_ldm_dict = ldms[0]



    
    
    creator = GenericObjectCreator(Literate_01) 
    show_phase(f"Creating model from dictionary: {yaml_dict_file}")
    the_ldm_model = creator.create(the_ldm_dict)
    print(f"Created model: {the_ldm_model.__class__}")
    
    # test_ldm_model(the_ldm_model)

    show_phase("Validating model")
    validate_model(the_ldm_model)
    from validate_fields import all_validation_errors
    
    show_phase("counting errors")
    counts = count_strings(all_validation_errors)
    print(counts)
    for key, value in counts.items():
        print(value, "\t", key)

    show_phase("Serialing model ...")
    # Serialize it to files
    json_model_path = f"{results_dir}/{model_name}.model.json"
    yaml_model_path = f"{results_dir}/{model_name}.model.yaml"
    json_sample = model_to_json_file(the_ldm_model, json_model_path)
    yaml_sample = model_to_yaml_file(the_ldm_model, yaml_model_path)
    print(f"..Created model files: {json_model_path} and {yaml_model_path}")
    

    show_phase("Rendering back to markdown")    # Render
    # Render
    render_path2 = f"{results_dir}/{model_name}.rendered.md"
    rendering = render_to_markdown(the_ldm_model)
    write_text(render_path2, rendering)
    
    # Create HTML
    show_phase("Creating HTML from model dict")
    html_path = f"{results_dir}/{model_name}.html"

    create_dict_html(the_ldm_dict, html_path)
    show_phase("Skipping PDF creation")

    show_phase("Creating PDF from html and css")
    css_path = "ldm/Literate.css"
    pdf_path = f"{results_dir}/{model_name}.pdf"
    weasy.generate_weasy_pdf(html_path, css_path=css_path, output_path=pdf_path)
    
def show_phase(caption: str):
    print(f"\nPhase: {caption}")

def count_strings(string_list):
    string_counts = {}
    for string in string_list:
        if string in string_counts:
            string_counts[string] += 1
        else:
            string_counts[string] = 1
    return string_counts

def validate_model(the_model) -> List[str]:
    
    import ldm.ldm_validators as ldm_validators
    # Validate the model
    errors = ldm_validators.validate_model(the_model)
    print("Validating references...")
    errors += ldm_validators.validate_references(the_model)
    if errors:
        print("Validation errors:", len(errors))
        # for error in errors:
        #     print(f"- {error}")
    else:
        print("No validation errors found.") 
    
        



def render_to_markdown(the_model):
    markdown_output = ldm_renderers.render_ldm(the_model)
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

