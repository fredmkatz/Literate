### 4.2 Rule Generation

The grammar generator will generate rules for classes, fields, and values:

```python
def _generate_class_rules(self, class_name, cls):
    """
    Generate grammar rules for a specific class.
    
    Args:
        class_name: Name of the class
        cls: Class object
    """
    if class_name in self.processed_classes:
        return
        
    self.processed_classes.add(class_name)
    
    # Add comment indicating the class rules
    self.rules.append(f"// ========== {class_name.upper()} ==========")
    
    # Get class metadata (from both in-code Meta and external config)
    metadata = self._get_class_metadata(cls, class_name)
    
    # Check if this is an abstract class that shouldn't generate direct rules
    if metadata.get('is_abstract', False):
        # Only generate type hierarchy rule
        self._generate_type_hierarchy_rule(class_name)
        return
        
    # Generate the header rule if template exists
    if metadata.get('presentable_header'):
        self._generate_header_rule(class_name, cls, metadata['presentable_header'])
    
    # Generate field clause rules
    self._generate_field_clauses(class_name, cls)
    
    # Generate the class body rule
    self._generate_body_rule(class_name, cls)
    
    # Generate the type hierarchy rule
    self._generate_type_hierarchy_rule(class_name)
    
    # Add empty line for readability
    self.rules.append("")

def _generate_header_rule(self, class_name, cls, template):
    """
    Generate a header rule for a class based on a template.
    
    Args:
        class_name: Name of the class
        cls: Class object
        template: Header template
    """
    # Convert template to grammar rule
    rule_name = self._to_snake_case(class_name) + "_header"
    rule_parts = self._template_to_grammar_parts(template, class_name)
    
    # Create the header rule
    rule = f"{rule_name}: {' '.join(rule_parts)}"
    self.rules.append(rule)
    self.rule_names.add(rule_name)

def _template_to_grammar_parts(self, template, class_name):
    """
    Convert a template string to grammar rule parts.
    
    Args:
        template: Template string
        class_name: Name of the class for field references
        
    Returns:
        List of grammar rule parts
    """
    parts = []
    
    # Pattern to match field references like {name}
    field_pattern = r'\{([^{}#>/]+)\}'
    
    # Pattern to match conditionals like {{#if field}}...{{/if}}
    conditional_pattern = r'\{\{#if ([^}]+)\}\}(.*?)\{\{/if\}\}'
    
    # Pattern to match partials like {{> partial}}
    partial_pattern = r'\{\{> ([^}]+)\}\}'
    
    # First replace conditionals with optional parts
    template = re.sub(conditional_pattern, 
                     lambda m: f"[{m.group(2)}]", 
                     template)
    
    # Replace partials with rule references
    template = re.sub(partial_pattern,
                     lambda m: f"{self._to_snake_case(m.group(1))}", 
                     template)
    
    # Process the simplified template
    tokens = []
    current_token = ""
    i = 0
    while i < len(template):
        # Field reference
        if template[i] == '{':
            if current_token:
                tokens.append(current_token)
                current_token = ""
            
            end = template.find('}', i)
            if end != -1:
                field_name = template[i+1:end]
                tokens.append(f"{{{field_name}}}")
                i = end + 1
                continue
        
        # Special token handling
        if template[i] in self.config.get('special_tokens', {
            '#': 'HASH',
            '*': 'ASTERISK', 
            '_': 'UNDERSCORE',
            '-': 'DASH'
        }):
            if current_token:
                tokens.append(current_token)
                current_token = ""
            
            special = template[i]
            token_name = self.config.get('special_tokens', {}).get(special)
            tokens.append(token_name)
            self.terminals.add(token_name)
            i += 1
            continue
        
        # Normal character
        current_token += template[i]
        i += 1
    
    # Add final token if any
    if current_token:
        tokens.append(current_token)
    
    # Process tokens into grammar parts
    for token in tokens:
        if token.startswith('{') and token.endswith('}'):
            # Field reference
            field_name = token[1:-1]
            field_rule = f"{class_name}_{field_name}_value"
            parts.append(field_rule)
            # Make sure we add a rule for this value later
            self.rule_names.add(field_rule)
        elif token.startswith('"') and token.endswith('"'):
            # Literal string
            parts.append(token)
        elif token in self.terminals:
            # Terminal token
            parts.append(token)
        else:
            # Text token - may need to be converted to terminal
            if token.strip():
                # Convert to proper terminal name or literal
                term_name = self._to_terminal_name(token.strip())
                parts.append(term_name)
                self.terminals.add(term_name)
    
    return parts

def _generate_field_clauses(self, class_name, cls):
    """
    Generate field clause rules for a class, handling inheritance and specialization.
    
    Args:
        class_name: Name of the class
        cls: Class object
    """
    # Get specialized fields (fields redefined in this class)
    specialized_fields = self._get_specialized_fields(cls)
    
    # Track processed fields to avoid duplicates
    processed_fields = set()
    
    # Process fields defined in this class
    for field_obj in fields(cls):
        # Skip private fields
        if field_obj.name.startswith('_'):
            continue
            
        # Generate field clause and value rules
        self._generate_field_rules(class_name, field_obj.name, field_obj)
        processed_fields.add(field_obj.name)
    
    # Process inherited fields that aren't overridden
    for base_name in self.class_hierarchy[class_name]['bases']:
        if base_name not in self.class_hierarchy:
            continue
            
        base_cls = self.class_hierarchy[base_name]['class']
        
        for field_obj in fields(base_cls):
            # Skip private fields and already processed fields
            if field_obj.name.startswith('_') or field_obj.name in processed_fields:
                continue
                
            # Skip fields that are specialized in this class
            if field_obj.name in specialized_fields:
                continue
                
            # Generate field clause and value rules
            self._generate_field_rules(class_name, field_obj.name, field_obj)
            processed_fields.add(field_obj.name)

def _get_specialized_fields(self, cls):
    """
    Get fields that are specialized (redefined) in this class.
    
    Args:
        cls: Class to analyze
        
    Returns:
        Set of field names that are specialized
    """
    specialized = set()
    
    # Get base classes
    bases = [base for base in cls.__bases__ 
            if is_dataclass(base) and base.__name__ in self.class_hierarchy]
    
    # Get fields in this class
    cls_fields = {f.name: f.type for f in fields(cls)}
    
    # Check each base class
    for base in bases:
        base_fields = {f.name: f.type for f in fields(base)}
        
        # Find fields with the same name but different types
        for name, type_hint in cls_fields.items():
            if name in base_fields and type_hint != base_fields[name]:
                specialized.add(name)
    
    return specialized

def _generate_field_rules(self, class_name, field_name, field_obj):
    """
    Generate rules for a field clause and value.
    
    Args:
        class_name: Name of the class
        field_name: Name of the field
        field_obj: Field object
    """
    # Generate field clause rule
    self._generate_field_clause_rule(class_name, field_name, field_obj)
    
    # Generate field value rule based on type
    self._generate_field_value_rule(class_name, field_name, field_obj)

def _generate_field_clause_rule(self, class_name, field_name, field_obj):
    """
    Generate a rule for a field clause.
    
    Args:
        class_name: Name of the class
        field_name: Name of the field
        field_obj: Field object
    """
    # Get the field clause template
    template = self.config.get('field_clause_template', '{field_name}: {field_value}')
    
    # Get field metadata
    metadata = self._get_field_metadata(field_obj, class_name, field_name)
    
    # Check if field has its own template
    if 'field_clause_template' in metadata:
        template = metadata['field_clause_template']
    
    # Replace placeholders with actual values
    rule_text = template.replace('{field_name}', field_name.upper())
    rule_text = rule_text.replace('{field_value}', f"{class_name}_{field_name}_value")
    
    # Create the rule
    rule_name = f"{class_name}_{field_name}_clause"
    rule = f"{rule_name}: {rule_text}"
    
    self.rules.append(rule)
    self.rule_names.add(rule_name)
    
    # Add the field name to terminals
    self.terminals.add(field_name.upper())

def _generate_field_value_rule(self, class_name, field_name, field_obj):
    """
    Generate a rule for a field value based on its type.
    
    Args:
        class_name: Name of the class
        field_name: Name of the field
        field_obj: Field object
    """
    # Get field type and metadata
    field_type = field_obj.type
    metadata = self._get_field_metadata(field_obj, class_name, field_name)
    
    # Rule name
    rule_name = f"{class_name}_{field_name}_value"
    
    # Handle custom template if specified
    if 'presentable_template' in metadata:
        template_parts = self._template_to_grammar_parts(
            metadata['presentable_template'], class_name)
        self.rules.append(f"{rule_name}: {' '.join(template_parts)}")
        self.rule_names.add(rule_name)
        return
    
    # Handle different field types
    if self._is_primitive_type(field_type):
        # Primitive type (str, int, bool)
        self._generate_primitive_value_rule(rule_name, field_type, metadata)
    elif self._is_list_type(field_type):
        # List type
        self._generate_list_value_rule(rule_name, field_type, metadata)
    elif self._is_optional_type(field_type):
        # Optional type - handle the underlying type
        element_type = self._get_optional_element_type(field_type)
        self._generate_field_value_rule_for_type(rule_name, element_type, metadata)
    elif self._is_class_type(field_type):
        # Class type - reference the class rule
        self._generate_class_value_rule(rule_name, field_type)
    else:
        # Default case - generic value
        self.rules.append(f"{rule_name}: value")
    
    self.rule_names.add(rule_name)

def _generate_type_hierarchy_rule(self, class_name):
    """
    Generate a rule for type hierarchy (parent class with subtypes).
    
    Args:
        class_name: Name of the class
    """
    # Get subtypes of this class
    subtypes = self.class_hierarchy[class_name].get('subtypes', [])
    
    # If this class has subtypes, create a rule for the hierarchy
    if subtypes:
        rule_name = self._to_snake_case(class_name)
        subtype_rules = " | ".join(self._to_snake_case(st) for st in subtypes)
        
        # Add class's own rule if not abstract
        metadata = self._get_class_metadata(
            self.class_hierarchy[class_name]['class'], class_name)
        
        if not metadata.get('is_abstract', False):
            # Include the class's own body rule
            body_rule = f"{rule_name}_body"
            if subtype_rules:
                rule = f"{rule_name}: {subtype_rules} | {body_rule}"
            else:
                rule = f"{rule_name}: {body_rule}"
        else:
            # Abstract class - only subtypes
            rule = f"{rule_name}: {subtype_rules}"
        
        self.rules.append(rule)
        self.rule_names.add(rule_name)

def _generate_body_rule(self, class_name, cls):
    """
    Generate a body rule for a class.
    
    Args:
        class_name: Name of the class
        cls: Class object
    """
    # Rule name
    rule_name = f"{self._to_snake_case(class_name)}_body"
    
    # Get all field clause rules for this class
    field_clauses = self._get_all_field_clauses(class_name)
    
    # Create the rule text
    if field_clauses:
        rule_text = f"({' | '.join(field_clauses)})*"
        rule = f"{rule_name}: {rule_text}"
    else:
        rule = f"{rule_name}: /* No fields */"
    
    self.rules.append(rule)
    self.rule_names.add(rule_name)

def _get_all_field_clauses(self, class_name):
    """
    Get all field clause rule names for a class.
    
    Args:
        class_name: Name of the class
        
    Returns:
        List of field clause rule names
    """
    return [rule for rule in self.rule_names 
            if rule.startswith(f"{class_name}_") and rule.endswith("_clause")]

def _get_class_metadata(self, cls, class_name):
    """
    Get metadata for a class, combining in-code Meta with external config.
    
    Args:
        cls: Class object
        class_name: Name of the class
        
    Returns:
        Dictionary of metadata
    """
    # Start with defaults
    metadata = {
        "presentable_header": None,
        "presentable_template": None,
        "is_abstract": False
    }
    
    # Check for in-code Meta class
    if hasattr(cls, 'Meta'):
        if hasattr(cls.Meta, 'presentable_header'):
            metadata['presentable_header'] = cls.Meta.presentable_header
        if hasattr(cls.Meta, 'presentable_template'):
            metadata['presentable_template'] = cls.Meta.presentable_template
        if hasattr(cls.Meta, 'is_abstract'):
            metadata['is_abstract'] = cls.Meta.is_abstract
    
    # Override with external metadata from config
    external_metadata = self.config.get_class_metadata(class_name)
    metadata.update(external_metadata)
    
    return metadata

def _get_field_metadata(self, field_obj, class_name, field_name):
    """
    Get metadata for a field, combining field metadata with external config.
    
    Args:
        field_obj: Field object
        class_name: Name of the class
        field_name: Name of the field
        
    Returns:
        Dictionary of metadata
    """
    # Start with defaults
    metadata = {
        "required": True,
        "presentable_true": None,
        "presentable_false": None,
        "explicit": False,
        "list_format": None
    }
    
    # Check for field-level metadata
    if hasattr(field_obj, 'metadata'):
        metadata.update(field_obj.metadata)
    
    # Override with external metadata from config
    external_metadata = self.config.get_field_metadata(class_name, field_name)
    metadata.update(external_metadata)
    
    return metadata
```

