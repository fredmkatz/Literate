# Version: 2025-02-22_222609

from __future__ import annotations
from typing import List, Optional, Dict, Any, Union


from utils.util_pydantic import PydanticMixin,  dataclass, field
from utils.class_container import Container
from utils.debug_pydantic import debug_dataclass_creation
from utils.class_casing import *
from functools import cached_property # You need to import cached_property

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

from enum import Enum, StrEnum

class Cardinality(StrEnum):
    MANY_ONE = "M_1"
    ONE_MANY = "1_M"
    ONE_ONE = "O_O"
    MANY_MANY = "M_M"

@dataclass 
class Trivial():
    pass

@dataclass
class Natural(PydanticMixin, Trivial):
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

@dataclass
class ClassReference(ClassName, Container):
    content: Any
    container: Optional["Container"] = field(default=None, kw_only=True)
## NOTE: MAGIC treatment for adding Containter as parent:
### redeclare the container attribute and set kw_only = True for it

@dataclass
class SubjectName(NormalCase):
    pass


@dataclass
class AttributeSectionName(NormalCase):
    pass


@dataclass
class AttributeName(LowerCamel, Container):
    content: Any
    container: Optional["Container"] = field(default=None, kw_only=True)


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
    category: str = ""
    message: Optional[str] = None

    severity: str = "Error"
    constraint_name: str = ""

    def __str__(self):
        return f"{self.severity} ({self.category}) on {self.object_type} named {self.object_name}: {self.message}"

    def shared_post_init(self):
        if self.message == None:
            self.message = ""


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
class Component(MinorComponent, Container):
    prefix: Optional[str] = None
    name: CamelCase = None
    parenthetical: Optional[str] = None
    abbreviation: Optional[str] = None

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
    name: SubjectName = None
    prefix: str = ""
    classes: List[Class] = block_list_field(default_factory=list)
    
    def containees(self):
        return self.classes
    

    def shared_post_init(self):
        super().shared_post_init()
        if isinstance(self.name, str):
            print("Fixing Subject name!")
            self.name = SubjectName(self.name)
        if not self.classes:
            self.classes = []
        if not self.subjects:
            self.subjects = []

    def all_classes(self):
        return self.all_classes_p
    
    @cached_property
    def all_classes_p(self) -> List[Class]:
        # print("Calcing all_classes for ", self)
        # print(f"- locally, there are {len(self.classes)} classes for {self}")
        
        # Note. Need to make a copy of the list of classes
        # otherwise as all_classes gets extended, so does self.classes
        all_classes = [c for c in self.classes]

        for subject in self.subjects:
            all_classes.extend(subject.all_classes_p)
        # print(f"- allclasses for {self} contains {len(all_classes)}; locally just {len(self.classes)}")
        return all_classes

    def is_trivial(self):
        return self.is_trivial_p
    
    @cached_property
    def is_trivial_p(self) -> bool:
        if "trivial" in self.name.content.lower():
            print(f"{self} is Trivial!")
            return True
        parent_subject = self.containing(Subject)
        if not parent_subject:
            print(f"{self} is NOT Trivial!")
            return False
        print(f"{self} doesn't look Trivial, but ascending...")
        return self.containing(Subject).is_trivial()

    class Meta:
        presentable_header = "#####  {{name}{? - {one_liner}} NEWLINE"


