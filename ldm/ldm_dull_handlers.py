import re
from dataclasses import dataclass
from abc import ABC

# from typing import Any, List, Dict, Tuple, Union, Callable, Optional
from typing import Any, List, Dict, Tuple, Optional
from utils.util_json import clean_dict

from ldm.Literate_01 import (
    ClassName,
    ClassReference,
    AttributeName,
    Label,
    SubjectName,
    AttributeSectionName,
    SubtypingName,
)
from Literate_01 import (
    DataTypeClause,
    BaseDataType,
    ListDataType,
    SetDataType,
    AsValue,
    MappingDataType,
)
from Literate_01 import OneLiner, DataType, IsOptional

# from utils.util_fmk_pom import as_yaml
from utils.class_casing import UpperCamel, LowerCamel


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
    LineStart("Class", "Class"),
    LineStart("CodeType:", "CodeType"),
    LineStart("ValueType:", "ValueType"),
    LineStart("-", "Attribute"),
    LineStart("#####", "Section5"),
    LineStart("####", "Section4"),
    LineStart("###", "Section3"),
    LineStart("##", "Section2"),
    LineStart("#", "LiterateModel"),
    LineStart("```", "CodeBlock"),
]

keywords = [
    # for Components
    Keyword("abbreviation"),
    Keyword("name"),
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
    Keyword("ocl"),
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
    IDENTIFIERS = rf"{IDENTIFIER}(\s+{IDENTIFIER})*"

    return re.fullmatch(IDENTIFIERS, str(name))


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

    def round_trip(self, the_string: str) -> Tuple[Any, Optional[List[str]]]:
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
            messages.append(f"ERROR: {value} does not validate " + "==" + message)
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
class ParseSubtypeOf(ParseHandler):

    # parses list of subtypes into dict from Supertyping to SUbtyping of Supertype
    # subtype_of Product byFlavor, Concept byColor
    # yields:
    # {
    #   Product: byFlavor,
    #   Concept: byColor
    # }
    # if the byPhrase is omitted, "Subtypes" is used instead
    def parse(self, input_str) -> List[Tuple[ClassReference, SubtypingName]]:
        print("parsing subtypeOfs: ", input_str)
        pairs = input_str.split(",")
        result = []
        for pair in pairs:
            pieces = pair.split(" by", 2)
            class_name0 = pieces[0]
            if len(pieces) > 1:
                subtyping_name0 = pieces[1]
                subtyping_name0 = parse_name("by " + subtyping_name0)

            else:
                subtyping_name0 = "Subtypes"
            class_name = ClassReference(parse_name(class_name0))
            subtyping_name = SubtypingName(subtyping_name0)
            subtype_of = {
                "_type": "SubtypeBy",
                "class_name": class_name,
                "subtyping_name": subtyping_name
            }
            result.append(subtype_of)
        print("SubtypeOf result is ", result)

        return result

    def render(self, pairs: List[Tuple[ClassReference, SubtypingName]]) -> str:
        pair_strs = []
        for cname, stname in pairs:
            if stname == "subtypes":
                pair_str = cname
            else:
                pair_str = f"{cname} {stname}"
            pair_strs.append(pair_str)
        return ", ".join(pair_strs)

    def validate(self, names: List[ClassReference]) -> Tuple[bool, Optional[str]]:
        return True, None

from utils.util_flogging import trace_method, flogger

@dataclass
class ParseNameList(ParseHandler):
    
    def parse(self, input_str: str) -> list[ClassReference]:
        """Parse a comma-separated list of names with potential markdown formatting."""
        # print(f"parse_name_list: {input_str}")
        if not input_str:
            return []

        # Split by commas
        parts = re.split(r",\s*", input_str)

        # Clean each part
        cleaned_names = [parse_name(part) for part in parts]

        # Filter out empty strings - and create ClassReferences
        the_list =  [ClassReference(name) for name in cleaned_names if name]
        print("ParseNameList returning: ", the_list)
        return the_list

    def render(self, names: List[ClassReference]) -> str:
        return ", ".join(names)

    def validate(self, names: List[ClassReference]) -> Tuple[bool, Optional[str]]:
        # print("validating name list: ", names)
        if not isinstance(names, List):
            return False, f"NameList doesn't seem to be a list at all: {names}"
        for name in names:
            if not is_name(name.content):
                return False, f"Name in NameList is not a name: {name}"
        return True, None


###
@dataclass
class ParseAttributeReference(ParseHandler):
    def parse(self, input_str: str) -> dict:
        """Parse a reference in the form ClassReference.AttributeName."""
        if not input_str:
            return {
                "_type": "AttributeReference",
                "class_name": "",
                "attribute_name": "",
            }

        # Clean the input first to remove any markdown
        cleaned = parse_name(input_str)

        # Split by dot
        parts = re.split(r"\.\s*", str(cleaned), 1)
        class_name = ClassReference(parts[0].strip())
        attribute_name = AttributeName(parts[1].strip()) if len(parts) > 1 else ""

        if len(parts) == 2:
            return {
                "_type": "AttributeReference",
                "class_name": class_name,
                "attribute_name": attribute_name,
            }
        else:
            # If there's no dot, assume it's just a class name
            return {
                "_type": "AttributeReference",
                "class_name": cleaned,
                "attribute_name": "",
            }

    def render(self, ar_dict: Dict) -> str:
        """Render the attribute reference as ClassReference.AttributeName."""
        class_name = ar_dict.get("class_name", "NoClassReference")
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
            use_prefix = starter.starter
            if use_prefix == "Class":
                use_prefix = "_"
            return {
                "line_type": starter.line_type,
                # "prefix": starter.starter,
                "prefix": use_prefix,
                "rest_of_line": rest,
            }

    # Check for emoji followed by label and colon
    emoji_match = re.match(r"^([\U0001F300-\U0001F9FF]+)\s+([^:]+):(.*)", line)
    if emoji_match:
        print("Found emoji match in parse_input_line")
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
        """Renders a header dictionary to a string.

        Constructs a header string from a dictionary containing header components.

        Args:
            head_dict: A dictionary containing header information.

        Returns:
            A formatted header string.
        """
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
    # print(f"\n\n===\nParsingHeader header: {header}")

    result = {"prefix": "", "name": None, "one_liner": None, "parenthetical": ""}

    # First, identify the line type and get the rest of the line
    parsed = parse_input_line(header)
    # print("PARSED AS INPUT LINE ", parsed)
    if "rest_of_line" not in parsed:
        print("No rest of line")
        return result

    prefix = parsed.get("prefix", "").strip()
    result["prefix"] = prefix

    # print("PREFIX IS:", prefix)
    rest = parsed.get("rest_of_line", "")

    # Extract name (everything up to a dash or parenthesis)
    name_match = re.match(r"^([^-\(]+)(?:[-\(]|$)", rest)

    if name_match:
        raw_name = parse_name(name_match.group(1)).replace(":", "")
        deep_name = None
        if prefix == "_" or prefix == "Class":
            deep_name = ClassName(raw_name)
        elif prefix is None or prefix == "":
            print("Empty prefix")
            deep_name = raw_name
        elif prefix == "-":
            deep_name = AttributeName(raw_name)
        elif "#" in prefix:
            deep_name = SubjectName(raw_name)
        elif "__" in prefix:
            deep_name = AttributeSectionName(raw_name)
        elif "Value" in prefix:
            print(f"raw name = {raw_name}, deep = {deep_name}")
            deep_name = ClassName(raw_name)
        elif "Code" in prefix:
            deep_name = ClassName(raw_name)
        else:
            print(f"prefix not associatedw with name type? - {prefix}")
            deep_name = raw_name
        result["name"] = deep_name
        rest = rest[len(name_match.group(1)) :].strip()

    # Extract one-liner (between dash and parenthesis, if present)
    if rest.startswith("-"):
        rest = rest[1:].strip()  # Remove the dash
        one_liner_match = re.match(r"^([^\(]+)(?:\(|$)", rest)
        if one_liner_match:
            content = one_liner_match.group(1).strip()
            result["one_liner"]  = {"_type": "OneLiner", "content": content}
            rest = rest[len(one_liner_match.group(1)) :].strip()

    # Extract parenthetical
    parenthetical_match = re.match(r"^\(([^\)]+)\)", rest)
    parenthetical = ""
    if parenthetical_match:

        parenthetical = parenthetical_match.group(1).strip()

    if parenthetical:
        if prefix.strip() == "-":
            dtc = parse_data_type_clause(parenthetical)
            # print("setting data_type_clause to to_typed_dict", dtc.to_typed_dict())
            result["data_type_clause"] = dtc.to_typed_dict()
        if prefix.strip() == "__":  # Attribute Section
            is_optional = IsOptional(parenthetical)
            result["is_optional"] = is_optional
            # print(f"AttSection: {is_optional} Result is {result}")
        else:
            result["parenthetical"] = parenthetical

    # print(f"ParsingHeader result: {result}\n===\n")

    # return clean_dict(result)
    return result


from utils.util_json import as_json


def parse_data_type_clause(parenthetical: str) -> DataTypeClause:
    is_optional = False
    phrase = parenthetical.replace("*", "")
    phrase = phrase.strip()
    if phrase.lower().startswith("optional "):
        phrase = phrase.replace("optional ", "")
        is_optional = True

    is_optional_str = "optional"
    if not is_optional:
        is_optional_str = "required"
    # now parse the rest as a mere data type
    dt = parse_data_type(phrase)
    # print("Found dt: ", dt)
    # print("Found dt as dict: ", dt.to_typed_dict())
    dtc = DataTypeClause(data_type=dt, is_optional_lit=IsOptional(is_optional_str))
    dtc = DataTypeClause(data_type=dt.to_typed_dict(), is_optional_lit=IsOptional(is_optional_str))
    # print("Created dtc", dtc.to_typed_dict())
    return dtc


from ldm.parsedt import parse_dt_phrase


def parse_data_type(phrase) -> DataType:
    (operator, typeA, typeB) = parse_dt_phrase(phrase)
    if operator == "ListOf":
        dt0 = parse_data_type(typeA)
        dt = ListDataType(dt0)
        # print("Created list dt: ", dt)
        return dt
    if operator == "SetOf":
        dt0 = parse_data_type(typeA)
        dt = SetDataType(dt0)
        # print("Created set dt: ", dt)
        return dt
    if operator == "Mapping":
        dt1 = parse_data_type(typeA)
        dt2 = parse_data_type(typeB)
        dt = MappingDataType(dt1, dt2)
        # print("Created Mapping dt: ", dt)
        return dt

    if is_name(phrase):
        name_obj = ClassReference(phrase)
        # print("Arg to basedata type is ", name_obj)
        dt = BaseDataType(class_name=ClassReference(phrase), as_value_type=AsValue("reference"))
        return dt

    print("Inventing name for: ", phrase)
    phrase = "Invented Name"
    dt = BaseDataType(class_name=ClassReference(phrase), as_value_type=AsValue("value"))
    return dt


def render_header(head_dict: Dict) -> str:
    """Renders a header string from a dictionary.

    Constructs a header string using components provided in a dictionary, using default values if components are missing.

    Args:
        head_dict: A dictionary containing header components: 'prefix', 'name', 'one_liner', and 'parenthetical'.

    Returns:
        The formatted header string.
    """
    prefix = head_dict.get("prefix", "PREFIX?")
    name = head_dict.get("name", None)
    one_liner = head_dict.get("one_liner", None)
    parenthetical = head_dict.get("parenthetical", None)

    header = prefix + " "

    header += str(name) if name else "NAME?"
    if one_liner:
        header += " - " + str(one_liner)
    if parenthetical:
        header += " (" + parenthetical + ")"
    return header


def validate_header(head_dict: Dict) -> Tuple[bool, Optional[str]]:
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
        
        print("Parsing annotation: ", input_str)
        parsed = parse_input_line(input_str)
        if parsed.get("line_type") == "labeled_value":
            print("Returning parsed from ParseAnnotaion", parsed)
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
    return clean_dict(the_dict)
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
    emoji = annotation_dict.get("emoji", None)

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
    assert att_ref_parser.parse("ClassReference.AttributeName") == {
        "class_name": "ClassReference",
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
    from utils.util_json import as_json

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
            line oneliner(Type)",
    ]
    for header in headers:
        # print("TestingHeader: ", header)
        result = head_parser.parse(header)
        # print(as_json(result))

    annotations = [
        "🔄 **Default**: value if none provided",
        '***Example***: "LDM" is the short form of "Literate Data Model".',
        "🔄 ***NoteA***: This attribute is set to true for components that are automatically generated or added during the fleshing out, review, or rendering processes, such as implied attributes or suggested model elements. It helps distinguish embellishments from the core model elements defined in the original LDM source.",
        "ℹ️  ***NoteA***: This attribute is set to true for components that are automatically generated or added during the fleshing out, review, or rendering processes, such as implied attributes or suggested model elements. It helps distinguish embellishments from the core model elements defined in the original LDM source.",
        "\u2139\ufe0f ***Note***: This attribute is set to true for annotations that are automatically generated or added during the fleshing out, review, or rendering processes, such as suggestions, issues, or diagnostic messages. It helps distinguish embellishment annotations from the annotations defined in the original LDM source.",
        "wildly: This is an unregistered annotation",
    ]

    annotation_parser = ParseAnnotation()
    for annotation in annotations:
        # print()
        # print("TestingAnnotation: ", annotation)

        result = annotation_parser.parse(annotation)
        # print(as_json(result))
        rendered = annotation_parser.render(result)
        # print(f"Renders as: {rendered}")


# Run the tests
if __name__ == "__main__":
    test_parsers()
