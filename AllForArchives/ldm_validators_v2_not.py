
# import sys
from typing import List, Any
from collections import defaultdict

from faculty_base import faculty_class, patch_on, show_patches, resolve_patched_method

from ldm.ldm_validators_generic import validate_fields

from ldm.Literate_01 import *

All_Diagnostics = []
All_Classes = None
All_Class_Mapping = None
All_Class_Names = None


"""To Dos for Validation
    
    Class level
    - inflect for plurals
    - subtypings and subtypes list
    - check based on and subtypeOf references
    
    
    Attribute
    - check class references (in all data types)
    - overrides Attributes
    - overrides Derivation, Default, DataType,  oneliner
        and from where
    - inherited from
    
    - inverses
    - create implied attributes
    - check explicit inverses: 
        cardinality
        name and one liner, using inflect
    
    Also
    - output error counts
    - get faculty working
    
    """

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


def calc_model(model):
    global All_Classes, All_Class_Mapping, All_Class_Names

    All_Classes = get_all_classes(model)
    All_Class_Mapping = {str(c.name): c for c in All_Classes}
    All_Class_Names = set(str(c.name) for c in All_Classes)
    print("All class names are", All_Class_Names)
    print("class mapping is ")
    for k, v in All_Class_Mapping.items():
        print(k, " => ", v)
    
    All_Based_Ons = []
    print("Calc Dependents")
    dependents = defaultdict(list)
    for c in All_Classes:
        if c.based_on:
            for b in c.based_on:
                bsimple = str(b)
                print(f"{c.name} is based on {bsimple}")
                dependents[bsimple].append(str(c.name))
    for base, deps in dependents.items():
        print("Dependents of ", base, " are ", deps)
        print("base is ", repr(base))
        base_class = All_Class_Mapping.get(base, None)
        if not base_class:
            print("Class not found")
            continue
        dependents_list = [ClassName(d) for d in deps]
        print("And the list is ", dependents_list)
        base_class.dependents = dependents_list
    
def calc_class(cls):
    derive_presumed_plural(cls)
    derive_plural(cls)

def derive_presumed_plural(cls):
    print("Calcing presumed_plural")
    class_name = str(cls.name)
    cls.presumed_plural = class_name + "!es"
    
    print(f"Set presumed plural for {cls}: name is {class_name}, presuming {cls.presumed_plural}")

def derive_plural(cls):
    # default: presumed_plural
    plural = cls.plural
    if plural is not None:
        print(f"{cls} has explicit plural {plural}")
        return
    print(f"Using presumed plural for {cls}")
    plural = cls.presumed_plural


@faculty_class
class Validators:
    """Faculty for adding validation methods to LDM classes."""
    
    @patch_on(Component)
    def validate(self):
        # Base validation for all Components
        # print(f"Component.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        if not self.name:
            createError(self, "Missing field", "Name is missing")
        if not self.one_liner:
            createError(self, "Missing field", "Missing oneLiner")
        elif len(str(self.one_liner)) > 90:
            createWarning(self, "Style", f"oneLiner is too long. ({len(str(self.one_liner))} chars).")

    @patch_on(LiterateModel)
    def validate(self):
        # print(f"LiterateModel.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")

        # Call super validator
        call_super_validate(self, 'LiterateModel')
        calc_model(self)

        print("Validating references...")
        validate_references(self)


    

    @patch_on(SubjectE)     # lowest level Subject (ie deepest)
    def validate(self):
        # print(f"SubjectE.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        # Call super validator
        call_super_validate(self, 'SubjectE')

        classes_count = len(getattr(self, 'classes', []))
        subjects_count = len(getattr(self, 'subjects', []))
        
        obj_type = type(self).__name__
        # print(f"{obj_type} of SubjectE: {classes_count} classes, {subjects_count} subjects")
        validate_each(getattr(self, 'classes', []))
        validate_each(getattr(self, 'subjects', []))
    
    
    @patch_on(Class)
    def validate(self):
        """Validate Class instances."""
        # print(f"Class.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        # Call super validator
        call_super_validate(self, 'Class')
        
        calc_class(self)
        # Class-specific validations
        validate_each(getattr(self, 'constraints', []))
        validate_each(getattr(self, 'attributes', []))
        validate_each(getattr(self, 'attribute_sections', []))
    
    

    @patch_on(AttributeSection)
    def validate(self):
        """Validate AttributeSection instances."""
        # print(f"AttributeSection.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        # Call super validator
        call_super_validate(self, 'AttributeSection')
        
        if not hasattr(self, "attributes") or self.attributes is None:
            createError(self, "Empty AttributeSection", "Missing list of Attributes")
        
        validate_each(getattr(self, 'attributes', []))
    
    @patch_on(Attribute)
    def validate(self):
        """Validate Attribute instances."""
        # print(f"Attribute.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
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
        # print(f"DataTypeClause.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        validate_presence(self, "data_type")

        # createError(self, "DTC Issue", "validate(DataTypeClause) - worked!")
    
    @patch_on(Formula)
    def validate(self):
        """Validate Formula instances."""
        # print(f"Formula.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        one_liner = getattr(self, "one_liner", "")
        if len(str(one_liner)) > 90:
            createError(self, "Style", f"Formula one_liner is too long ({len(str(one_liner))} chars)")
        
        validate_presence(self, "code")
    
    @patch_on(Constraint)
    def validate(self):
        """Validate Constraint instances."""
        # print(f"Constraint.validate() called on {type(self).__name__}: {getattr(self, 'name', 'NoName')}")
        
        # Call super validator
        call_super_validate(self, 'Constraint')


# Updated helper functions with debug
def validate_each(objects: List):
    if not objects:
        # print("validate_each: empty list")
        return
    # print(f"validate_each: processing {len(objects)} objects")
    for i, obj in enumerate(objects):
        # print(f"  [{i}] validating: {type(obj).__name__} - {getattr(obj, 'name', 'NoName')}")
        validate_object(obj)

def validate_presence(obj, attribute):
    value = getattr(obj, attribute, None)
    if value:
        return
    createError(obj, "NonPresence", f"Missing value for '{attribute}'")


# Global reference to validators instance (needed for super calls)
_validation_faculty = None

def validate_object(obj: Any):
    """Validate an object."""
    
    # todo: Make this an exception?
    if not obj:
        # print("validate_object: obj is None/empty")
        return

    patched_func = resolve_patched_method(_validation_faculty, obj)
    # Try to validate
    if patched_func:
        patched_func(obj)
    # Always do field validation
    validate_fields(obj)


def call_super_validate(obj, current_class_name):
    """Helper function to call the next validation method in the MRO"""
    
    patched_func = resolve_patched_method(_validation_faculty, obj, current_class_name)
    if patched_func:
        return patched_func(obj)
    return None



# Create the validators instance to trigger the patching
_validation_faculty = Validators()  # Set global reference

print("Created Validators() = ", _validation_faculty)
show_patches(_validation_faculty.all_patches)


def validate_model(the_model):
    """Validate an entire LDM model."""
    # No need to attach to modules - patching happened at import time
    
    validate_object(the_model)
    
    return All_Diagnostics

# Reference validation (unchanged)
ClassListAttributes = ["based_on",  "dependents"]
# to do for validate_references
#   - navigate to lower level subjects to get all classes
#   - change assumption that subtypes are sinple class names
#   - add other clauses
#   - add check to field types refering to class, too
#   - attribute references

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