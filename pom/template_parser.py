# template_parser.py
from lark import Lark, Transformer, Token, Tree
from typing import List, Dict, Any, Optional, Set


class TemplateParser:
    """
    Parser for template strings with fields and conditionals.
    Converts them to various formats like Handlebars.
    """

    def __init__(self):
        # Define the grammar for parsing templates
        self.grammar = r"""
            ?start: template
            
            template: (field | conditional | text)*
            
            field: "{" NAME "}"
            conditional: "{?" template "}"
            text: /[^{]+/ | "{" /[^{}?]/
            
            NAME: /[a-zA-Z0-9_-]+/
            
            %import common.WS
        """

        # Create the parser with explicit error handling
        self.parser = Lark(self.grammar, parser="lalr", propagate_positions=True)

    def parse(self, template_str):
        """Parse a template string into a parse tree."""
        if not template_str:
            # Special case for empty templates
            return None
        try:
            return self.parser.parse(template_str)
        except Exception as e:
            print(f"Error parsing template: {template_str}")
            print(f"Error: {e}")
            # Return a minimal valid tree for empty or invalid templates
            return Tree("template", [])

    def to_handlebars(self, template_str):
        """Convert a template string to Handlebars format."""
        if not template_str:
            return ""

        try:
            tree = self.parse(template_str)
            if tree is None:
                return ""

            transformer = HandlebarsTransformer()
            result = transformer.transform(tree)
            return result
        except Exception as e:
            print(f"Error converting to handlebars: {e}")
            # Fallback to simple string replacement
            import re

            # Convert {field} to {{field}}
            result = re.sub(r"\{([^?{}]+)\}", r"{{\1}}", template_str)
            # Convert {? ... } to {{#if ...}}...{{/if}}
            result = re.sub(
                r"\{\?\s*(.*?)\}",
                lambda m: self._handle_conditional(m.group(1)),
                result,
            )
            return result

    def _handle_conditional(self, content):
        """Simple handler for conditionals in fallback mode."""
        import re

        # Find the first field in the content
        fields = re.findall(r"{{([^{}]+)}}", content)
        if fields:
            # Avoid f-string with multiple braces - use string formatting instead
            return "{{#if {}}}{}{{/if}}".format(fields[0], content)
        return content

    def to_grammar_rule(self, template_str, class_name):
        """Convert a template string to a grammar rule format."""
        if not template_str:
            return ""

        try:
            tree = self.parse(template_str)
            if tree is None:
                return ""

            transformer = GrammarRuleTransformer(class_name)
            return transformer.transform(tree)
        except Exception as e:
            print(f"Error converting to grammar rule: {e}")
            # Fallback to regex-based processing
            return self._fallback_grammar_rule(template_str, class_name)

    def _fallback_grammar_rule(self, template_str, class_name):
        """Fallback grammar rule generator using regex."""
        from utils.class_casing import LowerCamel
        import re
        from pom.class_field_type import field_terminals, punctuation_terminals
        from pom_config import named_pmarks, pmark_named

        # Replace field references
        def field_replacement(match):
            field_name = match.group(1)
            return f"{class_name}_{LowerCamel(field_name)}_value"

        # First handle conditionals (to avoid nested replacements)
        parts = []
        i = 0
        in_conditional = False
        conditional_start = 0

        while i < len(template_str):
            if template_str[i : i + 2] == "{?" and not in_conditional:
                # Start of conditional
                if i > 0:
                    # Add text before conditional
                    parts.append(self._process_text(template_str[0:i], class_name))

                in_conditional = True
                conditional_start = i + 2
                i += 2
            elif template_str[i] == "}" and in_conditional:
                # End of conditional
                conditional_content = template_str[conditional_start:i]
                # Process the conditional content recursively
                processed = self._fallback_grammar_rule(conditional_content, class_name)
                parts.append(f"[{processed}]")

                in_conditional = False
                template_str = template_str[i + 1 :]
                i = 0
            else:
                i += 1

        # Process any remaining text
        if not in_conditional and template_str:
            # Replace field references
            result = re.sub(r"\{([^?{}]+)\}", field_replacement, template_str)

            # Process text segments
            parts.append(self._process_text(result, class_name))

        return " ".join(parts)

    def _process_text(self, text, class_name):
        """Process text segments in fallback mode."""
        from pom.class_field_type import field_terminals, punctuation_terminals
        from pom_config import named_pmarks, pmark_named

        # Skip if the text is already a field reference
        if text.startswith(class_name) and "_value" in text:
            return text

        # Process the text token by token
        tokens = []
        i = 0
        while i < len(text):
            if text[i] == "\n":
                tokens.append("NEWLINE")
                punctuation_terminals.add("NEWLINE")
                i += 1
                continue

            # Check for punctuation
            if text[i] in named_pmarks:
                term_name = named_pmarks[text[i]]
                punctuation_terminals.add(term_name)
                tokens.append(term_name)
                i += 1
                continue

            # Check for words
            if text[i].isalpha() or text[i] == "_":
                word = ""
                j = i
                while j < len(text) and (text[j].isalpha() or text[j] == "_"):
                    word += text[j]
                    j += 1

                if word in pmark_named:
                    term_name = word
                    punctuation_terminals.add(term_name)
                else:
                    term_name = word.upper()
                    field_terminals.add(term_name)

                tokens.append(term_name)
                i = j
                continue

            # Other characters
            if text[i].isalnum():
                term_name = text[i].upper()
                field_terminals.add(term_name)
                tokens.append(term_name)

            i += 1

        return " ".join(tokens) if tokens else ""

    def find_fields(self, template_str) -> Set[str]:
        """Find all field references in the template."""
        if not template_str:
            return set()

        # Use regex as a reliable fallback
        import re

        return set(re.findall(r"\{([^?{}]+)\}", template_str))


