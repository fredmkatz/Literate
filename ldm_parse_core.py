import re
from dataclasses import dataclass, field
from abc import ABC
from typing import Any, List, Dict, Tuple, Union, Callable

from ldm_parse_bits import parse_header
from utils_pom.util_fmk_pom import as_yaml
from utils_pom.util_json_pom import as_json
from utils_pom.util_flogging import flogger, trace_method


# The Rules:
# - Line oriented grammar
# - Doc consists of:
# -- Parts, which contain clauses and other parts
# -- Minor clauses which contain:
# ---  A first clause line
# ---  And some supplemental text (a paragraph worth)
# -- Major clauses, which are also (minor) parts, with
# ---  A starting clause line (plus text?)
# ---  Additional clause lines (wwith their own text)
# ---  May not contain any
# ----   major  parts
# ----   loose text
# ----   minor clauses?
# -- Parts, contain
# --- a Headline (optional?)
# --- + clauses (major or minor)
# --- + other parts
# --- + text blocks/code blocks, etc

def parse_trivial(input_str: str) -> str:
    return input_str


def render_trivial(saved: str) -> str:
    return saved


def validate_trivial(saved: str) -> bool:
    if saved:
        return True
    return True

@dataclass
class ParseHandler:
    parse: Callable[
        [str], Any
    ]  # parse input string; may return any value (str, Dict, list...)
    render: Callable[[Any], str]  # render returned value as text
    validate: Callable[[Any], bool]  # check returned value

TRIVIAL_HANDLER = ParseHandler(parse = parse_trivial, render=render_trivial, validate=validate_trivial)

def keyword_pattern(word: str) -> str:
    if word == "AnAnnotation":
        pattern = "[ a-z]+"
        return pattern
    pattern2 = word.replace(" ", r"\s?")
    stars = r"[_\*]*"
    stars2 = r"[_\*:]*"
    pattern3 = f"{stars}{pattern2}{stars2}"
    final = pattern3
    print(f"final pattern for {word} = {final}")
    return final


## Grammar definition objects


@dataclass
class LineType(ABC):
    line_label: str = ""
    priority: int = 1

    def matches(self, string) -> bool:
        pass


@dataclass
class BlankLine(LineType):
    line_label: str = "BLANK_LINE"

    def matches(self, string) -> bool:
        return string == ""


@dataclass
class PartStarter(LineType):
    class_started: Any = ""  # subtype of Chunk
    line_label: str = ""  # Moved from parent with default


@dataclass
class HeadLine(PartStarter):
    starter_pattern: str = ""
    handlers: ParseHandler = None

    def __post_init__(self):
        self.line_label = self.class_started + "_Head"

    def matches(self, string) -> bool:
        return string.startswith(self.starter_pattern)


@dataclass
class ClauseLine(LineType):
    word: str = ""  # e.g. "based on"
    line_label: str = ""  # Moved from parent with default

    is_list: bool = False
    is_cum: bool = False
    special_pattern: str = ""

    handlers: ParseHandler = None
    kw_pattern: str = field(default="", init=False)  # for recognition
    
    # def __str__(self):
    #     return "ClauseLine: {self.line_label}"

    def __post_init__(self):
        if self.special_pattern:
            self.kw_pattern = self.special_pattern
        else:
            self.kw_pattern = keyword_pattern(self.word)
        self.line_label = self.word.replace(" ", "_").upper()
        if not self.handlers:
            self.handlers = TRIVIAL_HANDLER

    def matches(self, trimmed) -> bool:
        return re.match(self.kw_pattern, trimmed, re.IGNORECASE)


@dataclass
class MajorClause(ClauseLine, PartStarter):  # Order of inheritance is important
    # No additional fields, but we need to ensure parameter order is correct

    def __post_init__(self):
        super().__post_init__()
        # If needed, set line_label from both parents properly


@dataclass
class MinorClause(ClauseLine):
    # No new fields
    pass  # All initialization happens in parent classes


### Run time objects


@dataclass
class TypedLine:
    type_label: str
    line_Type: LineType
    content: str
    extra_text: List[str] = field(default_factory=list, init=False)

    def __str__(self):
        extras = ""
        if self.extra_text:
            extras = (" + ").join(self.extra_text)
        return f"{self.type_label}: {self.content}{extras}"

    def full_text(self) -> str:
        return self.content + str(self.extra_text)

    def display(self, level):
        indent = "_ " * level
        print(f"{indent}{self}")

    @trace_method
    def derive_dict(self, level=0) -> Dict:
        print(f"Derive dict for {self}")
        the_dict = {}
        full_text = self.full_text()
        if ":" not in full_text:
            print(f"ERROR: No colon in clause?? - {self}, full_text is {full_text}")
            return the_dict
        splits = full_text.split(":", 1)
        if len(splits) != 2:
            print(f"ERROR:  {len(splits)} splits found for {self}")
        (keyword, rest_of_line) = splits
        the_dict[keyword + "_raw"] = rest_of_line
            
        handlers = self.line_Type.handlers
        if handlers:
            rtvalue = round_trip(self.type_label, handlers, rest_of_line)
            print(f"adding non raw value. {keyword} -. {rtvalue}")
            the_dict[keyword] = rtvalue
            print(as_json(the_dict))
        else:
                print(f"Found clause-spec but no handlers for {self.type_label}")
        return the_dict

