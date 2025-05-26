# Version: 2025-02-22_222609

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional



@dataclass
class CamelCase:
    content: str


@dataclass
class UpperCamel(CamelCase):
    content: str


@dataclass
class LowerCamel(CamelCase):
    content: str


@dataclass
class ComponentName:
    name: CamelCase


@dataclass
class Label(ComponentName):
    name: LowerCamel


@dataclass
class ClassName(ComponentName):
    name: UpperCamel


@dataclass
class AttributeName(ComponentName):
    name: LowerCamel


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


@dataclass
class Component:
    name: ComponentName
    abbreviation: Optional[str] = None
    one_liner: Optional[OneLiner] = None
    elaboration: Optional[List[Paragraph]] = None
    annotations: Optional[List[Annotation]] = field(default_factory=list)
    _type: str = field(default="component", init=False)
    
    def __str__(self):
        return f"{self._type.capitalize()}: {self.name}"

    def __repr__(self):
        return f"{self._type.capitalize()}: {self.name} (repr)"
    
    def __post_init__(self):
        if self.annotations is None:
            self.annotations = []


@dataclass
class Annotation:
    label: Label
    content: OneLiner
    emoji: Optional[str] = None
    _type: str = field(default="annotation", init=False)


@dataclass
class LiterateDataModel(Component):
    classes: List[Class] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self._type = "literate-data-model"
    
    class Meta:
        presentable_header = "# name - one_liner"


@dataclass
class Class(Component):
    abbreviation: Optional[UpperCamel] = None
    plural: Optional[UpperCamel] = None
    subtype_of: Optional[List[ClassName]] = field(default_factory=list)   
    subtypes: Optional[List[ClassName]] = field(default_factory=list)
    based_on: Optional[List[ClassName]] = field(default_factory=list)
    dependents: Optional[List[ClassName]] = field(default_factory=list)
    is_value_type: bool = False
    where: Optional[str] = None
    attributes: List[Attribute] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._type = "class"
        if self.attributes is None:
            self.attributes = []
    
    class Meta:
        presentable_header = "_ name - one_liner"


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
    data_type_clause: Optional[DataTypeClause] = None
    derivation: Optional[Derivation] = None
    default: Optional[Default] = None
    constraints: Optional[List[Constraint]] = field(default_factory=list)
    
    def __post_init__(self):
        super().__post_init__()
        self._type = "attribute"
    
    class Meta:
        presentable_header = "- name - one_liner (data_type_clause)"


@dataclass
class DataType:
    '''
    A simple or complex data type
    '''
    _type: str = field(default="data-type", init=False)


@dataclass
class BaseDataType(DataType):
    class_name: str    # the name of a class, or primitive?
    is_value: bool = field(default=False, metadata={
        "presentable_true": "value", 
        "presentable_false": "reference"
    })
    _type: str = field(default="base-data-type", init=False)
    
    class Meta:
        presentable_template = "is_value class_name"
    
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
        presentable_template = "LIST_OF element_type"
    
    def __str__(self):
        return f"List of {self.element_type}"


@dataclass
class SetDataType(DataType):
    element_type: DataType  # what's inside the set
    _type: str = field(default="set-data-type", init=False)
    
    class Meta:
        presentable_template = "SET_OF element_type"
    
    def __str__(self):
        return f"Set of {self.element_type}"


@dataclass
class MappingDataType(DataType):
    domain_type: DataType  # Mapping from this
    range_type: DataType  # Mapping to this
    _type: str = field(default="mapping-data-type", init=False)
    
    class Meta:
        presentable_template = "MAPPING_FROM {domain_type TO range_type"
    
    def __str__(self):
        return f"Mapping from {self.domain_type} to {self.range_type}"

from class_pom_token import PresentableBoolean, IsOptional
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
    is_optional: bool = field(default=False, metadata={
        "presentable_true": "optional", 
        "presentable_false": "required",
        "explicit": False  # Whether to show the false value explicitly
    })
    is_also_optioanl: IsOptional
    cardinality: Optional[str] = None
    _type: str = field(default="data-type-clause", init=False)

    class Meta:
        presentable_template = "isOptional data_type"   
    
    def __str__(self):
        req_or_optional = "optional" if self.is_optional else "required"
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
    message: Optional[str] = None
    _type: str = field(default="formula", init=False)


@dataclass
class Constraint(Formula):
    _type: str = field(default="constraint", init=False)


@dataclass
class Derivation(Formula):
    _type: str = field(default="derivation", init=False)


@dataclass
class Default(Formula):
    _type: str = field(default="default", init=False)