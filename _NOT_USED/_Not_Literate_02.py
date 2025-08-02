from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import List, Optional, Dict, Union, Literal, Annotated
from abc import ABC, abstractmethod
from functools import partial

# First, let's create a Pydantic-compatible block_list_field
def block_list_field(default_factory=list, **kwargs):
    """Pydantic version of block_list_field with metadata support"""
    metadata = kwargs.pop('metadata', {})
    return Field(
        default_factory=default_factory,
        json_schema_extra=metadata,
        **kwargs
    )

class MinorComponent(BaseModel, ABC):
    """
    Abstract base component with common fields.
    Uses Pydantic's ABC support instead of dataclass ABC.
    """
    _type: str = Field(default=None, exclude=True)
    one_liner: Optional['OneLiner'] = None
    elaboration: List[Union['Paragraph', 'CodeBlock']] = block_list_field(
        metadata={"list": "{element}+"}
    )
    annotations: List['Annotation'] = block_list_field()
    diagnostics: List['Diagnostic'] = block_list_field()
    is_embellishment: bool = False

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra='forbid',
        json_schema_extra={
            'is_abstract': True
        }
    )

    @field_validator('_type', mode='before')
    def set_type(cls, v):
        return v or cls.__name__


# class MinorComponent(BaseModel, ABC):
#     @abstractmethod
#     def abstract_method(self):
#         pass

#     model_config = ConfigDict(
#         json_schema_extra={'is_abstract': True},
#         extra='forbid'
#     )

    class Meta:
        is_abstract = True


# class Component(MinorComponent):
#     """Concrete component with additional fields"""
#     prefix: Optional[str] = None
#     name: 'CamelCase' = None
#     parenthetical: Optional[str] = None
#     abbreviation: Optional['CamelCase'] = None

#     model_config = ConfigDict(
#         json_schema_extra={
#             'presentable_header': "COMPONENT: {name}{? - {one_liner}} NEWLINE"
#         }
#     )

#     def __str__(self):
#         return f"{self._type.capitalize()}: {self.name}"

#     class Meta:
#         presentable_header = "COMPONENT: {name}{? - {one_liner}} NEWLINE"
        
class Class(Component):
    """Pydantic version of Class model with all relationships"""
    name: 'ClassName' = None
    plural: Optional[str] = None
    subtype_of: Dict['ClassName', 'SubtypingName'] = Field(default_factory=dict)
    subtypings: List['Subtyping'] = block_list_field(
        metadata={"list": "{element}+"}
    )
    subtypes: Dict['ClassName', 'SubtypingName'] = Field(default_factory=dict)
    based_on: List['ClassName'] = Field(default_factory=list)
    dependents: List['ClassName'] = Field(default_factory=list)
    is_value_type: bool = False
    where: Optional['OneLiner'] = None
    constraints: List['Constraint'] = block_list_field()
    attributes: List['Attribute'] = block_list_field()
    attribute_sections: List['AttributeSection'] = block_list_field()

    _type: Literal['Class'] = Field(default='Class', exclude=True)

    @field_validator('name', mode='before')
    def validate_name(cls, v):
        if isinstance(v, str):
            print("Converting string to ClassName")
            return ClassName(v)
        return v

    model_config = ConfigDict(
        json_schema_extra={
            'presentable_header': "_ {name}{? - {one_liner}} NEWLINE"
        }
    )

    class Meta:
        presentable_header = "_ {name}{? - {one_liner}} NEWLINE"


class AttributeSection(Component):
    name: 'AttributeSectionName' = None
    is_optional: 'IsOptional' = Field(default_factory=lambda: IsOptional(False))
    attributes: List['Attribute'] = block_list_field()

    _type: Literal['AttributeSection'] = Field(default='AttributeSection', exclude=True)

    @field_validator('name', mode='before')
    def validate_name(cls, v):
        if isinstance(v, str):
            return AttributeSectionName(v)
        return v

class Attribute(Component):
    name: 'AttributeName' = None
    data_type_clause: 'DataTypeClause' = None
    overrides: Optional['AttributeReference'] = None
    inverse: Optional['AttributeReference'] = None
    inverse_of: Optional['AttributeReference'] = None
    derivation: Optional['Derivation'] = None
    default: Optional['Default'] = None
    constraints: List['Constraint'] = block_list_field()

    _type: Literal['Attribute'] = Field(default='Attribute', exclude=True)
    

# class Component(MinorComponent):
#     meta: dict = Field(
#         default={
#             'presentable_header': "COMPONENT: {name}{? - {one_liner}} NEWLINE"
#         },
#         exclude=True
#     )

# recommended
# model_config = ConfigDict(
#     json_schema_extra={
#         'presentable_header': "_ {name}{? - {one_liner}} NEWLINE",
#         'is_abstract': False
#     }
# )