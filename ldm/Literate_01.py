# Version: 2025-02-22_222609

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any, Union
from abc import ABC, abstractmethod
import json

# import ldm_renderers
# Import the casing classes
from class_casing import UpperCamel, LowerCamel, CamelCase

from class_pom_token import (
    PresentableBoolean,
    PresentableToken,
    IsOptional,
    ReferenceOrValue,
    IsReallyRequired,
    MarkedText,
    Emoji,
)

# Specify which imported classes should be included in the model
__model_imports__ = [
    UpperCamel,
    LowerCamel,
    CamelCase,
    IsOptional,
    IsReallyRequired,
    ReferenceOrValue,
    MarkedText,
    Emoji,
]


def block_list_field(*args, **kwargs):
    """Helper function to create fields for block lists within dataclasses."""
    # Extract block list specific parameters
    separator = kwargs.pop("separator", None)
    leader = kwargs.pop("leader", None)

    # Create the block list metadata
    block_list_metadata = {
        "list": (
            "{element}+" if not separator else f"{{element}} ({separator} {{element}})*"
        ),
        "field_value": (
            "{field_value}" if not leader else f"{leader} NEWLINE {{field_value}}"
        ),
    }

    # Get any existing metadata from kwargs
    metadata = kwargs.pop("metadata", {})

    # Merge the metadata
    merged_metadata = {**metadata, **block_list_metadata}

    # Add it back to kwargs
    if merged_metadata:
        kwargs["metadata"] = merged_metadata

    # This function is intended to be used in a dataclass context
    from dataclasses import field as dataclass_field

    return dataclass_field(*args, **kwargs)


@dataclass
class Paragraph():
    _type: str = field(default="Paragraph", init=False)
    content: str = ""

        
    def __post_init__(self):
        if self._type is None:
            self._type = "Paragraph"

    class Meta:
        presentable_template = "{content}"
@dataclass
class CodeBlock():
    content: str = None
    _type: str = field(default="CodeBlock", init=False)

        
    def __post_init__(self):
        if self._type is None:
            self._type = "CodeBlock"
        if self.content is None:
            self.content = ""

    class Meta:
        presentable_template = "{content}"
        
@dataclass
class OneLiner(MarkedText):
    def __post_init__(self):
        super().__post_init__()
        self._type = "one-liner"



@dataclass
class ClassName(UpperCamel):
    def __init__(self, input_string):
        super().__init__(input_string)
        repre = type(self).__name__ + "(" + self.output + ")"

        # print(f"created class name: {repre}")
        # print(f"created class name: {repr(self)}")
        # self._type = "ClassName"

@dataclass
class AttributeName(LowerCamel):
    def __init__(self, input_string):
        super().__init__(input_string)

@dataclass
class Label(UpperCamel):
    def __init__(self, input_string):
        super().__init__(input_string)


@dataclass
class Annotation:
    label: Label
    content: OneLiner
    emoji: Optional[Emoji] = None
    elaboration: Optional[List[Paragraph]] = block_list_field(default_factory=list)
    _type: str = field(default="Annotation", init=False)

    def __post_init__(self):
        if self._type is None:
            self._type = "Annotation"
        if self.elaboration is None:
            self.elaboration = []

    class Meta:
        presentable_template = "{?{emoji}}  {label}: {content} NEWLINE"

@dataclass
class Diagnostic():
    
    object_type: str = ""
    object_name: str  = ""
    message:str  = ""

    severity: str = "Error"
    constraint_name: str  = ""

    def __str__(self):
        return f"{self.severity} on {self.object_type} named {self.object_name}: {self.message}"
    def __post_init__(self):
        self._type = "Diagnostic"


