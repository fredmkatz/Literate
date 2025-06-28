from __future__ import annotations

from utils.util_pydantic import PydanticMixin,  dataclass, field

from typing import Any, Union

from utils.debug_pydantic import debug_dataclass_creation

from utils.class_templates import PomTemplate
def raise_error(message):
    print(message)

# @debug_dataclass_creation
@dataclass
class PresentableToken(PydanticMixin):
    """
    Abstract base class for token types.

    Attributes:
        content (str): The original input string.
        output (str): The words translated to the proper casing.
    """
    content: str = ""
    _type: str = field(init=False)
    # using_normal: bool = False
    # using_pydantic: bool = False
    # as_entered: str = field(default="", init=False)
    
    __field_order__ = ["_type", "content"]


    def shared_post_init(self):
        super().shared_post_init()

        self.as_entered = self.content

    def full_display(self) -> dict:
        return { "_type": self._type,
                "as_entered": self.as_entered,
                "content": self.content,
                "repr": repr(self),
                "str": str(self)
                }
        



    def __init_subclass__(cls):
        return super().__init_subclass__()

    # @abstractmethod
    def token_pattern(self) -> str:
        """
        Returns the regex pattern, or other rule for this token type.
        So: PomToken: token_pattern - will appear in the grammar rule.

        """
        return ""

    # @abstractmethod
    def value(self) -> Any:
        """
        Returns the template format for this token type.
        Different subclasses will have different values types.
        """
        return ""
    def __str__(self):
        return self.content if self.content else "NoToeknContent"

    # @abstractmethod
    def rendering_template(self) -> PomTemplate:
        """
        Returns the template format for this token type, in simpified format
        """
        return ""

    # @abstractmethod
    def handlebars_template(self) -> str:
        """
        Returns the template format for this token type, in Handlebars format
        """

        # The Handlebars template for this token type.
        # This is a simplified version of the rendering template.
        # It can be used to render the value in a more complex way, if needed.
        # For example, it can include conditionals or loops.
        # The rendering template is used for the final output, while the Handlebars template is used for intermediate steps.
        return ""


#@debug_dataclass_creation
@dataclass
class PresentableBoolean(PresentableToken):
    content: Union[str, bool] 

    # Accept initial value through dataclass mechanism
    # as_entered : Union[str, bool]  = field(default="", init=False)

    # Class attributes that should be overridden by subclasses
    true_word = None
    false_word = None
    default_value = False
    is_explicit = True

    # Will be auto-populated in __post_init__
    true_words = None
    false_words = None
    token_pattern_str = None

    def shared_post_init(self):
        super().shared_post_init()
        # print("content on entry is ", self.content)
        # save as_entered; content will be set to the determined value, if one is found
        self.as_entered = self.content

        # Initialize word lists
        if self.true_word is None or self.false_word is None:
            raise NotImplementedError("Subclasses of PresentableBoolean must define true_word and false_word")

        # Initialize words lists if not already set
        # always accept true/yes, false/no
        if self.true_words is None:
            self.true_words = [self.true_word.lower(), "true", "yes"]
        if self.false_words is None:
            self.false_words = [self.false_word.lower(), "false", "no"]

        # Generate the token pattern
        all_words = [f'"{word}"i' for word in self.true_words + self.false_words]
        self.token_pattern_str = " | ".join(all_words)
        
        # above should be done for class definition?
        
        self.content = False    # establish False as default, in case of errors

        # make sure the argument is either a string or a boolean
        if not isinstance(self.as_entered, str) and not isinstance(self.as_entered, bool):
            raise_error(f"Expected string or boolean, got {type(self.content)} {self.content}")

        # Process the input value (now in as_entered)
        if isinstance(self.as_entered, str):
            # Normalize to lowercase for comparison
            normalized_value = self.as_entered.lower()
            if normalized_value in self.true_words:
                self.content = True
            elif normalized_value in self.false_words:
                self.content = False
            else:
                raise_error(
                    f"Invalid boolean value for {type(self).__name__}: {self.as_entered} - should be in:\n\t   {self.true_words}\n\tor {self.false_words}"
                )
                self.content = False
        else:
            # already know that as_entered is a bool. 
            self.content = self.as_entered

    def full_display(self):
        display =  super().full_display()   
        display["true_words"] = self.true_words
        display["false_words"] = self.false_words
        display["is_explicit"] = self.is_explicit
        return display

    def __str__(self):
        """String representation based on the value and settings."""
        val = self.content  # will be book for a constructed intance

        if val is None:
            return "NoValue"


        # If not explicit and value matches default, return empty string
        if not self.is_explicit and val == self.default_value:
            return ""

        # Otherwise return appropriate word
        return self.true_word if val else self.false_word

    @classmethod
    def token_pattern(cls) -> str:
        """Return the grammar pattern for this token."""
        instance = cls(
            False
        )  # Create a temporary instance to access instance attributes
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


