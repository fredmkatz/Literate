from pydantic.dataclasses import dataclass
 from utils.util_pydantic import PydanticMixin
 from utils.class_casing import *

from typing import *


@dataclass
class ClassName(UpperCamel):
    pass


@dataclass
class AttributeName(LowerCamel):
    pass


@dataclass
class Attribute(PydanticMixin):
    name: LowerCamel


@dataclass
class Class(PydanticMixin):
    name: UpperCamel
    attributes: List[Attribute]
