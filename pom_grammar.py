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

from class_grammar import Grammar, ParseResult
from utils_pom.util_flogging import flogger
from pom_config import PomConfig
from pom_grammar_generator import PomGrammarGenerator

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
        flogger.infof(f"Loaded model module: {self.model_module.__name__ if hasattr(self.model_module, '__name__') else 'unnamed'}")

        # Create central configuration
        self.pom_config = PomConfig(
            model_name=self.model_name,
            format_name=self.format_name,
            config_dict=self.custom_config
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
        self._lark_grammar = self._grammar_generator.generate_grammar(self.model_module, model_name=self.model_name, format_name=self.format_name)

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
        rules_file = os.path.join(self.model_dir, f"{self.model_name}_{self.format_name}_grammar.lark")
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
                config_params = self.pom_config._config_params
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
            self._renderer = PomRenderer(
                self.model_module, self.pom_config
            )

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