### 4.3 Type-Specific Rule Generation

The grammar generator will include methods for handling different field types:

```python
def _generate_primitive_value_rule(self, rule_name, field_type, metadata):
    """
    Generate a rule for a primitive value.
    
    Args:
        rule_name: Name of the rule
        field_type: Field type
        metadata: Field metadata
    """
    if field_type == str:
        # String type
        terminal = self.config.get('terminals', {}).get('string_format', 'STRING')
        self.rules.append(f"{rule_name}: {terminal}")
        
    elif field_type == bool:
        # Boolean type with possible special representation
        if 'presentable_true' in metadata and 'presentable_false' in metadata:
            true_val = metadata['presentable_true'].upper()
            false_val = metadata['presentable_false'].upper()
            
            # Add terminals
            self.terminals.add(true_val)
            self.terminals.add(false_val)
            
            # Create rule
            if metadata.get('explicit', True):
                self.rules.append(f"{rule_name}: {true_val} | {false_val}")
            else:
                # Only required value is included if not explicit
                if metadata.get('default', False):
                    self.rules.append(f"{rule_name}: [{true_val}]")
                else:
                    self.rules.append(f"{rule_name}: [{false_val}]")
        else:
            # Default boolean
            self.rules.append(f"{rule_name}: {self.config.get('terminals', {}).get('boolean_format', 'BOOLEAN')}")
            
    elif field_type in (int, float):
        # Numeric type
        self.rules.append(f"{rule_name}: {self.config.get('terminals', {}).get('number_format', 'NUMBER')}")
        
    else:
        # Other primitive type - fallback to generic value
        self.rules.append(f"{rule_name}: value")

def _generate_list_value_rule(self, rule_name, field_type, metadata):
    """
    Generate a rule for a list value.
    
    Args:
        rule_name: Name of the rule
        field_type: Field type (list or similar)
        metadata: Field metadata
    """
    # Get element type
    element_type = self._get_list_element_type(field_type)
    
    # Get list format
    list_format = metadata.get('list_format', self.config.get('list_format', {
        'opener': '[',
        'closer': ']',
        'separator': ',',
        'whitespace': True
    }))
    
    # Create terminals for delimiters if needed
    opener = list_format.get('opener', '[')
    closer = list_format.get('closer', ']')
    separator = list_format.get('separator', ',')
    
    # Add whitespace if configured
    sep_with_space = f" {separator} " if list_format.get('whitespace', True) else separator
    
    # Generate element type rule if needed
    element_rule = self._get_rule_for_type