@dataclass
class Component(ABC):
    prefix: Optional[str] = None
    name: CamelCase = None
    one_liner: Optional[OneLiner] = None
    parenthetical: Optional[str] = None
    abbreviation: Optional[UpperCamel] = None
    elaboration: Optional[List[Paragraph]] = block_list_field(default_factory=list)
    annotations: Optional[List[Annotation]] = block_list_field(default_factory=list)
    diagnostics: Optional[List[Diagnostic]] = block_list_field(default_factory=list)
    _type: str = field(default=None, init=False)

    class Meta:
        is_abstract = True
        presentable_header = "COMPONENT: {name}{? - {one_liner}} NEWLINE"

    def __str__(self):
        return f"{self._type.capitalize()}: {self.name}"

    def __repr__(self):
        return f"{self._type.capitalize()}: {self.name} (repr)"

    def __post_init__(self):
        if self._type is None:
            self._type = "Component"

        # Ensure collections are initialized
        if self.annotations is None:
            self.annotations = []
        if self.diagnostics is None:
            self.diagnostics = []
        if self.elaboration is None:
            self.elaboration = []
    def show_name(self):
        return f"I am a {self._type.capitalize()}: named {self.name} "


## # Subject classes
## # These classes represent different levels of subjects in a hierarchy.
## # Each subject can contain other subjects and classes.
## # Each subject may contain a list of subjects of any lower level.
## # That it: levels may be skipped.


@dataclass
class SubjectE(Component):
    prefix: str = ""
    classes: List[Class] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "SubjectE"

    class Meta:
        presentable_header = "#####  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class SubjectD(SubjectE):
    subjects: List[SubjectE] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "SubjectD"

    class Meta:
        presentable_header = "####  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class SubjectC(SubjectD):
    subjects: List[SubjectD] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "SubjectC"

    class Meta:
        presentable_header = "###  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class SubjectB(SubjectC):
    subjects: List[SubjectC] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "SubjectB"

    class Meta:
        presentable_header = "##  {{name}{? - {one_liner}} NEWLINE"

@dataclass
class LDM(SubjectB):
    def __init__(self, name=None, description=None, **kwargs):
        # Call the parent constructor
        super().__init__(name, description)
        
        # Set the type explicitly
        self._type = "LDM"
        
        
        # Initialize other attributes
        self.prefix = kwargs.get('prefix', '')
        self.abbreviation = kwargs.get('abbreviation', '')
        self.parenthetical = kwargs.get('parenthetical', '')
        self.one_liner = kwargs.get('one_liner', '')
        self.elaboration = kwargs.get('elaboration', '')
        self.annotations = kwargs.get('annotations', [])
        self.subjects = kwargs.get('subjects', [])
        self.classes = kwargs.get('classes', [])
    
    # Replace the from_dict method in LDM class in Literate_01.py

    @classmethod
    def from_dict(cls, data_dict):
        """Create a model instance from a dictionary representation"""
        from ldm_object_creator import GenericObjectCreator
        import ldm.Literate_01 as Literate_01
        
        creator = GenericObjectCreator(Literate_01) 
        # print(f"Creating model from dictionary: {data_dict}")
        model = creator.create(data_dict)
        print(f"Created model: {model.__class__}")
        
        
        return model

    class Meta:
        presentable_header = "#  {{name}{? - {one_liner}} NEWLINE"


Subject = SubjectB
@dataclass
class DataType(ABC):
    """A simple or complex data type"""

    _type: str = field(default="DataType", init=False)

    def __post_init__(self):
        if self._type is None:
            self._type = "DataType"

    class Meta:
        is_abstract = True


@dataclass
class BaseDataType(DataType):
    class_name: str  # The name of a class, or primitive?
    is_value: ReferenceOrValue = field(default_factory=ReferenceOrValue)

    def __post_init__(self):
        super().__post_init__()
        self._type = "BaseDataType"

    class Meta:
        presentable_template = "{class_name} {? - {is_value}}"

    def __str__(self):
        ref_or_value = "reference"
        if self.is_value:
            ref_or_value = "value"
        return f"{ref_or_value} {self.class_name}"


@dataclass
class ListDataType(DataType):
    element_type: DataType  # What's inside the list

    def __post_init__(self):
        super().__post_init__()
        self._type = "ListDataType"

    class Meta:
        presentable_template = "List of {element_type}"

    def __str__(self):
        return f"List of {self.element_type}"


