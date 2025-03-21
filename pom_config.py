"""
Configuration system for Presentable Object Model (POM) package.

This module provides configuration management for the POM package,
including support for format templates and model metadata.
"""

import os
import yaml
from typing import Dict, Any, Optional
import importlib.resources as pkg_resources
from dataclasses import fields, is_dataclass

class PomConfig:
    """
    Configuration manager for the Presentable Object Model system.
    
    Supports loading configuration from YAML files and accessing
    class and field metadata.
    """
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_dict: Optional initial configuration dictionary
        """
        self._config = config_dict or {}
        self._formats = {}
        self._model_metadata = {}
        
        # Load default configuration
        self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration from package resources."""
        try:
            # Try to load default format
            from . import formats
            default_format_path = pkg_resources.files(formats) / 'default_format.yaml'
            
            with open(default_format_path, 'r') as f:
                self._formats['default'] = yaml.safe_load(f)
            
            # Use default format as base configuration
            self._config.update(self._formats['default'])
        except (ImportError, FileNotFoundError):
            # Fallback to minimal default configuration
            self._config.update({
                'terminals': {
                    'string_format': '"\\""[^"\\"]*"\\""',
                    'number_format': '/[0-9]+(\\.[0-9]+)?/',
                    'boolean_format': '"true" | "false"'
                },
                'special_tokens': {
                    '#': 'HASH',
                    '*': 'ASTERISK',
                    '_': 'UNDERSCORE',
                    '-': 'DASH',
                    '(': 'LPAREN',
                    ')': 'RPAREN',
                    '[': 'LBRACK',
                    ']': 'RBRACK',
                    '{': 'LBRACE',
                    '}': 'RBRACE',
                    ',': 'COMMA',
                    ':': 'COLON',
                    '.': 'DOT'
                },
                'list_format': {
                    'opener': '[',
                    'closer': ']',
                    'separator': ',',
                    'whitespace': True
                },
                'case_sensitive': False
            })
    
    def load_format(self, format_name: str):
        """
        Load a named format configuration.
        
        Args:
            format_name: Name of the format to load
        """
        if format_name in self._formats:
            # Already loaded
            self._config.update(self._formats[format_name])
            return
        
        try:
            # Try to load from package resources
            from . import formats
            format_path = pkg_resources.files(formats) / f'{format_name}_format.yaml'
            
            with open(format_path, 'r') as f:
                format_config = yaml.safe_load(f)
                self._formats[format_name] = format_config
                self._config.update(format_config)
        except (ImportError, FileNotFoundError):
            # Try to load from current directory
            format_path = f'{format_name}_format.yaml'
            if os.path.exists(format_path):
                with open(format_path, 'r') as f:
                    format_config = yaml.safe_load(f)
                    self._formats[format_name] = format_config
                    self._config.update(format_config)
            else:
                raise ValueError(f"Format '{format_name}' not found")
    
    def load_model_metadata(self, model_name: str):
        """
        Load metadata for a specific model.
        
        Args:
            model_name: Name of the model module
        """
        if model_name in self._model_metadata:
            # Already loaded
            return
        
        # Try to load from current directory
        metadata_path = f'{model_name}_grammar.yaml'
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = yaml.safe_load(f)
                self._model_metadata[model_name] = metadata
    
    def load_from_file(self, file_path: str):
        """
        Load configuration from a YAML file.
        
        Args:
            file_path: Path to the YAML file
        """
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
            self._config.update(config)
    
    def update(self, config_dict: Dict[str, Any]):
        """
        Update configuration with new values.
        
        Args:
            config_dict: Configuration dictionary to update with
        """
        self._config.update(config_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def __getitem__(self, key: str) -> Any:
        """
        Get a configuration value using dictionary syntax.
        
        Args:
            key: Configuration key
            
        Returns:
            Configuration value
        """
        return self._config[key]
    
    def get_class_metadata(self, class_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dictionary of class metadata
        """
        for model_name, metadata in self._model_metadata.items():
            if 'classes' in metadata and class_name in metadata['classes']:
                return metadata['classes'][class_name]
        
        return {}
    
    def get_field_metadata(self, class_name: str, field_name: str) -> Dict[str, Any]:
        """
        Get metadata for a specific field.
        
        Args:
            class_name: Name of the class
            field_name: Name of the field
            
        Returns:
            Dictionary of field metadata
        """
        for model_name, metadata in self._model_metadata.items():
            if 'classes' in metadata and class_name in metadata['classes']:
                class_meta = metadata['classes'][class_name]
                if 'fields' in class_meta and field_name in class_meta['fields']:
                    return class_meta['fields'][field_name]
        
        return {}
