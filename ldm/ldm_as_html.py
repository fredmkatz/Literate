from utils.util_flogging import trace_decorator
import json
from pathlib import Path
from typing import Dict, List

from bs4 import BeautifulSoup, NavigableString
from Literate_01 import *
from utils.class_fluent_html import  FluentTag
import utils.util_all_fmk as fmk
HEADER_KEYS = [
    "prefix",
    "name",
    "one_liner",
    "parenthetical",
    "data_type_clause",
    "is_optional",
    "content",
    "is_value_type",
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
    "Label",
    "Emoji",
    
]
BARE_FIELDS = [
    "label",
    "content",
    "class_name",
    "attribute_name",
]

SPECIAL_TYPES = [ 
    "DataTypeClause", 
    "BaseDataType",
    "ListDataType",
    "MappingDataType",
    "AsValue",
    "IsOptional",
    "Diagnostic",
    "Annotation",
    
    ]

def is_headed(class_name: str) -> bool:
    return class_name in HEADED_CLASSES or class_name.startswith("Subject")


def is_formula(class_name: str) -> bool:
    return class_name in FORMULA_CLASSES

# as_html:
#   scalar: return string
#   list: return list( as_html (each))
#   dict: header if needed
#       then a clause for each key
#           except for header keys - collect   those into header
#           except for headless lists - then just attach htmls of each element
#       and maybe special cases, which are like headers (ie. attach all field values without key spans)

def as_html(obj):
    if isinstance(obj, str):
        return obj
    
    type_label = "NA"

    if isinstance(obj, str):
        return obj
    elif isinstance(obj, bool):
        return obj
    elif isinstance(obj, int):
        return obj
    elif isinstance(obj, list):
        print("Orphaned list: ", obj)
        
        items_h = []

        for item in obj:
            items_h. append ( as_html(item))
        list_h =  div_custom("orphaned list", items_h)
        print("listh", list_h)
        return list_h
    
    if isinstance(obj, dict):
        type_label = obj.get("_type", "NoDictTypeLabel")
        # print("htmling dict with _type = ", type_label)

    else:
        print("Orphaned ?", type(obj), ": ", obj, ". Should be str, int, bool, list, or dict")
        return f"{obj}"

    # Now, we have a dict, with a _type and python_type
    obj_type = type_label
    print("htmling object  ", type_label)

    if obj_type in SIMPLE_CONTENT_TYPES:
        the_content = obj.get("content", None)
        if not the_content:
            return None
        return span(the_content, class_ = obj_type)

    obj_classes = obj_type

    # Simplify SubjectB, etc
    if obj_type.startswith("Subject"):
        obj_classes = "Subject " + obj_type

        obj_type = "Subject"
    # print("Object type is ", obj_type)
    
    # Handle special types - ie where all fields are just 
    # collected and reformatted
    if obj_type in SPECIAL_TYPES:
        return handle_special(obj_type, obj)
    

    # set up an html container, based on the type
    object_h = div_custom(obj_classes)
    
    # if the object has a header, create one and collect the 
    # header attributes into it
    
    if is_headed(obj_type):
        # Start the header
        header_h = div_custom(f"{obj_type}_header header")
        object_h.append(header_h)

        # add header attributes
        for key, value in obj.items():
            if key not in HEADER_KEYS:
                continue
            if not value:
                continue
            if str(value).strip() == "":
                continue

            # special cases first
            if key == "name":
                name = value.get("content")
                header_h.append(anchor_html(key, name))
                continue

            if key == "is_optional":
                header_h.append(span(value, class_="is_optional"))
                continue

            # but mostly just put the value into the header, as html
            value_h = as_html(value)
            if not isinstance(value_h, FluentTag):
                value_h = NavigableString(str(value_h))
            else:
                value_h.add_class(key)
            header_h.append(value_h)
        # and add header to object
        object_h.append(header_h)
    
    # then add the other fields to to object html
    for key, value in obj.items():
        if key == "_type":
            continue
        
        if key  in HEADER_KEYS: # already have these
            continue
        if not value:
            continue
        if str(value).strip() == "":
            continue
        if key in USELESS_LIST_KEYS:
            add_headless_list_html(key, value, object_h)
            continue

        value_h = as_html(value)
        clause_h = clause_html(key, value_h)
        object_h.append(clause_h)
    return object_h