class HandlebarsTransformer(Transformer):
    """Transforms a template parse tree into Handlebars format."""

    def template(self, items):
        """Join all template pieces."""
        return "".join(item for item in items if item is not None)

    def field(self, items):
        """Convert field to Handlebars format."""
        # The token should be the name
        field_name = str(items[0].value) if items and hasattr(items[0], "value") else ""
        # Avoid f-string with multiple braces
        return "{{{}}}".format(field_name)

    def conditional(self, items):
        """Convert conditional to Handlebars format."""
        # The content should be the already transformed template
        content = items[0] if items else ""

        # Find the first field in the content
        import re

        fields = re.findall(r"{{([^#/][^{}]+?)}}", content)

        if fields:
            # Avoid f-string with multiple braces
            return "{{#if {}}}{}{{/if}}".format(fields[0], content)
        return content

    def text(self, items):
        """Pass through text unchanged."""
        return str(items[0].value) if items and hasattr(items[0], "value") else ""


class GrammarRuleTransformer(Transformer):
    """Transforms a template parse tree into a grammar rule format."""

    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name

    def template(self, items):
        """Join all template pieces with spaces."""
        filtered_items = [item for item in items if item is not None and item.strip()]
        return " ".join(filtered_items)

    def field(self, items):
        """Convert field to grammar rule reference."""
        from utils.class_casing import LowerCamel

        # The token should be the name
        field_name = str(items[0].value) if items and hasattr(items[0], "value") else ""
        if field_name:
            return f"{self.class_name}_{LowerCamel(field_name)}_value"
        return ""

    def conditional(self, items):
        """Convert conditional to optional sequence."""
        # The content should be the already transformed template
        content = items[0] if items else ""
        if content:
            return f"[{content}]"
        return ""

    def text(self, items):
        """Convert text to grammar tokens."""
        from pom.class_field_type import field_terminals, punctuation_terminals
        from pom_config import named_pmarks, pmark_named

        # Extract the text
        text = str(items[0].value) if items and hasattr(items[0], "value") else ""
        if not text or text.isspace():
            return None

        # Process the text token by token
        tokens = []
        i = 0
        while i < len(text):
            if text[i] == "\n":
                tokens.append("NEWLINE")
                punctuation_terminals.add("NEWLINE")
                i += 1
                continue

            # Check for punctuation
            if text[i] in named_pmarks:
                term_name = named_pmarks[text[i]]
                punctuation_terminals.add(term_name)
                tokens.append(term_name)
                i += 1
                continue

            # Check for words
            if text[i].isalpha() or text[i] == "_":
                word = ""
                j = i
                while j < len(text) and (text[j].isalpha() or text[j] == "_"):
                    word += text[j]
                    j += 1

                if word in pmark_named:
                    term_name = word
                    punctuation_terminals.add(term_name)
                else:
                    term_name = word.upper()
                    field_terminals.add(term_name)

                tokens.append(term_name)
                i = j
                continue

            # Other characters
            if text[i].isalnum():
                term_name = text[i].upper()
                field_terminals.add(term_name)
                tokens.append(term_name)

            i += 1

        return " ".join(tokens) if tokens else None
