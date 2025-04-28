
import re
from dataclasses import dataclass
from abc import ABC
# from typing import Any, List, Dict, Tuple, Union, Callable, Optional
from typing import Any, List, Dict, Tuple, Optional
from utils_pom.util_json_pom import tidy_empties

# from utils_pom.util_fmk_pom import as_yaml

def keyword_pattern(word: str) -> str:
    if word == "AnAnnotation":
        pattern = "[ a-z]+"
        return pattern
    pattern2 = word.replace(" ", r"\s?")
    stars = r"[_\*]*"
    stars2 = r"[_\*:]*"
    pattern3 = f"{stars}{pattern2}{stars2}"
    final = pattern3
    # print(f"final pattern for {word} = {final}")
    return final




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
    LineStart("__", "AttributeSection"),
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


def is_name(name: str) -> bool:
    SYLLABLE = r"[A-Za-z][A-Za-z0-9]*"
    IDENTIFIER = rf"{SYLLABLE}(SYLLABLE)*"
    
    return re.fullmatch(IDENTIFIER, name)


@dataclass
class ParseHandler(ABC):

    def __post_init__(self):
        pass

    def parse(self, input_str: str) -> Any:
        return "X"

    def validate(self, result: Any) -> Tuple[bool, Optional[str]]:
        return (True, "No message")

    def render(self, result: Any) -> str:
        return "X"


    def round_trip(self, the_string : str) -> Tuple[Any, Optional[List[str]]]:
        messages = []

        value = self.parse(the_string)

        returns = self.validate(value)
        if not isinstance(returns, List):
            validated = returns
            message = "NOMESSAGE"
        else:
            validated = returns[0]
            message = returns[1]

        if not validated:
            messages.append(
                f"ERROR: {value} does not validate " + "==" + message
            )
        else:
            messages.append(f"OK. {value} ok for ")

        output = self.render(value)
        # print(f"RoundTrip  renders as - '{output}'")

        value2 = self.parse(output)
        # print(f"RoundTrip : reparses as - {value2}")

        success = "SUCCESS"
        if value2 != value:
            success = "FAILURE"
        messages.append(
            f"RoundTrip {success}: {the_string}\n\t\t=parse=> {value} \n\t\t=render=> {output} \n\t\t=parse=> {value2}"
        )
        return value, messages





@dataclass
class ParseTrivial(ParseHandler):

    def parse(self, input_str: str) -> str:
        return input_str

    def render(self, saved: str) -> str:
        return saved

    def validate(self, saved: str) -> Tuple[bool, Optional[str]]:
        return True, "No message for trivial1"
 
TRIVIAL_HANDLER = ParseTrivial()


@dataclass
class ParseName(ParseHandler):
    
    def parse(self, input_str: str) -> str:
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

    def render(self, saved: str) -> str:
        return saved

    def validate(self, saved_name: str) -> Tuple[bool, Optional[str]]:
    
        if not saved_name:
            return False, "Name is missing"
        if not is_name(saved_name):
            return False, f"Name - {saved_name} - not a valid name"
        return True, None

 
@dataclass
class ParseNameList(ParseHandler):
    
        def parse(self, input_str: str) -> list[str]:
            """Parse a comma-separated list of names with potential markdown formatting."""
            # print(f"parse_name_list: {input_str}")
            if not input_str:
                return []
    
            # Split by commas
            parts = re.split(r",\s*", input_str)
    
            # Clean each part
            cleaned_names = [parse_name(part) for part in parts]
    
            # Filter out empty strings
            return [name for name in cleaned_names if name]
    
    
        def render(self, names: List[str]) -> str:
            return ", ".join(names)
    
    
        def validate(self, names: List[str]) -> Tuple[bool, Optional[str]]:
            # print("validating name list: ", names)
            if not isinstance(names, List):
                return False, f"NameList doesn't seem to be a list at all: {names}"
            for name in names:
                if not is_name(name):
                    return False, f"Name in NameList is not a name: {name}"
            return True, None
###

@dataclass
class ParseAttributeReference(ParseHandler):
    def parse(self, input_str: str) -> dict:
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
        
    def render(self, ar_dict: Dict) -> str:
        """Render the attribute reference as ClassName.AttributeName."""
        class_name = ar_dict.get("class_name", "NoClassName")
        attribute_name = ar_dict.get("attribute_name", "NoAttributeName")
        return f"{class_name}.{attribute_name}"
    
    def validate(self, ar_dict: Dict) -> Tuple[bool, Optional[str]]:
        """Validate the attribute reference dictionary."""
        if not isinstance(ar_dict, Dict):
            return False, "Attribute reference dict is not a Dict"
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
        return True, None





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

@dataclass
class ParseHeader(ParseHandler):
    def parse(self, input_str: str) -> dict:
        """
        Parse a header line with the pattern "PREFIX NAME - one liner (parenthetical)".

        Returns a dict containing:
        - name: The extracted name
        - one_liner: The one-liner description (if present)
        - parenthetical: The content in parentheses (if present)
        """
        return parse_header(input_str)

    def render(self, head_dict: Dict) -> str:
        return render_header(head_dict)

    def validate(self, head_dict: Dict) -> Tuple[bool, Optional[str]]:
        return validate_header(head_dict)   

