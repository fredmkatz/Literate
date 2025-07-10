import sys
from utils.util_fmk import write_text
from utils.util_json import as_json, write_yaml, write_json, as_yaml, make_tidy_yaml
from utils.util_fmk import create_fresh_directory

from utils.typed_dict_tools_diff import TypedDict
import utils.do_weasy_pdf as weasy

import ldm.ldm_renderers as ldm_renderers
import ldm.ldm_validators_v3 as ldm_validators
from ldm.ldm_htmlers import create_model_html_with_faculty

import utils.util_all_fmk as fmk

from dull_dsl.dull_parser import parse_model_doc
from utils.util_pydantic import gen_schema

from dataclasses import fields

import ldm.Literate_01 as Literate_01
from typing import Dict, List

models_dir = ""
model_dir = ""
model_results_dir = ""
model_assets_dir = ""
ldm_assets_dir = ""

all_clauses_by_priority = None
part_plurals = None
part_parts = None

from utils.util_pydantic import TYPE_REGISTRY, dataclass, USING_PYDANTIC
from ldm.Literate_01 import *

from utils.util_inspect import inspect_module


def build_dull_dsl(dull_specs: Dict):

    global model_assets_dir
    models_dir = dull_specs["models_dir"]
    ldm_assets_dir = f"{models_dir}/ldm_assets"

    model_name = dull_specs["model_name"]
    model_doc = model_name + ".md"

    model_dir = f"{models_dir}/{model_name}"
    model_doc_path = f"{model_dir}/{model_doc}"

    # model_module = dull_specs["model_module"]
    # model_module_path = f"{model_dir}/{model_module}"
    results_dir = f"{model_dir}/{model_name}_results"
    model_assets_dir = f"{results_dir}/assets"

    pd_or_not = "DC"
    if USING_PYDANTIC:
        pd_or_not = "PD"

    if USING_PYDANTIC:
        create_fresh_directory(results_dir)
        create_fresh_directory(model_assets_dir)

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
    print("Assets dir: ", model_assets_dir)

    trace_path = f"{results_dir}/{model_name}_00_trace.txt"
    print("Trace path: ", trace_path)

    print("Rediirecting to: ", trace_path)
    sys.stdout = open(trace_path, "w", encoding="utf-8")

    #    start by capturing the schema
    show_phase("Creating schema and survey of Literate_01")
    gen_schema(
        LiterateModel,
        f"LiterateMetaModel_01_{pd_or_not}",
        f"{results_dir}/LiterateMeta",
    )
    model_schema_path = f"{results_dir}/LiterateMeta/LiterateMetaModel_01_{pd_or_not}_schema.yaml"
    inspect_module(
        Literate_01, "LiterateMetaModel_survey.txt", f"{results_dir}/LiterateMeta"
    )

    yaml_dict_path = f"{results_dir}/{model_name}_{pd_or_not}_02.dict.yaml"
    yaml_model_path = f"{results_dir}/{model_name}_{pd_or_not}_03.model.yaml"
    valid_model_path = f"{results_dir}/{model_name}_{pd_or_not}_04.v_model.yaml"
    valid_model_jpath = f"{results_dir}/{model_name}_{pd_or_not}_04.v_model.json"
    regenned_model_path = f"{results_dir}/{model_name}_{pd_or_not}_05.r_model.yaml"

    yaml_dict_path2 = yaml_dict_path.replace(".yaml", ".tidy.yaml")

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

    the_ldm_dict = TypedDict(the_ldm_dict)
    the_ldm_dict.save_as(yaml_dict_path)
    show_phase(f".. full dict saved  in {yaml_dict_path}")

    the_ldm_model_py: LiterateModel = None
    CREATING_WITH_PYDANTIC = True
    if CREATING_WITH_PYDANTIC:
        show_phase(
            f"Creating model with from_typed_dict() => to_typed_dict() => {yaml_model_path}"
        )
        print("Calling LiterateModel.from_typed_dict ...")
        the_ldm_model_py = LiterateModel.from_typed_dict(the_ldm_dict)
        show_phase("have py  model from dict")

        show_phase(f"Creating model_dict from model => {yaml_model_path}")  # _03_
        # the_ldm_dict = the_ldm_model_py.to_typed_dict()
        the_ldm_dict = TypedDict(the_ldm_model_py)
        the_ldm_dict.save_as(yaml_model_path)

    else:
        show_phase("Skipping Pydantic model creation from dict")

    VALIDATING = True
    if VALIDATING:

        show_phase(f"Validating model tp {valid_model_path}")

        # Validate the model
        diagnostics = ldm_validators.validate_model(the_ldm_model_py)
        if diagnostics:
            print("Validation diagnostics:", len(diagnostics))
            for diagnostic in diagnostics:
                print(f"- {diagnostic}")
        else:
            print("No validation diagnostics found.")

        # valid_model_dict = the_ldm_model_py.to_typed_dict()

        valid_model_dict = TypedDict(the_ldm_model_py)
        valid_model_dict.save_as(valid_model_path)
        valid_model_dict.save_as(valid_model_jpath)
        the_ldm_dict = valid_model_dict

        print(f"..Created dict for validated model: {valid_model_path}")  # _04_

        show_phase("counting diagnostics")
        d_strings = [
            f"{d.severity} - {d.object_type} - {d.category}- {d.constraint_name}"
            for d in diagnostics
        ]
        counts = count_strings(d_strings)
        print(counts)
        for key, value in counts.items():
            print(value, "\t", key)
    else:
        show_phase("SKIPPING Validation")

    fmk.compare_dicts(results_dir, model_name=model_name, result_suffix="90_census")
    # exit(0)

    show_phase("Create extract for diagrams")

    from ldm.ldm_extractors import create_model_extract_with_faculty
    
    the_extract_path = f"{results_dir}/{model_name}_{pd_or_not}_15_extract.yaml"
    
    create_model_extract_with_faculty(the_ldm_model_py, the_extract_path)
    show_phase("Validating to JSON Schema")
    from utils.util_jsonschema import validate_to_schema
    validate_to_schema(schema_path=model_schema_path, object_path=valid_model_path)

    RENDER_MD = False
    if RENDER_MD:
        render_path = f"{results_dir}/{model_name}_{pd_or_not}_05.rendered.md"
        show_phase(f"Rendering back to markdown => {render_path}")  # Render

        rendering = render_to_markdown(the_ldm_model_py)
        write_text(render_path, rendering)
    else:
        show_phase("Skipping Render to Markdown")

    # Create HTML

    CREATE_HTML_AS2 = True
    if CREATE_HTML_AS2:
        show_phase("Creating HTML using the Faculty")
        html_path = f"{results_dir}/{model_name}_{pd_or_not}_07_as.html"
        web_css_path = "../../ldm_assets/Literate.css"

        create_model_html_with_faculty(the_ldm_model_py, html_path, web_css_path)

    CREATE_HTML_FOR_PDF = True
    if CREATE_HTML_FOR_PDF:
        show_phase("Creating HTML for PDF using the Faculty")
        html_pdf_path = f"{results_dir}/{model_name}_{pd_or_not}_08_as_pdf.html"
        print_css_path = "../../ldm_assets/LiteratePrint.css"

        create_model_html_with_faculty(the_ldm_model_py, html_pdf_path, print_css_path)

    from utils.util_prince import html2pdf_prince

    CREATE_PRINCE_PDF = True
    if CREATE_PRINCE_PDF:
        show_phase("Creating PDF from html and css - using Prince")
        pdf_path1 = f"{results_dir}/{model_name}_{pd_or_not}_09prince.pdf"
        html2pdf_prince(html_pdf_path, output_pdf_path=pdf_path1)
        from utils.util_pikepdf import set_pdf_viewing
        pdf_path1a = pdf_path1.replace(".pdf", ".twoup.pdf")
        set_pdf_viewing(pdf_path1, pdf_path1a)

    else:
        show_phase("Skipping PDF creation")

    CREATE_PLAYWRIGHT_PDF = True
    if CREATE_PLAYWRIGHT_PDF:
        from utils.util_playwright import html2pdf_playwright

        pdf_path2 = f"{results_dir}/{model_name}_{pd_or_not}_10_playwright.pdf"
        html2pdf_playwright(html_pdf_path, pdf_path2)
        from utils.util_pikepdf import set_pdf_viewing
        pdf_path2a = pdf_path2.replace(".pdf", ".twoup.pdf")
        set_pdf_viewing(pdf_path2, pdf_path2a)


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
