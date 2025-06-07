# Version: 2025-02-22_222609

from __future__ import annotations
from typing import List, Optional, Dict, Any, Union


from utils.util_pydantic import PydanticMixin,  dataclass, field

from utils.debug_pydantic import debug_dataclass_creation
from utils.class_casing import *


# from abc import ABC, abstractmethod
import json


# First, let's create a Pydantic-compatible block_list_field
def block_list_field(default_factory=list, **kwargs):
    """Pydantic version of block_list_field with metadata support"""
    metadata = kwargs.pop("metadata", {})
    return field(default_factory=default_factory, json_schema_extra=metadata, **kwargs)


# import ldm_renderers
# Import the casing classes
from utils.class_casing import UpperCamel, LowerCamel, CamelCase, NormalCase

from utils.class_pom_token import (
    PresentableBoolean,
    PresentableToken,
    IsOptional,
    AsValue,
    IsExhaustive,
    IsExclusive,
    # MarkedText,
    Emoji,
)

# Specify which imported classes should be included in the model
__model_imports__ = [
    UpperCamel,
    LowerCamel,
    CamelCase,
    IsOptional,
    AsValue,
    IsExhaustive,
    IsExclusive,
    # MarkedText,
    Emoji,
]

# TODO: subtypings
# todo: codes


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
class Natural(PydanticMixin):
    content: str = ""

    def __str__(self):
        return self.content

    class Meta:
        presentable_template = "{content}"


# @debug_dataclass_creation
@dataclass
class OneLiner(Natural):

    pass

@dataclass
class Paragraph(Natural):
    pass

@dataclass
class CodeBlock(PydanticMixin):
    content: str = None


    class Meta:
        presentable_template = "{content}"


@dataclass
class OneLiner(Natural):
    pass


@dataclass
class ModelName(NormalCase):
    pass


@dataclass
class ClassName(UpperCamel):
    content: Any
    pass


@dataclass
class SubjectName(NormalCase):
    pass


@dataclass
class AttributeSectionName(NormalCase):
    pass


@dataclass
class AttributeName(LowerCamel):
    pass


@dataclass
class SubtypingName(LowerCamel):
    pass


@dataclass
class Label(LowerCamel):
    pass


@dataclass
class Annotation(PydanticMixin):
    label: Label
    content: OneLiner
    emoji: Optional[Emoji] = None
    elaboration: Optional[List[Union[Paragraph, CodeBlock]]] = block_list_field(
        default_factory=list
    )

    def shared_post_init(self):
        if self.elaboration is None:
            self.elaboration = []

    class Meta:
        presentable_template = "{?{emoji}}  {label}: {content} NEWLINE"


@dataclass
class Diagnostic(PydanticMixin):
    object_name: str = ""
    object_type: str = ""
    message: Paragraph = None

    severity: str = "Error"
    constraint_name: str = ""

    def __str__(self):
        return f"{self.severity} on {self.object_type} named {self.object_name}: {self.message}"

    def shared_post_init(self):
        if self.message == None:
            self.message = Paragraph("")


@dataclass
class MinorComponent(PydanticMixin):  # TO DO: Change to subtype of Component, or vv
    one_liner: Optional[OneLiner] = None
    elaboration: Optional[List[Union[Paragraph, CodeBlock]]] = block_list_field(
        default_factory=list
    )
    annotations: Optional[List[Annotation]] = block_list_field(default_factory=list)
    diagnostics: Optional[List[Diagnostic]] = block_list_field(default_factory=list)
    is_embellishment: bool = False

    class Meta:
        is_abstract = True

    def shared_post_init(self):
        super().shared_post_init()

        # Ensure collections are initialized
        if self.annotations is None:
            self.annotations = []
        if self.diagnostics is None:
            self.diagnostics  = []
        if self.elaboration is None:
            self.elaboration = []