#@debug_dataclass_creation
@dataclass
class IsOptional(PresentableBoolean):
    """Class representing a boolean token for "is required"."""


    # Class attributes - no need for __init__ or __post_init__ override
    true_word = "Optional"
    false_word = "Required"
    true_words = ["optional", "true", "sure", "yes"]
    false_words = ["required", "false", "no way"]
    default_value = False
    is_explicit = False

#@debug_dataclass_creation
@dataclass
class IsExclusive(PresentableBoolean):
    """
    Class representing a boolean token for "is exclusive".

    Attributes:
        value (bool): The boolean value.

    """


    true_word = "Exclusive"
    true_words = ["Exclusive"]

    false_word = "non Exclusive"
    false_words = ["non Exclusive", "nonexclusive"]
    default_value = True
    is_explicit = False


#@debug_dataclass_creation
@dataclass
class IsExhaustive(PresentableBoolean):
    """
    Class representing a boolean token for "is exhaustive".

    Attributes:
        value (bool): The boolean value.

    """


    true_word = "exhaustive"
    true_words = ["exhaustive"]

    false_word = "nonExhaustive"
    false_words = ["nonExhaustive"]
    default_value = True
    is_explicit = False

#@debug_dataclass_creation
@dataclass
class AsValue(PresentableBoolean):
    """
    Class representing a boolean token for whether
    a class is Reference or Value

    Attributes:
        value (bool): The boolean value.

    """


    true_word = "reference"
    true_words = ["reference"]
    false_word = "value"
    false_words = ["value"]
    default_value = True
    is_explicit = False


#@debug_dataclass_creation
import emoji
@dataclass
class Emoji(PresentableToken):
    as_entered: str = field(default="", init=True)

    token_pattern_str = r"/\d+(.*?)[\u263a-\U0001f645]/"
    # regex = re.compile(r'\d+(.*?)[\u263a-\U0001f645]')

    def shared_post_init(self):
        super().shared_post_init()

        self.shortcode = self.as_entered
        self.symbol = self.as_entered
        
        if self.as_entered.startswith(":"):
            self.symbol = emoji.emojize(self.shortcode)
        else:
            self.shortcode = emoji.demojize(self.symbol)


    @classmethod
    def token_pattern(cls) -> str:
        return cls.token_pattern_str
    
    def value(self):
        return self.input

    def rendering_template(self) -> PomTemplate:
        return PomTemplate("{value}")

    def handlebars_template(self) -> str:
        return "{{value}}"

    def as_shortcode(self):
        return self.shortcode
    
    
    def as_symbol(self):
        return self.symbol

    def __str__(self):
        if self.symbol:
            return self.symbol
        return "NoEmojiSupplied"
    
    def full_display(self):
        display =  super().full_display()
        display['shortcode'] = self.shortcode
        display['symbol'] = self.symbol
        return display