import json
from pathlib import Path
from utils.util_fmk import write_text
from typing import Dict, List

from Literate_01 import *

# Perplexity on md to html
# https://www.perplexity.ai/search/best-python-markdown-to-html-b-R1stqFsKQ.6gGtS1PWnsLw
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
    "LDM",
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
    html = []

    # print(f"htmling {data}")

    if isinstance(data, str):
        return data

    python_type = type(data)
    type_label = "NA"
    if isinstance(data, dict):
        type_label = data.get("_type", "NoDictTypeLabel")
        print("htmling dict with _type = ", type_label)
    else:
        type_label = getattr(data, "_type", "NoNonDictTypeLabel")
        print("htmling Python type  ", python_type, "; type_label is ", type_label)

    if type_label == "ClassName":
        return class_name_link(data)

    if isinstance(data, dict):

        obj_type = "DICT"
        for key, value in data.items():
            if key == "_type":
                obj_type = value
                break
        if obj_type in SIMPLE_CONTENT_TYPES:
            add_html_simple_content(obj_type, data, html)

            return "\n".join(html)
        if obj_type == "DataTypeClause":
            return dt_as_html(data)
        if obj_type == "BaseDataType":
            print("bdt. dict is ", data)
            print("bdt. classname is ", data.get("class_name"))

            bdt_html2 = span_div(data, "BaseDataType", "class_name", "as_value_type")
            return bdt_html2
        if obj_type == "MappingDataType":
            print("mdt. dict is ", data)
            print("mdt. domain_type is ", data.get("domain_type"))
            print("mdt. range_type is ", data.get("range_type"))

            mdt_html2 = span_div(data, "MappingDataType", "domain_type", "range_type")
            return mdt_html2
        if obj_type == "ListDataType":
            print("ldt. dict is ", data)
            print("ldt. element_type is ", data.get("element_type"))

            ldt_html2 = span_div(data, "ListDataType", "element_type")
            return ldt_html2
        if obj_type == "DataTypeClause":
            return span_div(data, "DataTypeClause", "is_optional_lit", "data_type")
        if obj_type == "ClassName":
            return class_name_link(data)
        if obj_type == "AsValue":
            print("Found ASVALUE dict", data)
            as_value = AsValue(data["t_value"])
            if not as_value:
                return ""
            return str(f'<span class="as_value">{as_value}</span>')
        if obj_type == "IsOptional":
            opt_value = str(IsOptional(data["t_value"])).strip()
            print("opt value is ", opt_value)
            if not opt_value:
                return ""
            print("using opt value is ", opt_value)

            return str(f'<span class="is_optional">{opt_value}</span>')

        if obj_type == "Annotation":
            emoji = spanned_value(data, "emoji")
            label = spanned_value(data, "label")
            content = spanned_value(data, "content")
            return div("Annotation", [emoji, label, content])

        # if obj_type in ["Formula", "Constraint", "Derivation", "Default"]:
        #     content = dict_div(data, "content")
        #     message = dict_div(data, "message")
        #     code = dict_div(data, "code")
        #     severity = dict_div(data, "severity")
        #     notes = dict_div(data, "annotations")
        #     return div(obj_type, [content, code, message, severity, notes])

        # Simplify SubjectB, etc
        if obj_type.startswith("Subject"):
            obj_type = "Subject"
        # print("Object type is ", obj_type)
        html.append(f'<div class="{obj_type}">')

        # Gather into header: Prefix, name, oneliner, parenthetical
        if is_headed(obj_type):
            # Start the header
            html.append(f'<div class="{obj_type}_header header">')

            # add header attributes
            for key, value in data.items():
                if key == "_type":
                    continue
                if key not in HEADER_KEYS:
                    continue
                # print("kv is ", key, value)
                if str(value).strip() == "":
                    continue
                if key == "name":
                    add_anchor_html(key, value, html)
                    continue
                if key == "one_liner":
                    add_html_simple_content("OneLiner", value, html)
                    continue

                else:
                    add_classed_value_html(key, value, html)

            # end the header
            html.append("</div>")
        if is_formula(obj_type):
            one_liner = data.get("one_liner", "")
            add_html_clause(obj_type, one_liner, html)
            # formula class is open. Leave it so
            # collect all the details (code, english, etc)
            # "header" all in the clause above

        for key, value in data.items():

            if key == "_type":
                continue
            if key in HEADER_KEYS:
                continue
            if key in USELESS_LIST_KEYS:
                add_headless_list_html(key, value, html)
                continue
            if key == "subtype_of":
                add_subtype_of_clause(key, value, html)
                continue
            if key == "data_type":
                add_data_type_clause("dataType", value, html)
                continue

            if key in CLASS_LIST_KEYS:
                add_anchored_class_names_clause(key, value, html)
                continue

            # Defaults and Derivations need special treatment
            if key in ["default", "derivation"]:
                html.append(dict_to_html(value))
                continue
            # subclauses of Formulas

            if key == "code":
                add_html_clause(key, value, html)
                continue
            if key == "message":
                add_html_clause(key, value, html)
                continue
            if key == "severity":
                add_html_clause(key, value, html)
                continue
            print("Orphaned dict: ", key)
            add_key_value_html(key, value, html)
        html.append(f"</div>")

    elif isinstance(data, list):
        print("Orphaned list: ", data)

        html.append(f'<div class="list">')
        for item in data:
            html.append(dict_to_html(item))
        html.append(f"</div>")
    else:
        print("Orphaned ?", type(data), ": ", data)
        return f"{data}"

    return "\n".join(html)


