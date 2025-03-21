# Presentable Model Visitor Specification

## 6. Model Visitor

### 6.1 Base Visitor Class

The visitor processes Lark parse trees to construct object models, handling inheritance and field specialization correctly:

```python
# pom_visitor.py
import inspect
from dataclasses import is_dataclass, fields, field, MISSING
from typing import Dict, List, Any, Optional, Set, Union, get_origin, get_args
import re

from lark import Tree, Token
from lark.visitors import Visitor

from pom_diagnostics import DiagnosticRegistry, Diagnostic, SourceLocation, DiagnosticSeverity

class VisitContext:
    """Context tracker for the visitor pattern."""
    
    def __init__(self, prev_context=None):
        """
        Initialize a new context.
        
        Args:
            prev_context: Previous context to restore to when done
        """
        self._prev_context = prev_context
        self.objects = {}  # Maps type names to objects
    
    def with_object(self, type_name, obj):
        """
        Create a new context with the given object.
        
        Args:
            type_name: Type name for the object
            obj: Object to add to context
            
        Returns:
            New context containing the object
        """
        new_context = VisitContext(self)
        new_context.objects[type_name] = obj
        return new_context
    
    def get_object(self, type_name):
        """
        Get object of the given type from context.
        
        Args:
            type_name: Type name to look for
            
        Returns:
            Object of that type, or None if not found
        """
        if type_name in self.objects:
            return self.objects[type_name]
        if self._prev_context:
            return self._prev_context.get_object(type_name)
        return None
    
    def restore(self):
        """
        Restore the previous context.
        
        Returns:
            Previous context, or None if there wasn't one
        """
        return self._prev_context

class PomVisitor(Visitor):
    """
    Visitor for Presentable Object Model parse trees.
    Creates model objects from parse trees.
    """
    
    def __init__(self, model_module, diagnostics=None):
        """
        Initialize the visitor.
        
        Args:
            model_module: Module containing model classes
            diagnostics: Optional diagnostic registry
        """
        super().__init__()
        self.model_module = model_module
        self.diagnostics = diagnostics or DiagnosticRegistry()
        self.context = VisitContext()
        self.class_registry = self._build_class_registry(model_module)
    
    def _build_class_registry(self, model_module):
        """
        Build registry of model classes from the provided module.
        
        Args:
            model_module: Module containing model classes
            
        Returns:
            Dictionary mapping class names to class objects
        """
        registry = {}
        for name, obj in inspect.getmembers(model_module):
            if inspect.isclass(obj) and is_dataclass(obj):
                # Map both normal and snake_case names to class
                registry[name] = obj
                registry[self._to_snake_case(name)] = obj
        return registry
    
    def visit(self, tree):
        """
        Visit a parse tree node with smart handling.
        
        Args:
            tree: Parse tree node
            
        Returns:
            Constructed model object or component
        """
        # Extract node information
        if isinstance(tree, Tree):
            node_name = tree.data
        elif isinstance(tree, Token):
            # Handle token visits directly
            return self._process_token(tree)
        else:
            # Unknown node type
            return None
        
        # Class node handling (creating new objects)
        if self._is_class_node(node_name):
            return self._handle_class_node(tree, node_name)
        
        # Field value handling
        elif self._is_value_node(node_name):
            return self._handle_value_node(tree, node_name)
        
        # Default handling for other nodes
        return self._default_visit(tree, node_name)
    
    def _process_token(self, token):
        """
        Process a token node.
        
        Args:
            token: Token node
            
        Returns:
            Processed token value
        """
        # Attempt to convert to appropriate type
        value = token.value
        
        # Return the token value
        return value
    
    def _handle_class_node(self, tree, node_name):
        """
        Handle a class node by creating a new object.
        
        Args:
            tree: Parse tree node
            node_name: Name of the node
            
        Returns:
            Created object
        """
        # Get the class type
        class_type = self._get_class_type(node_name)
        if not class_type:
            self.diagnostics.add_error(
                f"Unknown class type: {node_name}",
                self._get_location(tree),
                code="UNKNOWN_CLASS"
            )
            return None
            
        # Create the object
        new_object = self._create_object(class_type)
        if not new_object:
            self.diagnostics.add_error(
                f"Failed to create object of type: {class_type}",
                self._get_location(tree),
                code="OBJECT_CREATION_FAILED"
            )
            return None
        
        # Store in context stack
        old_context = self.context
        self.context = self.context.with_object(node_name, new_object)
        
        # Add to parent collection if appropriate
        self._add_to_parent_if_needed(new_object, node_name)
        
        # Visit children to populate the object
        for child in tree.children:
            self.visit(child)
        
        # Restore context
        self.context = old_context
        
        return new_object
    
    def _handle_value_node(self, tree, node_name):
        """
        Handle a value node by assigning to a field.
        
        Args:
            tree: Parse tree node
            node_name: Name of the node
            
        Returns:
            Processed value
        """
        # Extract class and field names
        class_name, field_name = self._parse_value_node_name(node_name)
        
        # Get target object
        target_obj = self.context.get_object(class_name)
        if not target_obj:
            # Not an error - might be processing a fragment
            return self._process_value_children(tree)
        
        # Check if field has already been set (duplicate)
        if hasattr(target_obj, field_name) and getattr(target_obj, field_name) is not None:
            current_value = getattr(target_obj, field_name)
            
            # Special handling for list fields - append instead of error
            if isinstance(current_value, list):
                value = self._process_value_children(tree)
                if isinstance(value, list):
                    current_value.extend(value)
                else:
                    current_value.append(value)
                return value
            else:
                # Create diagnostic for duplicate field
                self.diagnostics.add_warning(
                    f"Field '{field_name}' appears multiple times in {class_name}",
                    self._get_location(tree),
                    element=target_obj,
                    code="DUPLICATE_FIELD"
                )
                # Continue with last value wins semantics
        
        # Process value from children
        value = self._process_value_children(tree)
        
        # Assign value to the field
        try:
            setattr(target_obj, field_name, value)
        except Exception as e:
            # Create diagnostic for assignment error
            self.diagnostics.add_error(
                f"Failed to assign value to field '{field_name}': {str(e)}",
                self._get_location(tree),
                element=target_obj,
                code="ASSIGNMENT_ERROR"
            )
        
        return value
    
    def _process_value_children(self, tree):
        """
        Process the children of a value node.
        
        Args:
            tree: Parse tree node
            
        Returns:
            Processed value
        """
        # Special case: no children
        if not tree.children:
            return None
            
        # Special case: single child
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
            
        # Multiple children - collect values
        values = [self.visit(child) for child in tree.children]
        
        # Attempt to join string fragments
        if all(isinstance(v, str) for v in values):
            return " ".join(values)
            
        # Return as list
        return values
    
    def _default_visit(self, tree, node_name):
        """
        Default visit method for other node types.
        
        Args:
            tree: Parse tree node
            node_name: Name of the node
            
        Returns:
            Result of visiting children
        """
        # Just process each child and return last result
        result = None
        for child in tree.children:
            result = self.visit(child)
        return result
    
    def _get_class_type(self, node_name):
        """
        Get the class type for a node name.
        
        Args:
            node_name: Name of the node
            
        Returns:
            Class type, or None if not found
        """
        # Try exact match first
        if node_name in self.class_registry:
            return self.class_registry[node_name]
            
        # Try with converted name
        class_name = self._to_class_name(node_name)
        if class_name in self.class_registry:
            return self.class_registry[class_name]
            
        return None
    
    def _create_object(self, class_type):
        """
        Create an instance of the given class.
        
        Args:
            class_type: Class to instantiate
            
        Returns:
            New instance, or None if creation fails
        """
        try:
            # Create instance with default values
            return class_type()
        except Exception as e:
            self.diagnostics.add_error(
                f"Failed to create {class_type.__name__} instance: {str(e)}",
                code="INSTANTIATION_ERROR"
            )
            return None
    
    def _add_to_parent_if_needed(self, new_object, class_type):
        """
        Add the new object to its parent's collection if appropriate.
        
        Args:
            new_object: Newly created object
            class_type: Type of the object
        """
        # This is handled automatically through context and field assignment
        # No need for explicit collection management
        pass
    
    def _is_class_node(self, node_name):
        """
        Check if a node name represents a class.
        
        Args:
            node_name: Name of the node
            
        Returns:
            True if this is a class node, False otherwise
        """
        # Class nodes are not suffixed
        return (not self._is_value_node(node_name) and 
                not self._is_clause_node(node_name) and
                not node_name.endswith('_header') and
                not node_name.endswith('_body'))
    
    def _is_value_node(self, node_name):
        """
        Check if a node name represents a value.
        
        Args:
            node_name: Name of the node
            
        Returns:
            True if this is a value node, False otherwise
        """
        # Value nodes end with _value
        return node_name.endswith('_value')
    
    def _is_clause_node(self, node_name):
        """
        Check if a node name represents a clause.
        
        Args:
            node_name: Name of the node
            
        Returns:
            True if this is a clause node, False otherwise
        """
        # Clause nodes end with _clause
        return node_name.endswith('_clause')
    
    def _parse_value_node_name(self, node_name):
        """
        Parse a value node name into class and field components.
        
        Args:
            node_name: Name of the node (e.g., 'class_name_value')
            
        Returns:
            Tuple of (class_name, field_name)
        """
        # Remove _value suffix
        name_without_suffix = node_name[:-6]
        
        # Find the last underscore to split class and field
        last_underscore = name_without_suffix.rfind('_')
        if last_underscore == -1:
            # No underscore - treat whole name as class
            return name_without_suffix, "value"
            
        class_name = name_without_suffix[:last_underscore]
        field_name = name_without_suffix[last_underscore+1:]
        
        return class_name, field_name
    
    def _get_location(self, node):
        """
        Get source location from a parse tree node.
        
        Args:
            node: Parse tree node
            
        Returns:
            SourceLocation object, or None if not available
        """
        if hasattr(node, 'meta'):
            line = getattr(node.meta, 'line', None)
            column = getattr(node.meta, 'column', None)
            if line is not None and column is not None:
                return SourceLocation(
                    line=line,
                    column=