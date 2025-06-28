
# ldm_validators_refactored.py
import sys
from typing import List, Any
import ldm.Literate_01 as Literate_01
from ldm.Literate_01 import Diagnostic, OneLiner, Paragraph, SubjectB
from ldm.ldm_validators_generic import validate_fields
from faculty_base import faculty_class, patch_on

from ldm.Literate_01 import Component, Subject, SubjectB, Class, AttributeSection, Attribute, Formula, Constraint, DataTypeClause

# validation_faculty = Faculty()
# patch_on = validation_faculty.patch_on
All_Diagnostics = []

def createError(obj, category, message) -> Diagnostic:
    return createDiagnostic(obj, category, message, severity="Error")

def createWarning(obj, category, message) -> Diagnostic:
    return createDiagnostic(obj, category, message, severity="Warning")

def createDiagnostic(obj, category, message, severity="Error") -> Diagnostic:
    oname_str = ""
    oname = getattr(obj, "name", None)
    if oname:
        oname_str = oname.content
    
    d = Diagnostic(
        severity=severity, 
        category=category, 
        message=Paragraph(message), 
        object_type=obj._type, 
        object_name=oname_str
    )
    obj.diagnostics.append(d)
    All_Diagnostics.append(d)
    return d


@faculty_class
class Validators:
    """Faculty for adding validation methods to LDM classes."""

    def _find_modules(self):
        # Find modules containing Literate_01 classes
        possible_modules = []
        for module_name in sys.modules:
            if 'Literate_01' in module_name:
                module = sys.modules[module_name]
                if hasattr(module, 'SubjectB'):
                    possible_modules.append((module_name, module))
        return possible_modules
    
    @patch_on(Component)
    def validate(self):
        # Base validation for all Components
        if not self.name:
            createError(self, "Missing field", "Name is missing")
        if not self.one_liner:
            createError(self, "Missing field", "Missing oneLiner")
        elif len(str(self.one_liner)) > 90:
            createWarning(self, "Style", f"oneLiner is too long. ({len(str(self.one_liner))} chars).")

    @patch_on(Subject)
    def validate(self):
        # Call parent validation using proper MRO
        super(Subject, self).validate()  # This will call Component.validate
        validate_each(self.classes)
        validate_each(self.subjects)
    
    @patch_on(SubjectB)
    def validate(self):
        # Call parent validation using proper MRO  
        super(SubjectB, self).validate()  # This will call Subject.validate -> Component.validate
        validate_each(self.classes)
        validate_each(self.subjects)
    
    @patch_on(Class)
    def validate(self):
        """Validate Class instances."""
        print("Validating class: ", self.name)
        # Component validation
        super(Class, self).validate()  # This will call Component.validate
        
        # Class-specific validations
        validate_each(self.constraints)
        validate_each(self.attributes)
        validate_each(self.attribute_sections)
    
    @patch_on(AttributeSection)
    def validate(self):
        """Validate AttributeSection instances."""
        # Component validation
        super(AttributeSection, self).validate()  # This will call Component.validate
        
        if not hasattr(self, "attributes") or self.attributes is None:
            createError(self, "Empty AttributeSection", "Missing list of Attributes")
        
        validate_each(self.attributes)
    
    @patch_on(Attribute)
    def validate(self):
        """Validate Attribute instances."""
        super(Attribute, self).validate()  # This will call Component.validate
        
        validate_presence(self, "data_type_clause")
        validate_object(self.data_type_clause)
        validate_object(self.derivation)
        validate_object(self.default)
        validate_each(self.constraints)
    
    @patch_on(DataTypeClause)
    def validate(self):
        """Validate DataTypeClause instances."""
        validate_presence(self, "data_type")
    
    @patch_on(Formula)
    def validate(self):
        """Validate Formula instances."""
        one_liner = getattr(self, "one_liner", "")
        if len(str(one_liner)) > 90:
            createError(self, "Style", f"Formula one_liner is too long ({len(str(one_liner))} chars)")
        
        validate_presence(self, "code")
    
    @patch_on(Constraint)
    def validate(self):
        """Validate Constraint instances."""
        # Formula validation
        formula_validate(self)


# Helper functions
def component_validate(obj):
    """Standalone component validation that can be called from other validators."""
    if not obj.name:
        createError(obj, "Missing field", "Name is missing")

    if not obj.one_liner:
        createError(obj, "Missing field", "Missing oneLiner")
    elif len(str(obj.one_liner)) > 90:
        createWarning(obj, "Style", f"oneLiner is too long. ({len(str(obj.one_liner))} chars).")

def formula_validate(obj):
    """Standalone formula validation."""
    one_liner = getattr(obj, "one_liner", "")
    if len(str(one_liner)) > 90:
        createError(obj, "Style", f"Formula one_liner is too long ({len(str(one_liner))} chars)")
    
    validate_presence(obj, "code")

def validate_presence(obj, attname):
    value = getattr(obj, attname, None)
    if value is None:
        createError(obj, "No presence", f"No value for {attname}")

def validate_each(objects: List):
    for obj in objects:
        validate_object(obj)

def validate_object(obj: Any):
    """Validate an object, patching on-demand if needed."""
    if not obj:
        return

    otype = getattr(obj, "_type", "No type?")
    oname = getattr(obj, "name", "NoName?")
    print(f"V1 Validating object: {otype} == {oname}")

    # Try to validate
    if hasattr(obj, "validate"):
        obj.validate()
    else:
        # Try on-demand patching
        if validators.patch_object_on_demand(obj):
            obj.validate()
        else:
            print(f"... no validation method available for {otype}")

    # Always do field validation
    validate_fields(obj)

# Global validators instance
validators = Validators()

def validate_model(the_model):
    """Validate an entire LDM model."""
    validators.attach_to_modules()
    
    validate_object(the_model)
    validate_each(the_model.subjects)
    
    print("Validating references...")
    validate_references(the_model)
    
    return All_Diagnostics

# Reference validation (unchanged)
ClassListAttributes = ["based_on", "dependents"]

def validate_references(model):
    """Validate all references within a model."""
    all_classes = get_all_classes(model)
    class_names = set(str(c.name) for c in all_classes)
    
    for c in all_classes:
        for att in ClassListAttributes:
            attrefs = getattr(c, att, [])
            for ref in attrefs:
                ref_name = str(ref)
                if ref_name not in class_names:
                    createError(c, "Invalid class reference", f"Invalid reference to '{ref}' in {att}")

def get_all_classes(subject: Literate_01.SubjectB) -> List[Literate_01.Class]:
    all_classes = subject.classes
    for sub in subject.subjects:
        all_classes.extend(get_all_classes(sub))
    return all_classes
