from typing import List, Any
from collections import defaultdict

from faculty_base_v3 import Faculty, faculty_class, patch_on, show_patches
from ldm.Literate_01 import *

from utils.util_flogging import trace_decorator

from utils.util_html_helpers import *

from utils.class_fluent_html import FluentTag

import utils.util_all_fmk as fmk
PROSE_CONTENT_TYPES = [
    "Paragraph",
    "OneLiner",
    "CodeBlock",
]



@faculty_class
class Htmlers(Faculty):
    """Faculty for adding validation methods to LDM classes."""
    
    def object_html(self, obj: Any, method_name: str = "as_html"):
        """Create the html for an object using the appropriate patched method."""
        if not obj:
            return None

        patched_func = self.resolve_patched_method(obj, method_name)
        if patched_func:
            return patched_func(obj)
        return None
    
    # the ultimate fallback
    @patch_on(object, "as_html")
    def any_html(self):
        name = getattr(self, "name", "Anon")
        otype = type(self).__name__
        stub  = div(f"- Stub for {otype}: {name}")
        return stub

    
    @patch_on(Paragraph, "as_html")
    def paragraph_html(para):
        return html_prose_content("Paragraph", para)

    @patch_on(OneLiner, "as_html")
    def one_liner_html(para):
        return html_prose_content("OneLiner", para)
    
    # @patch_on(OneLiner, "as_html")
    # def one_liner_html(self):
        
    #     otype = type(self).__name__
    #     return  div(p(self.content), class_ = "OneLiner")

    @patch_on(CodeBlock, "as_html")
    def code_block_html(para):
        return html_prose_content("CodeBlock", para)

    @patch_on(str, "as_html")
    def str_html(self):
        
        # return span - to avoid NavigableStrings
        return span(self)

    def call_super_html(self, obj, current_class_name: str = None):
        """Helper to call super().as_html() equivalent."""
        return self.call_super_method(obj, "as_html", current_class_name)
    
    @patch_on(list, "as_html")
    def list_html(self):
        elements_h = html_for_elements_of(self)
        ldiv = div()
        for element in elements_h:
            ldiv.append(element)
        # print("From patched on list: ")
        # print(ldiv)
        return ldiv
    @patch_on(Annotation, "as_html")
    def annotation_html(self):
        achunk = html_chunk(self, "emoji", "label", "content")
        # print("Annotation chunk is : ", achunk)
        return achunk

    @patch_on(Emoji, "as_html")
    def emoji_html(self):
        symbol = getattr(self, "symbol", None)
        if not symbol:
            return None
        return span(symbol, class_ = "Emoji")

    @patch_on(Casing, "as_html")
    def casing_html(self):
        
        otype = type(self).__name__
        return  span(self.content, class_ = otype)
    
    # @patch_on(Paragraph, "as_html")
    # def paragraph_html(self):
        
    #     return  p(self.content)
    
    @patch_on(ClassName, "as_html")
    def class_name_html(self):
        
        otype = type(self).__name__
        return  span(self.content, class_ = otype, id=self.content)

    @patch_on(ClassReference, "as_html")
    def class_reference_html(self):
        class_anchor = link_html("class_reference", self.content, self.content)
        return class_anchor


    @patch_on(SubtypeBy, "as_html")
    def subtype_by_html(self):
        
        return html_chunk(self, "class_name", "subtping_name")

    @patch_on(DataTypeClause, "as_html")
    def dtc_html(self):
        
        return html_chunk(self, "is_optional_lit", "data_type", "cardinality")

    @patch_on(BaseDataType, "as_html")
    def bdt_html(self):
        as_plural  = False
        class_name = self.class_name
        as_value = self.as_value_type

        anchored_name = class_name.content
        displayed_name = anchored_name
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
            
        bdt_h = span(class_anchor, ref_or_value, class_ = "base_data_type")
        # print("bdt html is ", bdt_h)
        return bdt_h

    @patch_on(ListDataType, "as_html")
    def ldt_html(self):
        as_plural = False
        element_type = self.element_type
        
        # print("LDT element type is ", element_type)

        element_html = object_html(element_type)
        # print("LDT element html is: ", element_html)
        prefix = "List of"
        if as_plural:
            prefix = "Lists of"
        return span(prefix, element_html, class_ = "list_data_type" )

    @patch_on(SetDataType, "as_html")
    def sdt_as_html(self, as_plural: bool = False) -> str:
        element_type = self.element_type
        
        # print("SDT element type is ", element_type)

        element_html = object_html(element_type)
        # print("SDT element html is: ", element_html)
        prefix = "Set of"
        if as_plural:
            prefix = "Sets of"
        return span(prefix, element_html, class_ = "set_data_type" )
    
    @patch_on(MappingDataType, "as_html")
    def mdt_html(self):
        
        as_plural = False
        domain_type = self.domain_type
        range_type = self.domain_type

        domain_html = object_html(domain_type) #, False)
        range_html = object_html(range_type) #, True)
        prefix = "Mapping from"
        if as_plural:
            prefix = "Mappings from"
        return span(prefix,
                    domain_html, 
                    " to ", 
                    range_html, 
                    class_ = "mapping_data_type")

    @patch_on(IsOptional, "as_html")
    def is_optional_html(self):
        
        return span(str(self), class_ = "AsValue")
    
    @patch_on(AsValue, "as_html")
    def as_value_html(self):
        
        return span(str(self), class_ = "AsValue")
        
    @patch_on(Formula, "as_html")
    def formula_html(self):
        
        one_liner_h = html_for_value(self, "one_liner")
        
        formula_h = div()
        formula_h.append_all(one_liner_h,
                            clauses_for(self, "ocl", "message", "severity"),
                            each_listed(self, "annotations"),
                            each_listed(self, "diagnostics")
                             )
        
        return formula_h

    @patch_on(Diagnostic, "as_html")
    def diagnostic_html(self):
        return html_chunk(self, "severity", "category", 
                          "message", "object_type", "object_name")


    @patch_on(Component, "as_html")
    def component_html(self):
        """Base as_html for all Components"""
        
        name = self.name
        otype = type(self).__name__
        comp_h = div(class_ = otype)
        header_h = html_chunk(self, "prefix", "name", "one_liner", 
                              "parenthetical", "data_type_clause")
        header_h["class"] = ["header", otype + "_header"]
        
        if otype.startswith("Subject"):
            comp_h.add_class("Subject")
            header_h.add_class("Subject")
            
            # pspan = header_h.find('span', class_= "prefix")
            # if pspan:
            #     print("Found prefix span in ", header_h)
            #     print("pspan is ", pspan)

            #     pspan.string = "HI!"
            #     pspan.replace_with(span("HiAgain"), class_ = "prefix"))
            #     print("Now it says - ", header_h)
            # else:
            #     print("No prefix span in ", header_h)
        
        comp_h.append_all(header_h,
                        each_listed(self, "elaboration"),
                        each_listed(self, "annotations"),
                        each_listed(self, "diagnostics") )
        
        return comp_h
        

    @patch_on(LiterateModel, "as_html")
    def literate_model_html(self):
        
        # Handle as any old Subject
        # Call super validator with explicit class name
        comp_html = _html_faculty.call_super_html(self, 'LiterateModel')
        

        
        return comp_html

    @patch_on(SubjectE, "as_html")  # base for LDM and all Subjects
    def subject_html(self):
        # Call super validator with explicit class name
        
        # Get container for whole components, with header as a start
        comp_html = _html_faculty.call_super_html(self, 'SubjectE')
        
        comp_html.append_all(each_listed(self, "classes"),
                             each_listed(self, "subjects")
        )

        return comp_html
    
    @patch_on(Class, "as_html")  # and CodeType, ValueType
    def class_html(self):
        # Call super validator with explicit class name
        
        # Get container for whole components, with header as a start
        comp_html = _html_faculty.call_super_html(self, 'Class')
        
        pieces = clauses_for(self, "where",
                                    "plural",
                                    "presumed_plural",
                                    "based_on",
                                    "dependents",
                                    "subtype_of",
                                    )
        
        pieces.extend(each_listed(self, "subtypings"))

        constraint_clauses = clause_for_each(self, "constraints")

        if constraint_clauses:
            pieces.extend(constraint_clauses)
        pieces.extend(each_listed(self, "attributes"))
        pieces.extend(each_listed(self, "attribute_sections"))

        for piece in pieces:
            comp_html.append(piece)
        
        return comp_html
    
    @patch_on(Subtyping, "as_html")
    def subtyping_html(self):
        st_html2 = class_names_clause(self, "subtypes")
        return st_html2
        
    @patch_on(AttributeSection, "as_html")
    def attribute_section_html(self):
        # Get container for whole components, with header as a start
        comp_html = _html_faculty.call_super_html(self, 'AttributeSection')
        att_htmls = each_listed(self, "attributes")
        comp_html.append_all(att_htmls)

        return comp_html

    @patch_on(Attribute, "as_html") 
    def attribute_html(self):
        # Call super validator with explicit class name
        
        # Get container for whole components, with header as a start
        comp_html = _html_faculty.call_super_html(self, 'Attribute')
        
        pieces = [
            # clause_for(self, "data_type_clause"),
            clause_for(self, "inverse"),
            clause_for(self, "derivation"),
            clause_for(self, "default"),
            # clause_for_each(self, "constraints"),
            clause_for(self, "overrides"),
        ]
        
        constraint_clauses = clause_for_each(self, "constraints")
        if constraint_clauses:
            pieces.extend(constraint_clauses)
        # pieces.extend(each_listed(self, "constraints"))
        
        for piece in pieces:
            comp_html.append(piece)
            
        return comp_html
    
    @patch_on(AttributeName, "as_html")
    def attribute_name_html(self):
        
        otype = type(self).__name__
        return  span(self.content, class_ = otype, id=self._html_id)

    @patch_on(AttributeReference, "as_html") 
    def attribute_reference_html(self):
        link_display = self.class_name.content + "." + self.attribute_name.content
        link_id = self.class_name.content + "__" +  self.attribute_name.content
        aref_h = link_html("AttributeReference", link_display, link_id)
        return aref_h


    
