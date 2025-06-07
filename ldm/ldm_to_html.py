import json
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup
from Literate_01 import *
from utils.class_fluent_html import  FluentTag
from utils.util_json import as_yaml, clean_dict
import utils.util_all_fmk as fmk
HEADER_KEYS = [
    "prefix",
    "name",
    "one_liner",
    "parenthetical",
    "data_type_clause",
    "is_optional",
    "content",
]
HEADED_CLASSES = [
    "LiterateModel",
    "Subject",
    "Class",
    "AttributeSection",
    "Attribute",
]
FORMULA_CLASSES = ["Formula", "Derivation", "Default", "Constraint"]
USELESS_LIST_KEYS = [
    "attribute_sections",
    "constraints",
    "classes",
    "attributes",
    "annotations",
    "subjects",
    "diagnostics",
    "elaboration",
]

CLASS_LIST_KEYS = [
    "based_on",
    "dependent_of",
    "subtype_of",
    "subtypes",
]

SIMPLE_CONTENT_TYPES = [
    "Paragraph",
    "OneLiner",
    "CodeBlock",
]

from dataclasses import is_dataclass

def is_dataclass_instance(obj):
    return is_dataclass(obj) and not isinstance(obj, type)

def is_headed(class_name: str) -> bool:
    return class_name in HEADED_CLASSES or class_name.startswith("Subject")


def is_formula(class_name: str) -> bool:
    return class_name in FORMULA_CLASSES


def all_keys(data) -> List[str]:
    keys = set()
    if isinstance(data, dict):
        for key, value in data.items():
            keys.add(key)
            keys.update(all_keys(value))
    elif isinstance(data, List):
        for element in data:
            keys.update(all_keys(element))
    return keys


def dict_to_html(data):
    html_h = html()

    # print(f"htmling {data}")

    if isinstance(data, str):
        return data

    python_type = type(data)
    type_label = "NA"
    if isinstance(data, dict):
        type_label = data.get("_type", "NoDictTypeLabel")
        # print("htmling dict with _type = ", type_label)
    else:
        type_label = getattr(data, "_type", "NoNonDictTypeLabel")
        # print("htmling Python type  ", python_type, "; type_label is ", type_label)
    if type_label == "Diagnostic":
        object_type = spanned_value(data, "object_type")
        object_name = spanned_value(data, "object_name")
        severity = spanned_value(data, "severity")
        message = spanned_value(data, "message")
        return div_custom("Diagnostic", [severity, message, " on ", object_type])


    if type_label == "ClassName":
        return class_name_link(data)
    
    if is_dataclass_instance(data):
        data = clean_dict(data)

    if isinstance(data, dict) :

        obj_type = "DICT"
        for key, value in data.items():
            if key == "_type":
                obj_type = value
                break
        # print("Object type is ", obj_type)
        if obj_type in SIMPLE_CONTENT_TYPES:
            add_html_simple_content(obj_type, data, html_h)

            return html_h
        if obj_type == "DataTypeClause":
            return dt_as_html(data)
        if obj_type == "BaseDataType":
            # print("bdt. dict is ", data)
            # print("bdt. classname is ", data.get("class_name"))

            bdt_html2 = span_div(data, "BaseDataType", "class_name", "as_value_type")
            return bdt_html2
        if obj_type == "MappingDataType":
            # print("mdt. dict is ", data)
            # print("mdt. domain_type is ", data.get("domain_type"))
            # print("mdt. range_type is ", data.get("range_type"))

            mdt_html2 = span_div(data, "MappingDataType", "domain_type", "range_type")
            return mdt_html2
        if obj_type == "ListDataType":
            # print("ldt. dict is ", data)
            # print("ldt. element_type is ", data.get("element_type"))

            ldt_html2 = span_div(data, "ListDataType", "element_type")
            return ldt_html2
        if obj_type == "DataTypeClause":
            return span_div(data, "DataTypeClause", "is_optional_lit", "data_type")
        if obj_type == "ClassName":
            return class_name_link(data)
        if obj_type == "AsValue":
     #       print("Found ASVALUE dict", data)
            as_value = AsValue(data["t_value"])
            if not as_value:
                return ""
            return span_custom("as_value", [as_value])
        if obj_type == "IsOptional":
            return span_custom("is_optional", "Optional??")
            opt_value = str(IsOptional(data["t_value"])).strip()
            # print("opt value is ", opt_value)
            if not opt_value:
                return ""
            # print("using opt value is ", opt_value)
            return span_custom("is_optional", [opt_value])

        if obj_type == "Annotation":
            emoji = spanned_value(data, "emoji")
            label = spanned_value(data, "label")
            content = spanned_value(data, "content")
            return div_custom("Annotation", [emoji, label, content])

        # if obj_type in ["Formula", "Constraint", "Derivation", "Default"]:
        #     content = dict_div(data, "content")
        #     message = dict_div(data, "message")
        #     code = dict_div(data, "code")
        #     severity = dict_div(data, "severity")
        #     notes = dict_div(data, "annotations")
        #     return div(obj_type, [content, code, message, severity, notes])

        obj_classes = obj_type

        # Simplify SubjectB, etc
        if obj_type.startswith("Subject"):
            obj_classes = "Subject " + obj_type

            obj_type = "Subject"
        # print("Object type is ", obj_type)
        object_h = div_custom(obj_classes)
        html_h.append(object_h)

        # Gather into header: Prefix, name, oneliner, parenthetical
        if is_headed(obj_type):
            # Start the header
            header_h = div_custom(f"{obj_type}_header header")
            object_h.append(header_h)

            # add header attributes
