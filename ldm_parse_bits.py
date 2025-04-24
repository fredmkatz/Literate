import random
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, List



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


def coloned(word: str) -> str:
    pass


@dataclass
class LineStart:
    starter: str
    line_type: str


@dataclass
class Keyword:
    word: str
    pattern: str
    label: str

    def __init__(self, word):
        self.word = word
        self.pattern = keyword_pattern(word)
        self.label = word.replace(" ", "_").upper()


line_starts = [
    LineStart("_", "Class"),
    LineStart("-", "Attribute"),
    LineStart("#####", "Section5"),
    LineStart("####", "Section4"),
    LineStart("###", "Section3"),
    LineStart("##", "Section2"),
    LineStart("#", "LDM"),
    LineStart("```", "CodeBlock"),
]

keywords = [
    # for Components
    Keyword("abbreviation"),
    Keyword("name"),
    Keyword("plural"),
    Keyword("note"),
    Keyword("issue"),
    Keyword("example"),
    Keyword("see"),
    # for Classes
    Keyword("subtype of"),
    Keyword("subtypes"),
    Keyword("based on"),
    Keyword("dependents"),
    Keyword("Constraint"),
    Keyword("dependent of"),
    Keyword("where"),
    Keyword("plural"),
    # For Attributes
    Keyword("data type"),
    Keyword("inverse"),
    Keyword("inverse of"),
    Keyword("overrides"),
    Keyword("Derivation"),
    Keyword("Default"),
    # for Formulas
    Keyword("code"),
    Keyword("english"),
    Keyword("message"),
    Keyword("severity"),
    # TBD
    Keyword("value type"),
    Keyword("AnAnnotation"),
]

# A name consists of one or more words, separated by spaces
#   Each word contains upper or lower case letters, digits, and
#   underscores
# parse_name should return the "bare" names, in whatever case
# they have in the input, retaining any speces
# The complication:  these names are coming from markdown docs.
# They might be boldfaced or italicized or both
# they might even include markdown anchors
# In some cases, they might be boldfaced or italiciized along with
# a trailing colon.  So parse name has to get through all that
# to just produce the bare words.


# def parse_name(input: str) -> str:
#     pass
# def parse_name_list(input: str) -> str:
#     # for a comma separated list of names, with all the complexities
#     # above

#     pass
# def parse_attribute_reference(input: str) -> Dict:
#     # for ClassName.AttributeName, each name as above

#     # class_name
#     # attribute_name
#     pass
# def parse_input_line(input: str) -> Dict:
#     # to figure out what kind of line we have.  Could be:
#     # - a header line, with one of the prefixes listed in line_starts
#     # - a labeled value:   Label: value
#     #     The label might be one of the terms listed in Keywords
#     #       or a variant, based on case and presence of spaces
#     #       And, with all the highlighting issues of names
#     #       But it might also be an arbitrary name.
#     #
#     #    If the line starts with a prefix, then return the corresponding
#     #       word in LineStarts
#     #   If it starts wth a name + colon, return the name as label
#     #   Labels might be preceded by emojis; if so return the emoji as
#     #   well

#     # Returns a dict with
#         # emoji
#         # label
#         # prefix
#         # rest_of_line

#     pass
# def parse_full_header(header: str) -> Dict:
#     # A header line will start with one of the  prefixes above, followed by
#     #   NAME - one liner (parenthetical) - all but name is optional.
#     #       also: the parenthetical may be followed by a period - other
#     #       than the period, it must be at the end of the line.  If it's
#     #       in the middles of the line, it's just part of the one liner
#     # Returns dict containing:
#     #     - name
#     #     - one_liner
#     #     - parenthetical

#     pass

import re


def parse_trivial(input_str: str) -> str:
    return input_str


def render_trivial(saved: str) -> str:
    return saved


def validate_trivial(saved: str) -> bool:
    if saved:
        return True
    return True


def parse_name(input_str: str) -> str:
    """Extract a bare name from text that might include markdown formatting."""
    if not input_str:
        return ""

    # First, remove markdown formatting symbols
    # Remove bold and italic markers (*, _, **, __)
    cleaned = re.sub(r"[*_]+", "", input_str)

    # Remove any markdown links [text](url) -> text
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)

    # Remove any trailing colons
    cleaned = re.sub(r":+\s*$", "", cleaned)

    # Remove any leading/trailing whitespace
    cleaned = cleaned.strip()

    return cleaned


