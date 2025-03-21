# Presentable Model Visitor Specification

## 1. Overview

This specification outlines a streamlined visitor pattern for processing parse trees generated from Presentable Model grammars. The design leverages consistent naming patterns to minimize specialized visitor code while maintaining flexibility for custom processing.

## 2. Architecture

### 2.1 Core Components

1. **GenericVisitor**
   - Base visitor class with generic handling logic
   - Implements the visitor interface for the parser

2. **VisitContext**
   - Stack-like context manager
   - Tracks objects being constructed
   - Associates objects with their type identifiers

3. **ModelBuilder**
   - Coordinates visitor processing
   - Handles final object construction and validation

### 2.2 Processing Flow

1. Create a visitor instance for the specific model type
2. Parse input text using the generated grammar
3. Visit the parse tree to build object hierarchy
4. Return the completed model object

## 3. Visitor Design

### 3.1 Generic Visitor Pattern

```python
class PresentableVisitor(BaseLarkVisitor):
    """Generic visitor for Presentable Model parse trees."""
    
    def __init__(self):
        self.context = VisitContext()
        self.object_registry = {}  # Maps object IDs to constructed objects
    
    def visit(self, node):
        """Generic visit method with smart node handling."""
        node_name = self._get_node_name(node)
        
        # Object creation for class nodes (no suffix)
        if self._is_class_node(node_name):
            return self._handle_class_node(node, node_name)
            
        # Field value assignment for *_value nodes
        elif self._is_value_node(node_name):
            return self._handle_value_node(node, node_name)
            
        # Default to normal child visiting for other nodes
        return self.visitChildren(node)
    
    def _handle_class_node(self, node, node_name):
        """Create a new object for a class node and set up context."""
        class_type = self._get_class_type(node_name)
        new_object = self._create_object(class_type)
        
        # Store in context stack
        old_context = self.context
        self.context = self.context.with_object(class_type, new_object)
        
        # Add to parent collection if appropriate
        self._add_to_parent_if_needed(new_object, class_type)
        
        # Visit children to populate the object
        self.visitChildren(node)
        
        # Restore context
        self.context = old_context
        return new_object
    
    def _handle_value_node(self, node, node_name):
        """Process a value node and assign to the appropriate field."""
        # Extract class and field names from the node name pattern
        class_name, field_name = self._parse_value_node_name(node_name)
        
        # Get the target object from context
        target_obj = self.context.get_object(class_name)
        if not target_obj:
            return self.visitChildren(node)
        
        # Get value from child nodes
        value = self.visitChildren(node)
        
        # Assign value to the appropriate field
        setattr(target_obj, field_name, value)
        return value
```

### 3.2 Context Management

```python
class VisitContext:
    """Context tracker for the visitor pattern."""
    
    def __init__(self, prev_context=None):
        self._prev_context = prev_context
        self.objects = {}  # Maps type names to objects
    
    def with_object(self, type_name, obj):
        """Create a new context with the given object."""
        new_context = VisitContext(self)
        new_context.objects[type_name] = obj
        return new_context
    
    def get_object(self, type_name):
        """Get object of the given type from context."""
        if type_name in self.objects:
            return self.objects[type_name]
        if self._prev_context:
            return self._prev_context.get_object(type_name)
        return None
    
    def restore(self):
        """Restore the previous context."""
        return self._prev_context
```

## 4. Specialized Visitor Methods

While most nodes can be handled generically, some require specialized processing:

### 4.1 Name Transformation Methods

```python
def visit_camel_case_value(self, node):
    """Process a camel case name, combining multiple identifiers."""
    tokens = [token.getText() for token in node.getChildren() if self._is_identifier(token)]
    return self._combine_to_camel_case(tokens, upper_first=False)

def visit_upper_camel_value(self, node):
    """Process an upper camel case name."""
    tokens = [token.getText() for token in node.getChildren() if self._is_identifier(token)]
    return self._combine_to_camel_case(tokens, upper_first=True)

def _combine_to_camel_case(self, tokens, upper_first=False):
    """Helper to convert tokens to camelCase or UpperCamelCase."""
    if not tokens:
        return ""
    
    result = []
    for i, token in enumerate(tokens):
        if i == 0 and not upper_first:
            result.append(token.lower())
        else:
            result.append(token.capitalize())
    
    return "".join(result)
```

