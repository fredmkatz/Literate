"""
Unit tests for PomGrammarGenerator class.
"""

import unittest
from ..pom_grammar_generator import PomGrammarGenerator
from ..pom_config import PomConfig
from .models.test_model import SimpleClass, ComplexClass

class TestPomGrammarGenerator(unittest.TestCase):
    """Tests for the PomGrammarGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = PomConfig()
        self.generator = PomGrammarGenerator(self.config, "TestGrammar")
    
    def test_simple_grammar_generation(self):
        """Test generating grammar for a simple model."""
        # Import test_model module for testing
        import sys
        from . import models
        models_module = sys.modules[models.__name__ + '.test_model']
        
        # Generate grammar
        grammar = self.generator.generate_grammar(models_module)
        
        # Check that grammar is not empty
        self.assertTrue(grammar)
        
        # Check that it contains rules for our test classes
        self.assertIn("simple_class:", grammar)
        self.assertIn("complex_class:", grammar)
        
        # Check that it has generated field rules
        self.assertIn("NAME:", grammar)
        self.assertIn("VALUE:", grammar)
    
    def test_template_processing(self):
        """Test processing of templates."""
        # Create a test class with Meta class
        class TestClassWithTemplate:
            class Meta:
                presentable_header = "# **{name}** - {description}"
        
        # Process the template
        result = self.generator._template_to_grammar_parts(
            TestClassWithTemplate.Meta.presentable_header, 
            "test_class"
        )
        
        # Check result
        self.assertIn("HASH", result)
        self.assertIn("ASTERISK", result)
        self.assertIn("test_class_name_value", result)
        self.assertIn("test_class_description_value", result)
    
    def test_boolean_field_handling(self):
        """Test generation of boolean field rules."""
        # Create a model class with a boolean field with presentable values
        class TestBoolean:
            def __init__(self):
                self.is_optional = False
        
        # Generate a field value rule for the boolean field
        field_obj = type('FieldObject', (), {
            'name': 'is_optional',
            'type': bool,
            'metadata': {
                'presentable_true': 'OPTIONAL',
                'presentable_false': 'REQUIRED',
                'explicit': True
            }
        })
        
        # Setup context for the test
        self.generator.terminals = set()
        self.generator.rules = []
        
        # Generate rule
        self.generator._generate_primitive_value_rule(
            "test_class_is_optional_value",
            bool,
            field_obj.metadata
        )
        
        # Check that the rule was generated correctly
        rule = self.generator.rules[0]
        self.assertIn("OPTIONAL", rule)
        self.assertIn("REQUIRED", rule)
        
        # Check that terminals were added
        self.assertIn("OPTIONAL", self.generator.terminals)
        self.assertIn("REQUIRED", self.generator.terminals)
    
    def test_list_field_handling(self):
        """Test generation of list field rules."""
        # Create a field type for a list of strings
        field_type = list[str]
        
        # Setup context for the test
        self.generator.terminals = set()
        self.generator.rules = []
        
        # Generate rule
        self.generator._generate_list_value_rule(
            "test_class_items_value",
            field_type,
            {}
        )
        
        # Check that the rule was generated correctly
        rule = self.generator.rules[0]
        self.assertIn("LBRACK", rule)
        self.assertIn("RBRACK", rule)
        self.assertIn("STRING", rule)
    
    def test_type_detection(self):
        """Test type detection methods."""
        # Test primitive type detection
        self.assertTrue(self.generator._is_primitive_type(str))
        self.assertTrue(self.generator._is_primitive_type(bool))
        self.assertTrue(self.generator._is_primitive_type(int))
        self.assertFalse(self.generator._is_primitive_type(list))
        
        # Test list type detection
        self.assertTrue(self.generator._is_list_type(list[str]))
        self.assertFalse(self.generator._is_list_type(str))
        
        # Test optional type detection
        from typing import Optional
        self.assertTrue(self.generator._is_optional_type(Optional[str]))
        self.assertFalse(self.generator._is_optional_type(str))
        
        # Test class type detection
        # First, analyze model to build class hierarchy
        import sys
        from . import models
        models_module = sys.modules[models.__name__ + '.test_model']
        self.generator._analyze_model(models_module)
        
        # Now test class type detection
        self.assertTrue(self.generator._is_class_type(SimpleClass))
        self.assertFalse(self.generator._is_class_type(str))

if __name__ == '__main__':
    unittest.main()