# HEADER_KEYS = [
#     "prefix",
#     "name",
#     "parenthetical",
#     "data_type_clause",
#     "is_optional",
#     "one_liner",

#     "content",
# ]
            for key in HEADER_KEYS:
                value = data.get(key, None)
                if value is None:
                    continue
                # print("kv is ", key, value)
                if str(value).strip() == "":
                    continue
                if key == "name":
                    add_anchor_html(key, value, header_h)
                    continue
                if key == "one_liner":
                    add_html_simple_content("OneLiner", value, header_h)
                    continue

                else:
                    add_classed_value_html(key, value, header_h)

            # end the header
            # print(f"{obj_type} header is", header_h)
        if is_formula(obj_type):
            one_liner = data.get("one_liner", "")
            add_html_clause(obj_type, one_liner, html_h)
            # formula class is open. Leave it so
            # collect all the details (code, english, etc)
            # "header" all in the clause above

        for key, value in data.items():

            if key == "_type":
                continue
            if key in HEADER_KEYS:
                continue
            if key in USELESS_LIST_KEYS:
                add_headless_list_html(key, value, html_h)
                continue
            if key == "subtype_of":
                add_subtype_of_clause(key, value, html_h)
                continue
            if key == "data_type":
                add_data_type_clause("dataType", value, html_h)
                continue

            if key in CLASS_LIST_KEYS:
                add_anchored_class_names_clause(key, value, html_h)
                continue

            # Defaults and Derivations need special treatment
            if key in ["default", "derivation"]:
                html_h.append(dict_to_html(value))
                continue
            # subclauses of Formulas

            if key == "code":
                add_html_clause(key, value, html_h)
                continue
            if key == "message":
                add_html_clause(key, value, html_h)
                continue
            if key == "severity":
                add_html_clause(key, value, html_h)
                continue
            if key == "is_embellishment":
                if value == False:
                    continue
                add_html_clause(key, value, html_h)
                continue
            print("Orphaned dictkey: ", key)
            add_key_value_html(key, value, html_h)

    elif isinstance(data, list):
        print("Orphaned list: ", data)

        html_h.append(div_custom("list"))
        for item in data:
            html_h.append(dict_to_html(item))
    else:
        print("Orphaned ?", type(data), ": ", data)
        return f"{data}"

    return html_h


from utils.util_flogging import trace_decorator


# @trace_decorator
def dt_as_html(data_type, as_plural: bool = False) -> str:
    dtype = data_type.get("_type")
    if dtype == "DataTypeClause":
        return dt_as_html(data_type.get("data_type"))
    if dtype == "BaseDataType":
        return bdt_as_html(data_type, as_plural)
    if dtype == "ListDataType":
        return ldt_as_html(data_type, as_plural)
    if dtype == "SetDataType":
        return sdt_as_html(data_type, as_plural)
    if dtype == "MappingDataType":
        return mdt_as_html(data_type, as_plural)
    print(f"DT_AS_HTML called for dtype = {dtype}")
    return str(data_type)


def plural_of(name):
    if isinstance(name, dict):
        return name["content"] + "-es"
    return str(name) + "_es"