### 4.2 Boolean Field Handling

```python
def visit_boolean_value(self, node):
    """Process boolean values with metadata-based representation."""
    token_text = node.getText().lower()
    
    # Get metadata from context if available
    field_info = self._get_current_field_metadata()
    
    if field_info and "presentable_true" in field_info:
        if token_text == field_info["presentable_true"].lower():
            return True
        elif token_text == field_info["presentable_false"].lower():
            return False
    
    # Default handling
    return token_text in ("true", "yes", "1")
```

### 4.3 Container Type Processing

```python
def visit_list_value(self, node):
    """Process list values."""
    elements = []
    
    # Skip brackets and comma tokens, collect only values
    for child in node.getChildren():
        if not self._is_separator(child):
            value = self.visit(child)
            if value is not None:
                elements.append(value)
    
    return elements
```

## 5. Object Creation and Assignment

### 5.1 Object Creation

```python
def _create_object(self, class_type):
    """Create an instance of the appropriate class."""
    class_map = {
        "model": LiterateDataModel,
        "subject": Subject,
        "class_": Class,
        "attribute": Attribute,
        "data_type": DataType,
        # ... other mappings
    }
    
    if class_type in class_map:
        return class_map[class_type]()
    
    # Default fallback
    return None
```

### 5.2 Parent Collection Assignment

```python
def _add_to_parent_if_needed(self, new_object, class_type):
    """Add the new object to its parent's collection if appropriate."""
    parent_field_map = {
        "subject": {"model": "subjects", "subject": "subjects"},
        "class_": {"subject": "classes", "model": "classes"},
        "attribute": {"class_": "attributes", "attribute_section": "attributes"},
        # ... other mappings
    }
    
    if class_type not in parent_field_map:
        return
    
    for parent_type, field_name in parent_field_map[class_type].items():
        parent = self.context.get_object(parent_type)
        if parent:
            # Get or create the collection
            collection = getattr(parent, field_name, None)
            if collection is None:
                collection = []
                setattr(parent, field_name, collection)
            
            # Add the new object
            collection.append(new_object)
            break
```

## 6. Implementation for Literate Model

For the Literate model specifically, the following specialized visitors would be needed:

### 6.1 Required Specialized Visitors

1. **Class Node Visitors**
   - `visit_literate_data_model` - Create LiterateDataModel instance
   - `visit_subject` - Create Subject instance
   - `visit_class_` - Create Class instance
   - `visit_attribute` - Create Attribute instance
   - `visit_data_type` - Process abstract DataType selection
   - `visit_base_data_type` - Create BaseDataType instance
   - `visit_list_data_type` - Create ListDataType instance
   - `visit_set_data_type` - Create SetDataType instance
   - `visit_mapping_data_type` - Create MappingDataType instance

2. **Value Node Visitors**
   - `visit_component_name_value` - Process component names
   - `visit_camel_case_value` - Process camelCase values
   - `visit_upper_camel_value` - Process UpperCamelCase values
   - `visit_lower_camel_value` - Process lowerCamelCase values
   - `visit_data_type_clause_value` - Process data type clauses
   - `visit_formula_value` - Process formula values
   - `visit_constraint_value` - Process constraint values
   - `visit_elaboration_value` - Process elaboration content
   - `visit_annotation_value` - Process annotations

3. **List Processing**
   - `visit_list_value` - Process generic list values
   - `visit_constraints_value` - Process constraint lists
   - `visit_classes_value` - Process class reference lists
   - `visit_attributes_value` - Process attribute lists

### 6.2 Extension Points

The visitor framework should provide clear extension points for customization:

1. **Custom Transformers**
   - Allow registering custom transformer functions for specific node types
   - Support pre- and post-processing hooks for standard transformations

2. **Metadata-Based Processing**
   - Enable class-level configuration via Meta classes
   - Support field-level metadata to drive visitor behavior