@dataclass
class Component(MinorComponent):
    prefix: Optional[str] = None
    name: CamelCase = None
    parenthetical: Optional[str] = None
    abbreviation: Optional[CamelCase] = None

    class Meta:
        is_abstract = True
        presentable_header = "COMPONENT: {name}{? - {one_liner}} NEWLINE"

    def __str__(self):
        return f"{self._type.capitalize()}: {self.name}"

    def __repr__(self):
        return f"{self._type.capitalize()}: {self.name} (repr)"


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

    def shared_post_init(self):
        super().shared_post_init()
        if isinstance(self.name, str):
            print("Fixing Subject name!")
            self.name = SubjectName(self.name)

    class Meta:
        presentable_header = "#####  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class SubjectD(SubjectE):
    subjects: List[SubjectE] = block_list_field(default_factory=list)


    class Meta:
        presentable_header = "####  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class SubjectC(SubjectD):
    subjects: List[SubjectD] = block_list_field(default_factory=list)


    class Meta:
        presentable_header = "###  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class SubjectB(SubjectC):
    subjects: List[SubjectC] = block_list_field(default_factory=list)


    class Meta:
        presentable_header = "##  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class LiterateModel(SubjectB):

    # def __init__(self, name=None, description=None, **kwargs):
    #     # Call the parent constructor
    #     super().__init__(name, description)

    #     # Set the type explicitly
    #     self._type = "LiterateModel"

    #     # Initialize other attributes
    #     self.name = kwargs.get("name", "")
    #     self.prefix = kwargs.get("prefix", "")
    #     self.abbreviation = kwargs.get("abbreviation", "")
    #     self.parenthetical = kwargs.get("parenthetical", "")
    #     self.one_liner = kwargs.get("one_liner", "")
    #     self.elaboration = kwargs.get("elaboration", "")
    #     self.annotations = kwargs.get("annotations", [])
    #     self.subjects = kwargs.get("subjects", [])
    #     self.classes = kwargs.get("classes", [])

    def shared_post_init(self):
        super().shared_post_init()
        if isinstance(self.name, str):
            print("Fixing LiterateModel name!")
            self.name = ModelName(self.name)

    # Replace the from_dict method in LDM class in Literate_01.py

    @classmethod
    # def from_dict(cls, data_dict):
    #     """Create a model instance from a dictionary representation"""
    #     from ldm_object_creator import GenericObjectCreator
    #     import ldm.Literate_01 as Literate_01

    #     creator = GenericObjectCreator(Literate_01)
    #     # print(f"Creating model from dictionary: {data_dict}")
    #     model = creator.create(data_dict)
    #     print(f"Created model: {model.__class__}")

    #     return model

    class Meta:
        presentable_header = "#  {{name}{? - {one_liner}} NEWLINE"


Subject = SubjectB


@dataclass
class DataType(PydanticMixin):
    """A simple or complex data type"""
    

    def shared_post_init(self):
        super().shared_post_init()
        # print("Data type type is ", self._type)
        

    class Meta:
        is_abstract = True


@dataclass
class BaseDataType(DataType):
    class_name: Any #ClassName = field(default_factory=ClassName)
    as_value_type: AsValue = field(default_factory=AsValue)

    def shared_post_init(self):
        super().shared_post_init()
        if isinstance(self.class_name, str):
            self.class_name = ClassName(self.class_name)
        # print("Created BDT is ", self)
        # print("Base Data type type is ", self._type)
        # print("Base Data type is (repr)", self.__repr__())
        # print("Base Data type is (to_typed_dict)", self.to_typed_dict())


    class Meta:
        presentable_template = "{class_name} {? - {is_value}}"

    # def __str__(self):
    #     return f"{self.as_value_type} {self.class_name}"


@dataclass
class ListDataType(DataType):
    element_type: DataType  # What's inside the list



    class Meta:
        presentable_template = "List of {element_type}"

    def __str__(self):
        return f"List of {self.element_type}"


@dataclass
class SetDataType(DataType):
    element_type: DataType  # What's inside the set


    class Meta:
        presentable_template = "Set of {element_type}"

    def __str__(self):
        return f"Set of {self.element_type}"


@dataclass
class MappingDataType(DataType):
    domain_type: DataType  # Mapping from this
    range_type: DataType  # Mapping to this


    class Meta:
        presentable_template = "Mapping from {domain_type} TO {range_type}"

    def __str__(self):
        return f"Mapping from {self.domain_type} to {self.range_type}"


@dataclass
class DataTypeClause(PydanticMixin):
    """
    Represents the type information for an attribute.

    Attributes:
        data_type: The data type
        is_optional: Whether the attribute is optional (default: False)
        cardinality: Optional cardinality constraint (e.g., "0..1", "1..*")
    """

    data_type: Any
    # is_optional_lit: Optional[IsOptional] = field(default="Required")
    is_optional_lit: Optional[IsOptional] = field(default_factory=lambda: IsOptional(content=False))

    cardinality: Optional[str] = None


    class Meta:
        presentable_template = "{is_optional_lit} {data_type}{? {cardinality}}"

    def __str__(self):
        req_or_optional = "optional" if self.is_optional_lit else "required"
        return f"{req_or_optional} {self.data_type}"


@dataclass
class FormulaCoding(PydanticMixin):
    content: str



@dataclass
class Formula(MinorComponent):
    english: Optional[Paragraph] = None
    code: Optional[FormulaCoding] = None


    def shared_post_init(self):
        super().shared_post_init()
        if self.english is None:
            self.english = Paragraph("")


@dataclass
class Constraint(Formula):
    message: Optional[Paragraph] = None
    severity: Optional[str] = None

    def shared_post_init(self):
        super().shared_post_init()
        if self.message is None:
            self.message = Paragraph("")


@dataclass
class Derivation(Formula):
    pass



@dataclass
class Default(Formula):
    pass

@dataclass
class SubtypeBy(PydanticMixin):
    class_name: ClassName = None
    subtyping_name: SubtypingName = None