def round_trip(type_label: str, handlers: ParseHandler, string) -> str:
    print(f"RoundTrip {type_label}: input is - '{string}'")

    value = handlers.parse(string)
    print(f"RoundTrip {type_label}: value is - {value}")

    if not handlers.validate(value):
        print(f"ERROR: {value} does not validate - for {type_label}")
    else:
        print(f"OK. {value} ok for {type_label}")
        

    output = handlers.render(value)
    print(f"RoundTrip {type_label}: renders as - '{output}'")

    value2 = handlers.parse(output)
    print(f"RoundTrip {type_label}: reparses as - {value2}")

    success = "SUCCESS"
    if value2 != value:
        success = "FAILURE"
    print(f"RoundTrip {success}: {string}\n\t\t=parse=> {value} \n\t\t=render=> {output} \n\t\t=parse=> {value2}")
    return value

@dataclass
class DocPart:
    part_type: str
    parent_part: "DocPart" = None

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
        indent = ". " * level
        print(f"{indent}{self.part_type} - {self.__class__} ")
        level = level + 1
        indent = ". " * level

        for item in self.items:
            item.display(level)

    def derive_dict(self, level: int = 0) -> Dict:
        # identify the full oneliner - ie all text lines immediately after
        # the header should be included.

        ntexts = 0
        the_dict = {}
        the_dict["_type"] = self.part_type

        paragraphs = []

        print("DerivingDict for Part: ", self.part_type)
        for item in self.items:
            # if isinstance(item, TextBlock):
            #     ## collect the paragrapsh for the elaboration
            #     paras = []
            #     paralines = []
            #     for line in lines[ntexts + 1 :]:
            #         if line.type_label == "BLANK_LINE":  # End current para, start a fresh one
            #             if paralines:
            #                 para = "\n".join(paralines)
            #                 paras.append(para)
            #                 paralines = []
            #             continue  # i.e. ignore blank lines
            #         if line.type_label == "TEXT_LINE":
            #             paralines.append(line.content)
            #     if paras:
            #         print("\t\tELABORATION is: ", paras)
            #         the_dict["elaboration"] = paras
            if isinstance(item, TypedLine):
                label = item.type_label
                header_dict = {}
                if label.endswith("_Head"):
                    full_header = item.full_text()
                    print(f"\t\tFull header is: {full_header}")
                   
                    handlers = item.line_Type.handlers
                    header_dict = round_trip(label, handlers, full_header)
                        
                    the_dict["full_header"] = full_header
                    the_dict.update(header_dict)
                    continue

                if label == "CODE_FENCE":
                    print("--- adding CODE_FENCE para")
                    paragraphs.append(item)
                    continue

                if label == "TEXT_LINE":
                    print("--- adding TEXT para")
                    paragraphs.append(item)
                    continue

                if label == "BLANK_LINE":
                    print("--- skipping BLANK_LINE")
                    continue

                # Note. In order to place the alaboration just after the header
                # elemeents (name, oneliner, etc):
                # =  Once you see something that's not the header, or text
                # insert the elaboration
                if paragraphs:
                    the_dict["elaboration"] = paragraphs
                    paragraphs = None  # to avoid reinserting it

                clause_dict = item.derive_dict(level)
                for keyword, value in clause_dict.items():
                    # always collect the raw values as a cum list (possibly of lists)
                    if keyword.endswith("_raw"):
                        the_dict = absorb_into(
                            the_dict, keyword, value, is_list=False, is_cum=True
                        )
                        continue
                    # for the real value, we need clause spec
                    the_dict = absorb_into(
                        the_dict,
                        keyword,
                        value,
                        item.line_Type.is_list,
                        item.line_Type.is_cum,
                    )

            elif isinstance(item, DocPart):

                # Note: a part may be the  first  element after the
                # elaboration.  So check again, here
                if paragraphs:
                    the_dict["elaboration"] = paragraphs
                    paragraphs = None  # to avoid reinserting it

                part_dict = item.derive_dict(level)
                part_type = item.part_type
                the_dict = absorb_into(
                    the_dict, part_type, part_dict, is_list=False, is_cum=True
                )

            else:
                print("DeriveDICT ignoring item??: ", item)

        displayables = ["AttributeSection"]
        displayables = ["Class"]
        # displayables = ["LDM"]
        # ["Class", "Attribute", "Formula", "Default"]
        if self.part_type in displayables:
            print("Re-display for Part: ", self.part_type)

            self.display(1)
            print("DerivedDict for Part: ", self.part_type)
            print(as_json(the_dict))
        # if the_dict.get("name", "") == "Component":
        #     exit(0)
        return the_dict


def absorb_into(
    the_dict: Dict, keyword: str, value: Any, is_list: bool, is_cum: bool
) -> Dict:

    if not is_cum and not is_list:
        # to do:  always check if the value is already there
        #  if it is for non-cum, that's an error
        print("\tNeither is_list nor is_cum; create scalar value")
        the_dict[keyword] = value

    else:  # create an empty list value, if necessary
        # to do.  If not cum, still an error to have a dup entry
        print("\tEither is_list or is_cum; create list value")

        if not the_dict.get(keyword, None):
            the_dict[keyword] = []

        if not is_list:  # ie single value from parse function
            the_dict[keyword].append(value)
        else:
            the_dict[keyword].extend(value)
    return the_dict