3. **Model-Specific Overrides**
   - Allow model-specific visitor classes
   - Support mixing in specialized behavior

## 7. Integration with META definitions

Meta classes can be used to provide visitor customization:

```python
@dataclass
class CamelCase:
    content: str
    
    class Meta:
        # Specify visitor method to use
        visitor_method = "camel_case_transform"
        
        # Provide custom transformation logic
        @staticmethod
        def camel_case_transform(tokens):
            return "".join(tokens[0].lower() + "".join(t.capitalize() for t in tokens[1:]))
```

This approach allows models to specify their own transformation logic while maintaining the generic visitor structure.

## 8. Examples

### 8.1 Processing a Simple Class Definition

Input:
```
_ **MyClass** - A sample class
    name: "TestClass"
    abbreviation: "TC" 
    is_value_type: true
```

Visitor processing sequence:
1. Visit `class_` node:
   - Create new Class instance
   - Push to context
2. Visit `class_name_value` node:
   - Get component_name
   - Assign to Class.name
3. Visit `class_abbreviation_value` node:
   - Get string value
   - Assign to Class.abbreviation
4. Visit `class_is_value_type_value` node:
   - Get boolean value
   - Assign to Class.is_value_type
5. Visit `class_one_liner_value` node:
   - Get string "A sample class"
   - Assign to Class.one_liner
6. Complete Class object and return

### 8.2 Processing a Data Type Hierarchy

Input:
```
List of Customer Reference
```

Visitor processing sequence:
1. Visit `list_data_type` node:
   - Create ListDataType instance
2. Visit `list_data_type_element_type_value` node:
   - Process "Customer Reference"
   - Create BaseDataType with class_="Customer", is_value=false
   - Assign to ListDataType.element_type
3. Complete ListDataType object and return

### 8.3 Extended Example: Attribute with Derivation

To illustrate how our visitor processes complex structures with inheritance, let's consider an attribute with a derivation. This example demonstrates the visitor handling of nested objects and inheritance hierarchies.

#### Relevant Model Classes

```python
@dataclass
class Component:
    name: ComponentName
    one_liner: Optional[OneLiner] = None
    # other Component fields...

@dataclass
class Attribute(Component):
    data_type_clause: Optional[DataTypeClause] = None
    derivation: Optional[Derivation] = None
    # other Attribute fields...

@dataclass
class Formula:
    english: Optional[str] = None
    code: Optional[CodeExpression] = None
    message: Optional[str] = None

@dataclass
class Derivation(Formula):
    # Inherits all fields from Formula
    pass
```

#### Input Text

```
- **calculateTotal** - Calculates order total (required Order)
    derivation:
        english: "Sum of all line item totals"
        code: "return order.items.reduce((sum, item) => sum + item.price * item.quantity, 0)"
```

#### Simplified Parse Tree

```
attribute
├── attribute_header
│   ├── DASH
│   ├── ASTERISK
│   ├── attribute_name_value
│   │   └── component_name
│   └── ...
└── attribute_body
    ├── attribute_derivation_clause
    │   ├── DERIVATION
    │   ├── COLON
    │   └── attribute_derivation_value
    │       └── derivation
    │           ├── formula_english_clause
    │           │   ├── ENGLISH
    │           │   ├── COLON
    │           │   └── formula_english_value
    │           │       └── "Sum of all line item totals"
    │           └── formula_code_clause
    │               ├── CODE
    │               ├── COLON
    │               └── formula_code_value
    │                   └── "return order.items.reduce((sum, item) => sum + item.price * item.quantity, 0)"
```

#### Visitor Processing Sequence

Let's walk through how our generic visitor processes this structure:

1. **Visit `attribute` node**:
   ```python
   def visit(self, node):
       node_name = self._get_node_name(node)  # "attribute"
       
       # Is class node without suffix -> Handle object creation
       if self._is_class_node(node_name):  # True for "attribute"
           return self._handle_class_node(node, node_name)
   ```

