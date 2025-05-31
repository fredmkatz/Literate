"""Classes to handle CamelCase and variants.
- Casing - abstract base for all
- UpperCamel
- LowerCamel
- SnakeCase (all lower case)
- UpperSnake (UPPER_SNAKE_CASE)
- kebab

Casing has
- token_pattern_str - a common pattern for recognizing any or all of these,
possible separated by spaces (but not by tabs or newlines)
- words - the input string, split into a list of words (strs)
- input - the string passed into init on construction
- content - the words, xlated to the proper casing

The str() function should return the value of content

The init should also handle UpperCamel(SnakeCase("xxx"), ...)
    really any list of items that have str() representations
    It should join the strs for the items in the list, separated by space,
    as the original input, split into words, ...
"""

from __future__ import annotations

import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from dataclasses import is_dataclass, fields, field

from utils.util_json import as_json
 from utils.class_pom_token import PresentableToken
 from utils.class_templates import PomTemplate


@dataclass
class Casing(PresentableToken):
    content: str = ""
    _type: str = field(default="Casing", init=False)

    """
    Abstract base class for different casing styles.

    Attributes:
        input (str): The original input string.
        words (list): The input string split into a list of words.
        output (str): The words translated to the proper casing.
    """

    # Partial patterns
    SYLLABLE = r"[A-Za-z][A-Za-z0-9]*"
    IDENTIFIER = rf"{SYLLABLE}(?:[-_.]{SYLLABLE})*"
    IDENTIFIER = rf"{SYLLABLE}(?:[ ]{SYLLABLE})*"
    IDENTIFIER = rf"{SYLLABLE}"

    # Full pattern for one or more IDENTIFIERS separated by spaces
    token_pattern_str = rf"/(?:{IDENTIFIER})(?:\s+(?:{IDENTIFIER}))*/"
    # token_pattern_str = f"/{IDENTIFIER}/"

    def __post_init__(self):
        if isinstance(self.content, list):
            self.content = " ".join(str(item) for item in self.content)
        self.argument = self.content
        self.input = self.content
        self.words = self.split_to_words(self.content)
        self.content = self.convert()
        self._type = type(self).__name__

    def value(self) -> str:
        return self.content

    @classmethod
    def token_pattern(cls) -> str:
        return cls.token_pattern_str

    def rendering_template(self) -> PomTemplate:
        return PomTemplate("{value}")

    def handlebars_template(self) -> str:
        return "{{value}}"

    def split_to_words(self, input_string):
        """_summary_
        split a string into words, using spaces, -,_ and . as separators. Also,
        split camel case words into separate words.

        Args:
            input_string (_type_): _description_

        Returns:
            _type_: _description_
        """
        words1 = re.split(r"[-_.\s]", input_string)  # split on spaces,  -,_ and .
        words2 = [word for word in words1 if word]  # remove empty strings
        #  split all camel case words, combine into flat list
        words3 = [
            word
            for word in [self.split_camel(word) for word in words2]
            for word in word
        ]
        return words3

    def split_camel(self, input_string):
        """
        Split a CamelCase string into words.
        """
        return re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)", input_string)

    @abstractmethod
    def convert(self):
        """
        Abstract method to convert words to the desired casing.
        """
        pass

    def __str__(self):
        return self.content
        # def __repr__(self):
        return type(self).__name__ + "(" + self.content + ")"

    def __json__(self):
        return str(self)

    def __dict__(self):
        return {"_type": self._type, "content": self.content}

    def toJSON(self):
        """Convert the object to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_dict(self):
        """Simplified serialization with just type and input"""
        return {
            "_type": self._type,  # Your existing code already sets this correctly
            "content": self.content,
        }

    @classmethod
    def from_dict(cls, data):
        """Standard deserialization method"""
        if isinstance(data, dict):
            content = data.get("content", "")
            return cls(content=content)
        return cls(content=str(data))

    def __json__(self):
        """Convert the object to a JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    def to_json(self):
        """
        Convert the object to a JSON string.
        """
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class NormalCase(Casing):
    _type: str = field(default="NormalCase", init=False)

    def convert(self):
        return " ".join(str(word) for word in self.words)


@dataclass
class CamelCase(Casing):
    _type: str = field(default="CamelCase", init=False)

    # def __post_init__(self):
    #     super().__post_init__()

    def convert(self):
        return "".join(word.capitalize() for word in self.words)


@dataclass
class UpperCamel(CamelCase):
    _type: str = field(default="UpperCamel", init=False)

    """
    Converts words to UpperCamelCase.
    """

    def convert(self):
        upper = "".join(word.capitalize() for word in self.words)
        # print(f"Casing: UpperCamel for {self.words} = {upper}")
        return upper


@dataclass
class LowerCamel(CamelCase):
    _type: str = field(default="LowerCamel", init=False)

    """
    Converts words to lowerCamelCase.
    """
    # def __post_init__(self):
    #     super().__post_init__()

    def convert(self):
        if not self.words:
            return ""
        lower = self.words[0].lower() + "".join(
            word.capitalize() for word in self.words[1:]
        )
        # print(f" LowerCamel for {self.words} = {lower}")
        return lower


@dataclass
class SnakeCase(Casing):
    _type: str = field(default="SnakeCase", init=False)

    """
    Converts words to snake_case.
    """

    def convert(self):
        snake = "_".join(word.lower() for word in self.words)
        # print(f"Snake for {self.words} = {snake}")
        return snake


@dataclass
class UpperSnake(Casing):
    """
    Converts words to UPPER_SNAKE_CASE.
    """

    _type: str = field(default="UpperSnake", init=False)

    def convert(self):
        return "_".join(word.upper() for word in self.words)


NTCase = SnakeCase
TokenCase = UpperSnake


@dataclass
class Kebab(Casing):
    """
    Converts words to kebab-case.
    """

    _type: str = field(default="Kebab", init=False)

    def convert(self):
        return "-".join(word.lower() for word in self.words)


@dataclass
class PascalCase(Casing):
    """
    Converts words to PascalCase.
    """

    _type: str = field(default="PascalCase", init=False)

    def convert(self):
        return "".join(word.capitalize() for word in self.words)


@dataclass
class DotCase(Casing):
    """
    Converts words to dot.case.
    """

    _type: str = field(default="DotCase", init=False)

    def convert(self):
        return ".".join(word.lower() for word in self.words)


@dataclass
class TrainCase(Casing):
    """
    Converts words to Train-Case.
    """

    _type: str = field(default="TrainCase", init=False)

    def convert(self):
        return "-".join(word.capitalize() for word in self.words)


# Aliases
UpperCamelCase = UpperCamel
lowerCamel = LowerCamel
snake_case = SnakeCase
UPPER_SNAKE_CASE = UpperSnake
kebab_case = Kebab
pascalCase = PascalCase
dot_case = DotCase
train_case = TrainCase


if __name__ == "__main__":
    print("UpperCamel", UpperCamel("this is a test"))
    print("UpperCamel", UpperCamel("UpperCamel"))
    print("LowerCamel", LowerCamel("this is a test"))
    print("SnakeCase", SnakeCase("this is a test"))
    print("UpperSnake", UpperSnake("this is a test"))
    print("Kebab", Kebab("this is a test"))
    print("PascalCase", PascalCase("this is a test"))
    print("DotCase", DotCase("this is a test"))
    print("TrainCase", TrainCase("this is a test"))

    ids = ["This is the first identifer", "This is the second identifier"]
    kcase = kebab_case(ids)
    print(kcase.to_json())

    ucamel = UpperCamel("UpperCamel")
    print(ucamel.to_json())
