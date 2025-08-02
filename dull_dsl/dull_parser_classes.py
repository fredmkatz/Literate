import re
from dataclasses import dataclass, field
from abc import ABC
from typing import Any, List, Dict, Tuple, Callable, Optional
from ldm.ldm_parse_fns import (
    ParseHandler,
    ParseName,
    ParseNameList,
    ParseTrivial,
    ParseAttributeReference,
    ParseHeader,
    ParseAnnotation,
    keyword_pattern,
    # print_messages,
    TRIVIAL_HANDLER,
)


# from ldm_parse_bits import parse_header
# from utils.util_fmk_pom import as_yaml
# from utils.util_json_pom import as_json
from utils.util_flogging import flogger, trace_method

from utils.class_casing import LowerCamel, SnakeCase


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
# all_clauses_by_priority = None
# part_plurals = None
# part_parts = None
# listed_parts = None


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
class Clause(LineType):
    word: str = ""  # e.g. "based on"
    line_label: str = ""  # Moved from parent with default
    attribute_name: str = ""
    is_list: bool = False
    is_cum: bool = False
    special_pattern: str = ""
    plural: str = ""

    handlers: ParseHandler = None
    kw_pattern: str = field(default="", init=False)  # for recognition

    # def __str__(self):
    #     return "Clause: {self.line_label}"

    def __post_init__(self):
        if self.special_pattern:
            self.kw_pattern = self.special_pattern
        else:
            self.kw_pattern = keyword_pattern(self.word)
        if not self.line_label:
            self.line_label = self.word.replace(" ", "_").upper()
        if not self.handlers:
            self.handlers = TRIVIAL_HANDLER
        if not self.attribute_name:
            self.attribute_name = self.word

        # self.attribute_name = str(SnakeCase(self.attribute_name))

        if not self.plural:
            if self.is_list:  # assume that the name is already plural
                self.plural = self.attribute_name
            else:
                self.plural = self.attribute_name + "_s"

    def matches(self, trimmed) -> bool:
        return re.match(self.kw_pattern, trimmed, re.IGNORECASE)


@dataclass
class MajorClause(Clause, PartStarter):  # Order of inheritance is important
    # No additional fields, but we need to ensure parameter order is correct

    def __post_init__(self):
        super().__post_init__()
        # If needed, set line_label from both parents properly


@dataclass
class MinorClause(Clause):
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
            extras = (" \n+ ").join(self.extra_text)
        return f"{self.type_label}: {self.content}{extras}"

    def full_text(self) -> str:
        # print("content is ", self.content)
        # print("extra_text is ", self.extra_text)
        return self.content + "\n" + ("\n").join(self.extra_text)

    def display(self, level):
        print(self.displayed(level))

    def displayed(self, level) -> str:
        indent = "_ " * level
        return f"{indent}{self}\n"


class ClauseLine(TypedLine):
    line_Type: Clause

    # @trace_method
    def derive_clause_dict(self, level=0) -> Dict:
        # print(f"derive_clause_dict for {self}")
        the_dict = {}
        full_text = self.full_text()

        if ":" not in full_text:
            print(f"ERROR: No colon in clause?? - {self}, full_text is {full_text}")
            return the_dict
        splits = full_text.split(":", 1)
        if len(splits) != 2:
            print(f"ERROR:  {len(splits)} splits found for {self}")
        (keyword, rest_of_line) = splits

        handlers = self.line_Type.handlers
        # print("Using handlers: ", handlers)

        att_name = self.line_Type.attribute_name
        # print(f"att_name is {att_name} for {self.line_Type} is {att_name}")
        if att_name == "constraint":
            att_name = "one_liner"
            # print(f"Patched att_name is {att_name} for {self.line_Type} is {att_name}")

        from ldm.Literate_01 import OneLiner
        import utils.util_all_fmk as fmk
        if handlers:

            # get the attribute name from the type, not the label
            # (rtvalue, messages) = handlers.round_trip(rest_of_line)
            rtvalue = handlers.parse(rest_of_line)
            # print(f"adding name value. {att_name} -. {rtvalue}")
            # print_messages(messages)
            if att_name == "one_liner":
                # the_dict[att_name] = OneLiner(rtvalue)  # todo - This is a hack!
                the_dict[att_name] = {"_type": "OneLiner", "content": rtvalue}
                # print(f"thedict[{att_name}] =", the_dict[att_name])
            else:
                the_dict[att_name] = rtvalue
                # print(f"thedict[{att_name}] =", the_dict[att_name])

            # print(the_dict)
        else:
            print(f"Found clause-spec but no handlers for {self.type_label}")
        return the_dict


def print_messages(messages: List[str]):
    print("Messages...")
    for message in messages:
        print("..Message: ", message)
