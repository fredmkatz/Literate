# Presentable Model Grammar Generator Specification

## 1. Overview

This specification outlines the implementation of a grammar generator and visitor system for Presentable Object Models. The system will automatically create Lark grammars from dataclass definitions, enabling flexible parsing and construction of object models from textual representations.

The implementation will consist of three main components:
1. **Configuration System** - Manages format templates and grammar settings
2. **Grammar Generator** - Creates Lark grammar rules from dataclass definitions
3. **Model Visitor** - Processes parse trees to build object models

The code should be extensively commented, with clear references to this specification to explain implementation details.

## 2. Project Structure

```
presentable/
├── pom_config.py          # Configuration management (using confuse)
├── pom_grammar_generator.py  # Grammar generation
├── pom_visitor.py         # Parse tree visitor
├── pom_diagnostics.py     # Diagnostic system
├── pom_utils.py           # Utility functions
└── formats/               # Default format configurations
    ├── default_format.yaml
    ├── json_format.yaml
    ├── yaml_format.yaml
    └── markdown_format.yaml
```

## 3. Configuration System

### 3.1 Configuration Management with Confuse

The configuration system will use the Confuse library to handle YAML configuration files with appropriate cascading and overrides.

```python
# pom_config.py
import confuse
import os
from typing import Dict, Any, Optional, List

class PomConfig:
    """Configuration manager for the Presentable Object Model (POM) tools."""
    
    def __init__(self, app_name: str = 'pom'):
        """
        Initialize the configuration system.
        
        Args:
            app_name: Application name for config directories
        """
        # Initialize confuse Configuration
        self.config = confuse.Configuration(app_name)
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration values."""
        # Default values for grammar generation
        self.config.set_defaults({
            'field_clause_template': '{field_name}: {field_value}',
            'list_format': {
                'opener': '[',
                'closer': ']',
                'separator': ',',
                'whitespace': True
            },
            'terminals': {
                'string_format': '"[^"]*"',
                'boolean_format': 'true|false'
            }
        })
    
    def load_format(self, format_name: Optional[str] = None) -> None:
        """
        Load a specific format configuration.
        
        Args:
            format_name: Name of the format to load (json, yaml, etc.)
        """
        if not format_name:
            return
            
        # Try to load the specified format
        try:
            self.config.add(confuse.ConfigSource.of_filename(
                f"{format_name}_format.yaml"))
        except confuse.ConfigError:
            print(f"Warning: Format '{format_name}' not found")
    
    def load_model_metadata(self, model_name: str) -> None:
        """
        Load model-specific metadata.
        
        Args:
            model_name: Name of the model to load metadata for
        """
        # Try to find and load model metadata
        try:
            self.config.add(confuse.ConfigSource.of_filename(
                f"{model_name}_grammar.yaml"))
        except confuse.ConfigError:
            pass
    
    def set_profile(self, profile: str) -> None:
        """
        Activate a specific configuration profile.
        
        Args:
            profile: Name of the profile to activate
        """
        # Set profile environment variable to enable profile-specific configs
        os.environ['POM_PROFILE'] = profile
        
        # Reload configuration to pick up profile-specific settings
        self.config.clear()
        self._load_defaults()
    
    def override(self, overrides: Dict[str, Any]) -> None:
        """
        Apply programmatic overrides to the configuration.
        
        Args:
            overrides: Dictionary of values to override
        """
        self.config.set(overrides)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (dot-separated for nested values)
            default: Default value if key is not found
            
        Returns:
            Configuration value
        """
        try:
            value = self.config[key].get()
            return value
        except confuse.NotFoundError:
            return default
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the complete configuration dictionary.
        
        Returns:
            Dictionary with all configuration values
        """
        return self.config.get()
    
    def get_class_metadata(self, class_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dictionary of class metadata
        """
        try:
            return self.config['classes'][class_name].get()
        except confuse.NotFoundError:
            return {}
    
    def get_field_metadata(self, class_name: str, field_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific field, considering both class-specific
        and global field specifications.
        
        Args:
            class_name: Name of the class
            field_name: Name of the field
            
        Returns:
            Dictionary of field metadata
        """
        # Start with any global field specifications
        metadata = {}
        try:
            metadata.update(self.config['fields'][f".{field_name}"].get())
        except confuse.NotFoundError:
            pass
        
        # Override with class-specific field metadata if available
        try:
            metadata.update(
                self.config['classes'][class_name]['fields'][field_name].get())
        except confuse.NotFoundError:
            pass
            
        return metadata
```

