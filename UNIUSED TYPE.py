def _get_rule_for_type_UNUSED(self, type_):
        """
        Get a rule name for a given type.
        
        Args:
            type_: A type (class, primitive, etc.)
            
        Returns:
            Rule name for that type
        """
        print("get_rule_for_type: ", type_) 
        flogger.infof(f"Type: {type_}")
        if self._is_primitive_type(type_):
            # Primitive type
            if type_ == str:
                return "STRING"
            elif type_ == bool:
                return "BOOLEAN"
            elif type_ in (int, float):
                return "NUMBER"
            else:
                return "value"
                
        elif self._is_class_type(type_):
            flogger.infof(f"Not a primitive -- Type: {type_}")
            # Class type
            if isinstance(type_, str):
                # Handle forward reference as string
                class_name = type_.strip("'")
            else:
                class_name = type_.__name__
                
            return str(UpperCamel(class_name))
            
        elif self._is_list_type(type_):
            # List type - create a generic list rule
            element_type = self._get_list_element_type(type_)
            element_rule = self._get_rule_for_type(element_type)
            return f"list_{element_rule}"
            
        elif self._is_optional_type(type_):
            # Optional type - use the underlying type
            element_type = self._get_optional_element_type(type_)
            return self._get_rule_for_type(element_type)
            
        else:
            # Default
            return "value"
    
    def _is_primitive_typeUNUSED(self, field_type):
        """Check if a type is a primitive type."""
        return field_type in (str, int, float, bool)
    
    def _is_list_typeUNUSED(self, field_type):
        """Check if a type is a list or similar container."""
        
        origin = get_origin(field_type)

        flogger.infof(f"fieldtype = {field_type}, origin == {origin}")
        flogger.infof(f"meta info: {field_type}")
        print_meta_info(field_type)
        return origin is list or str(origin) == "<class 'list'>"
    
    def _is_optional_typeUNUSED(self, field_type):
        """Check if a type is Optional."""
        origin = get_origin(field_type)
        if origin is Union or str(origin) == "<class 'typing.Union'>":
            args = get_args(field_type)
            return type(None) in args or 'NoneType' in str(args)
        return False
    
    def _is_class_typeUNUSED(self, field_type):
        """Check if a type is a custom class type."""
        # Handle forward references in string form
        flogger.infof(f"Field type: {field_type}, is_string: {isinstance(field_type, str)}, is type: {isinstance(field_type, type)}")
        flogger.infof(f"Field type: {field_type}, in hierarchy: {field_type in self.class_hierarchy}, is type: {isinstance(field_type, type)}")
        flogger.infof(f"Field type: {field_type}, repr: {field_type.__repr__()}, is type: {isinstance(field_type, type)}")
        print(self.class_hierarchy.keys())
        if isinstance(field_type, str):
            class_name = field_type.strip("'")
            return class_name in self.class_hierarchy
        
        # Handle actual class types
        return (isinstance(field_type, type) and 
                field_type.__name__ in self.class_hierarchy)
    
    def _get_list_element_typeUNUSED(self, field_type):
        """Get the element type of a list."""
        args = get_args(field_type)
        if args:
            return args[0]
        return Any  # Default if can't determine
    
    def _get_optional_element_typeUNUSED(self, field_type):
        """Get the underlying type of an Optional."""
        args = get_args(field_type)
        # Find the non-None type
        for arg in args:
            if arg is not type(None) and str(arg) != "<class 'NoneType'>":
                return arg
        return Any  # Default if can't determine