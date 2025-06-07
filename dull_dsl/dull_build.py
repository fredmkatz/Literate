import sys
from utils.util_fmk import write_text
from utils.util_json import as_json, write_yaml, write_json, as_yaml, make_tidy_yaml
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

from utils.util_pydantic import TYPE_REGISTRY, dataclass, USING_PYDANTIC
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
    
    pd_or_not = "DC"
    if USING_PYDANTIC:
        pd_or_not = "PD"

    if USING_PYDANTIC:
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
    
#    start by capturing the schema
    show_phase("Creating schema and survey of Literate_01")
    gen_schema(LiterateModel, "LiterateMetaModel_01", f"{results_dir}/LiterateMeta")
    
    inspect_module(Literate_01, "LiterateMetaModel_survey.txt", f"{results_dir}/LiterateMeta")
    
    yaml_dict_path = f"{results_dir}/{model_name}_{pd_or_not}_02.dict.yaml"
    yaml_model_path = f"{results_dir}/{model_name}_{pd_or_not}_03.model.yaml"
    valid_model_path = f"{results_dir}/{model_name}_{pd_or_not}_04.v_model.yaml"
    regenned_model_path = f"{results_dir}/{model_name}_{pd_or_not}_05.r_model.yaml"


    if False:
        print("TYPE REGISTRY IS")
        for k, v in TYPE_REGISTRY.items():
            print(k, " -> ", v)

    show_phase(f"Parsing model: {model_doc_path}")
    doc_part = parse_model_doc(dull_specs, model_doc_path)
    displayed = doc_part.displayed()

    write_text(f"{results_dir}/{model_name}_01.parsed.txt", displayed)

    show_phase("Deriving dict from parse => {yaml_dict_file}")
    the_dict = doc_part.derive_dict_for_document(dull_specs)
    ldms = the_dict.get("literate_models", [])
    if not ldms:
        print("No LiterateModels found in the dictionary")
        return
    the_ldm_dict = ldms[0]

    
    write_yaml(the_ldm_dict, yaml_dict_path)    # _01_
    show_phase(f".. full dict saved  in {yaml_dict_path}")
    make_tidy_yaml(yaml_dict_path)
            
    the_ldm_model_py: LiterateModel = None
    CREATING_WITH_PYDANTIC = True
    if CREATING_WITH_PYDANTIC:
        show_phase(f"Creating model with from_typed_dict() => to_typed_dict() => {yaml_model_path}")
        print("Calling LiterateModel.from_typed_dict ...")
        the_ldm_model_py = LiterateModel.from_typed_dict(the_ldm_dict)
        show_phase("have py  model from dict")
        
        show_phase(f"Creating model_dict from model => {yaml_model_path}") # _03_
        model_dict = the_ldm_model_py.to_typed_dict()
        write_yaml(model_dict, yaml_model_path)     
        make_tidy_yaml(yaml_model_path)

    else:
        show_phase("Skipping Pydantic model creation from dict")

    VALIDATING = True
    if VALIDATING:

        show_phase(f"Validating model tp {valid_model_path}")
        validate_model(the_ldm_model_py)
        valid_model_dict = the_ldm_model_py.to_typed_dict()

        write_yaml(valid_model_dict, valid_model_path)
        make_tidy_yaml(valid_model_path)
        print(f"..Created dict for validated model: {valid_model_path}") # _04_

        from validate_fields import all_validation_errors

        show_phase("counting errors")
        counts = count_strings(all_validation_errors)
        print(counts)
        for key, value in counts.items():
            print(value, "\t", key)
    else:
        show_phase("SKIPPING Validation")
        
    fmk.compare_dicts(results_dir, model_name=model_name, result_suffix="90_census")
    # exit(0)


    
    SERIALIZING_WITH_PYDANTIC = False
    if SERIALIZING_WITH_PYDANTIC:

        show_phase(f"Serializing dict from model with Pydantic: {regenned_model_path}")
        regenned_model_dict = the_ldm_model_py.to_typed_dict()
        # print(regenned_model_dict)
        write_yaml(regenned_model_dict, regenned_model_path)
        make_tidy_yaml(regenned_model_path)

    else:
        show_phase("SKIPPING - Pydantic serialization of model")
    # exit(0)
    # test_ldm_model(the_ldm_model)
    
    # recreate from exported model dict
    
    REGENNING = False
    
    if REGENNING:

        creator2 = GenericObjectCreator(Literate_01)
        show_phase(f"Re Creating model from dumped model - with ObjectCreator: {regenned_model_path}")
        the_ldm_model2 = creator2.create(regenned_model_dict)
        # the_ldm_model.model_rebuild()
        print(f"Created model: {the_ldm_model2.__class__}")
        if isinstance(the_ldm_model2, dict):
            show_phase("ldm model2 is merely a dict - stopping!")
            exit(0)
            
        show_phase(" And re serializing the regenned model")
        regenned_model_dict_model_dict = the_ldm_model2.to_typed_dict()
        write_yaml(regenned_model_dict_model_dict, yaml_regenned_dict_file2)
    show_phase("Comparing counts")
    fmk.compare_dicts(results_dir, model_name=model_name, result_suffix="90_census")

    RENDER_MD = False
    if RENDER_MD:
        render_path = f"{results_dir}/{model_name}_{pd_or_not}_05.rendered.md"
        show_phase(f"Rendering back to markdown => {render_path}")  # Render

        rendering = render_to_markdown(the_ldm_model_py)
        write_text(render_path, rendering)
    else:
        show_phase("Skipping Render to Markdown")

    # Create HTML
    CREATE_HTML = False
    if CREATE_HTML:
        show_phase("Creating HTML from model dict")
        html_path = f"{results_dir}/{model_name}_{pd_or_not}_06.html"

        create_model_html(the_ldm_model_py, html_path)
    else:
        show_phase("Skipping Render to HTML")

    show_phase("Skipping PDF creation")

    # show_phase("Creating PDF from html and css")
    # css_path = "ldm/Literate.css"
    # pdf_path = f"{results_dir}/{model_name}_{pd_or_not}_07.pdf"
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