def handle_special(obj_type, data):
    if obj_type == "DataTypeClause":
        # return as_html(data)
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
    if obj_type == "AsValue":
    #       print("Found ASVALUE dict", data)
        as_value = AsValue(data["t_value"])
        if not as_value:
            return ""
        return span_custom("as_value", [as_value])
    if obj_type == "IsOptional":
        opt_value = str(IsOptional(data["content"])).strip()
        # print("opt value is ", opt_value)
        if not opt_value:
            return ""
        # print("using opt value is ", opt_value)
        return span_custom("is_optional", [opt_value])
    if obj_type == "Diagnostic":
        object_type = spanned_value(data, "object_type")
        object_name = spanned_value(data, "object_name")
        category = spanned_value(data, "category")
        severity = spanned_value(data, "severity")
        
        message = ""
        message_obj = data.get("message", None)
        if message_obj:
            message = message_obj.get("content")
        message = span_custom("message", [message])
        print("Diagnostic message is ", message)
        return div_custom("Diagnostic", [severity, category, message, " on ", object_type])
    
    # If nothing list, then just pile all attributes into a div
    print("Special special for ", obj_type)
    special_h = div(class_ = obj_type)
    for key, value in data.items():
        if key == "_type":
            continue
        special_h.append( field_value_html(key, value))
    print(f"Special {obj_type} becomes:\n", special_h)
    return special_h
        

def field_value_html(field_name, value):
    value_h = as_html(value)
    if not isinstance(value_h, FluentTag):
        value_h = NavigableString(str(value_h))
    else:
        value_h.add_class(field_name)
    return value_h


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

def bdt_as_html(data_type, as_plural: bool = False) -> str:
    class_name = data_type["class_name"]
    as_value = data_type["as_value_type"]

    anchored_name = class_name["content"]
    displayed_name = class_name["content"]
    if as_plural:
        displayed_name = plural_of(class_name)

    # print(f"BDT anchored name is {anchored_name}, display name is {displayed_name}")
    class_anchor = link_html("base_class", displayed_name, anchored_name)
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

def add_headless_list_html(key, value, html_h):
    print("Adding headless list: ", key)
    list_h = div()
    list_h["class"] = [key, "list"]

    for item in value:
        list_h.append(as_html(item))
    html_h.append(list_h)

def div_custom(css_class, pieces=[]):
    div_h = div(class_=css_class)
    for piece in pieces:
        div_h.append(piece)
    return div_h

def spanned_value(data, attribute):
    value = data.get(attribute)
    if attribute == "message":
        print("message value is ", value)
    if not value:
        return ""

    if isinstance(value, str):
        value = value.strip()
    return span(value, class_=attribute)

def span_custom(css_class, pieces):
    html_h = span()
    html_h["class"] = css_class
    # print("span Pieces are: ", pieces)
    for piece in pieces:
        html_h.append(piece)

    # print("span returning: ", html_h)
    return html_h

def clause_html(key, value_h):
    key_h = span(key, class_ = f"key {key}")
    clause_h = div(key_h, value_h, class_ = f"clause {key}_clause")
    return clause_h

def anchor_html(css_class, display_name, anchor_name = ""):
    if not anchor_name:
        anchor_name = display_name
    anchor_h = a(display_name, class_=css_class, id=f"{anchor_name}")
    return anchor_h

def link_html(css_class, display_name, anchor_name = ""):
    if not anchor_name:
        anchor_name = display_name
    anchor_h = a(display_name, class_=css_class, href=f"#{anchor_name}")
    return anchor_h

    
# def anchor_html(key_name, value):

#     the_name = str(value)
#     name_class = ""
#     if isinstance(value, dict):
#         the_name = value["content"]
#         name_class = value["_type"]
#     # print(f"add anchor called for key_name = {key_name}, value = {value} the_name = {the_name}")
#     anchor_h = a(the_name, id=the_name, class_=f"{name_class} {key_name}")
#     return anchor_h


def create_model_html_as(data, html_path):
    all_dict_keys = all_keys(data)
    print("All keys are: ")
    for x in all_dict_keys:
        print("\t", x)

    # Note html file is in
    #  ldm/ldm_models/MODEL/MODEL_results/Model.html

    # and css is in ldm/ldm_models/ldm_assets
    css_path = "../../ldm_assets/Literate.css"
    save_model_html_as(data, css_path, html_path)

from utils.class_fluent_html import create_html_root, wrap_deep
def save_model_html_as(data, css_path, output_path):
    model_h = as_html(data)
    
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
