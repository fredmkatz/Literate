# template_processor.py
import re
from typing import List, Set, Dict, Any
from class_field_type import field_terminals, punctuation_terminals
from pom_config import named_pmarks, pmark_named
from utils_pom.util_flogging import flogger, trace_method

class TemplateProcessor:
    """
    A simple, reliable template processor for converting between formats.
    """
    
    @staticmethod
    def find_fields(template: str) -> Set[str]:
        """Find all field references in a template."""
        if not template:
            return set()
        # Find all {field} references
        return set(re.findall(r'\{([^?{}]+)\}', template))
    
    @staticmethod
    def to_handlebars(template: str) -> str:
        """Convert a template to Handlebars format."""
        if not template:
            return ""
            
        # Process in multiple passes to handle nesting and special cases
        
        # First pass: identify and store conditionals to prevent nested processing
        conditionals = []
        
        def store_conditional(match):
            content = match.group(1)
            index = len(conditionals)
            conditionals.append(content)
            return f"__COND_{index}__"
            
        # Replace conditionals with placeholders
        processed = re.sub(r'\{\?\s*(.*?)\}', store_conditional, template)
        
        # Second pass: convert field references
        processed = re.sub(r'\{([^?{}]+)\}', r'{{\1}}', processed)
        
        # Third pass: restore and process conditionals
        for i, cond in enumerate(conditionals):
            # Process field references in the conditional
            cond_processed = re.sub(r'\{([^?{}]+)\}', r'{{\1}}', cond)
            
            # Find first field reference to use as condition
            fields = re.findall(r'{{([^{}]+?)}}', cond_processed)
            if fields:
                replacement = "{{#if " + fields[0] + "}}" + cond_processed + "{{/if}}"
            else:
                replacement = cond_processed
                
            # Replace the placeholder
            processed = processed.replace(f"__COND_{i}__", replacement)
            
        return processed
    
    @staticmethod
    def to_grammar_parts(template: str, class_name: str) -> List[str]:
        """Convert a template to grammar rule parts."""
        
        from class_casing import LowerCamel

        if not template:
            return []
            
        # Process the template
        parts = []
        i = 0
        
        # Template state tracking
        in_field = False
        in_conditional = False
        field_start = 0
        cond_start = 0
        
        while i < len(template):
            # Start of field reference
            if template[i:i+1] == "{" and i+1 < len(template) and template[i+1] != "?":
                if not in_field and not in_conditional:
                    # Process any text before the field
                    if i > 0:
                        parts.extend(TemplateProcessor._process_text(template[0:i]))
                    
                    in_field = True
                    field_start = i + 1
                    
            # End of field reference
            elif template[i:i+1] == "}" and in_field:
                field_name = template[field_start:i].strip()
                parts.append(f"{class_name}_{LowerCamel(field_name)}_value")
                
                in_field = False
                template = template[i+1:]
                i = 0
                continue
                
            # Start of conditional
            elif template[i:i+2] == "{?" and not in_field and not in_conditional:
                # Process any text before the conditional
                if i > 0:
                    parts.extend(TemplateProcessor._process_text(template[0:i]))
                
                in_conditional = True
                cond_start = i + 2
                
            # End of conditional
            elif template[i:i+1] == "}" and in_conditional:
                cond_content = template[cond_start:i]
                
                # Process the conditional content
                cond_parts = TemplateProcessor.to_grammar_parts(cond_content, class_name)
                if cond_parts:
                    parts.append("[")
                    parts.extend(cond_parts)
                    parts.append("]")
                
                in_conditional = False
                template = template[i+1:]
                i = 0
                continue
                
            i += 1
            
        # Process any remaining text
        if not in_field and not in_conditional and template:
            parts.extend(TemplateProcessor._process_text(template))
            
        return [p for p in parts if p]
    
    @staticmethod
    def _process_text(text: str) -> List[str]:
        """Process text segments into grammar tokens."""
        if not text:
            return []
            
        # Process the text token by token
        tokens = []
        i = 0
        
        while i < len(text):
            # Skip whitespace except newlines
            if text[i].isspace() and text[i] != '\n':
                i += 1
                continue
                
            # Handle newlines
            if text[i] == '\n':
                tokens.append("NEWLINE")
                punctuation_terminals.add("NEWLINE")
                i += 1
                continue
                
            # Check for punctuation
            if text[i] in named_pmarks:
                term_name = named_pmarks[text[i]]
                punctuation_terminals.add(term_name)
                tokens.append(term_name)
                i += 1
                continue
            
            # Check for words
            if text[i].isalpha() or text[i] == '_':
                word = ""
                j = i
                while j < len(text) and (text[j].isalpha() or text[j] == '_'):
                    word += text[j]
                    j += 1
                
                if word in pmark_named:
                    term_name = word
                    punctuation_terminals.add(term_name)
                else:
                    term_name = word.upper()
                    field_terminals.add(term_name)
                
                tokens.append(term_name)
                i = j
                continue
            
            # Other characters
            if text[i].isalnum():
                term_name = text[i].upper()
                field_terminals.add(term_name)
                tokens.append(term_name)
            
            i += 1
            
        return tokens