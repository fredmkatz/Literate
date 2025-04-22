import re
from dataclasses import dataclass
from typing import Set, List
from class_field_type import to_terminal_name, field_terminals, field_name_literals
from utils_pom.util_flogging import flogger, trace_method, trace_decorator

def literal_name(word: str)->str:
    """
    Convert a word to a literal name for use in grammar rules.
    
    Args:
        word: The word to convert.
        
    Returns:
        A string representing the literal name.
    """
    qword = word + "_Q"
    
    return qword.upper()

@dataclass
class PomTemplate:
    
    
    def __init__(self, template):
        """
        Initialize the PomTemplate with a template string .
        
        Args:
            template: Template string
            """
        
        self.template = template
    
    def __str__(self):
        return self.template
    
    def __repr__(self):
        return f"PomTemplate({self.template})"
    
    # @trace_decorator
    def to_fragment(self, class_name) -> str:
        parts = self.to_grammar_parts(class_name)
        return " ".join(parts)
    
    # @trace_decorator
    def to_grammar_parts(self, class_name) -> List[str]:
        """
        Convert a template string to grammar rule parts.
        
        Args:
            class_name: Name of the class for field references
            
        Returns:
            List of grammar rule parts
        """
        from class_casing import LowerCamel, NTCase  # To avoid circular import
        from pom_config import named_pmarks , pmark_named # Import named punctuation marks
        from class_field_type import punctuation_terminals

        # First, capture all field references
        all_field_refs = {}
        for match in re.finditer(r'\{([^?{}]+)\}', self.template):
            placeholder = f"__FIELD_{len(all_field_refs)}__"
            all_field_refs[placeholder] = match.group(1)
        
        # Replace field references with placeholders to protect them
        template = self.template
        for placeholder, field_name in all_field_refs.items():
            template = template.replace(f"{{{field_name}}}", placeholder)
        
        # Now process conditionals: {? content}
        template = re.sub(r'\{\?\s*(.*?)\}', r'[\1]', template)
        
        # Restore field references
        for placeholder, field_name in all_field_refs.items():
            template = template.replace(placeholder, f"{{{field_name}}}")
        
        # Log the template after preprocessing
        # flogger.infof(f"Preprocessed template: {template}")
        
        # Find all field references and mark their positions
        field_positions = []
        for match in re.finditer(r'\{([^?{}]+)\}', template):
            field_positions.append((match.start(), match.end(), match.group(1)))
        
        # Find all optional sections and mark their positions
        optional_positions = []
        i = 0
        while i < len(template):
            if template[i] == '[':
                start = i
                level = 1
                i += 1
                while i < len(template) and level > 0:
                    if template[i] == '[':
                        level += 1
                    elif template[i] == ']':
                        level -= 1
                    i += 1
                if level == 0:
                    optional_positions.append((start, i))
                    continue
            i += 1
        
        # Now process the template with awareness of special regions
        grammar_parts = []
        i = 0
        while i < len(template):
            # Check if we're at a field reference
            field_pos = next((p for p in field_positions if p[0] == i), None)
            if field_pos:
                field_name = field_pos[2]
                field_rule = f"{NTCase(class_name)}__{NTCase(field_name)}__value"
                grammar_parts.append(field_rule)
                i = field_pos[1]
                continue
            
            # Check if we're at an optional section
            opt_pos = next((p for p in optional_positions if p[0] == i), None)
            if opt_pos:
                # Extract content between brackets
                opt_content = template[i+1:opt_pos[1]-1]
                
                # Process optional content
                temp_template = PomTemplate(opt_content)
                opt_parts = temp_template.to_grammar_parts(class_name)
                
                # Add as optional sequence
                if opt_parts:
                    grammar_parts.append("[")
                    grammar_parts.extend(opt_parts)
                    grammar_parts.append("]")
                
                i = opt_pos[1]
                continue
            
            # Handle whitespace
            if template[i].isspace():
                if template[i] == '\n':
                    grammar_parts.append("NEWLINE")
                    punctuation_terminals.add("NEWLINE")
                    flogger.infof("Adding NEWLINE to punctuation_terminals")
                    flogger.infof(f"NEWLINE found in template: {template}")
                i += 1
                continue
            
            # Handle word tokens (consecutive letters or UNDERSCORE)
            if template[i].isalpha() or template[i] == '_':
                word = ""
                j = i
                while j < len(template) and (template[j].isalpha() or template[j] == '_'):
                    word += template[j]
                    j += 1
                
                # Add as a token if it's a word
                if len(word) > 1:
                    # flogger.infof(f"Found a WORD {word} ")

                    if word in pmark_named:
                        mark = pmark_named[word]
                        punctuation_terminals.add(word)
                        grammar_parts.append(word)
                        i = j
                        # flogger.infof(f"Punctuation name {word} added for {mark}")
                        continue
                    
                    if word.endswith("_QF"):
                        term_name = word
                        field_name_literals.add(word)

                    else:
                        term_name = literal_name(word)
                        field_terminals.add(term_name)

                    grammar_parts.append(term_name)
                    i = j
                    continue
            
            # Handle single characters
            char = template[i]
            
            # Use named punctuation marks
            if char in named_pmarks:
                term_name = named_pmarks[char]
                grammar_parts.append(term_name)
                punctuation_terminals.add(term_name)
            elif char.isalnum():
                # Single character
                term_name = char.upper()
                grammar_parts.append(term_name)
                field_terminals.add(term_name)
            
            i += 1
        
        # Log the final grammar parts
        # flogger.infof(f"Final grammar parts: {grammar_parts}")
        return grammar_parts
    
    @trace_method
    def find_fields(self) -> Set[str]:
        field_positions = []
        fields = set()
        
        for match in re.finditer(r'\{([^?{}]+)\}', self.template):
            field_positions.append((match.start(), match.end(), match.group(1)))
            fields.add(match.group(1))
            # flogger.infof(f"Field posiitons: {field_positions}")
        return fields
    
    def as_rule(self, class_name):
        """
        Convert simple template to grammar rule format for rendering
        """
        
        # Convert field references: {field_name} → {class_name}__{field_name}__value
        rule_template = re.sub(r'\{([^?{}]+)\}', rf'{class_name}_\1_value', self.template)
        
        # Convert conditionals: {? content} → [content]
        rule_template = re.sub(r'\{\?\s*(.*?)\}', r'[\1]', rule_template)
        
        return rule_template

    @trace_method
    def as_handlebars(self):
        """
        Convert template with {field} and {? conditional} syntax to Handlebars format.
        """
        # Split template into pieces with balanced brackets
        def split_into_pieces(template):
            pieces = []
            i = 0
            start = 0
            in_piece = False
            
            while i < len(template):
                if template[i] == '{':
                    # Start of a bracketed section
                    if not in_piece:
                        # If we have text before this bracket, add it
                        if i > start:
                            pieces.append(template[start:i])
                        start = i
                        in_piece = True
                    
                    # Check for conditional marker
                    if i + 1 < len(template) and template[i+1] == '?':
                        # It's a conditional - handle nested structures
                        bracket_level = 1
                        i += 2  # Skip '{?'
                        
                        # Find matching closing bracket
                        while i < len(template) and bracket_level > 0:
                            if template[i] == '{':
                                bracket_level += 1
                            elif template[i] == '}':
                                bracket_level -= 1
                            i += 1
                        
                        # End of conditional - add as piece
                        if bracket_level == 0:
                            pieces.append(template[start:i])
                            start = i
                            in_piece = False
                    else:
                        # Regular field reference
                        i += 1
                elif template[i] == '}' and in_piece:
                    # End of field reference
                    i += 1
                    pieces.append(template[start:i])
                    start = i
                    in_piece = False
                else:
                    # Regular character
                    i += 1
            
            # Add any remaining text
            if start < len(template):
                pieces.append(template[start:])
            
            return pieces
        
        # Find all field references in a string
        def find_fields(content):
            fields = []
            matches = re.finditer(r'\{([^?{}]+)\}', content)
            for match in matches:
                fields.append(match.group(1).strip())
            return fields
        
        # Convert template to Handlebars
        def convert_template(template_str):
            result = ""
            
            # For plain text without any brackets, return as is
            if '{' not in template_str:
                return template_str
            
            # Process the template
            pieces = split_into_pieces(template_str)
            
            for piece in pieces:
                if not piece.startswith('{'):
                    # Plain text - add as is
                    result += piece
                elif piece.startswith('{?'):
                    # Conditional section
                    conditional_content = piece[2:-1]
                    
                    # Find all fields in the conditional
                    fields = find_fields(conditional_content)
                    
                    if fields:
                        # Use the first field as the condition
                        condition_field = fields[0]
                        
                        # Process fields in the content
                        processed_content = conditional_content
                        for field in fields:
                            processed_content = processed_content.replace(
                                '{' + field + '}', 
                                '{{' + field + '}}'
                            )
                        
                        # Add the conditional with proper Handlebars syntax
                        result += "{{#if " + condition_field + "}}" + processed_content + "{{/if}}"
                    else:
                        # No fields found, add as is
                        result += conditional_content
                elif piece.startswith('{') and not piece.startswith('{{'):
                    # Field reference
                    field_name = piece[1:-1].strip()
                    result += "{{" + field_name + "}}"
                else:
                    # Other bracketed content (like {{existing}})
                    result += piece
            
            return result
        
        # Convert the template
        return convert_template(self.template)