@dataclass
class SubjectD(SubjectE):
    subjects: List[SubjectE] = block_list_field(default_factory=list)

    def containees(self):
        return self.classes + self.subjects

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
    subjects: List[SubjectB] = block_list_field(default_factory=list)

    def shared_post_init(self):
        super().shared_post_init()
        if isinstance(self.name, str):
            print("Fixing LiterateModel name!")
            self.name = ModelName(self.name)
        self.set_containees_back()
    
    def all_class_names(self):
        return self.all_class_names_p
    
    @cached_property
    def all_class_names_p(self) -> list[str]:
        print("Calcing all_class names  for ", self)
        return self.full_class_index().keys()

    def class_index(self):
        return self.class_index_p
    
    @cached_property
    def class_index_p(self) -> dict[str, Class]:
        the_index  = {str(c.name): c for c in self.all_classes()}
        if None in the_index:
            print("Found none in singular index")
        return the_index
    
    def plural_index(self):
        return self.plural_index_p
    
    @cached_property
    def plural_index_p(self) -> dict[str, Class]:
        the_index  = {c.derive_plural() : c for c in self.all_classes()}
        if None in the_index:
            print("Found none in p;ural index")
        return the_index
    
    def full_class_index(self):
        return self.full_class_index_p
    
    @cached_property
    def full_class_index_p(self) -> dict[str, Class]:
        return self.class_index() | self.plural_index()

    def class_named(self, cname: str)-> Class:
        return self.full_class_index().get(cname, None)


    class Meta:
        presentable_header = "#  {{name}{? - {one_liner}} NEWLINE"
        



Subject = SubjectB



@dataclass
class DataType(PydanticMixin, Container):
    """A simple or complex data type"""

    def shared_post_init(self):
        super().shared_post_init()
        # print("Data type type is ", self._type)
    
    def base_type_names(self) -> List[str]:
        pass    # this is an abstract class
        

    class Meta:
        is_abstract = True


@dataclass
class BaseDataType(DataType):
    class_name: Any  = None #ClassReference = field(default_factory=ClassReference)
    as_value_type: AsValue = None # field(default_factory=AsValue)
    container: Optional["Container"] = field(default=None, kw_only=True)
    
    def containees(self):
        return [self.class_name]

    def shared_post_init(self):
        super().shared_post_init()
        if isinstance(self.class_name, str):
            self.class_name = ClassReference(self.class_name)
        # print("Created BDT is ", self)
        # print("Base Data type type is ", self._type)
        # print("Base Data type is (repr)", self.__repr__())
        # print("Base Data type is (to_typed_dict)", self.to_typed_dict())

    def base_type_names(self) -> List[str]:
        return [self.class_name.content]


    class Meta:
        presentable_template = "{class_name} {? - {is_value}}"

    def __str__(self):
        return f"{self.as_value_type} {self.class_name}"


@dataclass
class ListDataType(DataType):
    element_type: DataType  = None # What's inside the list
    container: Optional["Container"] = field(default=None, kw_only=True)

    def containees(self):
        return [self.element_type]

    def base_type_names(self) -> List[str]:
        if not self.element_type:
            return []
        return self.element_type.base_type_names()


    class Meta:
        presentable_template = "List of {element_type}"

    def __str__(self):
        return f"List of {self.element_type}"


@dataclass
class SetDataType(DataType):
    element_type: DataType = None  # What's inside the set
    container: Optional["Container"] = field(default=None, kw_only=True)

    def containees(self):
        return [self.element_type]

    def base_type_names(self) -> List[str]:
        if not self.element_type:
            return []
        return self.element_type.base_type_names()

    class Meta:
        presentable_template = "Set of {element_type}"

    def __str__(self):
        return f"Set of {self.element_type}"


@dataclass
class MappingDataType(DataType):
    domain_type: DataType = None # Mapping from this
    range_type: DataType  = None # Mapping to this
    container: Optional["Container"] = field(default=None, kw_only=True)

    def containees(self):
        return [self.domain_type, self.range_type]

    def base_type_names(self) -> List[str]:
        return self.domain_type.base_type_names() + self.range_type.base_type_names()



    class Meta:
        presentable_template = "Mapping from {domain_type} TO {range_type}"

    def __str__(self):
        return f"Mapping from {self.domain_type} to {self.range_type}"


@dataclass
class DataTypeClause(PydanticMixin, Container):
    """
    Represents the type information for an attribute.

    Attributes:
        data_type: The data type
        is_optional: Whether the attribute is optional (default: False)
        cardinality: Optional cardinality constraint (e.g., "0..1", "1..*")
    """

    data_type: Any = None
    # is_optional_lit: Optional[IsOptional] = field(default="Required")
    is_optional_lit: Optional[IsOptional] = field(default_factory=lambda: IsOptional(content=False))

    cardinality: Optional[Cardinality] = field(default = Cardinality.ONE_ONE)

    def containees(self):
        return [self.data_type]
    class Meta:
        presentable_template = "{is_optional_lit} {data_type}{? {cardinality}}"

    def __str__(self):
        req_or_optional = "optional" if self.is_optional_lit else "required"
        return f"{req_or_optional} {self.data_type} ({self.cardinality})"
    
    


@dataclass
class FormulaCoding(PydanticMixin):
    content: str



@dataclass
class Formula(MinorComponent, Container):
    ocl: Optional[str] = ""
    container: Optional["Container"] = field(default=None, kw_only=True)


    def shared_post_init(self):
        super().shared_post_init()
        if self.ocl is None:
            self.ocl = ""


@dataclass
class Constraint(Formula):
    message: Optional[str] = None
    severity: Optional[str] = None

    def shared_post_init(self):
        super().shared_post_init()
        if self.message is None:
            self.message = ""


@dataclass
class Derivation(Formula):
    pass



@dataclass
class Default(Formula):
    pass

@dataclass
class SubtypeBy(PydanticMixin):
    class_name: ClassReference = None
    subtyping_name: SubtypingName = None


# to do: why do all of the field declarations make trouble for serializaing
# and why do I get FieldInfo values instead of empty lists? without the 
# "fixes" applied in shared_post_init?
@dataclass
class Class(Component):
    name: ClassName = None
    plural: str = None
    presumed_plural: str = None
    subtype_of: Optional[List[SubtypeBy]] =  None # field(default_factory=list)
    
    subtypings: Optional[List[Subtyping]] = block_list_field(default_factory=list)
    subtypes: Optional[List[SubtypeBy]]  = None # field(default_factory=list)
    
    based_on: Optional[List[ClassReference]] =  None # field(default_factory=list)
    dependents: Optional[List[ClassReference]] =  None # field(default_factory=list)
    is_value_type: bool = False
    where: Optional[str] = None
    constraints: Optional[List[Constraint]] = block_list_field(default_factory=list)

    attributes: List[Attribute] = block_list_field(default_factory=list)
    attribute_sections: List[AttributeSection] = block_list_field(default_factory=list)
    

    # Transients
    
    # actually: dict[str, class object]; optional to avoid validation errors
    # all_classes: Optional[Any] = field(init=False, repr=False, hash=False, compare=False)

    def containees(self):
        return self.attribute_sections + self.attributes + self.based_on + self.constraints
    


    def shared_post_init(self):
        super().shared_post_init()
        # Initialize all list fields consistently
        self.attributes = self.attributes or []
        self.attribute_sections = self.attribute_sections or []
        self.subtypings = self.subtypings or []
        self.constraints = self.constraints or []
        self.based_on = self.based_on or []
        self.dependents = self.dependents or []
        self.subtype_of = self.subtype_of or []
        self.subtypes = self.subtypes or []
        
        if isinstance(self.name, str):
            print("Fixing Class name!")
            self.name = ClassName(self.name)
        self.prefix = "Class"
        

    # calc derivation: presumed plural
    def derive_presumed_plural(self) -> str:
        # print("Calcing presumed_plural")
        class_name = str(self.name)
        self.presumed_plural = fmk.pluralize(class_name)
        # print(f"Set presumed plural for {self}: name is {class_name}, presuming {self.presumed_plural}")
        return self.presumed_plural

    def attribute_named(self, aname):
        return self.attribute_named_p.get(aname, None)
    
    # @cached_property
    @property
    def attribute_named_p(self) -> dict:
        attributes = self.all_attributes()
        the_dict =  {a.name.content: a for a in attributes}
        print(f"All attributes for {self} are: ", the_dict.keys())
        return the_dict
    
    def all_attributes(self):
        atts = self.attributes
        for section in self.attribute_sections:
            atts += section.attributes
        return atts
    
    # calc derivation: plural
    def derive_plural(self) -> str:
        plural = self.plural
        if plural is not None:
            plural = plural.strip()
            self.plural = plural
            return plural
        # print(f"Using presumed plural for {self}")

        self.plural = self.derive_presumed_plural()
        return self.plural

    def class_mro(self):
        return self.class_mro_p

    @cached_property
    def class_mro_p(self):
        
        cname = self.name.content
        the_model = self.containing(LiterateModel)
        print(f"In classs_mro, the_model = {the_model}")
        supers = getattr(self, "subtype_of", None)
        if not supers:
            return []

        if len(supers) > 1:
            print(f"> 1 supers for {cname} - {supers}")
        # Note only taking the first! TODO
        for supertype in supers:
            super_name = str(supertype.class_name)
            # print(cname, "\thas super: ", super_name)
            super_type = the_model.class_named(super_name)
            if not super_type:
                continue
            mro = [super_name] + super_type.class_mro_p
            print(f"MRO for {cname} => ", mro)
            return mro
        return []

    def is_trivial(self):
        return self.is_trivial_p
    
    @cached_property
    def is_trivial_p(self) -> bool:
        return self.containing(Subject).is_trivial()


    class Meta:
        presentable_header = "_ {name}{? - {one_liner}} NEWLINE"