from utils.util_flogging import trace_decorator


@trace_decorator
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
    return f"<a class='{css_class}' href='#{anchor_name}' >{display_name}</a>"


from utils.util_flogging import flogger, trace_decorator


@trace_decorator
def bdt_as_html(data_type, as_plural: bool = False) -> str:
    class_name = data_type["class_name"]
    as_value = data_type["as_value_type"]

    anchored_name = class_name["content"]
    displayed_name = class_name["content"]
    if as_plural:
        displayed_name = plural_of(class_name)

    print(f"BDT anchored name is {anchored_name}, display name is {displayed_name}")
    class_anchor = anchor_html("base_class", displayed_name, anchored_name)
    print("BDT class anchor is ", class_anchor)
    ref_or_value = "reference"
    if as_value:
        ref_or_value = "value"
    if as_plural:
        ref_or_value += "_es"

    return span("base_data_type", [class_anchor, ref_or_value])


def ldt_as_html(data_type, as_plural: bool = False) -> str:
    element_type = data_type["element_type"]

    element_html = dt_as_html(element_type, True)
    prefix = "List of"
    if as_plural:
        prefix = "Lists of"
    return span("list_data_type", [prefix, element_html])


def sdt_as_html(data_type, as_plural: bool = False) -> str:
    element_type = data_type["element_type"]

    element_html = dt_as_html(element_type, True)
    prefix = "Set of"
    if as_plural:
        prefix = "Sets of"
    return span("set_data_type", [prefix, element_html])


def mdt_as_html(data_type, as_plural: bool = False) -> str:
    domain_type = data_type["domain_type"]
    range_type = data_type["domain_type"]

    domain_html = dt_as_html(domain_type, False)
    range_html = dt_as_html(range_type, True)
    prefix = "Mapping from"
    if as_plural:
        prefix = "Mappings from"
    return span("mapping_data_type", [prefix, domain_html, " to ", range_html])


def spanned_value(data, attribute):
    value = data.get(attribute).strip()
    if not value:
        return ""
    return f"<span class={attribute}>{value}</span>"


def dict_div(data, css_class, *attributes):
    at_htmls = []
    for attribute in attributes:
        at_html = dict_to_html(data.get(attribute))
        at_htmls.append(at_html)
    print("htmls are: ", at_htmls)
    return div(css_class, at_htmls)


def span_div(data, css_class, *attributes):
    at_htmls = []
    for attribute in attributes:
        at_html = dict_to_html(data.get(attribute))
        at_htmls.append(at_html)
    print("htmls are: ", at_htmls)
    return span(css_class, at_htmls)


def div(css_class, pieces):
    html = f'<div class="{css_class}">\n'
    print("Pieces are: ", pieces)
    html += "\n".join(pieces)
    html += "</div>"
    print("Div returning: ", html)
    return html


