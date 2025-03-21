"""
Unit tests for PomParser class.
"""

import unittest
import os
import tempfile
from ..pom_parser import PomParser
from ..pom_config import PomConfig
from .models.test_model import SimpleClass, ComplexClass

class TestPomParser(unittest.TestCase):
    """Tests for the PomParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import test_model module for testing
        import sys
        from . import models
        self.model_module = sys.modules[models.__name__ + '.test_model']
        
        # Create a parser
        self.config = PomConfig()
        self.parser = PomParser(self.model_module, self.config)
    
    def test_grammar_generation(self):
        """Test that grammar is generated correctly."""
        # Check that grammar is not empty
        self.assertTrue(self.parser.grammar)
        
        # Check that it contains rules for our test classes
        self.assertIn("simple_class:", self.parser.grammar)
        self.assertIn("complex_class:", self.parser.grammar)
    
    def test_parse_simple_class(self):
        """Test parsing a simple class."""
        # Create a simple input string
        input_text = """
        simple_class {
            name: "TestClass"
            value: 42
        }
        """
        
        # Parse the input
        model, success = self.parser.parse(input_text, "simple_class")
        
        # Check that parsing was successful
        self.assertTrue(success)
        self.assertIsNotNone(model)
        
        # Check that the model was created correctly
        self.assertIsInstance(model, SimpleClass)
        self.assertEqual(model.name, "TestClass")
        self.assertEqual(model.value, 42)
    
    def test_parse_complex_class(self):
        """Test parsing a complex class."""
        # Create a complex input string
        input_text = """
        complex_class {
            name: "TestClass"
            items: [
                "item1",
                "item2"
            ]
            is_active: true
        }
        """
        
        # Parse the input
        model, success = self.parser.parse(input_text, "complex_class")
        
        # Check that parsing was successful
        self.assertTrue(success)
        self.assertIsNotNone(model)
        
        # Check that the model was created correctly
        self.assertIsInstance(model, ComplexClass)
        self.assertEqual(model.name, "TestClass")
        self.assertEqual(model.items, ["item1", "item2"])
        self.assertTrue(model.is_active)
    
    def test_parse_error_handling(self):
        """Test that parsing errors are handled correctly."""
        # Create an input with a syntax error
        input_text = """
        simple_class {
            name: "TestClass"
            value: 42
            invalid:
        }
        """
        
        # Parse the input
        model, success = self.parser.parse(input_text, "simple_class")
        
        # Check that parsing failed
        self.assertFalse(success)
        self.assertIsNone(model)
        
        # Check that diagnostics were created
        self.assertTrue(self.parser.diagnostics.has_errors())
    
    def test_parse_file(self):
        """Test parsing a file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("""
            simple_class {
                name: "TestClass"
                value: 42
            }
            """)
            file_path = f.name
        
        try:
            # Parse the file
            model, success = self.parser.parse_file(file_path, "simple_class")
            
            # Check that parsing was successful
            self.assertTrue(success)
            self.assertIsNotNone(model)
            
            # Check that the model was created correctly
            self.assertIsInstance(model, SimpleClass)
            self.assertEqual(model.name, "TestClass")
            self.assertEqual(model.value, 42)
        finally:
            # Clean up
            os.unlink(file_path)
    
    def test_save_grammar(self):
        """Test saving the grammar to a file."""
        # Create a temporary file path
        with tempfile.NamedTemporaryFile(delete=False, suffix='.lark') as f:
            file_path = f.name
        
        try:
            # Save the grammar
            success = self.parser.save_grammar(file_path)
            
            # Check that saving was successful
            self.assertTrue(success)
            
            # Check that the file was created and contains the grammar
            with open(file_path, 'r') as f:
                content = f.read()
                self.assertTrue(content)
                self.assertIn("simple_class:", content)
                self.assertIn("complex_class:", content)
        finally:
            # Clean up
            os.unlink(file_path)
    
    def test_error_context(self):
        """Test getting error context."""
        # Create an input with a syntax error
        input_text = """
        line 1
        line 2
        line 3 with error
        line 4
        line 5
        """
        
        # Create a mock error with line/column
        class MockError:
            line = 3
            column = 10
        
        # Get error context
        context = self.parser._get_error_context(input_text, MockError(), 1)
        
        # Check that the context contains the error line and marker
        self.assertIn("line 3 with error", context)
        self.assertIn("^", context)
    
    def test_custom_format(self):
        """Test using a custom format."""
        # Create a parser with a custom format
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_format.yaml') as f:
            f.write("""
            parser:
              case_sensitive: true
            
            field_clause_template: '"{field_name}": {field_value}'
            """)
            format_name = os.path.basename(f.name).replace('_format.yaml', '')
            file_path = f.name
        
        try:
            # Copy format file to current directory for testing
            with open(f"{format_name}_format.yaml", 'w') as f2:
                f2.write("""
                parser:
                  case_sensitive: true
                
                field_clause_template: '"{field_name}": {field_value}'
                """)
            
            # Create parser with custom format
            parser = PomParser(self.model_module, format_name=format_name)
            
            # Check that format was loaded
            self.assertTrue(parser.config.get("parser").get("case_sensitive"))
            
            # Check grammar has appropriate format
            self.assertIn('":"', parser.grammar)
        finally:
            # Clean up
            os.unlink(file_path)
            if os.path.exists(f"{format_name}_format.yaml"):
                os.unlink(f"{format_name}_format.yaml")

if __name__ == '__main__':
    unittest.main()