def anchor_html(css_class, display_name, anchor_name):
    anchor_h = a(display_name, class_=css_class, href=f"#{anchor_name}")
    return anchor_h


from utils.util_flogging import flogger, trace_decorator


# @trace_decorator
def bdt_as_html(data_type, as_plural: bool = False) -> str:
    class_name = data_type["class_name"]
    as_value = data_type["as_value_type"]

    anchored_name = class_name["content"]
    displayed_name = class_name["content"]
    if as_plural:
        displayed_name = plural_of(class_name)

    # print(f"BDT anchored name is {anchored_name}, display name is {displayed_name}")
    class_anchor = anchor_html("base_class", displayed_name, anchored_name)
    # print("BDT class anchor is ", class_anchor)
    ref_or_value = "reference"
    if as_value:
        ref_or_value = "value"
    if as_plural:
        ref_or_value += "_es"

    return span_custom("base_data_type", [class_anchor, ref_or_value])


def ldt_as_html(data_type, as_plural: bool = False) -> str:
    element_type = data_type["element_type"]

    element_html = dt_as_html(element_type, True)
    prefix = "List of"
    if as_plural:
        prefix = "Lists of"
    return span_custom("list_data_type", [prefix, element_html])


def sdt_as_html(data_type, as_plural: bool = False) -> str:
    element_type = data_type["element_type"]

    element_html = dt_as_html(element_type, True)
    prefix = "Set of"
    if as_plural:
        prefix = "Sets of"
    return span_custom("set_data_type", [prefix, element_html])


def mdt_as_html(data_type, as_plural: bool = False) -> str:
    domain_type = data_type["domain_type"]
    range_type = data_type["domain_type"]

    domain_html = dt_as_html(domain_type, False)
    range_html = dt_as_html(range_type, True)
    prefix = "Mapping from"
    if as_plural:
        prefix = "Mappings from"
    return span_custom("mapping_data_type", [prefix, domain_html, " to ", range_html])


def spanned_value(data, attribute):
    value = data.get(attribute)
    if not value:
        return ""

    if isinstance(value, str):
        value = value.strip()
    return span(value, class_=attribute)


def dict_div(data, css_class, *attributes):
    at_htmls = []
    for attribute in attributes:
        at_html = dict_to_html(data.get(attribute))
        at_htmls.append(at_html)
    # print("htmls are: ", at_htmls)
    return div_custom(css_class, at_htmls)


def span_div(data, css_class, *attributes):
    at_htmls = []
    for attribute in attributes:
        at_html = dict_to_html(data.get(attribute))
        at_htmls.append(at_html)
    # print("htmls are: ", at_htmls)
    return span_custom(css_class, at_htmls)


def div_custom(css_class, pieces=[]):
    div_h = div(class_=css_class)
    for piece in pieces:
        div_h.append(piece)
    return div_h


def span_custom(css_class, pieces):
    html_h = span()
    html_h["class"] = css_class
    # print("span Pieces are: ", pieces)
    for piece in pieces:
        html_h.append(piece)

    # print("span returning: ", html_h)
    return html_h


def add_value_html(value, html_h):

    value_html = dict_to_html(value)
    html_h.append(value_html)


def class_name_link(data):
    content = getattr(data, "content", None)
    if not content:
        content = data.get("content", "StillNoName")
    return span(content, class_="class_name_link", href=f"#{content}")


def add_subtype_of_clause(key, pairs, html_h):

    clause_h = div_custom(f"{key}_clause")
    add_html_clause_label(key, clause_h)
    clause_h.append(div_custom("subtype_pairs"))
    for pair in pairs:
        print("Subtyping pair is: ", pair)
        class_name_h = dict_to_html(pair.get("class_name"))
        subtyping_name_h = dict_to_html(pair.get("subtyping_name"))
        # print("Class name element is : ", class_name_h)
        # print("Subtyping element is : ", subtyping_element)
        pair_h = div_custom("subtype_pair", [class_name_h, subtyping_name_h])

        clause_h.append(pair_h)
    html_h.append(clause_h)


def add_data_type_clause(key, data_type, html_h):
    dt_clause_h = div_custom(f"{key}_clause")
    html_h.append(dt_clause_h)
    add_html_clause_label(key, dt_clause_h)
    value = dict_to_html(data_type)
    add_html_clause_value(key, value, dt_clause_h)


def add_anchored_class_names_clause(key, names, html_h):
    add_html_clause(key, names, html_h)