def span(css_class, pieces):
    html = f'<span class="{css_class}">\n'
    print("Pieces are: ", pieces)
    html += "\n".join(pieces)
    html += "</span>"
    print("span returning: ", html)
    return html


def add_value_html(value, html):

    value_html = dict_to_html(value)
    line = f"<div>{value_html}</div>"
    html.append(line)


def class_name_link(data):
    content = getattr(data, "content", None)
    if not content:
        content = data.get("content", "StillNoName")
    return f'<span class="class_name_link" href="#{content}">{content}</span>\n'


def add_subtype_of_clause(key, pairs, html):

    html.append(f'<div class="{key}_clause">')
    add_html_clause_label(key, html)
    html.append(f'<div class="subtype_pairs">')
    for pair in pairs:
        print("Subtyping pair is: ", pair)
        class_name_html = dict_to_html(pair[0])
        subtyping_element = pair[1]
        print("Subtyping element is : ", subtyping_element)
        # subtyping_name = subtyping_element.get("content", "subtypes")
        subtyping_name = "bySomething"
        if subtyping_name != "subtypes":
            pair_element = div("subtype_pair", [class_name_html, subtyping_name])
        else:
            pair_element = div("subtype_pair", [class_name_html])

        html.append(dict_to_html(pair_element))
        # html.append(f'<a class="class_name" href="#{name}">{name}</a>')
    html.append(f"</div>")
    html.append(f"</div>")


def add_data_type_clause(key, data_type, html):
    html.append(f'<div class="{key}_clause">')
    add_html_clause_label(key, html)
    value = dict_to_html(data_type)
    add_html_clause_value(key, value, html)

    html.append(f"</div>")


def add_anchored_class_names_clause(key, names, html):
    add_html_clause(key, names, html)


def add_html_clause(key, value, html):
    html.append(f'<div class="{key}_clause">')
    add_html_clause_label(key, html)
    print(f"For clause: {key}, seeking html for {value}")
    value_html = dict_to_html(value)
    print(f"And got html: {value_html}")
    html.append(value_html)
    html.append(f"</div>")


def add_html_clause_label(key, html):
    html.append(f'<span class="clause_label">{key}</span>')


def add_headless_list_html(key, value, html):

    html.append(f'<div class="{key} list">')
    for item in value:
        html.append(dict_to_html(item))
    html.append(f"</div>")


def add_anchor_html(key_name, value, html):

    the_name = str(value)
    name_class = ""
    if isinstance(value, dict):
        the_name = value["content"]
        name_class = value["_type"]
    print(
        f"add anchor called for key_name = {key_name}, value = {value} the_name = {the_name}"
    )
    html.append(f'<a class="{name_class} {key_name}"  id="{the_name}">{the_name}</a>')


def add_html_simple_content(obj_type, obj, html):
    from ldm.do_md_parse import as_prose_html

    print(f"Adding simple: {obj_type} ")
    content = ""
    if isinstance(obj, dict):
        content = obj.get("content", "No content found")
    else:
        content = getattr(obj, "content", "No object content found")

    html_content = as_prose_html(content)
    print(f"Adding simple: {obj_type} with {html_content}")
    html.append(f'<div class="{obj_type} mdhtml">')
    html.append(f"  {html_content}")
    html.append(f"</div>")


def add_html_div(obj_type, content, html):
    html.append(f'<div class="{obj_type}">')
    html.append(f"  {content}")
    html.append(f"</div>")


def add_key_value_html(key, value, html):

    value_type = getattr(value, "_type", type(value).__name__)
    html.append(f'<div class="{value_type}">')
    html.append(f'  <span class="key">{key}:</span>')
    html.append(f'  <span class="value">{dict_to_html(value)}</span>')
    html.append(f"</div>")


def add_html_clause(key, value, html):
    value_type = getattr(value, "_type", type(value).__name__)

    html.append(f'<div class="{key}_clause">')
    add_html_clause_label(key, html)
    add_html_clause_value(key, value, html)

    html.append("</div>")


def add_html_clause_value(key, value, html):
    value_html = dict_to_html(value)
    html.append(span(f"{key}_value value", [value_html]))


def add_classed_value_html(key, value, html):

    html.append(f' <span class="{key} value">{dict_to_html(value)}</span>')



