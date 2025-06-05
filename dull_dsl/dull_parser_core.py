# import re
from dataclasses import dataclass, field

# from typing import Any, List, Dict, Tuple, Union, Callable, Optional
from typing import Any, List, Dict, Union

# from ldm_parse_bits import parse_header
# from utils.util_fmk_pom import as_yaml
from utils.util_json import as_json, clean_dict
from utils.util_flogging import flogger, trace_method, trace_decorator
from dull_dsl.dull_parser_classes import (
    TypedLine,
    ClauseLine,
    MajorClause,
    # ParseHandler,
    # print_messages,
)
from utils.class_casing import LowerCamel, SnakeCase, UpperCamel

from ldm.Literate_01 import ClassName, AttributeName, OneLiner, Label, Emoji


all_clauses_by_priority = None
part_plurals = None
part_parts = None
listed_parts = None


@dataclass
class DocPart:
    part_type: str
    parent_part: "DocPart" = None
    saved_dull_specs: Dict = None

    items: List[Union[TypedLine, "DocPart", str]] = field(default_factory=list)

    def __init__(self, part_type: str, parent_part: "DocPart" = None):
        self.part_type = part_type
        self.parent_part = parent_part
        self.items = []

    def add_line(self, typed_line: TypedLine):
        # print(f"Adding line to a {self.part_type} Part")
        self.items.append(typed_line)
        nitems = len(self.items)
        # print(f".. now have {nitems} items  in {self.part_type} part")

    def add_doc_part(self, doc_part: "DocPart"):
        self.items.append(doc_part)

    def display(self, level: int = 0):
        displayed = self.displayed(level)
        print(displayed)

    def displayed(self, level: int = 0) -> str:
        displayed = ""
        indent = ". " * level
        displayed += f"{indent}{self.part_type} - {self.__class__} \n"
        level = level + 1
        indent = ". " * level

        for item in self.items:
            displayed += item.displayed(level)
        return displayed

    def derive_dict_for_document(self, dull_specs: Dict):

        self.saved_dull_specs = dull_specs
        global all_clauses_by_priority, part_plurals, part_parts, listed_parts
        all_clauses_by_priority = dull_specs["all_clauses_by_priority"]
        part_plurals = dull_specs["part_plurals"]
        part_parts = dull_specs["part_parts"]
        listed_parts = dull_specs["listed_parts"]

        return self.derive_dict_for_part(0)

    def derive_dict_for_part(self, level: int = 0) -> Dict:
        # identify the full oneliner - ie all text lines immediately after
        # the header should be included.

        ntexts = 0
        the_dict = {}
        the_dict["_type"] = self.part_type

        paragraphs = []

        # print("DerivingDict for Part: ", self.part_type)
        if self.part_type == "Annotation":
            nitems = len(self.items)
            # print(f"THIS IS AN ANNOTATION. All {nitems} items are...")
            # for item in self.items:
            #     print(repr(item))
            # print("...END OF ANNOTATION ITEMS")
        for item in self.items:

            # collect any text/code blocks into paragraphs
            if isinstance(item, TypedLine):
                label = item.type_label
                header_dict = {}
                if label == "CODE_FENCE":
                    print("--- ouch found CODE_FENCE para")
                    print("appending code item...")
                    print(item)
                    paragraphs.append(item)
                    continue

                if label == "TEXT_LINE":
                    print("--- ouch found TEXT para")
                    paragraphs.append(item)
                    continue

                if label == "BLANK_LINE":
                    print("--- ouch found BLANK_LINE")
                    continue

                if label == "ELABORATION":
                    # the_dict["elaboration"] = item
                    the_dict["elaboration"] = convert_to_paragraphs(item)
                    continue

                if label.endswith("_Head"):
                    full_header = item.full_text()
                    # print(f"\t\tFull header is: {full_header}")

                    handlers = item.line_Type.handlers
                    header_dict = handlers.parse(full_header)
                    # print_messages(messages)

                    # if label.startswith("Class"):
                    #     rawname = header_dict.get("name", "NoName")
                    #     # header_dict['name'] = ClassName(rawname)
                    #     header_dict['name'] = ClassName(rawname).to_dict()
                    #     print(repr(ClassName(rawname)))
                    #     print(f"{ClassName(rawname)}")
                    #     print(header_dict)

                    # the_dict["full_header"] = full_header
                    the_dict.update(header_dict)
                    continue

                if (
                    isinstance(item.line_Type, MajorClause)
                    and item.line_Type.class_started == "Annotation"
                ):
                    # print("SPOTTED ANNOTATION in DOCPART: ", item)
                    full_annotation = item.full_text()
                    # print(f"\t\tfull_annotation is: {full_annotation}")

                    handlers = item.line_Type.handlers
                    # (annotation_dict, messages) = handlers.round_trip(full_annotation)
                    annotation_dict = handlers.parse(full_annotation)
                    # print_messages(messages)

                    # the_dict["full_annotation"] = full_annotation
                    # print("Annotation dict: ", annotation_dict)
                    annotation_dict.pop("line_type", None)
                    annotation_dict["content"] = OneLiner(annotation_dict.pop("value", None))
                    # print(".. revised Annotation dict: ", annotation_dict)
                    
                    label = annotation_dict["label"]
                    annotation_dict["label"] = Label(label)
                    
                    emoji = annotation_dict["emoji"]
                    annotation_dict["emoji"] = Emoji(emoji)

                    # print("the dict: ", the_dict)
                    the_dict.update(annotation_dict)
                    continue

                # Note. In order to place the alaboration just after the header
                # elemeents (name, oneliner, etc):
                # =  Once you see something that's not the header, or text
                # insert the elaboration
                if paragraphs:
                    old_paragraphs = the_dict.get("elaboration", [])

                    paragraphs = [
                        "Might be more1"
                    ]  # to avoid reinserting it, but leave open the po ssibility of more text

                if isinstance(item, ClauseLine):
                    clause_dict = item.derive_clause_dict(level)
                    # print("Clause line dict is", clause_dict)
                    for keyword, value in clause_dict.items():
                        # for the real value, we need clause spec

                        att_name = SnakeCase(keyword).content
                        sc = SnakeCase(keyword)
                        # print(f"Keyword = {keyword}. attname = {att_name}, sc = {sc}")
                        if att_name != keyword:
                            print(f"Using ATT_NAME  {att_name} for {keyword}")
                            print(f"Adding value in ddforpart. {att_name} -. {value}")
                        the_dict = absorb_into(
                            the_dict,
                            att_name,
                            value,
                            item.line_Type.is_list,
                            item.line_Type.is_cum,
                        )
                        # print("And the dict has;;;")
                        # print(as_json(the_dict))
                    if (
                        isinstance(item.line_Type, MajorClause)
                        and item.line_Type.class_started in ["Default", "Derivation", "Constraint"]
                        and False
                    ):
                        print("Dict for Formula", the_dict)
                            
                    

                    continue

            elif isinstance(item, DocPart):

                # Note: a part may be the  first  element after the
                # elaboration.  So check again, here
                if paragraphs:
                    old_paragraphs = the_dict.get("elaboration", [])
                    the_dict["elaboration"] = old_paragraphs + paragraphs
                    paragraphs = ["Might be more2"]  # to avoid reinserting it

                part_dict = item.derive_dict_for_part(level)
                part_type = item.part_type
                plural = part_plurals.get(part_type, part_type + "s'")

                is_cum = part_type in listed_parts
                if is_cum:
                    att_name_for_part = SnakeCase(plural).content.lower()
                    # print("Using plural atttribute name: ", att_name_for_part)

                else:
                    att_name_for_part = SnakeCase(part_type).content
                    # print("Using singular atttribute name: ", att_name_for_part)
                if att_name_for_part.lower().startswith("subject"):
                    att_name_for_part = "subjects"
                if att_name_for_part.lower() == "code_types":
                    att_name_for_part = "classes"
                if att_name_for_part.lower() == "value_types":
                    att_name_for_part = "classes"
                att_name_for_part = att_name_for_part.replace("'", "")
                # print(f"att_name_for_part is {att_name_for_part}")
                the_dict = absorb_into(
                    the_dict, att_name_for_part, part_dict, is_list=False, is_cum=is_cum
                )

            else:
                print("DeriveDICT ignoring item??: ", item)

        displayables = ["AttributeSection"]
        displayables = ["Class"]
        displayables = ["Default", "Derivation", "Constraint"]
        displayables = []
        # ["Class", "Attribute", "Formula", "Default"]
        if self.part_type in displayables:
            # print("Re-display for Part: ", self.part_type)

            self.display(1)
            print("DerivedDict for Part: ", self.part_type)
            print(as_json(the_dict))
            print(the_dict)
        # if the_dict.get("name", "") == "Component":
        #     exit(0)
        return clean_dict(the_dict)