@dataclass
class SetDataType(DataType):
    element_type: DataType  # What's inside the set

    def __post_init__(self):
        super().__post_init__()
        self._type = "SetDataType"

    class Meta:
        presentable_template = "Set of {element_type}"

    def __str__(self):
        return f"Set of {self.element_type}"


@dataclass
class MappingDataType(DataType):
    domain_type: DataType  # Mapping from this
    range_type: DataType  # Mapping to this

    def __post_init__(self):
        super().__post_init__()
        self._type = "MappingDataType"

    class Meta:
        presentable_template = "Mapping from {domain_type} TO {range_type}"

    def __str__(self):
        return f"Mapping from {self.domain_type} to {self.range_type}"


@dataclass
class DataTypeClause:
    """
    Represents the type information for an attribute.

    Attributes:
        data_type: The data type
        is_optional: Whether the attribute is optional (default: False)
        cardinality: Optional cardinality constraint (e.g., "0..1", "1..*")
    """

    data_type: DataType
    is_required: IsReallyRequired = field(default_factory=IsReallyRequired)
    is_also_optional: IsOptional = field(default_factory=IsOptional)
    is_optional: bool = field(
        default=False,
        metadata={
            "bool": {
                "true": "optional",
                "false": "required",
                "is_explicit": False,  # Whether to show the false value explicitly
            }
        },
    )
    cardinality: Optional[str] = None
    _type: str = field(default=None, init=False)

    def __post_init__(self):
        if self._type is None:
            self._type = "DataTypeClause"

    class Meta:
        presentable_template = "{is_optional} {data_type}{? {cardinality}}"

    def __str__(self):
        req_or_optional = "optional" if self.is_also_optional else "required"
        return f"({req_or_optional}) {self.data_type})"


@dataclass
class FormulaCoding:
    content: str
    _type: str = field(default=None, init=False)

    def __post_init__(self):
        if self._type is None:
            self._type = "FormulaClause"


@dataclass
class Formula:
    as_entered: Optional[str] = None
    english: Optional[str] = None
    code: Optional[FormulaCoding] = None
    elaboration: Optional[List[Paragraph]] = block_list_field(default_factory=list)

    annotations: Optional[List[Annotation]] = block_list_field(default_factory=list)
    diagnostics: Optional[List[Diagnostic]] = block_list_field(default_factory=list)

    _type: str = field(default=None, init=False)

    def __post_init__(self):
        if self._type is None:
            self._type = "Formula"
        if self.annotations is None:
            self.annotations = []
        if self.diagnostics is None:
            self.diagnostics = []
        if self.elaboration is None:
            self.elaboration = []


@dataclass
class Constraint(Formula):
    message: Optional[str] = None
    severity: Optional[str] = None

    def __post_init__(self):
        super().__post_init__()
        self._type = "Constraint"


@dataclass
class Derivation(Formula):
    def __post_init__(self):
        super().__post_init__()
        self._type = "Derivation"


@dataclass
class Default(Formula):
    def __post_init__(self):
        super().__post_init__()
        self._type = "Default"


@dataclass
class Class(Component):
    name: UpperCamel = None
    plural: Optional[UpperCamel] = None
    subtype_of: Optional[List[ClassName]] = field(default_factory=list)
    subtypes: Optional[List[ClassName]] = field(default_factory=list)
    based_on: Optional[List[ClassName]] = field(default_factory=list)
    dependent_of: Optional[List[ClassName]] = field(default_factory=list)
    dependents: Optional[List[ClassName]] = field(default_factory=list)
    # samplerA: Tuple[int, str, DataType] = None
    is_value_type: bool = False
    where: Optional[OneLiner] = None
    constraints: Optional[List[Constraint]] = block_list_field(default_factory=list)

    attributes: List[Attribute] = block_list_field(default_factory=list)
    attribute_sections: List[AttributeSection] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "Class"
        if self.attributes is None:
            self.attributes = []
        if self.attribute_sections is None:
            self.attribute_sections = []

    class Meta:
        presentable_header = "_ {name}{? - {one_liner}} NEWLINE"