# to do: why do all of the field declarations make trouble for serializaing
@dataclass
class Class(Component):
    name: ClassName = None
    plural: Optional[str] = None
    subtype_of: Optional[List[SubtypeBy]] =  None # field(default_factory=list)
    subtypings: Optional[List[Subtyping]] = block_list_field(default_factory=list)

    subtypes: Optional[List[SubtypeBy]]  = None # field(default_factory=list)
    based_on: Optional[List[ClassName]] =  None # field(default_factory=list)
    dependent_of: Optional[List[ClassName]] =  None # field(default_factory=list)
    dependents: Optional[List[ClassName]] =  None # field(default_factory=list)
    is_value_type: bool = False
    where: Optional[OneLiner] = None
    constraints: Optional[List[Constraint]] = block_list_field(default_factory=list)

    attributes: List[Attribute] = block_list_field(default_factory=list)
    attribute_sections: List[AttributeSection] = block_list_field(default_factory=list)

    def shared_post_init(self):
        super().shared_post_init()
        if self.attributes is None:
            self.attributes = []
        if self.attribute_sections is None:
            self.attribute_sections = []
        if self.subtypings is None:
            self.subtypings = []
        if isinstance(self.name, str):
            print("Fixing Class name!")
            self.name = ClassName(self.name)

    class Meta:
        presentable_header = "_ {name}{? - {one_liner}} NEWLINE"


Class_ = Class


@dataclass
class ValueType(Class):

    def shared_post_init(self):
        super().shared_post_init()
        self.is_value_type = True

    class Meta:
        presentable_header = "_  ValueType : {name}{? - {one_liner}} NEWLINE"


@dataclass
class CodeType(ValueType):

    class Meta:
        presentable_header = "_  CodeType : {name}{? - {one_liner}} NEWLINE"


@dataclass
class ReferenceType(Class):
    pass


@dataclass
class Subtyping(PydanticMixin):
    name: SubtypingName = ""
    is_exclusive: IsExclusive = field(default_factory=IsExclusive)
    is_exhaustive: IsExhaustive = field(default_factory=IsExhaustive)
    subtypes: Optional[List[ClassName]] = field(default_factory=list)

    def shared_post_init(self):
        super().shared_post_init()
        self.is_exclusive = True
        self.is_exhaustive = True


@dataclass
class AttributeSection(Component):
    name: AttributeSectionName = None

    is_optional: IsOptional = None
    attributes: List[Attribute] = block_list_field(default_factory=list)

    def shared_post_init(self):
        super().shared_post_init()
        print(
            f"In AttSection post-init for {self.name}, is_optional = {self.is_optional}"
        )
        if self.attributes is None:
            self.attributes = []
        if self.is_optional is None:
            self.is_optional = IsOptional("Required")
        if isinstance(self.name, str):
            print("Fixing AttSection name!")
            self.name = AttributeSectionName(self.name)

    class Meta:
        presentable_header = "-  {name}{? - {one_liner}}{? ({is_optional})} NEWLINE"

    # def render_markdown(self):
    #     print("Rendering AttributeSection")
    #     return ("ATTRIBUTE SECTION GOES HERE\n")
    #     return self.render_markdown_component(prefix="__ ", parenthetical=None)


@dataclass
class Attribute(Component):
    name: AttributeName = None
    data_type_clause: DataTypeClause = None
    overrides: Optional[AttributeReference] = None
    inverse: Optional[AttributeReference] = None
    inverse_of: Optional[AttributeReference] = None
    derivation: Optional[Derivation] = None
    default: Optional[Default] = None
    constraints: Optional[List[Constraint]] = block_list_field(default_factory=list)

    def shared_post_init(self):
        super().shared_post_init()
        if self.constraints is None:
            self.constraints = []
        if isinstance(self.name, str):
            print("Fixing attribute name!")
            self.name = AttributeName(self.name)

    class Meta:
        presentable_header = (
            "-  {name}{? - {one_liner}}{? ({data_type_clause})} NEWLINE"
        )


@dataclass
class AttributeReference(PydanticMixin):
    class_name: ClassName =  None 
    attribute_name: AttributeName = None


    # Note. With this in, to_typed_dict fails, but why?
    # def __str__(self):
    #     """Convert the object to a string."""
    #     return f"{self.class_name.content}.{self.attribute_name.content}"


    @classmethod
    def from_dict(cls, data):
        """Specialized deserialization for AttributeReference"""
        if not isinstance(data, dict):
            return None
        class_name = (
            ClassName.from_dict(data.get("class_name"))
            if data.get("class_name")
            else None
        )
        attribute_name = (
            AttributeName.from_dict(data.get("attribute_name"))
            if data.get("attribute_name")
            else None
        )
        return cls(class_name=class_name, attribute_name=attribute_name)


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
    LiterateModel,
    Paragraph,
    OneLiner,
    Annotation,
    ClassName,
    Label,
    PresentableBoolean,
    PresentableToken,
    IsOptional,
    AsValue,
    # MarkedText,
    Emoji,
]
