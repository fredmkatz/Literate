from typing import List

from utils.util_flogging import trace_decorator

from utils.util_html_helpers import *

from utils.class_fluent_html import FluentTag
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
    "subtype_of",
    "subtypes",
]

SIMPLE_CONTENT_TYPES = [
    # "Paragraph",
    # "OneLiner",
    # "CodeBlock",
    "Label",
    "Emoji",
]
PROSE_CONTENT_TYPES = [
    "Paragraph",
    "OneLiner",
    "CodeBlock",
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
    "SubtypeBy",
    "ClassName",
] + FORMULA_CLASSES


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
    if obj is None:
        return None

    if isinstance(obj, (int, float, bool, str)):
        str_value = str(obj).strip()
        if str_value == "":
            return None
        
        return span(str_value)


    obj_type = "NA"

    if isinstance(obj, list):
        print("Orphaned list: ", obj)

        items_h = []

        for item in obj:
            items_h.append(as_html(item))
        list_h = div_custom("orphaned list", items_h)
        print("listh", list_h)
        return list_h

    if isinstance(obj, dict):
        obj_type = obj.get("_type", "NoDictTypeLabel")

    else:
        print(
            "Orphaned ?",
            type(obj),
            ": ",
            obj,
            ". Should be str, int, bool, list, or dict",
        )
        return f"{obj}"

    # Now, we have a dict, with a _type and python_type
    # print("htmling object  ", obj_type)

    if obj_type in SIMPLE_CONTENT_TYPES:
        the_content = obj.get("content", None)
        if not the_content:
            return None
        return span(the_content, class_=obj_type)

    if obj_type in PROSE_CONTENT_TYPES:
        return html_prose_content(obj_type, obj)

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
            value_h = field_value_html(key, value)
            header_h.append(value_h)
        # and add header to object
        object_h.append(header_h)

    # then add the other fields to to object html
    for key, value in obj.items():
        if key == "_type":
            continue

        if key in HEADER_KEYS:  # already have these
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

    if obj_type == "ClassName":
        return class_anchor(data)
    if obj_type == "SubtypeBy":
        return as_html(data.get("class_name"))
        # return None
        sby_h = dict_div(data, "SubtypeBy", "class_name", "subtyping_name")

        print("SubtypingBy ", data, " =>\n", sby_h)
        return sby_h
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
        print("SPANDIV for DTC")
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
        object_type = spanned_dict_entry(data, "object_type")
        object_name = spanned_dict_entry(data, "object_name")
        category = spanned_dict_entry(data, "category")
        severity = spanned_dict_entry(data, "severity")

        message = ""
        message_obj = data.get("message", None)
        if message_obj:
            message = message_obj.get("content")
        message = span_custom("message", [message])
        print("Diagnostic message is ", message)
        return div_custom(
            "Diagnostic", [severity, category, message, " on ", object_type]
        )

    if obj_type in FORMULA_CLASSES:
        formula_h = dict_div(
            data,
            obj_type,
            "one_liner",
            "english",
            "code",
            "message",
            "severity",
            "annotations",
        )
        print("Formula data ", data)
        print("Formula html: \n", formula_h)
        return formula_h

    # If nothing listed, then just pile all attributes into a div
    # print("Special special for ", obj_type)
    special_h = div(class_=obj_type)
    for key, value in data.items():
        if key == "_type":
            # print(f"Skipping _type for {obj_type}.{key}")

            continue
        if value is None:
            print(f"Skipping None value for {obj_type}.{key}")

        fv_h = field_value_html(key, value)
        if fv_h is None:
            print(f"NOT Skipping Non html for {obj_type}.{key}")
            # continue
        special_h.append(fv_h)
    # print(f"Special {obj_type} becomes:\n", special_h)
    return special_h


def field_value_html(field_name, value):
    if value is None:
        return None
    value_h = as_html(value)
    if value_h is None:
        print("fvh returning None1 for ", field_name)
        return None

    if not isinstance(value_h, FluentTag):
        value_h = span(str(value_h))
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


def class_anchor(class_name, as_plural: bool = False):

    anchored_name = class_name["content"]
    displayed_name = class_name["content"]
    if as_plural:
        displayed_name = plural_of(class_name)

    # print(f"BDT anchored name is {anchored_name}, display name is {displayed_name}")
    class_anchor = link_html("base_class", displayed_name, anchored_name)
    return class_anchor


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
    # print("Adding headless list: ", key)
    list_h = div()
    list_h["class"] = [key, "list"]

    for item in value:
        list_h.append(as_html(item))
    html_h.append(list_h)


def clause_html(key, value_h):
    if value_h is None:
        return None
    if not isinstance(value_h, FluentTag):
        value_h = span(value_h)
    key_h = span(key, class_=f"key {key}")
    value_h.add_class(f"{key} value")
    clause_h = div(key_h, value_h, class_=f"clause {key}_clause")
    return clause_h


def dict_div(data, css_class, *attributes):
    at_htmls = []
    for attribute in attributes:
        at_html = as_html(data.get(attribute))
        at_htmls.append(at_html)
    # print("htmls are: ", at_htmls)
    return div_custom(css_class, at_htmls)


import traceback
import sys


def html_prose_content(obj_type, obj):
    from ldm.ldm_to_html_prose import as_prose_html

    # print(f"Adding simple: {obj_type} ")
    content = "SimpleContent?"
    if isinstance(obj, dict):
        content = obj.get("content", None)
        if not content:
            return None

    # print(" SIMPLE CONTENT")
    # print(content)

    try:
        content_h = as_prose_html(content)
        # print(f"Adding simple: {obj_type} with {content_h}")
        return div(content_h, class_=f"{obj_type} mdhtml")
    except Exception:
        print(
            f"failed on simple content: obj type is {obj_type}, content is...\n{content}"
        )
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=sys.stderr)




def create_model_html_as(model_dict, html_path):
    all_dict_keys = all_keys(model_dict)
    print("All keys are: ")
    for x in all_dict_keys:
        print("\t", x)

    # Note html file is in
    #  ldm/ldm_models/MODEL/MODEL_results/Model.html

    # and css is in ldm/ldm_models/ldm_assets
    css_path = "../../ldm_assets/Literate.css"
    save_model_html_as(model_dict, css_path, html_path)


from utils.class_fluent_html import create_html_root


def save_model_html_as(model_dict, css_path, output_path):
    model_h = as_html(model_dict)

    html_h = create_html_root()
    head_h = head()
    html_h.append(head_h)

    head_h.append(link(rel="stylesheet", href=css_path))
    head_h.append(
        script(
            "import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs'",
            type="module",
        )
    )
    body_h = body()
    html_h.append(body_h)

    body_h.append(model_h)

    body_classes = html_h.find("body").get("class")
    print("Body classes are", body_classes)

    html_content = f"{html_h}"
    fmk.write_text(output_path, html_content)
    print(f"Saved styled dictionary to {output_path}")

    html_h.find("body").add_class("reviewing")
    body_classes = html_h.find("body").get("class")
    print("Body classes are", body_classes)
    html_content = f"{html_h}"

    review_output_path = output_path.replace(".html", ".review.html")
    fmk.write_text(review_output_path, html_content)

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