# Helper functions
import traceback
import sys

def html_prose_content(obj_type, obj):
    from ldm.ldm_to_html_prose import as_prose_html

    print(f"Adding simple: {obj_type} ")
    print("...obj is ", obj)
    content = obj.content
    if not content:
        content = f"Empty content for {obj_type}??"
        return None


    try:
        content_h = as_prose_html(content)
        print("...contenth for prose html is...")
        print(content_h)
        print("...end of contenth for prose html .")
        return div(content_h, class_=f"{obj_type} mdhtml")
    except Exception:
        print(
            f"failed on simple content: obj type is {obj_type}, content is...\n{content}"
        )
        traceback.print_exc(file=sys.stdout)
        traceback.print_exc(file=sys.stderr)


def plural_of(name):
    if isinstance(name, dict):
        return name["content"] + "-es"
    return str(name) + "_es"





def class_anchor(class_name, as_plural: bool = False):

    anchored_name = class_name.content
    displayed_name = class_name.content
    if as_plural:
        displayed_name = plural_of(class_name)

    # print(f"BDT anchored name is {anchored_name}, display name is {displayed_name}")
    class_anchor = link_html("base_class", displayed_name, anchored_name)
    # print("... and anchor is ", class_anchor)
    return class_anchor






def html_chunk(obj, *field_names):
    otype = type(obj).__name__
    
    object_h = div(class_ = otype)
    for field_name in field_names:
        field_value = getattr(obj, field_name, None)
        if not field_value:
            continue
        field_h = object_html(field_value) 
        if not field_h:
            continue
        field_h.add_class(field_name)
        object_h.append(field_h)
    return object_h