def parse_header(header: str) -> dict:
    """
    Parse a header line with the pattern "PREFIX NAME - one liner (parenthetical)".

    Returns a dict containing:
    - name: The extracted name
    - one_liner: The one-liner description (if present)
    - parenthetical: The content in parentheses (if present)
    """
    result = {"prefix": "", "name": "", "one_liner": "", "parenthetical": ""}

    # First, identify the line type and get the rest of the line
    parsed = parse_input_line(header)
    # print("PARSED AS INPUT LINE ", parsed)
    if "rest_of_line" not in parsed:
        print("No rest of line")
        return result
    
    result["prefix"] = parsed.get("prefix", "")

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

    return tidy_empties(result)

def render_header(head_dict: Dict) -> str:
    prefix = head_dict.get("prefix", "PREFIX?")
    name = head_dict.get("name", None)
    one_liner = head_dict.get("one_liner", None)
    parenthetical = head_dict.get('parenthetical', None)
    
    header = prefix +  " "
    
    header += name if name else "NAME?"
    if one_liner:
        header += " - " + one_liner
    if parenthetical:
        header += " (" + parenthetical + ")"
    return header

def validate_header(head_dict: Dict)-> Tuple[bool, Optional[str]]:
    # print("Validating header")
    name = head_dict.get("name", None)
    if not name:
        # print("REturning noname")
        return False, "No name found"
    if not is_name(name):
        # print("REturning bad name")

        return False, f"Name = '{name}' is not a valid name"
    # print("returnin True NOMESSAage")
    return True, "No Message"

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

@dataclass
class ParseAnnotation(ParseHandler):
    def parse(self, input_str: str) -> dict:
        """
        Parse an annotation line with the pattern "emoji label: value".

        Returns a dict containing:
        - emoji: The extracted emoji (if present)
        - label: The extracted label
        - value: The content after the label
        """
        parsed = parse_input_line(input_str)
        if parsed.get("line_type") == "labeled_value":
            return parsed
        else:
            return {"line_type": "text", "content": input_str}
        
    def render(self, annotation_dict: Dict) -> str:
        return render_annotation(annotation_dict)
    
    def validate(self, annotation_dict: Dict) -> Tuple[bool, Optional[str]]:
        return validate_annotation(annotation_dict)

def parse_annotation(input_str: str) -> dict:
    the_dict = parse_input_line(input_str)
    the_dict.pop("line_type", None)
    return tidy_empties(the_dict)
    # return the_dict

def validate_annotation(the_dict: Dict) -> Tuple[bool, Optional[str]]:
    label = the_dict.get("label", None)
    if not label:
        return False, "No label found for annotation"
    
    if not is_name(label):
        return False, f"[{label} is not a valid label for annotation]"
    value = the_dict.get("value", None)
    if not value:
        return False, "No value for annotation"
    return True, None

def render_annotation(annotation_dict: Dict) -> str:
    label = annotation_dict.get("label", "NoLABEL?")
    value = annotation_dict.get("value", "NoVALUE")
    emoji = annotation_dict.get('emoji', None)
    
    annotation = ""
    if emoji:
        annotation += f"{emoji} "
    annotation += label + ": " + value
    
    
    return annotation

def test_parsers():
    # Test parse_name
    name_parser = ParseName()
    assert name_parser.parse("**Test**") == "Test"
    assert name_parser.parse("*Example*:") == "Example"
    assert name_parser.parse("[Link Text](url)") == "Link Text"

    # Test parse_name_list
    name_list_parser = ParseNameList()
    assert name_list_parser.parse("Item1, Item2, Item3") == ["Item1", "Item2", "Item3"] 

    # Test parse_attribute_reference
    att_ref_parser = ParseAttributeReference()
    assert att_ref_parser.parse("ClassName.AttributeName") == {
        "class_name": "ClassName",
        "attribute_name": "AttributeName",
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
    head_parser = ParseHeader()
    assert head_parser.parse("_ **Component** - A building block") == { 
        "prefix": "_",
        "name": "Component",    
        "one_liner": "A building block",
        "parenthetical": "",    
    }
    
    

    print("All tests passed!")
    from utils_pom.util_json_pom import as_json
    tests = [
        "_ **Component** - A building block",
        "🔄 **Default**: value",
    ]
    for test in tests:
        print("Testing: ", test)
        result = parse_input_line(test)
        print(as_json(result))
    
    headers = [
        "_ **Component** - An element (Type)",
        "_ **Component** - An element  with a two \
            line oneliner(Type)"
    ]
    for header in headers:
        print("TestingHeader: ", header)
        result = head_parser.parse(header)
        print(as_json(result))

    annotations = [
        "🔄 **Default**: value if none provided",
        '***Example***: "LDM" is the short form of "Literate Data Model".',
        "🔄 ***NoteA***: This attribute is set to true for components that are automatically generated or added during the fleshing out, review, or rendering processes, such as implied attributes or suggested model elements. It helps distinguish embellishments from the core model elements defined in the original LDM source.",
        "ℹ️  ***NoteA***: This attribute is set to true for components that are automatically generated or added during the fleshing out, review, or rendering processes, such as implied attributes or suggested model elements. It helps distinguish embellishments from the core model elements defined in the original LDM source.",
"\u2139\ufe0f ***Note***: This attribute is set to true for annotations that are automatically generated or added during the fleshing out, review, or rendering processes, such as suggestions, issues, or diagnostic messages. It helps distinguish embellishment annotations from the annotations defined in the original LDM source.",
        'wildly: This is an unregistered annotation',

        
    ]
    
    annotation_parser = ParseAnnotation()
    for annotation in annotations:
        print()
        print("TestingAnnotation: ", annotation)

        result = annotation_parser.parse(annotation)
        print(as_json(result))
        rendered = annotation_parser.render(result)
        print(f"Renders as: {rendered}")

# Run the tests
if __name__ == "__main__":
    test_parsers()