### 3.2 External Metadata Format

The YAML format for external metadata will allow specifying presentation templates and field properties:

```yaml
# example_grammar.yaml
classes:
  # Class-level metadata
  Class:
    presentable_header: "_ **{name}**{{#if one_liner}} - {one_liner}{{/if}}"
    presentable_template: "{name}"
    
    # Field-specific metadata
    fields:
      attributes:
        list_format:
          opener: "{"
          closer: "}"
          separator: ","
      is_value_type:
        presentable_true: "ValueType"
        presentable_false: "ReferenceType"
        explicit: true

  # Another class with metadata
  Attribute:
    presentable_header: "- **{name}**{{#if one_liner}} - {one_liner}{{/if}} {data_type_clause}"
    
    fields:
      data_type_clause:
        required: false
      constraints:
        list_format:
          opener: "["
          closer: "]"
          separator: ","

# Global field specifications that apply to any class with these fields
fields:
  ".name":  # The dot prefix indicates a global field specification
    required: true
  
  ".one_liner":
    required: false
```

## 4. Grammar Generator

### 4.1 Base Grammar Generator

The `PomGrammarGenerator` class will inherit from the `Grammar` class and handle generating Lark grammar rules from dataclass definitions:

```python
# pom_grammar_generator.py
import inspect
import re
from dataclasses import is_dataclass, fields
from typing import Dict, List, Set, Any, Optional, Type, Union, get_type_hints
import json

from class_grammar import Grammar  # Import the base Grammar class

class PomGrammarGenerator(Grammar):
    """
    Grammar generator for Presentable Object Models.
    Creates Lark grammar from dataclass definitions.
    """
    
    def __init__(self, config, name="PresentableGrammar"):
        """
        Initialize the grammar generator.
        
        Args:
            config: Configuration for grammar generation
            name: Name of the grammar
        """
        super().__init__(name)
        self.config = config
        self.processed_classes = set()
        self.class_hierarchy = {}
        self.rules = []
        self.terminals = set()
        self.rule_names = set()
        
    def generate_grammar(self, model_module) -> str:
        """
        Generate a complete Lark grammar for the given model module.
        
        Args:
            model_module: Module containing dataclass definitions
            
        Returns:
            Complete Lark grammar as a string
        """
        # Reset state
        self.processed_classes.clear()
        self.class_hierarchy.clear()
        self.rules.clear()
        self.terminals.clear()
        self.rule_names.clear()
        
        # Analyze the model
        self._analyze_model(model_module)
        
        # Generate grammar components
        grammar_text = self._generate_grammar_text()
        
        # Store the generated grammar
        self._lark_grammar = grammar_text
        
        return grammar_text
    
    def _analyze_model(self, model_module):
        """
        Analyze the model module to build class hierarchy.
        
        Args:
            model_module: Module containing dataclass definitions
        """
        # Find all dataclasses in the module
        classes = {}
        for name, obj in inspect.getmembers(model_module):
            if inspect.isclass(obj) and is_dataclass(obj):
                classes[name] = obj
                
        # Build inheritance hierarchy
        for name, cls in classes.items():
            bases = [base for base in cls.__bases__ 
                    if base.__name__ in classes and base.__name__ != 'object']
            self.class_hierarchy[name] = {
                'class': cls,
                'bases': [base.__name__ for base in bases],
                'subtypes': []
            }
            
        # Fill in subtype information
        for name, info in self.class_hierarchy.items():
            for base_name in info['bases']:
                if base_name in self.class_hierarchy:
                    self.class_hierarchy[base_name]['subtypes'].append(name)
        
        # Now generate rules in dependency order
        self._generate_rules_in_order(classes)
    
    def _generate_rules_in_order(self, classes):
        """
        Generate grammar rules in an order that respects dependencies.
        
        Args:
            classes: Dictionary of class name to class object
        """
        # Process parent classes before their children
        processed = set()
        
        def process_class(name):
            """Process a class and its dependencies recursively."""
            if name in processed:
                return
                
            # Process base classes first
            for base in self.class_hierarchy.get(name, {}).get('bases', []):
                process_class(base)
                
            # Now process this class
            if name in classes:
                self._generate_class_rules(name, classes[name])
                processed.add(name)
        
        # Process all classes in original order (respecting dependencies)
        for name in self.class_hierarchy:
            process_class(name)
```

### 4.2 Rule Generation

The grammar generator will generate rules for classes, fields, and values:
