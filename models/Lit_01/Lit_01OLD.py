# Version: 2025-02-22_222609

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any, Union
from abc import ABC, abstractmethod


# Import the casing classes
from class_casing import UpperCamel, LowerCamel, CamelCase
from class_pom_token import (
    PresentableBoolean,
    IsOptional,
    ReferenceOrValue,
    IsReallyRequired,
)

# Specify which imported classes should be included in the model
__model_imports__ = [
    UpperCamel,
    LowerCamel,
    CamelCase,
    IsOptional,
    IsReallyRequired,
    ReferenceOrValue,
]


@dataclass
class Paragraph:
    content: str

    def __init__(self, content: str):
        self.content = content

    def __post_init__(self):
        self._type = "paragraph"


@dataclass
class OneLiner(Paragraph):

    def __init__(self, content: str):
        self.content = content

    def __post_init__(self):
        self._type = "one-liner"


ClassName = UpperCamel


@dataclass
class Label(CamelCase):
    name: LowerCamel


def block_list_field(*args, **kwargs):
    """Helper function to create fields for block lists within dataclasses."""
    # Create the block list metadata
    block_list_metadata = kwargs.pop("block_list_metadata", {})
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
    # from dataclasses import field as dataclass_field
    dataclass_field = field
    return dataclass_field(*args, **kwargs)


@dataclass
class Component(ABC):

    name: CamelCase
    one_liner: Optional[OneLiner] = None
    abbreviation: Optional[UpperCamel] = None
    elaboration: Optional[List[Paragraph]] = block_list_field(default_factory=list)
    annotations: Optional[List[Annotation]] = block_list_field(default_factory=list)

    _type: str = field(default="component", init=False)

    class Meta:
        is_abstract = True
        presentable_header = "_ {_type}: {name}{? - {one_liner}} NEWLINE"

    def __str__(self):
        return f"{self._type.capitalize()}: {self.name}"

    def __repr__(self):
        return f"{self._type.capitalize()}: {self.name} (repr)"

    def __post_init__(self):
        self.annotations = []


@dataclass
class Annotation:
    label: Label
    content: OneLiner
    emoji: Optional[str] = None
    _type: str = field(default="annotation", init=False)

    class Meta:
        presentable_template = "{?{emoji}}  {label}: {content} NEWLINE"


@dataclass
class SubjectE(Component):
    classes: List[Class] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "subject5"

    class Meta:
        presentable_header = "#####  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class SubjectD(SubjectE):
    subjects: List[SubjectE] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "subjectD"

    class Meta:
        presentable_header = "####  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class Subject3(SubjectD):
    subjects: List[SubjectD] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "subject3"

    class Meta:
        presentable_header = "###  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class Subject2(Subject3):
    subjects: List[Subject3] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "subject2"

    class Meta:
        presentable_header = "##  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class LDM(Subject2):
    subjects: List[Subject2] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "subject2"

    class Meta:
        presentable_header = "#  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class Class(Component):
    name: UpperCamel
    plural: Optional[UpperCamel] = None
    subtype_of: Optional[List[ClassName]] = field(default_factory=list)
    subtypes: Optional[List[ClassName]] = field(default_factory=list)
    based_on: Optional[List[ClassName]] = field(default_factory=list)
    dependents: Optional[List[ClassName]] = field(default_factory=list)
    samplerA: Tuple[int, str, DataType] = None
    is_value_type: bool = False
    where: Optional[str] = None
    attributes: List[Attribute] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "class"
        if self.attributes is None:
            self.attributes = []

    class Meta:
        presentable_header = "_ Class: {name}{? - {one_liner}} NEWLINE"


@dataclass
class ValueType(Class):
    def __post_init__(self):
        super().__post_init__()
        self.is_value_type = True
        self._type = "value-type"


@dataclass
class ReferenceType(Class):
    def __post_init__(self):
        super().__post_init__()
        self._type = "reference-type"


@dataclass
class Attribute(Component):
    name: LowerCamel
    data_type_clause: Optional[DataTypeClause] = None
    derivation: Optional[Derivation] = None
    default: Optional[Default] = None
    constraints: Optional[List[Constraint]] = block_list_field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "attribute"

    class Meta:
        presentable_header = (
            "-  {name}{? - {one_liner}}{? ({data_type_clause})} NEWLINE"
        )


@dataclass
class DataType(ABC):
    """
    A simple or complex data type
    """

    _type: str = field(default="data-type", init=False)

    class Meta:
        is_abstract = True


@dataclass
class BaseDataType(DataType):
    class_name: str  # the name of a class, or primitive?
    is_value: ReferenceOrValue = field(default_factory=ReferenceOrValue)
    _type: str = field(default="base-data-type", init=False)

    class Meta:
        presentable_template = "{class_name} {? - {is_value}}"

    def __str__(self):
        # Default implementation will be generated from the template
        # This can be overridden if needed
        ref_or_value = "reference"
        if self.is_value:
            ref_or_value = "value"
        return f"{ref_or_value} {self.class_name}"


@dataclass
class ListDataType(DataType):
    element_type: DataType  # what's inside the list
    _type: str = field(default="list-data-type", init=False)

    class Meta:
        template = "List of {element_type}"

    def __str__(self):
        return f"List of {self.element_type}"


@dataclass
class SetDataType(DataType):
    element_type: DataType  # what's inside the set
    _type: str = field(default="set-data-type", init=False)

    class Meta:
        presentable_template = "Set of {element_type}"

    def __str__(self):
        return f"Set of {self.element_type}"


@dataclass
class MappingDataType(DataType):
    domain_type: DataType  # Mapping from this
    range_type: DataType  # Mapping to this
    _type: str = field(default="mapping-data-type", init=False)

    class Meta:
        template = "Mapping from {domain_type} TO {range_type}"

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
    _type: str = field(default="data-type-clause", init=False)

    class Meta:
        presentable_template = "{is_optional} {data_type}{? {cardinality}}"

    def __str__(self):
        req_or_optional = "optional" if self.is_also_optional else "required"
        return f"({req_or_optional}) {self.data_type})"


@dataclass
class FormulaClause:
    content: str
    _type: str = field(default="formula-clause", init=False)


@dataclass
class Formula:
    _as_entered: Optional[str] = None
    english: Optional[str] = None
    code: Optional[FormulaClause] = None
    _type: str = field(default="formula", init=False)


@dataclass
class Constraint(Formula):
    _type: str = field(default="constraint", init=False)
    message: Optional[str] = None
    severity: Optional[str] = None


@dataclass
class Derivation(Formula):
    _type: str = field(default="derivation", init=False)


@dataclass
class Default(Formula):
    _type: str = field(default="default", init=False)