def each_listed(obj, att_name):
    the_list = getattr(obj, att_name, None)
    if not the_list:
        return []
    # print("Each listed: ", att_name)
    return html_for_elements_of(the_list)


def html_for_elements_of(lst):
    return [ object_html(item) for item in lst]

def html_for_value(obj, att_name):
    value = getattr(obj, att_name, None)
    if not value:
        return None
    value_h = object_html(value)
    return value_h

def clauses_for(obj, *att_names):
    return [clause_for(obj, att_name) for att_name in att_names]

CommaSeparatedLists = [
    'subtype_of',
    'subtypes',
    'dependents',
    'based_on',
]
def clause_for(obj, att_name):
    
    value = getattr(obj, att_name, None)
    if not value:
        return None
    if isinstance(value, list):
        if not att_name in CommaSeparatedLists:
            print("Unexpected list: ", att_name)
            value_h = object_html(value)
        else:
            # print("HTMLing list value for ", att_name)
            value_h = comma_separated_html(value)
    else:
        value_h = object_html(value)
    
    clause_h = clause_for_value(att_name, value_h)
    return clause_h

def class_names_clause(obj, att_name):
    value = getattr(obj, att_name, None)
    if not value:
        return None
    if not isinstance(value, list):
        print("class_names_list expects a LIST of ClassNames")
        return None
    
    print("for attribute ", att_name, " class_names_clause handed: ", value)
    class_names = [c.content for c in value]
    # class_names = [c.get("content", "ClassRef?") for c in value]
    print("class_names are: ", class_names)
    value_h = comma_separated_html(class_names)
    
    class_anchors = [class_anchor(c, as_plural=False) for c in value]
    print("class_anchors are: ", class_anchors)

    value_h = comma_separated_tags(class_anchors)
    
    clause_h = clause_for_value(att_name, value_h)
    return clause_h

