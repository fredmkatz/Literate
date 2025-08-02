"""
Main entry point for the Presentable Object Model (POM) grammar system.

This module provides the PresentableGrammar class which serves as the primary
interface for users to parse, generate, and work with Presentable models.
"""

from dataclasses import is_dataclass, fields
from typing import Any, Dict, List, Optional, Type
from pathlib import Path
import os
import sys
import importlib.util
import json
import yaml

from pom.class_grammar import Grammar, ParseResult
from utils.util_flogging import flogger
from pom_config import PomConfig
from pom_grammar_generator import PomGrammarGenerator


# Add these imports at the top of pom_grammar.py
try:
    from lark.visitors import TraceRule
except ImportError:
    # Create dummy TraceRule if not available
    class TraceRule:
        def visit_topdown(self, tree):
            print("WARNING: TraceRule not available in your version of Lark")
            return tree


class PresentableGrammar(Grammar):
    """
    A Grammar implementation for Presentable Model parsing and generation.

    This class provides the main interface to the underlying Presentable
    system, handling model loading, grammar generation, parsing, and rendering.
    """

    def __init__(self, model_name, format_name=None, config=None):
        """
        Initialize a PresentableGrammar instance.

        Args:
            model_name: Name of the model (used to find model files)
            format_name: Optional format to use (default, json, yaml, etc.)
            config: Optional custom configuration
        """
        flogger.infof(
            f"Initializing PresentableGrammar with model_name={model_name}, format_name={format_name}"
        )
        super().__init__(f"Presentable_{model_name}")

        self.model_name = model_name
        self.format_name = format_name
        self.custom_config = config

        # Find model directory and files
        self.model_dir = self._find_model_dir(model_name)
        flogger.infof(f"Found model directory: {self.model_dir}")

        self.model_module = self._load_model_module()
        flogger.infof(
            f"Loaded model module: {self.model_module.__name__ if hasattr(self.model_module, '__name__') else 'unnamed'}"
        )

        # Create central configuration
        self.pom_config = PomConfig(
            model_name=self.model_name,
            format_name=self.format_name,
            config_dict=self.custom_config,
        )

        # Initialize components (lazily loaded)
        self._grammar_generator = None
        self._parser = None
        self._visitor = None
        self._renderer = None

        # Initialize the grammar
        self._initialize_grammar()
        flogger.info("PresentableGrammar initialization complete")

    def _find_model_dir(self, model_name):
        """
        Find the directory containing the model.

        Args:
            model_name: Name of the model

        Returns:
            Path to the model directory
        """
        # Try standard locations
        base_paths = [
            # Current directory
            os.path.abspath("."),
            # Presentable/models directory
            os.path.join(os.path.dirname(__file__), "models"),
            # Parent directory (if in Presentable subdir)
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "models"),
        ]

        for base in base_paths:
            model_dir = os.path.join(base, model_name)
            if os.path.isdir(model_dir):
                return model_dir

        # If not found, default to a subdirectory of current dir
        model_dir = os.path.join(os.path.abspath("."), model_name)
        os.makedirs(model_dir, exist_ok=True)
        return model_dir

    def _load_model_module(self):
        """
        Load the model module from file.

        Returns:
            Loaded model module
        """
        # Look for model file
        model_file = os.path.join(self.model_dir, f"{self.model_name}.py")

        if not os.path.exists(model_file):
            raise FileNotFoundError(f"Model file not found: {model_file}")

        # Create an empty __init__.py file in the model directory if it doesn't exist
        init_file = os.path.join(self.model_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Auto-generated __init__.py for model package\n")

        # Add the parent directory to sys.path to make imports work
        parent_dir = os.path.dirname(self.model_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)

        # Load the module from file
        module_name = f"{os.path.basename(self.model_dir)}.{self.model_name}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, model_file)
            module = importlib.util.module_from_spec(spec)

            # Add to sys.modules before executing
            sys.modules[module_name] = module

            spec.loader.exec_module(module)
            return module
        except Exception as e:
            flogger.warning(f"Error loading model module: {e}")
            # Try an alternative method
            flogger.info("Trying alternative loading method...")
            try:
                with open(model_file, "r") as f:
                    code = f.read()
                # Create a new module dictionary
                module_dict = {}
                # Execute the code in this dictionary
                exec(code, module_dict)

                # Create a simple module-like object
                class SimpleModule:
                    pass

                module = SimpleModule()
                for key, value in module_dict.items():
                    if not key.startswith("__"):
                        setattr(module, key, value)
                return module
            except Exception as e2:
                flogger.error(f"Alternative loading also failed: {e2}")
                raise ImportError(f"Could not load model module: {e}, {e2}")

    def _initialize_grammar(self):
        """Initialize the grammar components."""
        # Create grammar generator and generate grammar
        self._grammar_generator = PomGrammarGenerator(
            self.pom_config, f"Presentable_{self.model_name}"
        )

        # Generate the grammar
        self._lark_grammar = self._grammar_generator.generate_grammar(
            self.model_module, model_name=self.model_name, format_name=self.format_name
        )

        from utils.util_lark_static import (
            find_rule_overlaps,
            find_terminal_conflicts,
        )

        find_terminal_conflicts(self._lark_grammar)
        find_rule_overlaps(self._lark_grammar)
        # Save the grammar to file
        self.save_rules()

        # Also generate and save the templates
        self.save_templates()

    def save_rules(self):
        """
        Save grammar rules to a file.

        Returns:
            Path to the saved rules file
        """
        rules_file = os.path.join(
            self.model_dir, f"{self.model_name}_{self.format_name}_grammar.lark"
        )
        with open(rules_file, "w", encoding="utf-8") as f:
            f.write(self._lark_grammar)

        flogger.infof(f"Saved grammar rules to {rules_file}")
        return rules_file

    def save_templates(self):
        """
        Save grammar templates to a file.

        Returns:
            Path to the saved templates file
        """
        # Get templates from grammar generator
        templates = self._grammar_generator.get_templates()

        # Save to file
        templates_file = os.path.join(
            self.model_dir, f"{self.model_name}_{self.format_name}_templates.hbs"
        )
        with open(templates_file, "w", encoding="utf-8") as f:
            for key, template in templates.items():
                f.write(f"{key}: {str(template)}\n")

        flogger.infof(f"Saved templates to {templates_file}")
        return templates_file

    def save_visitor(self):
        """
        Generate and save visitor code if needed.

        Returns:
            Path to the visitor file
        """
        # This would generate a custom visitor if needed
        visitor_file = os.path.join(self.model_dir, f"{self.model_name}_visitor.py")

        # For now, we don't generate custom visitors
        # We use the generic PomVisitor
        flogger.info("No custom visitor generated (using generic PomVisitor)")
        return visitor_file

    def print_token_stream(self, input_text):
        """Print the token stream generated by the lexer."""
        try:
            # Make sure parser is initialized
            if self._parser is None:
                from pom_parser import PomParser

                self._parser = PomParser(
                    model_module=self.model_module,
                    grammar=self._lark_grammar,
                    config_params=self.pom_config._config_params,
                )

            # Now get the tokens
            from lark import Lark, Token

            parser = self._parser._parser  # Access the Lark parser

            # Create a lexer just for tokenization
            lexer = parser.lexer
            tokens = list(lexer.lex(input_text))

            print("TOKEN STREAM:")
            for token in tokens:
                print(f"  {token.type}: '{token.value}'")
            return tokens
        except Exception as e:
            print(f"Error getting token stream: {e}")
            import traceback

            traceback.print_exc()
            return []

    def debug_tokens(self, input_text):
        """Debug token patterns and matching."""
        print("\n===== TOKEN DEBUGGING =====")

        try:
            from lark import Lark

            # Create a simple parser just for tokenization
            # Use a modified grammar with just terminals
            terminals_grammar = ""
            for line in self._lark_grammar.split("\n"):
                if (
                    line.strip().startswith("%ignore")
                    or ":" in line
                    and not line.strip().startswith("//")
                ):
                    if any(
                        token in line
                        for token in ["STRING", "NUMBER", "WHITESPACE", "IDENTIFIER"]
                    ):
                        terminals_grammar += line + "\n"

            terminals_grammar += "%ignore WHITESPACE\n"
            terminals_grammar += "start: STRING\n"  # Dummy rule to make it valid

            # Create lexer-only parser
            try:
                lexer_parser = Lark(terminals_grammar, parser="earley", lexer="basic")
                lexer = lexer_parser.parser.lexer

                print("\nTokenizing with grammar rules:")
                tokens = list(lexer.lex(input_text))

                for i, token in enumerate(tokens):
                    print(f"{i:3d}: {token.type:15s} '{token.value}'")

                return tokens
            except Exception as e:
                print(f"Error creating lexer: {e}")
        except Exception as e:
            print(f"Error in debug_tokens: {e}")
            import traceback

            traceback.print_exc()

        # Fall back to manual token debug
        return self._manual_token_debug(input_text)

    def _manual_token_debug(self, input_text):
        """Manual token debugging using regex patterns."""
        import re

        # Define basic token patterns
        patterns = [
            ("UNDERSCORE", r"_"),
            ("DASH", r"-"),
            ("COLON", r":"),
            ("NEWLINE", r"\n"),
            ("MARKED_TEXT", r"<<<.*?>>>"),
            ("UPPER_CAMEL", r"[A-Z][a-zA-Z0-9]*"),
            ("LOWER_CAMEL", r"[a-z][a-zA-Z0-9]*"),
            ("WHITESPACE", r"[ \t\r]+"),
            ("STRING", r'"[^"]*"'),
            ("IDENTIFIER", r"[a-zA-Z][a-zA-Z0-9_]*"),
        ]

        compiled_patterns = []
        for name, pattern in patterns:
            try:
                regex = re.compile(pattern)
                compiled_patterns.append((name, regex, pattern))
            except re.error as e:
                print(f"Error compiling regex for {name}: {e}")

        # Try matching
        position = 0
        line = 1
        col = 1
        tokens = []

        print("\nManual tokenization:")
        while position < len(input_text):
            matched = False

            # Skip whitespace
            if input_text[position : position + 1].isspace():
                if input_text[position] == "\n":
                    line += 1
                    col = 1
                else:
                    col += 1
                position += 1
                continue

            for name, regex, pattern in compiled_patterns:
                match = regex.match(input_text[position:])
                if match:
                    value = match.group(0)
                    tokens.append((name, value, line, col))
                    print(f"  Line {line}, Col {col}: {name} -> '{value}'")

                    # Update position and column
                    if name == "NEWLINE":
                        line += 1
                        col = 1
                    else:
                        col += len(value)
                    position += len(value)
                    matched = True
                    break

            if not matched:
                # No match found
                print(
                    f"  Line {line}, Col {col}: UNMATCHABLE -> '{input_text[position]}'"
                )
                col += 1
                position += 1

        return tokens

    def debug_with_trace(self, input_text, start_rule=None):
        """Use Lark's TraceRule to debug rule applications."""
        print("\n===== TRACING PARSE RULES =====")

        try:
            from lark import Lark

            # Create new parser with trace
            parser = Lark(
                self._lark_grammar, parser="earley", start=start_rule or "start"
            )

            # Parse with tracing
            try:
                tree = parser.parse(input_text)

                # Create a tracer and apply it
                tracer = TraceRule()
                tracer.visit_topdown(tree)

                return True, tree
            except Exception as e:
                print(f"Parse error during tracing: {e}")
                return False, None

        except Exception as e:
            print(f"Error in debug_with_trace: {e}")
            import traceback

            traceback.print_exc()
            return False, None

    def debug_incremental_parse(self, input_text):
        """Try to parse the input incrementally to identify failure points."""
        print("\n===== INCREMENTAL PARSING =====")

        lines = input_text.split("\n")
        last_success = 0

        for i in range(len(lines)):
            # Try with increasing number of lines
            test_input = "\n".join(lines[: i + 1]) + "\n\n"
            if not test_input.strip():
                continue

            print(f"\nTrying to parse lines 1-{i+1}:")
            print(f"Input: {test_input}")

            try:
                from lark import Lark
                from utils.util_lark import pretty_print_parse_tree

                result = self.parse(test_input)
                if not result:
                    print("---- FAILURE! --- ")
                elif str(result.parse_tree) == "None":
                    print(" Softer FAILURE - parse tree is 'None' ")
                else:
                    print("  SUCCESS!")

                    print("---- Prettier Parse Tree ----")
                    print(
                        pretty_print_parse_tree(
                            result.parse_tree, max_text_length=30, text_column_width=35
                        )
                    )
                    print("-----------------------------")

                    last_success = i + 1
            except Exception as e:
                print(f"  FAILED with EXCEPTION: {e}")

                # Try with common start rules if main parse fails
                for rule in ["class_", "attribute", "data_type"]:
                    try:
                        print(f"  Trying with start rule '{rule}'...")
                        result = self.parse(test_input)
                        print(f"  SUCCESS with start rule '{rule}'!")
                        break
                    except Exception as e:
                        pass

        print(f"\nSuccessfully parsed up to line {last_success} out of {len(lines)}")

        # If we failed before the end, show the problem area
        if last_success < len(lines):
            print("\nProblem area may be around:")
            start = max(0, last_success - 1)
            end = min(len(lines), last_success + 2)
            for i in range(start, end):
                prefix = ">>>" if i == last_success else "   "
                print(f"{prefix} Line {i+1}: {lines[i]}")

        return last_success

    def parse(self, text, start_rule=None) -> ParseResult:
        """
        Parse input text and return a ParseResult.

        Args:
            text: Input text to parse
            start_rule: Optional start rule name

        Returns:
            ParseResult object
        """
        # Initialize parser if needed
        if self._parser is None:
            from pom_parser import PomParser

            self._parser = PomParser(
                model_module=self.model_module,
                grammar=self._lark_grammar,
                config_params=self.pom_config._config_params,
            )

        # Parse the input
        flogger.infof(f"Parsing input text (length: {len(text)})")
        model_obj, success, parse_tree = self._parser.parse(text, start_rule)

        # Create parse result
        result = ParseResult()
        result.parse_tree = parse_tree
        result.pretty_tree = str(parse_tree) if parse_tree else ""
        result.pretty_errors = ""

        # Get diagnostics
        if not success:
            result.errors = self._parser.diagnostics.get_all()
            result.pretty_errors = "\n".join(str(error) for error in result.errors)
        else:
            result.errors = []

        result.model_obj = model_obj

        return result

    def createObject(self, parse_result: ParseResult) -> Any:
        """
        Create an object from a parse result.

        Args:
            parse_result: ParseResult from parsing

        Returns:
            Created model object
        """
        # The object is already created during parsing in our implementation
        return parse_result.model_obj

    def render(self, obj: Any) -> str:
        """
        Render a model object as text.

        Args:
            obj: Model object to render

        Returns:
            Rendered text
        """
        # Initialize renderer if needed
        if self._renderer is None:
            # Import lazily to avoid circular imports
            from pom_renderer import PomRenderer

            self._renderer = PomRenderer(self.model_module, self.pom_config)

        # Render the object
        flogger.infof(f"Rendering object of type {type(obj).__name__}")
        return self._renderer.render(obj)

    def path_for(
        self, ppass: str, subdir: str, name: str = None, extension: str = ""
    ) -> Path:
        """
        Get a path for a file related to this grammar.

        Args:
            ppass: Pass name (e.g., 'grammar', 'templates')
            subdir: Subdirectory name
            name: Optional name (defaults to model name)
            extension: Optional file extension

        Returns:
            Path object
        """
        name = name or self.model_name
        file_name = f"{name}{extension}"

        # Create directory if needed
        dir_path = os.path.join(self.model_dir, ppass, subdir)
        os.makedirs(dir_path, exist_ok=True)

        return Path(os.path.join(dir_path, file_name))
