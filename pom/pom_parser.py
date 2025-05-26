"""
Parser for Presentable Object Models.

This module provides the parser service that integrates with Lark parser,
and visitor pattern to create model objects from text input.
"""

from typing import Optional, Any, Dict, Tuple, Union
from utils.util_flogging import flogger

try:
    from lark import Lark, ParseError, Tree
    from lark.exceptions import UnexpectedToken, UnexpectedCharacters
except ImportError:
    # Create dummy classes if lark is not available
    class Lark:
        """Dummy Lark class."""

        def __init__(self, *args, **kwargs):
            pass

        def parse(self, *args, **kwargs):
            raise ImportError("lark-parser is not installed")

    class ParseError(Exception):
        """Dummy ParseError class."""

        pass

    class UnexpectedToken(ParseError):
        """Dummy UnexpectedToken class."""

        pass

    class UnexpectedCharacters(ParseError):
        """Dummy UnexpectedCharacters class."""

        pass

    class Tree:
        """Dummy Tree class."""

        pass


from pom_visitor import PomVisitor
from pom_diagnostics import (
    DiagnosticRegistry,
    Diagnostic,
    DiagnosticSeverity,
    SourceLocation,
)


class PomParser:
    """
    Parser for Presentable Object Models.

    This class provides parsing services using Lark parser and
    passes parsed trees to the visitor for model construction.
    """

    def __init__(self, model_module, grammar, config_params):
        """
        Initialize the parser.

        Args:
            model_module: Module containing model classes
            grammar: Lark grammar string
            config_params: parameters to control parsing
        """
        self.model_module = model_module
        self.config_params = config_params

        self.grammar = grammar

        # Initialize diagnostics
        self.diagnostics = DiagnosticRegistry()

        # Create the parser (deferred until needed)
        self._parser = None
        self.parse_tree = None

        flogger.info("PomParser initialized")

    def _get_parser(self, start_rule=None):
        """
        Get the parser, creating it if necessary.

        Args:
            start_rule: Optional start rule for the parser

        Returns:
            Lark parser
        """
        create_new = self._parser is None or start_rule is not None
        lark_config = self.config_params.get("lark", {})

        if create_new:
            # Create parser with appropriate configuration
            parser_settings = {
                "start": start_rule or lark_config.get("start", "start"),
                "parser": lark_config.get("parser", "earley"),  # Most flexible parser
                "debug": True,  # lark_config.get("debug", False),
                "ambiguity": (
                    "explicit"
                    if lark_config.get("ambiguity", "resolve") == "explicit"
                    else "resolve"
                ),
            }

            try:
                flogger.infof(
                    f"Creating new Lark parser with settings: {parser_settings}"
                )
                self._parser = Lark(self.grammar, **parser_settings)
            except Exception as e:
                flogger.errorf(f"Error creating parser: {e}")
                self.diagnostics.add_error(
                    f"Error creating parser: {str(e)}", code="PARSER_CREATE_ERROR"
                )
                raise

        return self._parser

    def parse(self, input_text, start_rule=None, file_path=None):
        """
        Parse input text to create a model object.

        Args:
            input_text: Input text to parse
            start_rule: Optional start rule for the parser
            file_path: Optional file path for error reporting

        Returns:
            Tuple of (model_object, success, parse_tree)
        """
        # Clear previous diagnostics
        self.diagnostics = DiagnosticRegistry()
        self.parse_tree = None

        try:
            # Get the parser
            parser = self._get_parser(start_rule)

            # Parse the input
            flogger.info("Parsing input text")
            self.parse_tree = parser.parse(input_text)
            flogger.info("Input parsed successfully")

            # Create and configure visitor
            visitor = PomVisitor(self.model_module, self.diagnostics)

            # Visit the parse tree to build the model
            flogger.info("Visiting parse tree to build model object")
            model = visitor.visit(self.parse_tree)
            flogger.infof(
                f"Created model object: {type(model).__name__ if model else 'None'}"
            )

            return model, True, self.parse_tree

        except UnexpectedToken as e:
            flogger.warning(f"Unexpected token during parsing: {e}")
            # Handle token-based parsing errors
            self._handle_unexpected_token(e, input_text, file_path)
            return None, False, None

        except UnexpectedCharacters as e:
            flogger.warning(f"Unexpected character during parsing: {e}")
            # Handle character-based parsing errors
            self._handle_unexpected_character(e, input_text, file_path)
            return None, False, None

        except Exception as e:
            flogger.error(f"Error during parsing: {e}")
            # Handle other errors
            self._handle_generic_error(e, input_text, file_path)
            return None, False, None

    def _handle_unexpected_token(self, error, input_text, file_path=None):
        """
        Handle an unexpected token error by creating appropriate diagnostics.

        Args:
            error: The UnexpectedToken exception
            input_text: The input text that was being parsed
            file_path: Optional file path for error reporting
        """
        location = SourceLocation(
            line=error.line, column=error.column, file_path=file_path
        )

        # Build more helpful error message
        expected = ", ".join(str(x) for x in error.expected)
        found = error.token

        message = f"Unexpected token: expected {expected}, found {found}"

        # Get context lines for better error reporting
        context = self._get_error_context(input_text, error)

        self.diagnostics.add_error(
            f"{message}\n{context}", location, code="SYNTAX_ERROR"
        )

    def _handle_unexpected_character(self, error, input_text, file_path=None):
        """
        Handle an unexpected character error by creating appropriate diagnostics.

        Args:
            error: The UnexpectedCharacters exception
            input_text: The input text that was being parsed
            file_path: Optional file path for error reporting
        """
        location = SourceLocation(
            line=error.line, column=error.column, file_path=file_path
        )

        # Build more helpful error message
        expected = (
            ", ".join(str(x) for x in error.allowed)
            if hasattr(error, "allowed")
            else "valid token"
        )
        found = error.char

        message = f"Unexpected character: expected {expected}, found '{found}'"

        # Get context lines for better error reporting
        context = self._get_error_context(input_text, error)

        self.diagnostics.add_error(
            f"{message}\n{context}", location, code="SYNTAX_ERROR"
        )

    def _handle_generic_error(self, error, input_text, file_path=None):
        """
        Handle a generic error by creating appropriate diagnostics.

        Args:
            error: The exception that occurred
            input_text: The input text that was being parsed
            file_path: Optional file path for error reporting
        """
        # Get location if available
        location = None
        if hasattr(error, "line") and hasattr(error, "column"):
            location = SourceLocation(
                line=error.line, column=error.column, file_path=file_path
            )

            # Get context lines for better error reporting
            context = self._get_error_context(input_text, error)

            self.diagnostics.add_error(
                f"Error during parsing: {str(error)}\n{context}",
                location,
                code="PARSE_ERROR",
            )
        else:
            # Generic error without location
            self.diagnostics.add_error(
                f"Error during parsing: {str(error)}", code="PARSE_ERROR"
            )

    def _get_error_context(self, input_text, error, context_lines=2):
        """
        Get context lines around an error for better error reporting.

        Args:
            input_text: Input text
            error: Error with line/column attributes
            context_lines: Number of context lines to include

        Returns:
            String with context lines
        """
        if not hasattr(error, "line"):
            return ""

        # Split input into lines
        lines = input_text.splitlines()
        if not lines:
            return ""

        # Calculate line range
        start_line = max(0, error.line - 1 - context_lines)
        end_line = min(len(lines) - 1, error.line - 1 + context_lines)

        # Build context
        context = []
        for i in range(start_line, end_line + 1):
            line_num = i + 1  # 1-based line numbers
            prefix = "-> " if line_num == error.line else "   "
            context.append(f"{prefix}{line_num}: {lines[i]}")

            # Add error marker
            if line_num == error.line and hasattr(error, "column"):
                column = error.column
                # Skip any leading whitespace matching the line
                marker_indent = len(lines[i]) - len(lines[i].lstrip())
                marker_column = max(0, column - marker_indent)
                context.append("   " + " " * marker_column + "^")

        return "\n".join(context)

    def parse_file(self, file_path, start_rule=None):
        """
        Parse a file to create a model object.

        Args:
            file_path: Path to the file to parse
            start_rule: Optional start rule for the parser

        Returns:
            Tuple of (model_object, success)
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                input_text = f.read()

            return self.parse(input_text, start_rule, file_path)

        except IOError as e:
            self.diagnostics.add_error(
                f"Error reading file '{file_path}': {str(e)}", code="FILE_ERROR"
            )
            return None, False

    def save_grammar(self, file_path):
        """
        Save the generated grammar to a file.

        Args:
            file_path: Path to save the grammar to

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.grammar)

            return True

        except IOError as e:
            self.diagnostics.add_error(
                f"Error writing grammar to '{file_path}': {str(e)}", code="FILE_ERROR"
            )
            return False
