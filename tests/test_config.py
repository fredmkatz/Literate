"""
Unit tests for PomConfig class.
"""

import unittest
import os
import tempfile
from ..pom_config import PomConfig

class TestPomConfig(unittest.TestCase):
    """Tests for the PomConfig class."""
    
    def test_default_config(self):
        """Test that default configuration is loaded."""
        config = PomConfig()
        
        # Check that default configuration has required sections
        self.assertIn('special_tokens', config.get(""))
        self.assertIn('list_format', config.get(""))
        
        # Check specific default value
        self.assertEqual(config.get("list_format").get("opener"), "[")
    
    def test_update_config(self):
        """Test updating configuration."""
        config = PomConfig()
        
        # Update a value
        config.update({"new_section": {"test_key": "test_value"}})
        
        # Check that update worked
        self.assertEqual(config.get("new_section").get("test_key"), "test_value")
    
    def test_load_from_file(self):
        """Test loading configuration from a file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
            f.write("""
            test_section:
              test_key: test_value
            """)
            file_path = f.name
        
        try:
            # Load configuration from file
            config = PomConfig()
            config.load_from_file(file_path)
            
            # Check that it was loaded
            self.assertEqual(config.get("test_section").get("test_key"), "test_value")
        finally:
            # Clean up
            os.unlink(file_path)
    
    def test_get_class_metadata(self):
        """Test getting class metadata."""
        # Setup test configuration with class metadata
        config = PomConfig()
        config.update({
            "class_templates": {
                "TestClass": {
                    "presentable_header": "test_header",
                    "is_abstract": True
                }
            }
        })
        
        # Add metadata to model_metadata
        config._model_metadata = {
            "test_model": {
                "classes": {
                    "TestClass": {
                        "fields": {
                            "test_field": {
                                "presentable_true": "YES",
                                "presentable_false": "NO"
                            }
                        }
                    }
                }
            }
        }
        
        # Test getting class metadata
        class_metadata = config.get_class_metadata("TestClass")
        self.assertIn("fields", class_metadata)
        
        # Test getting field metadata
        field_metadata = config.get_field_metadata("TestClass", "test_field")
        self.assertEqual(field_metadata.get("presentable_true"), "YES")
        self.assertEqual(field_metadata.get("presentable_false"), "NO")
    
    def test_load_format(self):
        """Test loading a format configuration."""
        # Create a temporary format file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='_format.yaml') as f:
            f.write("""
            test_section:
              test_key: test_value
            """)
            format_name = os.path.basename(f.name).replace('_format.yaml', '')
            file_path = f.name
        
        try:
            # Load configuration from format file
            config = PomConfig()
            
            # Copy format file to current directory for testing
            with open(f"{format_name}_format.yaml", 'w') as f2:
                f2.write("""
                test_section:
                  test_key: test_value
                """)
            
            # Load format
            config.load_format(format_name)
            
            # Check that it was loaded
            self.assertEqual(config.get("test_section").get("test_key"), "test_value")
        finally:
            # Clean up
            os.unlink(file_path)
            if os.path.exists(f"{format_name}_format.yaml"):
                os.unlink(f"{format_name}_format.yaml")

if __name__ == '__main__':
    unittest.main()
