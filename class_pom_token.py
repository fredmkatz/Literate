from __future__ import annotations

import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


from dataclasses import is_dataclass, fields

from utils_pom.util_json_pom import as_json

from class_templates import PomTemplate


class PresentableToken(ABC):
    """
    Abstract base class for token types.

    Attributes:
        input (str): The original input string.
        output (str): The words translated to the proper casing.
    """

    input: str = None  # The original input string, as recognized by the parser.

    def __init_subclass__(cls):
        return super().__init_subclass__()

    @abstractmethod
    def token_pattern(self) -> str:
        """
        Returns the regex pattern, or other rule for this token type.
        So: PomToken: token_pattern - will appear in the grammar rule.

        """

    @abstractmethod
    def value(self) -> Any:
        """
        Returns the template format for this token type.
        Different subclasses will have different values types.
        """

    @abstractmethod
    def rendering_template(self) -> PomTemplate:
        """
        Returns the template format for this token type, in simpified format
        """

    @abstractmethod
    def handlebars_template(self) -> str:
        """
        Returns the template format for this token type, in Handlebars format
        """

        # The Handlebars template for this token type.
        # This is a simplified version of the rendering template.
        # It can be used to render the value in a more complex way, if needed.
        # For example, it can include conditionals or loops.
        # The rendering template is used for the final output, while the Handlebars template is used for intermediate steps.
        return


@dataclass
class PresentableBoolean(PresentableToken, ABC):
    t_value: bool = field(default=False, init=True)  # Accept initial value through dataclass mechanism
    _type: str = field(default="PresentableBoolean", init=False)
    
    # Class attributes that should be overridden by subclasses
    true_word = None
    false_word = None
    default_value = False
    is_explicit = True
    
    # Will be auto-populated in __post_init__
    true_words = None
    false_words = None
    token_pattern_str = None
    
    def __post_init__(self):
        # Initialize word lists
        if self.true_word is None or self.false_word is None:
            raise NotImplementedError("Subclasses must define true_word and false_word")
            
        # Initialize words lists if not already set
        if self.true_words is None:
            self.true_words = [self.true_word.lower(), "true", "yes"]
        if self.false_words is None:  
            self.false_words = [self.false_word.lower(), "false", "no"]
            
        # Process the input value
        if isinstance(self.t_value, str):
            # Normalize to lowercase for comparison
            normalized_value = self.t_value.lower()
            if normalized_value in self.true_words:
                self.t_value = True
            elif normalized_value in self.false_words:
                self.t_value = False
            else:
                print(f"Invalid boolean value: {self.t_value} - should be {self.true_word} or {self.false_word}")
                self.t_value = False
        elif not isinstance(self.t_value, bool):
            raise TypeError(f"Expected string or boolean, got {type(self.t_value)}")
        
        # Generate the token pattern
        all_words = [f'"{word}"i' for word in self.true_words + self.false_words]
        self.token_pattern_str = " | ".join(all_words)

    # Rest of your methods would remain the same
    def toJSON(self):
        return {"_type": self._type, "value": self.t_value}


    def __str__(self):
        """String representation based on the value and settings."""
        val = self.t_value

        # If not explicit and value matches default, return empty string
        if not self.is_explicit and val == self.default_value:
            return ""

        # Otherwise return appropriate word
        if val is None:
            return "NoValue"

        return self.true_word if val else self.false_word


    @classmethod
    def token_pattern(cls) -> str:
        """Return the grammar pattern for this token."""
        instance = cls(False)  # Create a temporary instance to access instance attributes
        return instance.token_pattern_str


    def handlebars_template(self) -> str:
        """Return the Handlebars template for rendering."""
        # Full Handlebars template with conditionals
        if self.is_explicit:
            return "{{#if value}}{{true_word}}{{else}}{{false_word}}{{/if}}"
        else:
            return "{{#if (eq value default_value)}}{{else}}{{#if value}}{{true_word}}{{else}}{{false_word}}{{/if}}{{/if}}"

    def rendering_template(self) -> PomTemplate:
        """Return simplified template for basic rendering."""
        # Simplified template that can't handle conditionals
        return PomTemplate("{value}")

    def value(self) -> bool:
        return self.value


def create_boolean_type(
    name,
    true_word,
    false_word,
    true_words=None,
    false_words=None,
    default_value=False,
    is_explicit=True,
):
    """Factory function to create custom boolean token types."""
    # Default word lists if not provided
    if true_words is None:
        true_words = [true_word.lower(), "true", "yes"]
    if false_words is None:
        false_words = [false_word.lower(), "false", "no"]

    # Create a new class dynamically
    return type(
        name,
        (PresentableBoolean,),
        {
            "true_word": true_word,
            "false_word": false_word,
            "true_words": true_words,
            "false_words": false_words,
            "default_value": default_value,
            "is_explicit": is_explicit,
        },
    )


@dataclass
class IsOptional(PresentableBoolean):
    """Class representing a boolean token for "is required"."""
    _type: str = field(default="IsOptional", init=False)
    
    # Class attributes - no need for __init__ or __post_init__ override
    true_word = "Optional"
    false_word = "Required"
    true_words = ["optional", "true", "sure", "yes"]
    false_words = ["required", "false", "no way"]
    default_value = False
    is_explicit = False

@dataclass
class IsExclusive(PresentableBoolean):
    """
    Class representing a boolean token for "is exclusive".

    Attributes:
        value (bool): The boolean value.

    """

    _type: str = field(default="IsExclusive", init=False)

    true_word = "exclusive"
    true_words = ["exclusive"]

    false_word = "nonExclusive"
    false_words = ["nonExclusive"]
    default_value = True
    is_explicit = False


@dataclass
class IsExhaustive(PresentableBoolean):
    """
    Class representing a boolean token for "is exhaustive".

    Attributes:
        value (bool): The boolean value.

    """

    _type: str = field(default="IsExhaustive", init=False)

    true_word = "exhaustive"
    true_words = ["exhaustive"]

    false_word = "nonExhaustive"
    false_words = ["nonExhaustive"]
    default_value = True
    is_explicit = False


@dataclass
class AsValue(PresentableBoolean):
    """
    Class representing a boolean token for whether
    a class is Reference or Value

    Attributes:
        value (bool): The boolean value.

    """

    _type: str = field(default="AsValue", init=False)

    true_word = "reference"
    true_words = ["reference"]
    false_word = "value"
    false_words = ["value"]
    default_value = True
    is_explicit = False


class MarkedText(PresentableToken):
    token_pattern_str = '"<<<" + /.*?/ + ">>>"'

    def __init__(self, input_string):
        self.input = input_string
        self.content = input.string.replace("<<<", "").replace(">>>", "")

    def value(self) -> str:
        return self.content

    @classmethod
    def token_pattern(cls) -> str:
        return cls.token_pattern_str

    def rendering_template(self) -> PomTemplate:
        return PomTemplate("{value}")

    def handlebars_template(self) -> str:
        return "{{value}}"


@dataclass
class Emoji(PresentableToken):

    token_pattern_str = r"/\d+(.*?)[\u263a-\U0001f645]/"
    # regex = re.compile(r'\d+(.*?)[\u263a-\U0001f645]')

    @classmethod
    def token_pattern(cls) -> str:
        return cls.token_pattern_str

    def rendering_template(self) -> PomTemplate:
        return PomTemplate("{value}")

    def handlebars_template(self) -> str:
        return "{{value}}"
