import re
from dataclasses import dataclass
from typing import Set, List
from class_field_type import to_terminal_name, field_terminals, field_name_literals
from utils_pom.util_flogging import flogger, trace_method, trace_decorator
from template_processor import TemplateProcessor


@dataclass
class PomTemplate:
    """Template class for Presentable Object Models."""
    
    def __init__(self, template):
        """
        Initialize the PomTemplate with a template string.
        
        Args:
            template: Template string
        """
        self.template = template
    
    def __str__(self):
        return self.template
    
    def __repr__(self):
        return f"PomTemplate({self.template})"
    
    @trace_method
    def to_fragment(self, class_name) -> str:
        """Convert the template to a grammar fragment."""
        parts = self.to_grammar_parts(class_name)
        return ' '.join(parts)
    @trace_method
    def as_rule(self, class_name) -> str:
        """Convert the template to a grammar fragment."""
        parts = self.to_grammar_parts(class_name)
        return ' '.join(parts)
    
    @trace_method
    def to_grammar_parts(self, class_name) -> List[str]:
        """
        Convert a template string to grammar rule parts.
        
        Args:
            class_name: Name of the class for field references
            
        Returns:
            List of grammar rule parts
        """
        return TemplateProcessor.to_grammar_parts(self.template, class_name)
    
    @trace_method
    def find_fields(self) -> Set[str]:
        """Find all field references in the template."""
        return TemplateProcessor.find_fields(self.template)
    
    @trace_method
    def as_handlebars(self):
        """Convert template to Handlebars format."""
        return TemplateProcessor.to_handlebars(self.template)