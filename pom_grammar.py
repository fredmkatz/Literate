from dataclasses import is_dataclass, fields
from typing import Any, Dict, List, Optional, Type
from pathlib import Path
import os
import sys
import importlib.util
import json
import yaml

from class_grammar import Grammar, ParseResult

class PresentableGrammar(Grammar):
    """
    A Grammar implementation for Presentable Model parsing and generation.
    
    This class provides a simplified interface to the underlying Presentable
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
        super().__init__(f"Presentable_{model_name}")
        
        self.model_name = model_name
        self.format_name = format_name
        self.custom_config = config
        
        # Find model directory and files
        self.model_dir = self._find_model_dir(model_name)
        self.model_module = self._load_model_module()
        
        # Components (loaded on demand)
        self._config = None
        self._grammar_generator = None
        self._parser = None
        self._visitor = None
        
        # Initialize the grammar
        self._initialize_grammar()
    
    def _find_model_dir(self, model_name):
        """Find the directory containing the model."""
        # Try standard locations
        base_paths = [
            # Current directory
            os.path.abspath('.'),
            # Presentable/models directory
            os.path.join(os.path.dirname(__file__), 'models'),
            # Parent directory (if in Presentable subdir)
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        ]
        
        for base in base_paths:
            model_dir = os.path.join(base, model_name)
            if os.path.isdir(model_dir):
                return model_dir
        
        # If not found, default to a subdirectory of current dir
        model_dir = os.path.join(os.path.abspath('.'), model_name)
        os.makedirs(model_dir, exist_ok=True)
        return model_dir
    
    def _load_model_module(self):
        """Load the model module from file."""
        # Look for model file
        model_file = os.path.join(self.model_dir, f"{self.model_name}.py")
        
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"Model file not found: {model_file}")
        
        # Load the module from file
        spec = importlib.util.spec_from_file_location(self.model_name, model_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return module
    
    def _initialize_grammar(self):
        """Initialize the grammar components."""
        # Import necessary components
        from pom_config import PomConfig
        from pom_grammar_generator import PomGrammarGenerator
        
        # Create configuration
        self._config = PomConfig()
        
        # Load format if specified
        if self.format_name:
            self._config.load_format(self.format_name)
        
        # Load model metadata if available
        metadata_file = os.path.join(self.model_dir, f"{self.model_name}_grammar.yaml")
        if os.path.exists(metadata_file):
            self._config.load_from_file(metadata_file)
        
        # Apply custom config if provided
        if self.custom_config:
            self._config.update(self.custom_config)
        
        # Create grammar generator and generate grammar
        self._grammar_generator = PomGrammarGenerator(self._config, f"Presentable_{self.model_name}")
        
        # Generate the grammar
        self._lark_grammar = self._grammar_generator.generate_grammar(self.model_module)
        
        # Save the grammar to file
        self.save_rules()
        
        # Also generate and save the templates
        self.save_templates()
    
    def save_rules(self):
        """Save grammar rules to a file."""
        rules_file = os.path.join(self.model_dir, f"{self.model_name}_grammar.lark")
        with open(rules_file, 'w', encoding="utf-8") as f:
            f.write(self._lark_grammar)
        
        return rules_file
    
    def save_templates(self):
        """Save grammar templates to a file."""
        # Get templates from grammar generator
        templates = self._grammar_generator.get_templates()
        
        # Save to file
        templates_file = os.path.join(self.model_dir, f"{self.model_name}_templates.hbs")
        with open(templates_file, 'w', encoding="utf-8") as f:
            json.dump(templates, f, indent=2)
        
        return templates_file
    
    def save_visitor(self):
        """Generate and save visitor code if needed."""
        # This would generate a custom visitor if needed
        visitor_file = os.path.join(self.model_dir, f"{self.model_name}_visitor.py")
        
        # For now, we don't generate custom visitors
        # We use the generic PomVisitor
        
        return visitor_file
    
    def _ensure_parser(self):
        """Ensure parser is initialized."""
        if self._parser is None:
            from pom_parser import PomParser
            self._parser = PomParser(self.model_module, self._config, self.format_name)
    
    def parse(self, text, start_rule=None) -> ParseResult:
        """
        Parse input text and return a ParseResult.
        
        Args:
            text: Input text to parse
            start_rule: Optional start rule name
            
        Returns:
            ParseResult object
        """
        self._ensure_parser()
        
        # Parse the input
        model_obj, success = self._parser.parse(text, start_rule)
        
        # Create parse result
        result = ParseResult()
        result.parse_tree = self._parser.parse_tree if hasattr(self._parser, 'parse_tree') else None
        result.pretty_tree = str(result.parse_tree) if result.parse_tree else ""
        result.errors = self._parser.diagnostics.get_all() if success else []
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
        # Import the renderer
        from pom_renderer import PomRenderer
        
        # Create renderer if needed
        if not hasattr(self, '_renderer'):
            self._renderer = PomRenderer(self.model_module, self._config, self.format_name)
        
        # Render the object
        return self._renderer.render(obj)
    
    def path_for(self, ppass: str, subdir: str, name: str = None, extension: str = "") -> Path:
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