# ldm_validators.py
from typing import List, Any

from ldm.ldm_validators_generic import validate_fields
import ldm.Literate_01 as Literate_01
from ldm.Literate_01 import Diagnostic, OneLiner, Paragraph, SubjectB

All_Diagnostics = []

def createError(obj, category, message) -> Diagnostic:
    return createDiagnostic(obj, category,  message, severity="Error")


def createWarning(obj, category, message) -> Diagnostic:
    return createDiagnostic(obj, category, message, severity="Warning")


def createDiagnostic(obj, category, message, severity="Error") -> Diagnostic:
    oname_str = ""
    oname = getattr(obj, "name", None)
    if oname:
        print("oname for diagnostic is ", oname)
        oname_str = oname.content
    print("oname_str for diag is ", oname_str)
    d = Diagnostic(
        severity=severity, category = category, message=Paragraph(message), object_type=obj._type, object_name=oname_str
    )
    obj.diagnostics.append(d)
    All_Diagnostics.append(d)
    # print(d)
    return d


# to do for validate_references
#   - navigate to lower level subjects to get all classes
#   - change assumption that subtypes are sinple class names
#   - add other clauses
#   - add check to field types refering to class, too
#   - attribute references

ClassListAttributes = [
    "based_on",
    "dependent_of",
    "dependents",
]

def validate_references(model) :
    """Validate all references within a model."""
    all_classes = get_all_classes(model)
    class_names = set(str(c.name) for c in all_classes)
    print("All class names are", class_names)
    
    # Second pass: validate references
    for c in all_classes:
        for att in ClassListAttributes:
            attrefs = getattr(c, att, [])
            # print("Refs for ", att, " are ", attrefs)
            for ref in attrefs:
                ref_name = str(ref)

                if ref_name not in class_names:
                    createError(c, "Invalid class reference", f"Invalid reference to '{ref}' in {att}")
                    

def get_all_classes(subject: Literate_01.SubjectB) -> List[Literate_01.Class]:
    all_classes = subject.classes

    for subject in subject.subjects:
        all_classes.extend(get_all_classes(subject))
    return all_classes


def validate_component(component) -> List[str]:
    """Base validation for all Components."""

    component_type = component._type
    name = component.name
    if not name:
        d = createError(component, "Missing field", "Name is missing")

    one_liner = component.one_liner
    if not one_liner:
        createError(component, "Missing field", "Missing oneLiner")
        
    if one_liner and len(str(one_liner)) > 90:
        createWarning(
            component, "Style", f"oneLiner is too long. ({len(str(one_liner))} chars)."
        )
        


def validate_subject(self) -> List[str]:
    validate_component(self)

    validate_each(self.classes)
    validate_each(self.subjects)


def validate_attribute_section(self) -> List[str]:
    """Validate AttributeSection instances."""
    validate_component(self)

    # Check that the attributes list is present
    if not hasattr(self, "attributes") or self.attributes is None:
        createError(self, "Empty AttributeSection", "Missing list of Attributes", severity="ERROR")
        

    # Validate each attribute
    validate_each(self.attributes)


def validate_class(self) -> List[str]:
    """Validate Class instances."""

    validate_component(self)

    # Class-specific validations
    # ...
    validate_each(self.constraints)

    # Validate attributes and attribute sections
    validate_each(self.attributes)
    validate_each(self.attribute_sections)


def validate_attribute(attrib):
    validate_component(attrib)

    validate_presence(attrib, "data_type_clause")
    validate_object(attrib.data_type_clause)
    validate_object(attrib.derivation)
    validate_object(attrib.default)
    validate_each(attrib.constraints)


def validate_data_type_clause(dtc):
    validate_presence(dtc, "data_type")


def validate_formula(formula):

    one_liner = getattr(formula, "one_liner", "")
    if len(str(one_liner)) > 90:
        createError(
                formula, "Style", f"Formula one_liner is too long ({len(str(one_liner))} chars)"
        )

    validate_presence(formula, "code")


def validate_constraint(constraint):
    validate_formula(constraint)


def validate_presence(obj, attname):
    value = getattr(obj, attname, None)
    if value == None:
        createError(obj, "No presence", f"No value for {attname}")


def validate_each(objects: List):
    for obj in objects:
        validate_object(obj)




# Helper function to validate entire model
def validate_model(the_model):
# Call this function after all imports are complete
    attach_validation_methods()
    # attach_validation_methods_alternative()
    """Validate an entire LDM model."""
    validate_component(the_model)
    validate_each(the_model.subjects)
    
    print("Validating references...")

    return All_Diagnostics

classes_to_patch = {
    'Component': validate_component,
    'Subject': validate_subject,
    'SubjectB': validate_subject,
    'Class': validate_class,
    'AttributeSection': validate_attribute_section,
    'Attribute': validate_attribute,
    'Formula': validate_formula,
    'Constraint': validate_constraint,
    'DataTypeClause': validate_data_type_clause,
}

def attach_validation_methods():
    """Attach validation methods to classes - handle different import paths."""
    import sys
    
    # Find all possible ways the Literate_01 module might be imported
    possible_modules = []
    
    for module_name in sys.modules:
        if 'Literate_01' in module_name:
            module = sys.modules[module_name]
            if hasattr(module, 'SubjectB'):
                possible_modules.append((module_name, module))
                print(f"Found Literate_01 module as: {module_name}")
    
    if not possible_modules:
        print("ERROR: No Literate_01 modules found!")
        return
    
    # Patch all possible modules
    
    for module_name, module in possible_modules:
        print(f"Patching module: {module_name}")
        for class_name, validation_func in classes_to_patch.items():
            cls = getattr(module, class_name, None)
            if cls:
                setattr(cls, 'validate', validation_func)
                print(f"  Attached validate method to {module_name}.{class_name}")
            else:
                print(f"  WARNING: Class {class_name} not found in {module_name}")


def validate_object(obj: Any):
    """Modified validate_object that patches on-the-fly if needed."""
    if not obj:
        return

    otype = getattr(obj, "_type", "No type?")
    pytype = type(obj)
    pytype_name = pytype.__name__
    oname = getattr(obj, "name", "NoName?")
    print(f"Validating object: {otype} Py: {pytype}, PyName: {pytype_name} == {oname}")

    # Check if object has validate method
    if hasattr(obj, "validate"):
        print(f"... found validate method! - {obj.validate.__name__}")
        obj.validate()
    else:
        print(f"... no validate method attached for {otype} {oname}")
        
        # Try to attach the method on-the-fly
        validation_func = get_validation_function_for_type(pytype_name)
        if validation_func:
            print(f"... attempting to attach {validation_func.__name__} to {pytype}")
            setattr(pytype, 'validate', validation_func)
            
            # Now try again
            if hasattr(obj, "validate"):
                print(f"... successfully attached! Calling validate...")
                obj.validate()
            else:
                print(f"... failed to attach method")

    # But in all cases, do deep field validation
    validate_fields(obj)

def get_validation_function_for_type(type_name):
    """Return the appropriate validation function for a given type name."""
    
    return classes_to_patch.get(type_name)
    # type_to_func_map = {
    #     'Component': validate_component,
    #     'Subject': validate_subject,
    #     'SubjectB': validate_subject,
    #     'Class': validate_class,
    #     'AttributeSection': validate_attribute_section,
    #     'Attribute': validate_attribute,
    #     'Formula': validate_formula,
    #     'Constraint': validate_constraint,
    #     'DataTypeClause': validate_data_type_clause,
    # }
    # return type_to_func_map.get(type_name)