# @trace_decorator
def convert_to_paragraphs(item: TypedLine) -> List[str]:
    """
    Convert a TypedLine item into a list of paragraphs.
    """
    # print("Converting to paragraphs: ", item)
    pieces = []
    subitems = item.content
    for subitem in subitems:
        # print("Subitem: ", as_json(subitem))
        element_type = None
        if subitem.type_label == "CODE_FENCE":
            element_type = "CodeBlock"  # "CodeBlock"
            code_content = subitem.content
            # print("CodeContent: ", code_content)
            code_full_text = subitem.full_text()
            # print("CodeFullText: ", code_full_text)
            piece = {"_type": element_type, "content": code_full_text}
            # print("PieceContent: ", piece)
            pieces.append(piece)
            continue

        elif subitem.type_label == "PARAGRAPH":
            element_type = "Paragraph"
        if element_type:
            # Assuming item.content contains the text to be converted
            content = subitem.content
            # print("PieceContent: ", content)
            # for x in content:
            #     print("\t x is ", x)
            #     # print("\t and full text is ", x.full_text())
            para_text = " \n+ ".join(x.full_text() for x in content)
            piece = {"_type": element_type, "content": para_text}
            pieces.append(piece)
        else:
            print("DictingError: something odd  in elaboration--", item)

    # print("ReturningElaboration: ", pieces)
    return pieces


def absorb_into(
    the_dict: Dict, keyword: str, value: Any, is_list: bool, is_cum: bool
) -> Dict:
    # print(f"Absorbing to {keyword} {value} into {the_dict}")
    # don't clutter the dict with empty values
    if not value:
        return the_dict

    if not is_cum and not is_list:
        # to do:  always check if the value is already there
        #  if it is for non-cum, that's an error
        # print("\tNeither is_list nor is_cum; create scalar value")
        the_dict[keyword] = value

    else:  # create an empty list value, if necessary
        # to do.  If not cum, still an error to have a dup entry
        # print("\tEither is_list or is_cum; create list value")

        if not the_dict.get(keyword, None):
            the_dict[keyword] = []

        if not is_list:  # ie single value from parse function
            # print(f"Append {value} to {keyword}")
            the_dict[keyword].append(value)
        else:
            # print(f"Extend {value} to {keyword}")

            the_dict[keyword].extend(value)
    # print("after absorb, dict has: ", the_dict)
    return the_dict