2. **In `_handle_class_node`**:
   ```python
   def _handle_class_node(self, node, node_name):
       # Create Attribute instance
       new_object = self.class_registry["attribute"]()  # new Attribute()
       
       # Store in context
       old_context = self.context
       self.context = self.context.with_object("attribute", new_object)
       
       # Add to parent collection (e.g., to Class.attributes if in Class context)
       self._add_to_parent_if_needed(new_object, "attribute")
       
       # Visit children (header and body)
       self.visitChildren(node)
       
       # Restore context
       self.context = old_context
       
       return new_object
   ```

3. **Process `attribute_header` node** (via visitChildren):
   - Generic visitor processes name_value, one_liner_value, etc.
   - Each *_value node sets the corresponding property on the Attribute object

4. **Visit `attribute_derivation_clause` node**:
   ```python
   def visit(self, node):
       node_name = "attribute_derivation_clause"
       
       # Not a class node, not a value node -> visit children
       return self.visitChildren(node)
   ```

5. **Visit `attribute_derivation_value` node**:
   ```python
   def visit(self, node):
       node_name = "attribute_derivation_value"
       
       # Is value node -> Handle field assignment
       if self._is_value_node(node_name):  # True for "*_value"
           return self._handle_value_node(node, node_name)
   ```

6. **In `_handle_value_node` for derivation value**:
   ```python
   def _handle_value_node(self, node, node_name):
       # Extract class and field names from pattern
       class_name, field_name = self._parse_value_node_name(node_name)
       # class_name = "attribute", field_name = "derivation"
       
       # Get Attribute from context
       target_obj = self.context.get_object(class_name)  # Gets Attribute instance
       
       # Get value by visiting children (processes the derivation node)
       value = self.visitChildren(node)  # This will create a Derivation object
       
       # Assign to field on Attribute
       setattr(target_obj, field_name, value)  # attribute.derivation = value
       
       return value
   ```

7. **Visit `derivation` node**:
   - Similar to step 1-2, creates a Derivation object
   - Pushes new context with the Derivation object
   - Visits children to process Formula fields
   - Restores context

8. **Visit `formula_english_clause` node**:
   - Similar to step 4, just visits children

9. **Visit `formula_english_value` node**:
   ```python
   def _handle_value_node(self, node, node_name):
       # class_name = "formula", field_name = "english"
       target_obj = self.context.get_object(class_name)  # Gets Derivation instance
       value = self.visitChildren(node)  # Gets string value
       setattr(target_obj, field_name, value)  # derivation.english = value
   ```

10. Similar process for `formula_code_value`

11. **Result**:
    - Attribute object created with name="calculateTotal", one_liner="Calculates order total"
    - Derivation object created as attribute.derivation
    - Derivation.english = "Sum of all line item totals"
    - Derivation.code = "return order.items.reduce(...)..."

#### Key Observations

1. **Generic Processing**: Notice how the same generic `visit()` method handles all nodes based on naming patterns
2. **Inheritance Handling**: Derivation inherits from Formula, but we don't need special code - fields are simply assigned to the Derivation instance
3. **Minimal Specialized Code**: The only specialized methods needed would be for transforming raw values (like camelCase conversion)
4. **Context Stack**: The context stack keeps track of the current object being populated at each level

This example demonstrates how the visitor's generic handling can process complex nested structures with inheritance without requiring specialized visitor methods for each node type.

## 9. Implementation Guidelines

1. **Naming Conventions**
   - Class nodes: snake_case of class name
   - Value nodes: `{class}_{field}_value`
   - Rule method names: `visit_{node_name}`

2. **Error Handling**
   - Provide clear error messages for parsing failures
   - Include source position information
   - Validate object completeness after construction

3. **Performance Considerations**
   - Minimize object creation during visiting
   - Use context effectively to reduce lookups
   - Consider lazy evaluation for complex transformations

4. **Testing Strategy**
   - Test with complete grammar examples
   - Verify object structure matches input
   - Test edge cases (empty values, maximal nesting)

This specification provides a streamlined approach to visiting parse trees generated from Presentable Model grammars, focusing on generic processing with minimal specialized code.
