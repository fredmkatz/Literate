# Enhanced validators with proper super() support
from typing import List, Any
from faculty_base import faculty_class, patch_on, show_patches
from ldm.ldm_validators_generic import validate_fields
from ldm.Literate_01 import *

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

# Global reference to validators instance (needed for super calls)
_validators_instance = None

def call_super_validate(obj, current_class_name):
    """Helper function to call the next validation method in the MRO"""
    cls = type(obj)
    mro = [c.__name__ for c in cls.__mro__]
    
    # Find current class in MRO
    try:
        current_index = mro.index(current_class_name)
        # Look for next class in MRO that has a validator
        for next_class_name in mro[current_index + 1:]:
            patched_func = _validators_instance.all_patches.get(next_class_name, None)
            if patched_func:
                print(f"super().validate() calling {next_class_name} validator")
                patched_func(obj)
                return
        print(f"super().validate() - no parent validator found after {current_class_name}")
    except ValueError:
        print(f"Warning: {current_class_name} not found in MRO: {mro}")

@faculty_class
class Validators:
    """Faculty for adding validation methods to LDM classes."""
    
    @patch_on(Component)
    def validate(self):
        # Base validation for all Components
        print(f"Component.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        if not self.name:
            createError(self, "Missing field", "Name is missing")
        if not self.one_liner:
            createError(self, "Missing field", "Missing oneLiner")
        elif len(str(self.one_liner)) > 90:
            createWarning(self, "Style", f"oneLiner is too long. ({len(str(self.one_liner))} chars).")

    @patch_on(LiterateModel)
    def validate(self):
        print(f"LiterateModel.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator
        call_super_validate(self, 'LiterateModel')
        
        classes_count = len(getattr(self, 'classes', []))
        subjects_count = len(getattr(self, 'subjects', []))
        print(f"LiterateModel: {classes_count} classes, {subjects_count} subjects")
        validate_each(getattr(self, 'classes', []))
        validate_each(getattr(self, 'subjects', []))
    
    @patch_on(SubjectB)
    def validate(self):
        print(f"SubjectB.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator
        call_super_validate(self, 'SubjectB')
        
        classes_count = len(getattr(self, 'classes', []))
        subjects_count = len(getattr(self, 'subjects', []))
        print(f"SubjectB: {classes_count} classes, {subjects_count} subjects")
        validate_each(getattr(self, 'classes', []))
        validate_each(getattr(self, 'subjects', []))
    
    @patch_on(SubjectC)
    def validate(self):
        print(f"SubjectC.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator
        call_super_validate(self, 'SubjectC')
        
        classes_count = len(getattr(self, 'classes', []))
        subjects_count = len(getattr(self, 'subjects', []))
        print(f"SubjectC: {classes_count} classes, {subjects_count} subjects")
        validate_each(getattr(self, 'classes', []))
        validate_each(getattr(self, 'subjects', []))
    
    @patch_on(Class)
    def validate(self):
        """Validate Class instances."""
        print(f"Class.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator
        call_super_validate(self, 'Class')
        
        # Class-specific validations
        validate_each(getattr(self, 'constraints', []))
        validate_each(getattr(self, 'attributes', []))
        validate_each(getattr(self, 'attribute_sections', []))
    
    @patch_on(AttributeSection)
    def validate(self):
        """Validate AttributeSection instances."""
        print(f"AttributeSection.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator
        call_super_validate(self, 'AttributeSection')
        
        if not hasattr(self, "attributes") or self.attributes is None:
            createError(self, "Empty AttributeSection", "Missing list of Attributes")
        
        validate_each(getattr(self, 'attributes', []))
    
    @patch_on(Attribute)
    def validate(self):
        """Validate Attribute instances."""
        print(f"Attribute.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator
        call_super_validate(self, 'Attribute')
        
        validate_presence(self, "data_type_clause")
        validate_object(getattr(self, 'data_type_clause', None))
        validate_object(getattr(self, 'derivation', None))
        validate_object(getattr(self, 'default', None))
        validate_each(getattr(self, 'constraints', []))
    
    @patch_on(DataTypeClause)
    def validate(self):
        """Validate DataTypeClause instances."""
        print(f"DataTypeClause.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        validate_presence(self, "data_type")
    
    @patch_on(Formula)
    def validate(self):
        """Validate Formula instances."""
        print(f"Formula.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator (if Formula has a parent in your hierarchy)
        call_super_validate(self, 'Formula')
        
        one_liner = getattr(self, "one_liner", "")
        if len(str(one_liner)) > 90:
            createError(self, "Style", f"Formula one_liner is too long ({len(str(one_liner))} chars)")
        
        validate_presence(self, "code")
    
    @patch_on(Constraint)
    def validate(self):
        """Validate Constraint instances."""
        print(f"Constraint.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator
        call_super_validate(self, 'Constraint')


# Helper functions
def validate_each(objects: List):
    if not objects:
        print("validate_each: empty list")
        return
    print(f"validate_each: processing {len(objects)} objects")
    for i, obj in enumerate(objects):
        print(f"  [{i}] validating: {type(obj).__name__} - {getattr(obj, 'name', 'NoName')}")
        validate_object(obj)

def validate_presence(obj, attribute):
    value = getattr(obj, attribute, None)
    if value:
        return
    createError(obj, "NonPresence", f"Missing value for '{attribute}'")
    
def validate_object(obj: Any):
    """Validate an object."""
    if not obj:
        print("validate_object: obj is None/empty")
        return

    patched_func = resolve_patched_method(_validators_instance, obj)
    if patched_func:
        patched_func(obj)
    else:
        actual_type = type(obj).__name__
        print(f"  ... no validation method available for {actual_type}")

    # Always do field validation
    validate_fields(obj)

def resolve_patched_method(validators, obj):
    otype = getattr(obj, "_type", "No type?")
    oname = getattr(obj, "name", "NoName?")
    actual_type = type(obj).__name__
    print(f"Resolving method for: {otype} == {oname} (actual type: {actual_type})")
    
    cls = type(obj)
    mro = [c.__name__ for c in cls.__mro__]
    print(f"\tmro for object is: {mro}")
    
    patched_func = None
    for cname in mro:
        patched_func = validators.all_patches.get(cname, None)
        if patched_func:
            print(f"..... found patched fn: {patched_func} on class: {cname}")
            break
    
    if not patched_func:
        print(f"..... NO patched fn for {actual_type} or any parent type")
    
    return patched_func

# Create the validators instance to trigger the patching
validators = Validators()
_validators_instance = validators  # Set global reference
print("Created Validators() = ", validators)
Validator_Patches = validators.all_patches
show_patches(Validator_Patches)

def validate_model(the_model):
    """Validate an entire LDM model."""
    validate_object(the_model)
    validate_each(the_model.subjects)
    
    print("Validating references...")
    validate_references(the_model)
    
    return All_Diagnostics

# Reference validation
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

def get_all_classes(subject: SubjectB) -> List[Class]:
    all_classes = subject.classes
    for sub in subject.subjects:
        all_classes.extend(get_all_classes(sub))
    return all_classes