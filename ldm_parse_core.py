import re
from dataclasses import dataclass, field
from abc import ABC
from typing import Any, List, Dict, Tuple

from ldm_parse_bits import parse_full_header
from utils_pom.util_fmk_pom import as_yaml
from ldm_parse_bits import (        # to do. Not really core
    parse_attribute_reference,
    parse_full_header,
    parse_input_line,
    parse_name,
    parse_input_line2,
    parse_name_list,
    parse_trivial,
)

# """
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
# """

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
    parse_function: str = "parse_trivial"
    kw_pattern: str = field(default="", init=False)  # for recognition

    def __post_init__(self):
        self.kw_pattern = keyword_pattern(self.word)
        self.line_label = self.word.replace(" ", "_").upper()

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
    extra_text: List[str] = field(default_factory=list, init=False )

    def __str__(self):
        extras = ""
        if self.extra_text:
            extras = "\nExtraText = \n" + ("\n\t").join(self.extra_text) + "\n"
        return f"{self.type_label}: {self.content}{extras}"
    
    def full_text(self) -> str:
        return self.content + str(self.extra_text) 

@dataclass
class DocPart:
    part_type: str
    parent_part: "DocPart" = None

    sublines: List[TypedLine] = field(default_factory=list)

    subparts: List["DocPart"] = field(default_factory=list)


    def __init__(self, part_type: str, parent_part: "DocPart" = None):
        self.part_type = part_type
        self.parent_part = parent_part
        self.sublines = []
        self.subparts = []
        if parent_part:
            parent_part.subparts.append(self)

    def add_line(self, typed_line: TypedLine):
        # print(f"Adding line to a {self.part_type} Part")
        self.sublines.append(typed_line)
        nlines = len(self.sublines)
        # print(f".. now have {nlines} in {self.part_type} part")

    def display(self, level: int = 0):
        indent = ". " * level
        print(f"{indent}{self.part_type} - {self.__class__} ")
        level = level + 1
        indent = ". " * level

        for line in self.sublines:
            print(f"{indent}{line}")

        for part in self.subparts:
            part.display(level)

    def process(self, level: int = 0) -> Dict:
        indent = ". " * level
        print(
            f"Processing {indent}{self.part_type} - {self.__class__}"
        )

        the_dict = self.process0(level)
        level = level + 1
        indent = ". " * level

        for part in self.subparts:
            part_dict = part.process(level)

            part_type = part.part_type
            specific_parts_name = part_type + "_PARTS"
            specific_parts_list = the_dict.get(specific_parts_name, [])
            specific_parts_list.append(part_dict)
            the_dict[specific_parts_name] = specific_parts_list

        if self.part_type in ["Class", "Attribute"]:
            print(f"Fully procesed YAML {self.part_type} Dict\n", as_yaml(the_dict))

        return the_dict

    def process0(self, level: int = 0) -> Dict:
        my_dict = {}
        my_dict["_type"] = self.part_type
        return my_dict

    def get_clause_values(self, keys_sought) -> List[Tuple]:
        clauses = []
        for line in self.sublines:
            if line.type_label in keys_sought:
                (keyword, rest_of_line) = line.content.split(":", 2)
                clauses.append([line.type_label, rest_of_line])
        return clauses


@dataclass
class ComponentChunk(DocPart):

    def __init__(self, part_type, parent):
        super().__init__(part_type, parent)


    def process0(self, level) -> Dict:
        from ldm_parse_ldm import all_clauses, all_clause_specs     # to do
        # identify the full oneliner - ie all text lines immediately after
        # the header should be included.
        lines = self.sublines
        ntexts = 0
        
        header_line = lines[0]
        full_header = header_line.full_text()
        if full_header != header_line.content:
            print("ExtraText here...")
        print(f"\t\tFull header is: {full_header}")

        the_dict = parse_full_header(full_header)
        the_dict["full_header"] = full_header
        ## collect the paragrapsh for the elaboration
        paras = []
        paralines = []
        for line in lines[ntexts + 1 :]:
            if line.type_label == "BLANK_LINE":  # End current para, start a fresh one
                if paralines:
                    para = "\n".join(paralines)
                    paras.append(para)
                    paralines = []
                continue  # i.e. ignore blank lines
            if line.type_label == "TEXT_LINE":
                paralines.append(line.content)
        if paras:
            print("\t\tELABORATION is: ", paras)
            the_dict["elaboration"] = paras

        clauses = self.get_clause_values(all_clauses)
        if clauses:
            print(f"Found clauses: {clauses}")
        for clause in clauses:
            (keyword, line) = clause
            the_dict[keyword] = line
            clause_spec = all_clause_specs.get(keyword, None)
            if clause_spec:  # tells us what to call and what to do with the value
                print(f"Found clause_spec  for {keyword}is {clause_spec}")
                funcname = clause_spec.parse_function
                value = globals()[funcname](line)
                valueterm = keyword + "_value"
                # if the value is not is_cum amd mot a list either, just add the value to the dict

                if not clause_spec.is_cum and not clause_spec.is_list:
                    # to do:  always check if the value is already there
                    #  if it is for non-cum, that's an error
                    print("\tNeither is_list nor is_cum; create scalar value")
                    the_dict[valueterm] = value
                    the_dict[keyword] = line

                else:  # create an empty list value, if necessary
                    # to do.  If not cum, still an error to have a dup entry
                    print("\tEither is_list or is_cum; create list value")

                    if not the_dict.get(valueterm, None):
                        the_dict[valueterm] = []
                        the_dict[keyword] = []
                    the_dict[keyword].append(line)
                    if not clause_spec.is_list:  # ie single value from parse function
                        the_dict[valueterm].append(value)
                    else:
                        the_dict[valueterm].extend(value)
            else:
                print(f"No clause_spec for clause: {keyword}???")
                the_dict[keyword] = line

        return the_dict




@dataclass
class FormulaChunk(DocPart):
    def __init__(self, part_type, parent):
        super().__init__(part_type, parent)


    def process(self, level: int = 0) -> Dict:
        the_dict = super().process(level)

        return the_dict

    def process0(self, level: int = 0) -> Dict:
        the_dict = super().process0(level)
        the_dict["_type"] = self.part_type
        line = self.sublines[0].content
        the_dict["top_text"] = line.split(":", 2)[1]
        return the_dict





@dataclass
class AnnotationChunk(DocPart):
    def __init__(self, part_type, parent):
        super().__init__(part_type, parent)


    def process(self, level: int = 0) -> Dict:
        the_dict = super().process(level)

        return the_dict

    def process0(self, level: int = 0) -> Dict:
        the_dict = super().process0(level)

        return the_dict
