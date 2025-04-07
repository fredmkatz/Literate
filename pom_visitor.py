"""
Visitor for Presentable Object Models.

This module provides classes for visiting parse trees generated from
Presentable Object Model grammars and constructing model objects.
"""

import inspect
from dataclasses import is_dataclass, fields, Field
from typing import Dict, List, Any, Optional, Type, get_type_hints
import re

try:
    from lark import Transformer, Tree, Token
    from lark.visitors import Interpreter
except ImportError:
    # Fallbacks for when lark is not available
    class Transformer:
        pass
    class Tree:
        def __init__(self, data, children, meta=None):
            self.data = data
            self.children = children
            self.meta = meta
    class Token:
        def __init__(self, type_, value, meta=None):
            self.type = type_
            self.value = value
            self.meta = meta
    
    # Dummy Interpreter
    class Interpreter:
        def visit(self, tree):
            """Visit a node."""
            return self._visit_tree(tree)
        
        def _visit_tree(self, tree):
            if isinstance(tree, Tree):
                method_name = "visit_" + tree.data
                if hasattr(self, method_name):
                    return getattr(self, method_name)(tree)
                else:
                    return self.visit_children(tree)
            else:
                return self.visit_token(tree)
        
        def visit_children(self, tree):
            """Visit all children of a node."""
            return [self.visit(child) for child in tree.children]
        
        def visit_token(self, token):
            """Visit a leaf node."""
            return token.value

from pom_diagnostics import DiagnosticRegistry, Diagnostic, DiagnosticSeverity, SourceLocation
from pom_utils import to_snake_case, to_upper_camel, to_lower_camel

class VisitContext:
    """
    Context tracker for the visitor pattern.
    
    Maintains a stack of objects being constructed and their hierarchical
    relationships.
    """
    
    def __init__(self, prev_context=None):
        """
        Initialize the context.
        
        Args:
            prev_context: Previous context to restore to when done
        """
        self._prev_context = prev_context
        self.objects = {}  # Maps type names to objects
    
    def with_object(self, type_name, obj):
        """
        Create a new context with the given object.
        
        Args:
            type_name: Type name of the object
            obj: The object to add to context
            
        Returns:
            New context with object added
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
            Object of the specified type or None
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
            Previous context
        """
        return self._prev_context
    
    def __str__(self):
        """String representation for debugging."""
        result = "VisitContext{\n"
        for type_name, obj in self.objects.items():
            result += f"  {type_name}: {obj}\n"
        result += "}"
        return result