def add_html_clause(key, value, html_h):

    clause_h = div(class_=f"{key}_clause")

    add_html_clause_label(key, clause_h)
    value_h = dict_to_html(value)
    clause_h.append(value_h)

    html_h.append(clause_h)


def add_html_clause_label(key, html_h):
    html_h.append(span_custom("clause_label", [key]))


def add_headless_list_html(key, value, html_h):
    # print("Adding headless list: ", key)
    list_h = div()
    list_h["class"] = [key, "list"]

    for item in value:
        list_h.append(dict_to_html(item))
    html_h.append(list_h)


def add_anchor_html(key_name, value, html_h):

    the_name = str(value)
    name_class = ""
    if isinstance(value, dict):
        the_name = value["content"]
        name_class = value["_type"]
    # print(f"add anchor called for key_name = {key_name}, value = {value} the_name = {the_name}")
    anchor_h = a(the_name, id=the_name, class_=f"{name_class} {key_name}")
    html_h.append(anchor_h)

import traceback
import sys
def add_html_simple_content(obj_type, obj, html_h):
    from ldm.ldm_to_html_prose import as_prose_html

    # print(f"Adding simple: {obj_type} ")
    content = ""
    if isinstance(obj, dict):
        content = obj.get("content", "No content found")
    else:
        content = getattr(obj, "content", "No object content found")

    # print(" SIMPLE CONTENT")
    # print(content)

    try:
        content_h = as_prose_html(content)
        # print(f"Adding simple: {obj_type} with {content_h}")
        html_h.append(div(content_h, class_=f"{obj_type} mdhtml"))
    except Exception:
        print(
            f"failed on simple content: obj type is {obj_type}, content is...\n{content}"
        )
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=sys.stderr)

# @trace_decorator
def add_key_value_html(key, value, html_h):

    value_type = getattr(value, "_type", type(value).__name__)
    div_h = div(class_=value_type)
    # print("ADD_KEY_VALUE")
    # print(div_h)
    
    span1_h = span(f"{key}:", class_="key")
    div_h.append(span1_h)
    div_h.span(dict_to_html(value), class_="value")
    html_h.append(div_h)


def add_html_clause(key, value, html_h):
    # value_type = getattr(value, '_type', type(value).__name__)

    html_h.append(div(class_=f"{key}_clause"))
    clause_h = div(class_=f"{key}_clause")
    html_h.append(clause_h)
    add_html_clause_label(key, html_h)
    add_html_clause_value(key, value, html_h)


def add_html_clause_value(key, value, html_h):
    value_h = span(dict_to_html(value), class_=f"{key}_value value")


def add_classed_value_html(key, value, html_h):
    html_h.append(span(dict_to_html(value), class_=f"{key} value"))


def create_model_html(data, html_path):
    all_dict_keys = all_keys(data)
    print("All keys are: ")
    for x in all_dict_keys:
        print("\t", x)

    # Note html file is in
    #  ldm/ldm_models/MODEL/MODEL_results/Model.html

    # and css is in ldm/ldm_models/ldm_assets
    css_path = "../../ldm_assets/Literate.css"
    save_model_html(data, css_path, html_path)

from utils.class_fluent_html import create_html_root, wrap_deep
def save_model_html(data, css_path, output_path):
    model_h = dict_to_html(data)
    
    html_h = create_html_root()
    head_h = head()
    html_h.append(head_h)

    head_h.append( link(rel="stylesheet", href=css_path))
    head_h.append( script(
                "import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'",
                type="module",
            ))
    body_h = body()
    html_h.append(body_h)
    
    body_h.append(model_h)
    
    body_classes = html_h.find('body').get("class")
    the_body = html_h.find('body')
    print("Body classes are", body_classes)
    # print("Body is: ", the_body)
    html_content = f"{html_h}"
    # Path(output_path).write_text(html_content, encoding="utf-8")
    fmk.write_text(output_path, html_content)
    print(f"Saved styled dictionary to {output_path}")

    html_h.find("body").add_class("reviewing")
    body_classes = html_h.find('body').get("class")
    print("Body classes are", body_classes)
    html_content = f"{html_h}"

    review_output_path = output_path.replace(".html", ".review.html")
    Path(review_output_path).write_text(html_content, encoding="utf-8")
    print(f"Saved styled dictionary (for review) to {review_output_path}")