Class_ = Class


@dataclass
class ValueType(Class):

    def shared_post_init(self):
        super().shared_post_init()
        self.is_value_type = True
        self.prefix = "Value Type"

    class Meta:
        presentable_header = "_  ValueType : {name}{? - {one_liner}} NEWLINE"

    
    
@dataclass
class CodeType(ValueType):

    class Meta:
        presentable_header = "_  CodeType : {name}{? - {one_liner}} NEWLINE"

    def shared_post_init(self):
        super().shared_post_init()
        self.is_value_type = True
        self.prefix = "Code Type"

@dataclass
class ReferenceType(Class):
    pass


@dataclass
class Subtyping(PydanticMixin):
    name: SubtypingName = ""
    is_exclusive: IsExclusive = field(default_factory=IsExclusive)
    is_exhaustive: IsExhaustive = field(default_factory=IsExhaustive)
    subtypes: Optional[List[ClassReference]] = field(default_factory=list)

    def shared_post_init(self):
        super().shared_post_init()
        self.is_exclusive = IsExclusive(True)
        self.is_exhaustive = IsExclusive(False)


@dataclass
class AttributeSection(Component):
    name: AttributeSectionName = None

    is_optional: IsOptional = None
    attributes: List[Attribute] = block_list_field(default_factory=list)
    container: Optional["Container"] = field(default=None, kw_only=True)
    
    def containees(self):
        return self.attributes

    def shared_post_init(self):
        super().shared_post_init()
        # print(
        #     f"In AttSection post-init for {self.name}, is_optional = {self.is_optional}"
        # )
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
    container: Optional["Container"] = field(default=None, kw_only=True)

    def containees(self):
        return [self.data_type_clause, self.name, self.inverse, self.overrides]
        # containess to add. overrides, inverse
    
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
class AttributeReference(PydanticMixin, Trivial, Container):
    class_name: ClassReference =  None 
    attribute_name: AttributeName = None
    container: Optional["Container"] = field(default=None, kw_only=True)

    def containees(self):
        return [self.class_name, self.attribute_name]

    # Note. With this in, to_typed_dict fails, but why?
    def __str__(self):
        """Convert the object to a string."""
        return f"{self.class_name}.{self.attribute_name}"


    @classmethod
    def from_dict(cls, data):
        """Specialized deserialization for AttributeReference"""
        if not isinstance(data, dict):
            return None
        class_name = (
            ClassReference.from_dict(data.get("class_name"))
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
    ClassReference,
    Label,
    PresentableBoolean,
    PresentableToken,
    IsOptional,
    AsValue,
    # MarkedText,
    Emoji,
]