def render_name(saved: str) -> str:
    if saved:
        return saved
    return saved

def is_name(name: str) -> bool:
    SYLLABLE = r"[A-Za-z][A-Za-z0-9]*"
    IDENTIFIER = rf"{SYLLABLE}(SYLLABLE)*"
    
    return re.fullmatch(IDENTIFIER, name)
 

def validate_name(saved_name: str) -> bool:
    if saved_name:
        return True
    return True


###
def parse_name_list(input_str: str) -> list[str]:
    """Parse a comma-separated list of names with potential markdown formatting."""
    print(f"parse_name_list: {input_str}")
    if not input_str:
        return []

    # Split by commas
    parts = re.split(r",\s*", input_str)

    # Clean each part
    cleaned_names = [parse_name(part) for part in parts]

    # Filter out empty strings
    return [name for name in cleaned_names if name]


def render_name_list(names: List[str]) -> str:
    return ", ".join(names)


def validate_name_list(names: List[str]) -> Tuple[bool, str]:
    print("validating name list: ", names)
    if not isinstance(names, List):
        return False, f"NameList doesn't seem to be a list at all: {names}"
    for name in names:
        if not is_name(name):
            return False, f"Name in NameList is not a name: {name}"
    return True


def parse_att_ref(input_str: str) -> dict:
    """Parse a reference in the form ClassName.AttributeName."""
    if not input_str:
        return {"class_name": "", "attribute_name": ""}

    # Clean the input first to remove any markdown
    cleaned = parse_name(input_str)

    # Split by dot
    parts = re.split(r"\.\s*", cleaned, 1)

    if len(parts) == 2:
        return {"class_name": parts[0].strip(), "attribute_name": parts[1].strip()}
    else:
        # If there's no dot, assume it's just a class name
        return {"class_name": cleaned, "attribute_name": ""}

def render_att_ref(ar_dict: Dict) -> str:
    class_name = ar_dict.get("class_name", "NoClassName")
    attribute_name = ar_dict.get("attribute_name", "NoAttributeName")
    return f"{class_name}.{attribute_name}"

def validate_att_ref(ar_dict: Dict) -> Tuple[bool, Optional[str]]:
    if not isinstance(ar_dict, Dict):
        return False, "attribute reference dict is not a Dict"
    class_name = ar_dict.get("class_name", None)
    attribute_name = ar_dict.get("attribute_name", None)
    if not class_name:
        return False, f"Missing class_name: {ar_dict}"
    if not attribute_name:
        return False, f"Missing attribute_name: {ar_dict}"
    if not is_name(class_name):
        return False, f"class_name, {class_name}, is not a name"
    if not is_name(attribute_name):
        return False, f"attribute_name, {attribute_name}, is not a name"
    return True


def parse_input_line(input_str: str) -> dict:
    """
    Parse an input line to determine its type and extract components.

    Returns a dict with keys that might include:
    - line_type: The type of line (header, labeled_value, etc.)
    - prefix: Any prefix found at the start
    - emoji: Any emoji at the start
    - label: Any label before a colon
    - value: The content after the label
    """
    if not input_str:
        return {"line_type": "empty"}

    # Trim whitespace
    line = input_str.strip()

    # Check for line starters
    for starter in line_starts:
        if line.startswith(starter.starter):
            # It's a header or special line type
            rest = line[len(starter.starter) :].strip()
            return {
                "line_type": starter.line_type,
                "prefix": starter.starter,
                "rest_of_line": rest,
            }

    # Check for emoji followed by label and colon
    emoji_match = re.match(r"^([\U0001F300-\U0001F9FF]+)\s+([^:]+):(.*)", line)
    if emoji_match:
        return {
            "line_type": "labeled_value",
            "emoji": emoji_match.group(1),
            "label": parse_name(emoji_match.group(2)),
            "value": emoji_match.group(3).strip(),
        }

    # Check for label and colon
    label_match = re.match(r"^([^:]+):(.*)", line)
    if label_match:
        return {
            "line_type": "labeled_value",
            "emoji": "",
            "label": parse_name(label_match.group(1)),
            "value": label_match.group(2).strip(),
        }

    # If none of the above, it's just regular text
    return {"line_type": "text", "content": line}


