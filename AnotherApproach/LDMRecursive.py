import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
import sys

# Import your model classes
from Lit_01 import (
    LDM, SubjectB, SubjectC, SubjectD, SubjectE,
    Class, Attribute, AttributeSection, Component,
    OneLiner, Paragraph, Annotation, 
    DataType, BaseDataType, ListDataType, SetDataType, MappingDataType,
    DataTypeClause, ValueType, ReferenceType,
    CamelCase, UpperCamel, LowerCamel
)

class ParseError(Exception):
    """Custom error for parsing issues with location information."""
    def __init__(self, message, line_number=None, line_content=None):
        self.message = message
        self.line_number = line_number
        self.line_content = line_content
        error_location = f" at line {line_number}" if line_number is not None else ""
        error_content = f"\n> {line_content}" if line_content is not None else ""
        super().__init__(f"{message}{error_location}{error_content}")

class LiterateParser:
    """
    Recursive descent parser for Literate Data Models.
    This parser reads Literate syntax and builds a model object.
    """
    
    def __init__(self, text):
        """Initialize with the text to parse."""
        self.text = text
        self.lines = text.split('\n')
        self.line_index = 0
        self.current_line = ""
        self.model = None
        self.current_subject = None
        self.current_class = None
        self.current_attribute = None
        self.current_attribute_section = None
    
    def create_paragraph(self, text):
        """Create a Paragraph object safely."""
        try:
            # Create paragraph with proper handling of input/output
            return Paragraph(output=text)
        except Exception as e:
            print(f"Error creating Paragraph: {e}")
            # Fallback
            p = Paragraph(output="")
            p.content = text
            return p
    
    def create_one_liner(self, text):
        """Create an OneLiner properly."""
        if not text:
            return None
            
        # Create without arguments and set properties manually
        one_liner = OneLiner()
        one_liner.input = text
        one_liner.content = text.replace("<<<", "").replace(">>>", "")
        return one_liner    
    
    def parse(self) -> LDM:
        """Parse the input text and return a Literate Data Model."""
        try:
            # Start with a top-level model
            print("creating model")
            # model_name = UpperCamel("Model")
            # print("modelname is ", model_name)
            self.model = LDM("TheModel")
            self.current_subject = self.model
            
            # Process the input line by line
            while self.line_index < len(self.lines):
                self.current_line = self.lines[self.line_index].strip()
                
                # Skip empty lines
                if not self.current_line:
                    self.line_index += 1
                    continue
                
                # Check for section header
                if self.is_section_header():
                    self.parse_section()
                
                # Check for class definition
                elif self.is_class_header():
                    print("found class header")
                    self.parse_class()
                
                # Check for attribute section
                elif self.is_attribute_section_header():
                    self.parse_attribute_section()
                
                # Check for attribute
                elif self.is_attribute_header():
                    self.parse_attribute()
                
                # Other line - could be a field, annotation, etc.
                else:
                    self.parse_component_field()
                    self.line_index += 1
            
            return self.model
            
        except ParseError as e:
            # Pass through parse errors
            raise
        except Exception as e:
            # Convert other exceptions to parse errors
            raise ParseError(
                f"Unexpected error: {str(e)}", 
                self.line_index + 1, 
                self.current_line
            ) from e
    
    def is_section_header(self) -> bool:
        """Check if the current line is a section header."""
        return self.current_line.startswith('#')
    
    def is_class_header(self) -> bool:
        """Check if the current line is a class header."""
        return self.current_line.startswith('_') and not self.current_line.startswith('__')
    
    def is_attribute_section_header(self) -> bool:
        """Check if the current line is an attribute section header."""
        return self.current_line.startswith('__')
    
    def is_attribute_header(self) -> bool:
        """Check if the current line is an attribute header."""
        return self.current_line.startswith('-')
    
    def parse_section(self):
        """Parse a section header and its contents."""
        line = self.current_line
        
        # Determine section level by counting #
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break
        
        # Extract section name and one-liner
        pattern = r'^#+\s+([^-]+)(?:\s+-\s+(.+))?$'
        match = re.match(pattern, line)
        
        if not match:
            raise ParseError(
                "Invalid section header format", 
                self.line_index + 1, 
                line
            )
        
        # Get name and optional one-liner
        name_text = match.group(1).strip()
        one_liner_text = match.group(2).strip() if match.group(2) else None
        
        # Create name and one-liner objects
        name = UpperCamel(name_text)
        one_liner = self.create_one_liner(one_liner_text) if one_liner_text else None
        
        # Create appropriate subject based on level
        if level == 1:
            # Top level - update the model
            self.model.name = name
            self.model.one_liner = one_liner
            self.current_subject = self.model
        elif level == 2:
            # Create SubjectB
            subject = SubjectB(name=name, one_liner=one_liner)
            self.model.subjects.append(subject)
            self.current_subject = subject
        elif level == 3:
            # Create SubjectC
            if not isinstance(self.current_subject, (SubjectB, LDM)):
                raise ParseError(
                    f"Level 3 section must be inside a level 2 section", 
                    self.line_index + 1, 
                    line
                )
            subject = SubjectC(name=name, one_liner=one_liner)
            self.current_subject.subjects.append(subject)
            self.current_subject = subject
        elif level == 4:
            # Create SubjectD
            if not isinstance(self.current_subject, (SubjectC, SubjectB, LDM)):
                raise ParseError(
                    f"Level 4 section must be inside a level 3 or higher section", 
                    self.line_index + 1, 
                    line
                )
            subject = SubjectD(name=name, one_liner=one_liner)
            self.current_subject.subjects.append(subject)
            self.current_subject = subject
        elif level == 5:
            # Create SubjectE
            if not isinstance(self.current_subject, (SubjectD, SubjectC, SubjectB, LDM)):
                raise ParseError(
                    f"Level 5 section must be inside a level 4 or higher section", 
                    self.line_index + 1, 
                    line
                )
            subject = SubjectE(name=name, one_liner=one_liner)
            self.current_subject.subjects.append(subject)
            self.current_subject = subject
        
        # Move to the next line
        self.line_index += 1
        
        # Parse the section's elaboration if present
        self.parse_elaboration()
    
    def parse_class(self):
        """Parse a class definition."""
        line = self.current_line
        
        # Extract class name and one-liner
        if "ValueType" in line:
            # Handle ValueType specifically
            pattern = r'^_\s+ValueType:\s+([^-]+)(?:\s+-\s+(.+))?$'
            is_value_type = True
        else:
            pattern = r'^_\s+([^-]+)(?:\s+-\s+(.+))?$'
            is_value_type = False
        
        match = re.match(pattern, line)
        
        if not match:
            raise ParseError(
                "Invalid class header format", 
                self.line_index + 1, 
                line
            )
        
        # Get name and optional one-liner
        name_text = match.group(1).strip()
        one_liner_text = match.group(2).strip() if match.group(2) else None
        
        # Create name and one-liner objects
        print("parsing class name")
        name = UpperCamel(name_text)
        print("parsing class oneliner")

        one_liner = self.create_one_liner(one_liner_text) if one_liner_text else None
        
        # Create the class
        if is_value_type:
            cls = ValueType(name=name, one_liner=one_liner)
        else:
            cls = Class(name=name, one_liner=one_liner)
        
        # Add class to current subject
        if self.current_subject:
            self.current_subject.classes.append(cls)
        else:
            raise ParseError(
                "Class defined outside of any subject", 
                self.line_index + 1, 
                line
            )
        
        # Set current class
        self.current_class = cls
        self.current_attribute = None
        self.current_attribute_section = None
        
        # Move to the next line
        self.line_index += 1
        
        # Parse class elaboration if present
        self.parse_elaboration()
        
        # Parse class fields until we hit the next component
        while self.line_index < len(self.lines):
            self.current_line = self.lines[self.line_index].strip()
            
            # Skip empty lines
            if not self.current_line:
                self.line_index += 1
                continue
            
            # If we hit a new component or separator, break
            if (self.is_section_header() or 
                self.is_class_header() or 
                self.is_attribute_section_header() or 
                self.is_attribute_header() or
                self.current_line.startswith('=====')):
                break
            
            # Otherwise, parse as class field
            self.parse_class_field()
            self.line_index += 1
    
    # The rest of the class implementation would remain the same...
    
    def parse_attribute_section(self):
        """Parse an attribute section."""
        line = self.current_line
        
        # Extract attribute section name and one-liner
        pattern = r'^__\s+\[([^\]]+)\](?:\s+-\s+(.+))?(?:\s+\((.+)\))?$'
        match = re.match(pattern, line)
        
        if not match:
            raise ParseError(
                "Invalid attribute section header format", 
                self.line_index + 1, 
                line
            )
        
        # Get name, optional one-liner, and required status
        name_text = match.group(1).strip()
        one_liner_text = match.group(2).strip() if match.group(2) else None
        is_required_text = match.group(3) if match.group(3) else "required"
        
        # Create name and one-liner objects
        name = UpperCamel(name_text)
        one_liner = self.create_one_liner(one_liner_text) if one_liner_text else None
        from Lit_01 import IsReallyRequired
        is_required = IsReallyRequired(is_required_text == "required")
        
        # Create the attribute section
        section = AttributeSection(
            name=name, 
            one_liner=one_liner,
            is_required=is_required
        )
        
        # Add section to current class
        if self.current_class:
            self.current_class.attribute_sections.append(section)
        else:
            raise ParseError(
                "Attribute section defined outside of any class", 
                self.line_index + 1, 
                line
            )
        
        # Set current attribute section
        self.current_attribute_section = section
        self.current_attribute = None
        
        # Move to the next line
        self.line_index += 1
        
        # Parse elaboration if present
        self.parse_elaboration()
    
    def parse_attribute(self):
        """Parse an attribute definition."""
        line = self.current_line
        
        # Extract attribute name, one-liner, and data type
        pattern = r'^-\s+\[([^\]]+)\](?:\s+-\s+(.+))?(?:\s+\((.+)\))?$'
        match = re.match(pattern, line)
        
        if not match:
            raise ParseError(
                "Invalid attribute header format", 
                self.line_index + 1, 
                line
            )
        
        # Get name, optional one-liner, and data type
        name_text = match.group(1).strip()
        one_liner_text = match.group(2).strip() if match.group(2) else None
        data_type_text = match.group(3) if match.group(3) else None
        
        # Create name and one-liner objects
        name = LowerCamel(name_text)
        one_liner = self.create_one_liner(one_liner_text) if one_liner_text else None
        
        # Create data type clause if specified
        data_type_clause = None
        if data_type_text:
            data_type_clause = self.parse_data_type_clause(data_type_text)
        
        # Create the attribute
        attribute = Attribute(
            name=name, 
            one_liner=one_liner,
            data_type_clause=data_type_clause
        )
        
        # Add attribute to current class or attribute section
        if self.current_attribute_section:
            self.current_attribute_section.attributes.append(attribute)
        elif self.current_class:
            self.current_class.attributes.append(attribute)
        else:
            raise ParseError(
                "Attribute defined outside of any class or attribute section", 
                self.line_index + 1, 
                line
            )
        
        # Set current attribute
        self.current_attribute = attribute
        
        # Move to the next line
        self.line_index += 1
        
        # Parse elaboration if present
        self.parse_elaboration()
    
    def parse_data_type_clause(self, data_type_text):
        """Parse a data type clause from text."""
        # Check for optional/required prefix
        is_optional = False
        if data_type_text.startswith("optional "):
            is_optional = True
            data_type_text = data_type_text[9:].strip()
        elif data_type_text.startswith("required "):
            data_type_text = data_type_text[9:].strip()
        
        # Parse the data type
        if data_type_text.startswith("List of ") or data_type_text.startswith("list of "):
            # List type
            element_type_text = data_type_text[8:].strip()
            element_type = self.parse_simple_data_type(element_type_text)
            data_type = ListDataType(element_type=element_type)
        elif data_type_text.startswith("Set of ") or data_type_text.startswith("set of "):
            # Set type
            element_type_text = data_type_text[7:].strip()
            element_type = self.parse_simple_data_type(element_type_text)
            data_type = SetDataType(element_type=element_type)
        elif "to" in data_type_text and data_type_text.startswith("Mapping from "):
            # Mapping type
            parts = data_type_text[14:].split(" to ", 1)
            if len(parts) != 2:
                raise ParseError(
                    f"Invalid mapping data type: {data_type_text}", 
                    self.line_index + 1, 
                    self.current_line
                )
            domain_type = self.parse_simple_data_type(parts[0].strip())
            range_type = self.parse_simple_data_type(parts[1].strip())
            data_type = MappingDataType(domain_type=domain_type, range_type=range_type)
        else:
            # Base type
            data_type = self.parse_simple_data_type(data_type_text)
        
        # Create the clause
        from Lit_01 import IsOptional
        return DataTypeClause(
            data_type=data_type,
            is_optional = IsOptional(is_optional)
        )
    
    def parse_simple_data_type(self, type_text):
        """Parse a simple data type from text."""
        # Check for value/reference suffix
        is_value = False
        if " value" in type_text:
            is_value = True
            type_text = type_text.replace(" value", "").strip()
        elif " reference" in type_text:
            type_text = type_text.replace(" reference", "").strip()
        
        # Create base data type
        from Lit_01 import ReferenceOrValue
        return BaseDataType(
            class_name=type_text,
            is_value=ReferenceOrValue(is_value)
        )
    
    def parse_elaboration(self):
        """Parse elaboration text (marked with <<<...>>>)."""
        elaboration_text = ""
        in_elaboration = False
        start_line = self.line_index
        
        while self.line_index < len(self.lines):
            line = self.lines[self.line_index]
            
            # If we're in an elaboration block
            if in_elaboration:
                elaboration_text += line + "\n"
                self.line_index += 1
                
                # Check for end of elaboration
                if ">>>" in line:
                    in_elaboration = False
                    break
            
            # Check for start of elaboration
            elif "<<<" in line:
                in_elaboration = True
                elaboration_text += line + "\n"
                self.line_index += 1
            
            # Not an elaboration line
            else:
                break
        
        # If we found elaboration text, add it to the current component
        if elaboration_text and not in_elaboration:
            paragraph = self.create_paragraph(elaboration_text)
            
            # Add to the current component
            if self.current_attribute:
                self.current_attribute.elaboration.append(paragraph)
            elif self.current_attribute_section:
                self.current_attribute_section.elaboration.append(paragraph)
            elif self.current_class:
                self.current_class.elaboration.append(paragraph)
            elif self.current_subject:
                self.current_subject.elaboration.append(paragraph)
        
        # If we're still in an elaboration block, that's an error
        elif in_elaboration:
            raise ParseError(
                "Unclosed elaboration block", 
                start_line + 1, 
                self.lines[start_line]
            )
    
    def parse_component_field(self):
        """Parse a field belonging to a component."""
        line = self.current_line
        
        # Look for field: value pattern
        field_match = re.match(r'^([a-zA-Z][a-zA-Z0-9_\s]*)\s*:\s*(.+)$', line)
        
        if not field_match:
            # Not a recognized field format
            return
        
        field_name = field_match.group(1).strip()
        field_value = field_match.group(2).strip()
        
        # Handle the field based on its name and current context
        if self.current_attribute:
            self.handle_attribute_field(field_name, field_value)
        elif self.current_attribute_section:
            self.handle_attribute_section_field(field_name, field_value)
        elif self.current_class:
            self.handle_class_field(field_name, field_value)
        elif self.current_subject:
            self.handle_subject_field(field_name, field_value)
    
    def parse_class_field(self):
        """Parse a field belonging to a class."""
        # This is similar to parse_component_field but specifically for class fields
        # that might span multiple lines
        line = self.current_line
        
        # Look for field: value pattern
        field_match = re.match(r'^([a-zA-Z][a-zA-Z0-9_ ]*)\s*:\s*(.+)$', line)
        
        if not field_match:
            # Not a recognized field format
            return
        
        field_name = field_match.group(1).strip().lower()
        field_value = field_match.group(2).strip()
        
        # Handle common class fields
        if field_name in ("subtype of", "subtypeof"):
            self.handle_class_subtypes(field_value)
        elif field_name == "plural":
            self.current_class.plural = UpperCamel(field_value)
        elif field_name == "abbreviation":
            self.current_class.abbreviation = UpperCamel(field_value)
        elif field_name in ("based on", "basedon"):
            self.handle_class_based_on(field_value)
        elif field_name == "dependents":
            self.handle_class_dependents(field_value)
        elif field_name == "where":
            self.current_class.where = self.create_one_liner(field_value)
        else:
            # Handle annotation
            self.handle_annotation(field_name, field_value)
    
    def handle_class_subtypes(self, value_text):
        """Handle subtype_of field for a class."""
        if not self.current_class:
            return
        
        # Parse comma-separated class names
        class_names = [name.strip() for name in value_text.split(',')]
        
        # Create ClassName objects and add to subtypes
        for name in class_names:
            if not name:
                continue
            
            try:
                # Try to create a ClassName object
                from Lit_01 import ClassName
                class_name = ClassName(name=UpperCamel(name))
                self.current_class.subtype_of.append(class_name)
            except Exception as e:
                print(f"Error creating ClassName: {e}")
                # Fallback: just use the UpperCamel name
                self.current_class.subtype_of.append(UpperCamel(name))
    
    def handle_class_based_on(self, value_text):
        """Handle based_on field for a class."""
        if not self.current_class:
            return
        
        # Parse comma-separated class names
        class_names = [name.strip() for name in value_text.split(',')]
        
        # Create ClassName objects and add to based_on
        for name in class_names:
            if not name:
                continue
            
            try:
                # Try to create a ClassName object
                from Lit_01 import ClassName
                class_name = ClassName(name=UpperCamel(name))
                self.current_class.based_on.append(class_name)
            except Exception as e:
                print(f"Error creating ClassName: {e}")
                # Fallback: just use the UpperCamel name
                self.current_class.based_on.append(UpperCamel(name))
    
    def handle_class_dependents(self, value_text):
        """Handle dependents field for a class."""
        if not self.current_class:
            return
        
        # Parse comma-separated class names
        class_names = [name.strip() for name in value_text.split(',')]
        
        # Create ClassName objects and add to dependents
        for name in class_names:
            if not name:
                continue
            
            try:
                # Try to create a ClassName object
                from Lit_01 import ClassName
                class_name = ClassName(name=UpperCamel(name))
                self.current_class.dependents.append(class_name)
            except Exception as e:
                print(f"Error creating ClassName: {e}")
                # Fallback: just use the UpperCamel name
                self.current_class.dependents.append(UpperCamel(name))
    
    def handle_annotation(self, label, content):
        """Handle an annotation field."""
        from Lit_01 import Label
        try:
            annotation = Annotation(
                label=Label(name=UpperCamel(label)),
                content=self.create_one_liner(content)
            )
            
            # Add to the current component
            if self.current_attribute:
                self.current_attribute.annotations.append(annotation)
            elif self.current_attribute_section:
                self.current_attribute_section.annotations.append(annotation)
            elif self.current_class:
                self.current_class.annotations.append(annotation)
            elif self.current_subject:
                self.current_subject.annotations.append(annotation)
        except Exception as e:
            print(f"Error creating annotation: {e}")
    
    def handle_attribute_field(self, field_name, field_value):
        """Handle a field belonging to an attribute."""
        # Similar to handle_class_field but for attributes
        pass
    
    def handle_attribute_section_field(self, field_name, field_value):
        """Handle a field belonging to an attribute section."""
        # Similar to handle_class_field but for attribute sections
        pass
    
    def handle_subject_field(self, field_name, field_value):
        """Handle a field belonging to a subject."""
        # Similar to handle_class_field but for subjects
        pass