class PomVisitor(Interpreter):
    """
    Generic visitor for Presentable Model parse trees.
    
    Uses a naming pattern-based approach to minimize specialized code
    for specific node types.
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
        self.object_registry = {}  # Maps object IDs to constructed objects
    
    def _build_class_registry(self, model_module):
        """
        Build registry of model classes from the provided module.
        
        Args:
            model_module: Module containing model classes
            
        Returns:
            Dictionary mapping rule names to class objects
        """
        registry = {}
        for name, obj in inspect.getmembers(model_module):
            if inspect.isclass(obj) and is_dataclass(obj):
                # Map snake_case name to class
                registry[to_snake_case(name)] = obj
        return registry
    
    def visit(self, tree):
        """
        Visit a parse tree node with generic handling based on node name pattern.
        
        Args:
            tree: Parse tree node
            
        Returns:
            Resulting value or object
        """
        # Get node name (rule name) for pattern matching
        node_name = tree.data if isinstance(tree, Tree) else None
        
        if node_name is None:
            # Token or other leaf node
            return self._visit_token(tree)
        
        # Object creation for class nodes (no suffix)
        if self._is_class_node(node_name):
            return self._handle_class_node(tree, node_name)
            
        # Field value assignment for *_value nodes
        elif self._is_value_node(node_name):
            return self._handle_value_node(tree, node_name)
            
        # Default to normal child visiting for other nodes
        return self.visit_children(tree)
    
    def _is_class_node(self, node_name):
        """
        Check if a node represents a class (no special suffix).
        
        Args:
            node_name: Name of the node
            
        Returns:
            True if this is a class node
        """
        # Class nodes have names matching class names in snake_case
        if node_name in self.class_registry:
            return True
        
        # Check for specific naming patterns like "base_data_type"
        return (not self._is_value_node(node_name) and
                not node_name.endswith('_clause') and
                not node_name.endswith('_header') and
                not node_name.endswith('_body'))
    
    def _is_value_node(self, node_name):
        """
        Check if a node represents a field value.
        
        Args:
            node_name: Name of the node
            
        Returns:
            True if this is a value node
        """
        return node_name.endswith('_value')
    
    def _handle_class_node(self, tree, node_name):
        """
        Create a new object for a class node and set up context.
        
        Args:
            tree: Parse tree node
            node_name: Name of the node
            
        Returns:
            Created object
        """
        # Get the class type
        class_type = self._get_class_type(node_name)
        if not class_type:
            # Unknown class type - just visit children
            self.diagnostics.add_warning(
                f"Unknown class type: {node_name}",
                self._get_location(tree)
            )
            return self.visit_children(tree)
        
        # Create the object
        new_object = self._create_object(class_type)
        if not new_object:
            # Failed to create object - just visit children
            self.diagnostics.add_error(
                f"Failed to create object of type {class_type.__name__}",
                self._get_location(tree)
            )
            return self.visit_children(tree)
        
        # Store in context stack
        old_context = self.context
        self.context = self.context.with_object(node_name, new_object)
        
        # Add to parent collection if appropriate
        self._add_to_parent_if_needed(new_object, node_name)
        
        # Visit children to populate the object
        self.visit_children(tree)
        
        # Restore context
        self.context = old_context
        
        # Store in object registry
        self.object_registry[id(new_object)] = new_object
        
        return new_object
    
    def _handle_value_node(self, tree, node_name):
        """
        Process a value node and assign to the appropriate field.
        
        Args:
            tree: Parse tree node
            node_name: Name of the node
            
        Returns:
            Processed value
        """
        # Extract class and field names from the node name pattern
        class_name, field_name = self._parse_value_node_name(node_name)
        
        # Get the target object from context
        target_obj = self.context.get_object(class_name)
        
        # Not finding the object in context is normal when processing fragments
        # (like just one class or attribute definition)
        if not target_obj:
            return self.visit_children(tree)
        
        # Get value from child nodes
        value = self._process_value(tree, field_name, target_obj)
        
        # Assign value to the appropriate field
        # Note: The return value has no real effect in most cases - the value
        # has already been stored in the target object
        try:
            setattr(target_obj, field_name, value)
        except AttributeError:
            # If the field doesn't exist on the object, that's a serious bug
            # (mismatch between grammar and object model)
            self.diagnostics.add_error(
                f"Bug: Field '{field_name}' does not exist on {class_name} object",
                self._get_location(tree)
            )
        
        return value
    
    def _process_value(self, tree, field_name, target_obj):
        """
        Process a value based on field type and tree structure.
        
        This method tries to process the value intelligently based on
        the expected field type.
        
        Args:
            tree: Parse tree node
            field_name: Name of the field
            target_obj: Target object to assign to
            
        Returns:
            Processed value
        """
        # Check special node types first
        method_name = f"visit_{field_name}_value"
        if hasattr(self, method_name):
            # Use specialized method if available
            return getattr(self, method_name)(tree)
        
        # Get expected field type if available
        field_type = self._get_field_type(target_obj, field_name)
        
        # Check for empty node
        if not tree.children:
            return None
        
        # If only one child, visit it directly
        if len(tree.children) == 1:
            return self.visit(tree.children[0])
        
        # Based on field type, process accordingly
        if self._is_list_type(field_type):
            return self._process_list_value(tree, field_type)
        elif self._is_bool_type(field_type):
            return self._process_boolean_value(tree, field_name, target_obj)
        elif self._is_string_type(field_type):
            return self._process_string_value(tree)
        
        # Default - visit children and return a list
        return self.visit_children(tree)
    
    def _visit_token(self, token):
        """
        Visit a leaf token node.
        
        Args:
            token: Token node
            
        Returns:
            Processed token value
        """
        # Handle different token types
        if hasattr(token, 'value'):
            # Access value property if possible
            value = token.value
        else:
            # Fallback to string conversion
            value = str(token)
        
        # Clean token value
        if isinstance(value, str):
            # Strip quotes from strings
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            # Convert boolean literals
            if value.lower() in ('true', 'yes', '1', 't', 'y'):
                return True
            elif value.lower() in ('false', 'no', '0', 'f', 'n'):
                return False
        
        return value
    
    def _parse_value_node_name(self, node_name):
        """
        Extract class and field names from a value node name.
        
        Args:
            node_name: Node name like "class_name_field_name_value"
            
        Returns:
            Tuple of (class_name, field_name)
        """
        # Extract everything before the last "_value"
        if not node_name.endswith('_value'):
            return None, None
        
        base_name = node_name[:-6]  # Remove "_value"
        
        # Find the field name (last part after underscore)
        parts = base_name.split('_')
        if len(parts) < 2:
            return base_name, ""
        
        field_name = parts[-1]
        class_name = base_name[:-len(field_name)-1]  # Remove field name and underscore
        
        return class_name, field_name
    
    def _get_class_type(self, node_name):
        """
        Get the class type for a node name.
        
        Args:
            node_name: Node name
            
        Returns:
            Class type or None
        """
        if node_name in self.class_registry:
            return self.class_registry[node_name]
        
        # Try to map to a class name
        class_name = to_upper_camel(node_name)
        for name, cls in inspect.getmembers(self.model_module):
            if name == class_name and is_dataclass(cls):
                return cls
        
        return None
    
    def _create_object(self, class_type):
        """
        Create an instance of the specified class.
        
        Args:
            class_type: Class type to create
            
        Returns:
            Created object or None
        """
        try:
            # Create with default values
            return class_type()
        except Exception as e:
            self.diagnostics.add_error(
                f"Error creating {class_type.__name__}: {str(e)}"
            )
            return None
    
    def _add_to_parent_if_needed(self, new_object, node_name):
        """
        Add the new object to its parent's collection if appropriate.
        
        Args:
            new_object: New object to add
            node_name: Node name (class type)
        """
        class_type = self._get_class_type(node_name)
        if not class_type:
            return
        
        # Map known collection fields based on object type
        parent_mappings = self._get_parent_mappings()
        
        if class_type.__name__ not in parent_mappings:
            return
            
        mappings = parent_mappings[class_type.__name__]
        
        # Check each possible parent type and field
        for parent_type, field_name in mappings.items():
            parent_node_name = to_snake_case(parent_type)
            parent = self.context.get_object(parent_node_name)
            
            if parent:
                # Get or create the collection
                collection = getattr(parent, field_name, None)
                if collection is None:
                    collection = []
                    setattr(parent, field_name, collection)
                
                # Add the new object
                collection.append(new_object)
                break
    
    def _get_parent_mappings(self):
        """
        Get mappings of class types to their parent containers.
        
        Returns:
            Dictionary of class name to parent type and field mappings
        """
        # Return cached value if available
        if hasattr(self, '_parent_mappings'):
            return self._parent_mappings
        
        # Build the mappings by analyzing the model classes
        mappings = {}
        
        for name, cls in inspect.getmembers(self.model_module):
            if not inspect.isclass(cls) or not is_dataclass(cls):
                continue
                
            # Check each field for collection types
            for field_obj in fields(cls):
                field_type = field_obj.type
                
                # Skip non-collection fields
                if not self._is_list_type(field_type):
                    continue
                
                # Get the element type
                element_type = self._get_list_element_type(field_type)
                if not element_type:
                    continue
                
                # Get the element class name
                element_name = self._get_type_name(element_type)
                if not element_name:
                    continue
                
                # Add the mapping
                if element_name not in mappings:
                    mappings[element_name] = {}
                
                mappings[element_name][name] = field_obj.name
        
        # Cache for future use
        self._parent_mappings = mappings
        return mappings
    
    def _get_location(self, tree):
        """
        Get source location from a parse tree node.
        
        Args:
            tree: Parse tree node
            
        Returns:
            SourceLocation object, or None if not available
        """
        if hasattr(tree, 'meta'):
            meta = tree.meta
            line = getattr(meta, 'line', None)
            column = getattr(meta, 'column', None)
            if line is not None and column is not None:
                return SourceLocation(
                    line=line,
                    column=column,
                    length=len(str(tree)) if hasattr(tree, '__str__') else None
                )
        return None
    
    def _get_field_type(self, obj, field_name):
        """
        Get the type of a field.
        
        Args:
            obj: Object containing the field
            field_name: Name of the field
            
        Returns:
            Field type or None
        """
        if not obj or not field_name:
            return None
            
        # Check if it's a dataclass with field information
        if is_dataclass(obj.__class__):
            # Try to get type hints
            try:
                hints = get_type_hints(obj.__class__)
                if field_name in hints:
                    return hints[field_name]
            except (NameError, TypeError):
                pass
                
            # Try to get field object
            if hasattr(obj.__class__, '__dataclass_fields__'):
                fields_dict = obj.__class__.__dataclass_fields__
                if field_name in fields_dict:
                    return fields_dict[field_name].type
        
        return None
    
    def _is_list_type(self, field_type):
        """
        Check if a field type is a list or similar container.
        
        Args:
            field_type: Field type
            
        Returns:
            True if it's a list type
        """
        if not field_type:
            return False
            
        try:
            # Check origin type (for typing.List, etc.)
            origin = getattr(field_type, '__origin__', None)
            return origin is list or str(origin) == "<class 'list'>"
        except (AttributeError, TypeError):
            # Fallback to isinstance check
            return isinstance(field_type, type) and issubclass(field_type, list)
    
    def _is_bool_type(self, field_type):
        """
        Check if a field type is boolean
        """