Class_ = Class

@dataclass
class ValueType(Class):
    def __post_init__(self):
        super().__post_init__()
        self.is_value_type = True
        self._type = "ValueType"
    class Meta:
        presentable_header = "_  ValueType : {name}{? - {one_liner}} NEWLINE"


@dataclass
class ReferenceType(Class):
    def __post_init__(self):
        super().__post_init__()
        self._type = "ReferenceType"


@dataclass
class AttributeSection(Component):
    is_required: IsReallyRequired = None
    attributes: List[Attribute] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "AttributeSection"
        if self.attributes is None:
            self.attributes = []
        if self.is_required is None:
            self.is_required = IsReallyRequired(True)

    class Meta:
        presentable_header = "-  {name}{? - {one_liner}}{? ({is_required})} NEWLINE"
        
    # def render_markdown(self):
    #     print("Rendering AttributeSection")
    #     return ("ATTRIBUTE SECTION GOES HERE\n")
    #     return self.render_markdown_component(prefix="__ ", parenthetical=None)
    


@dataclass
class Attribute(Component):
    name: LowerCamel = None
    data_type_clause: DataTypeClause = None
    overrides: Optional[AttributeReference] = None
    inverse: Optional[AttributeReference] = None
    inverse_of: Optional[AttributeReference] = None
    derivation: Optional[Derivation] = None
    default: Optional[Default] = None
    constraints: Optional[List[Constraint]] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "Attribute"
        if self.constraints is None:
            self.constraints = []

    class Meta:
        presentable_header = (
            "-  {name}{? - {one_liner}}{? ({data_type_clause})} NEWLINE"
        )

        
@dataclass
class AttributeReference:
    class_name: ClassName = None
    attribute_name: AttributeName = None
    _type: str = field(default="AttributeReference", init=False)
    
    def __init__(self, class_name: ClassName = None, attribute_name: AttributeName = None):
        self.class_name = ClassName(str(class_name))       # so caller can user str() or UpperCamel
        self.attribute_name = AttributeName(str(attribute_name)) # so caller can user str() or UpperCamel
        if self._type is None:
            self._type = "AttributeReference"
            
    def __dict__(self):
        return self.to_dict()



    def to_dict(self):
        """Specialized serialization for AttributeReference"""
        return {
            "_type": self._type,
            "class_name": self.class_name.to_dict() if self.class_name else None,
            "attribute_name": self.attribute_name.to_dict() if self.attribute_name else None
        }
    
    def __str__(self):
        """Convert the object to a string."""
        return f"{self.class_name}.{self.attribute_name}"
    
    def __json__(self):
        """Convert the object to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data):
        """Specialized deserialization for AttributeReference"""
        if not isinstance(data, dict):
            return None
        class_name = ClassName.from_dict(data.get("class_name")) if data.get("class_name") else None
        attribute_name = AttributeName.from_dict(data.get("attribute_name")) if data.get("attribute_name") else None
        return cls(class_name=class_name, attribute_name=attribute_name)

    def to_json(self):
        """
        Convert the object to a JSON string.
        """
        return json.dumps(self.to_dict(), indent=2)


    class Meta:
        presentable_template = "{name} ({class_name})"
AllLDMClasses = [
    SubjectB,
    SubjectC,
    SubjectD,
    SubjectE,           
    Class,
    ValueType,
    ReferenceType,
    AttributeSection,
    Attribute,
    DataType,
    BaseDataType,
    ListDataType,
    SetDataType,
    MappingDataType,
    DataTypeClause,
    Formula,
    Constraint,
    Derivation,
    Default,
    LDM,
    Paragraph,  
    OneLiner,
    Annotation,
    ClassName,
    Label,
    PresentableBoolean,
    PresentableToken,
    IsOptional,
    IsReallyRequired,
    ReferenceOrValue,
    MarkedText,
    Emoji,
]
