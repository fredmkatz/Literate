import sys
from utils.util_fmk import write_text
from utils.util_json import as_json, write_yaml, write_json, as_yaml
from utils.util_fmk import create_fresh_directory

import utils.do_weasy_pdf as weasy
from ldm_to_html import create_model_html

import ldm.ldm_renderers as ldm_renderers
import utils.util_all_fmk as fmk

from dull_dsl.dull_parser import parse_model_doc
from utils.util_pydantic import gen_schema

from dataclasses import fields

from ldm_object_creator import GenericObjectCreator
import ldm.Literate_01 as Literate_01
from typing import Dict, List

the_model_dir = ""
the_model_results_dir = ""
the_model_assets_dir = ""

all_clauses_by_priority = None
part_plurals = None
part_parts = None

from utils.util_pydantic import TYPE_REGISTRY, dataclass
from ldm.Literate_01 import  *

from utils.util_inspect import inspect_module

def build_dull_dsl(dull_specs: Dict):

    models_dir = dull_specs["models_dir"]
    model_name = dull_specs["model_name"]
    model_doc = model_name + ".md"
    model_dir = f"{models_dir}/{model_name}"
    model_doc_path = f"{model_dir}/{model_doc}"

    # model_module = dull_specs["model_module"]
    # model_module_path = f"{model_dir}/{model_module}"
    results_dir = f"{model_dir}/{model_name}_results"
    assets_dir = f"{results_dir}/assets"
    create_fresh_directory(results_dir)
    create_fresh_directory(assets_dir)

    global the_model_assets_dir
    the_model_assets_dir = assets_dir
    global the_model_results_dir
    the_model_results_dir = results_dir
    global the_model_dir
    the_model_dir = model_dir
    # print("Dull specs: ", as_json(dull_specs))
    show_phase("Warming up")
    print("Model dir: ", model_dir)
    print("Model name: ", model_name)
    print("Model doc: ", model_doc)
    print("Model name: ", model_name)
    print("Model doc path: ", model_doc_path)
    # print("Model module: ", model_module)
    # print("Model module path: ", model_module_path)
    print("Results dir: ", results_dir)

    trace_path = f"{results_dir}/{model_name}_00_trace.txt"
    print("Trace path: ", trace_path)

    print("Rediirecting to: ", trace_path)
    sys.stdout = open(trace_path, "w", encoding="utf-8")
    
    # start by capturing the schema
    # gen_schema(LiterateModel, "LiterateMetaModel_01", results_dir)
    
    # inspect_module(Literate_01)
    
    

    if False:
        print("TYPE REGISTRY IS")
        for k, v in TYPE_REGISTRY.items():
            print(k, " -> ", v)

    show_phase(f"Parsing model: {model_doc_path}")
    doc_part = parse_model_doc(dull_specs, model_doc_path)
    displayed = doc_part.displayed()

    write_text(f"{results_dir}/{model_name}_01.parsed.txt", displayed)

    show_phase("Deriving dict for model")
    the_dict = doc_part.derive_dict_for_document(dull_specs)
    yaml_dict_file = f"{results_dir}/{model_name}_02.dict.yaml"
    write_yaml(the_dict, yaml_dict_file)
    print(f".. full dict saved  in {yaml_dict_file}")
    
    ldms = the_dict.get("literate_models", [])
    if not ldms:
        print("No LiterateModels found in the dictionary")
        return
    the_ldm_dict = ldms[0]
    
    # the_clean_ldm_dict = fmk.clean_dict(the_ldm_dict)
    the_clean_ldm_dict = the_ldm_dict
    clean_yaml_dict_file = f"{results_dir}/{model_name}_02a.dict.clean.yaml"
    write_yaml(the_clean_ldm_dict, clean_yaml_dict_file)
    print(f".. full clean dict saved  in {clean_yaml_dict_file}")
    


    # CREATING_WITH_CREATOR = False
    # if CREATING_WITH_CREATOR:

    #     creator = GenericObjectCreator(Literate_01)
    #     show_phase(f"Creating model from dictionary - with ObjectCreator: {yaml_dict_file}")
    #     the_ldm_model = creator.create(the_clean_ldm_dict)
    #     # the_ldm_model.model_rebuild()
    #     print(f"Created model: {the_ldm_model.__class__}")
    #     yaml_model_path = f"{results_dir}/{model_name}_03.model.yaml"
        
    #     write_yaml(the_ldm_model, yaml_model_path)
    #     print(f"..Created model file: {yaml_model_path}")

    #     if isinstance(the_ldm_model, dict):
    #         show_phase("ldm model is merely a dict - stopping!")
    #         exit(0)
    # else:
    #     show_phase("Skipping Object Creator")
    # # exit(0)
    
    the_ldm_model_py: LiterateModel = None
    CREATING_WITH_PYDANTIC = True
    if CREATING_WITH_PYDANTIC:
        show_phase("Using pydantic to create model from dict")
        print("Calling LiterateModel.from_typed_dict ...")
        the_ldm_model_py = LiterateModel.from_typed_dict(the_clean_ldm_dict)
        show_phase("have py  model from dict")
        # show_phase("Serializing model ... the_ldm_model_py.to_typed_dict()")
     
        pd_yaml_model_path = f"{results_dir}/{model_name}_03.model_pd.yaml"
        
        model_dict = the_ldm_model_py.to_typed_dict()
        
        # print("Pretty print serialized model....")
        # import pprint
        # pp = pprint.PrettyPrinter(indent=1)
        # pp.pprint(model_dict)

        # print("Now as yaml.....")
        # print(as_yaml(model_dict))
        write_yaml(model_dict, pd_yaml_model_path)
        print(f"..Created pydantic model file: {pd_yaml_model_path}")




    else:
        show_phase("Skipping Pydantic model creation from dict")
    fmk.compare_dicts(results_dir, model_name=model_name)
    exit(0)

    VALIDATING = False
    if VALIDATING:
        show_phase("Validating model")
        validate_model(the_ldm_model)
        from validate_fields import all_validation_errors

        show_phase("counting errors")
        counts = count_strings(all_validation_errors)
        print(counts)
        for key, value in counts.items():
            print(value, "\t", key)
    else:
        show_phase("SKIPPING Validation")
        

    # Serialize it to files
 
    show_phase("Serializing model ... the_ldm_model_py.to_typed_dict()")

    yaml_model_path = f"{results_dir}/{model_name}_03.model.yaml"
    
    model_dict = the_ldm_model_py.to_typed_dict()

    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(model_dict)

    write_yaml(model_dict, yaml_model_path)
    print(f"..Created model file: {yaml_model_path}")

    
    SERIALIZING_WITH_PYDANTIC = True
    if SERIALIZING_WITH_PYDANTIC:

        yaml_regenned_dict_file = f"{results_dir}/{model_name}_03a.model_to_dict.yaml"
        show_phase(f"Serializing dict from model with Pydantic: {yaml_regenned_dict_file}")
        regenned_model_dict = the_ldm_model_py.to_typed_dict()
        # print(regenned_model_dict)
        write_yaml(regenned_model_dict, yaml_regenned_dict_file)
        
        # print(regenned_model_dict)
        write_yaml(regenned_model_dict, yaml_regenned_dict_file)

    else:
        show_phase("SKIPPING - Pydantic serialization of model")
    # exit(0)
    # test_ldm_model(the_ldm_model)
    
    # recreate from exported model dict
    
    REGENNING = False
    
    if REGENNING:

        creator2 = GenericObjectCreator(Literate_01)
        show_phase(f"Re Creating model from dumped model - with ObjectCreator: {yaml_regenned_dict_file}")
        the_ldm_model2 = creator2.create(regenned_model_dict)
        # the_ldm_model.model_rebuild()
        print(f"Created model: {the_ldm_model2.__class__}")
        if isinstance(the_ldm_model2, dict):
            show_phase("ldm model2 is merely a dict - stopping!")
            exit(0)
            
        show_phase(" And re serializing the regenned model")
        regenned_model_dict_model_dict = the_ldm_model2.to_typed_dict()
        yaml_regenned_dict_file2 = f"{results_dir}/{model_name}_03aa.remodel_to_dict.yaml"
        write_yaml(regenned_model_dict_model_dict, yaml_regenned_dict_file2)
    show_phase("Comparing counts")
    fmk.compare_dicts(results_dir, model_name=model_name)

    show_phase("Rendering back to markdown")  # Render
    # Render
    render_path = f"{results_dir}/{model_name}_04.rendered.md"
    rendering = render_to_markdown(the_ldm_model_py)
    write_text(render_path, rendering)

    # Create HTML
    show_phase("Creating HTML from model dict")
    html_path = f"{results_dir}/{model_name}_05.html"

    create_model_html(the_ldm_model_py, html_path)
    show_phase("Skipping PDF creation")

    # show_phase("Creating PDF from html and css")
    # css_path = "ldm/Literate.css"
    # pdf_path = f"{results_dir}/{model_name}.pdf"
    # weasy.generate_weasy_pdf(html_path, css_path=css_path, output_path=pdf_path)


def show_phase(caption: str):
    print(f"\nPhase: {caption}", file=sys.stderr)
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
    create_model_html(the_ldm_dict, html_path)
    exit(0)


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
            print("type of class, name is ", type(class_), type(class_.name))