def parse_header(header: str) -> dict:
    """
    Parse a header line with the pattern "PREFIX NAME - one liner (parenthetical)".

    Returns a dict containing:
    - name: The extracted name
    - one_liner: The one-liner description (if present)
    - parenthetical: The content in parentheses (if present)
    """
    result = {"name": "", "one_liner": "", "parenthetical": ""}

    # First, identify the line type and get the rest of the line
    parsed = parse_input_line(header)
    if "rest_of_line" not in parsed:
        return result

    rest = parsed.get("rest_of_line", "")

    # Extract name (everything up to a dash or parenthesis)
    name_match = re.match(r"^([^-\(]+)(?:[-\(]|$)", rest)
    if name_match:
        result["name"] = parse_name(name_match.group(1))
        rest = rest[len(name_match.group(1)) :].strip()

    # Extract one-liner (between dash and parenthesis, if present)
    if rest.startswith("-"):
        rest = rest[1:].strip()  # Remove the dash
        one_liner_match = re.match(r"^([^\(]+)(?:\(|$)", rest)
        if one_liner_match:
            result["one_liner"] = one_liner_match.group(1).strip()
            rest = rest[len(one_liner_match.group(1)) :].strip()

    # Extract parenthetical
    parenthetical_match = re.match(r"^\(([^\)]+)\)", rest)
    if parenthetical_match:
        result["parenthetical"] = parenthetical_match.group(1).strip()

    return result

def render_header(head_dict: Dict) -> str:
    name = head_dict.get("name", None)
    one_liner = head_dict.get("one_liner", None)
    parenthetical = head_dict.get('parenthetical', None)
    
    header = name if name else "NAME?"
    if one_liner:
        header += " - " + one_liner
    if parenthetical:
        header += " (" + parenthetical + ")"
    return header

def validate_header(head_dict: Dict)-> Tuple[bool, Optional[str]]:
    name = head_dict.get("name", None)
    if not name:
        return False, "No name found"
    if not is_name(name):
        return False, f"Name = '{name}' is not a valid name"
    return True, None

def parse_input_line2(input_str: str) -> dict:
    """
    Parse an input line from LDM markdown format.
    """
    if not input_str:
        return {"line_type": "empty"}

    # Trim whitespace
    line = input_str.strip()

    # Check for triple-angle bracket sections
    if line == "<<<":
        return {"line_type": "marked_text_start"}

    if line == ">>>":
        return {"line_type": "marked_text_end"}

    # Check for line starters
    for starter in line_starts:
        if line.startswith(starter.starter):
            # It's a header or special line type
            rest = line[len(starter.starter) :].strip()
            return {
                "line_type": starter.line_type,
                "prefix": starter.starter,
                "rest_of_line": rest,
            }

    # Check for emoji followed by label and colon
    emoji_match = re.match(r"^([\U0001F300-\U0001F9FF]+)\s+([^:]+):(.*)", line)
    if emoji_match:
        return {
            "line_type": "labeled_value",
            "emoji": emoji_match.group(1),
            "label": parse_name(emoji_match.group(2)),
            "value": emoji_match.group(3).strip(),
        }

    # Check for label and colon (with potential markdown formatting)
    label_match = re.match(r"^([*_]*[^:]+[*_]*):(.*)", line)
    if label_match:
        return {
            "line_type": "labeled_value",
            "emoji": "",
            "label": parse_name(label_match.group(1)),
            "value": label_match.group(2).strip(),
        }

    # If none of the above, it's just regular text
    return {"line_type": "text", "content": line}


def test_parsers():
    # Test parse_name
    assert parse_name("**Test**") == "Test"
    assert parse_name("*Example*:") == "Example"
    assert parse_name("[Link Text](url)") == "Link Text"

    # Test parse_name_list
    assert parse_name_list("**Item1**, *Item2*, Item3") == ["Item1", "Item2", "Item3"]

    # Test parse_attribute_reference
    assert parse_att_ref("Class.Attribute") == {
        "class_name": "Class",
        "attribute_name": "Attribute",
    }

    # Test parse_input_line
    assert (
        parse_input_line("_ **Component** - A building block").get("line_type")
        == "Class"
    )
    assert (
        parse_input_line("- **name** - The name (Type)").get("line_type") == "Attribute"
    )
    assert parse_input_line("🔄 **Default**: value").get("emoji") == "🔄"

    # Test parse_full_header
    header_result = parse_header("_ **Component** - An element (Type)")
    assert header_result["name"] == "Component"
    assert header_result["one_liner"] == "An element"
    assert header_result["parenthetical"] == "Type"

    print("All tests passed!")


# Run the tests
test_parsers()