def clause_for_value(att_name, value_h):
    if not value_h:
        return None
    value_h.add_class("value")
    value_h.add_class(att_name)
    clause_h = div(class_ = f"clause {att_name}_clause")
    upper_att_name = str(UpperCamel(att_name))
    clause_h.append(span(upper_att_name, class_ = f"key {att_name}"))
    clause_h.append(value_h)
    return clause_h

def clause_for_each(obj, att_name):
    values = getattr(obj, att_name, None)
    if not values:
        return None
    
    clauses_h = []
    for value in values:
        value_h = object_html(value)
        clause_h = clause_for_value(att_name, value_h)
        clauses_h.append(clause_h)
    
    # print("Clauses for each: ")
    # for clause in clauses_h:
    #     print(clause)
    return clauses_h
        
def comma_separated_html(the_list):
    
    elements_h = html_for_elements_of(the_list)
    ldiv = div()
    is_first = True
    for element in elements_h:
        if not is_first:
            ldiv.append(", ")
        is_first = False
        ldiv.append(element)
    return ldiv

def comma_separated_tags(the_list):
    
    elements_h = the_list
    ldiv = div()
    is_first = True
    for element in elements_h:
        if not is_first:
            ldiv.append(", ")
        is_first = False
        ldiv.append(element)
    return ldiv


# Create the htmlers instance
_html_faculty = Htmlers()
print("Created Htmlers() = ", _html_faculty)
show_patches(_html_faculty.all_patches)

def object_html(the_object):
    object_h = _html_faculty.object_html(the_object)
    return object_h




def create_model_html_with_faculty(the_model, html_path, css_path):

    # Note html file is in
    #  ldm/ldm_models/MODEL/MODEL_results/Model.html

    # and css is in ldm/ldm_models/ldm_assets
    save_model_html_with_faculty(the_model, css_path, html_path)


from utils.class_fluent_html import create_html_root


def save_model_html_with_faculty(the_model, css_path, output_path):
    model_h = object_html(the_model)

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
    
    body_h.append(div("FIRST PAGE LEFT LEFT BLANK", class_ = "true-first-page"))

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

