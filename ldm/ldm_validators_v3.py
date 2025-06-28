from typing import List, Any
from collections import defaultdict

from faculty_base_v3 import Faculty, faculty_class, patch_on, show_patches
from ldm.ldm_validators_generic import validate_fields
from ldm.Literate_01 import *
import ldm.Literate_01 as Literate_01

from utils.util_excel import read_annotation_types

    # Validation and fleshing out - To Dos

    # Global
    #     Calculate mro per class - OK but need to handle multiple parent TODO
    #     List of class names OK
    #       check for dups
    #     basic structural - generic field tests. OK
    #         - for data type clauses
    #     missing values for required attributes - OK
    #     derive dependents - OK
    
    #     derive subtpings and subtypes
    #     - default values for exclusive, exhaustive
    #     check for cycles in subtype of/based on

    # Per Class
    # - uniqueness of attribute names within a Class
    # - check class references
    #     - for based on, subtypes, etc
    #     - plurals and presumed plurals

    # Per Attribute
    # - create Implied attributes
    #     - inverses (Check of exists)
    #     - and note inverseOf on original and implied
    #     - derive datatype, cardinality
    #     - derive name, oneliner
    #     - Att1 overrides Att2
    #         for derivation, default
    #         adds constraint
    #         refines data type (check aa subtype)
            
    #         check for overrides by asceneding thru MRO

    # - Check that inverses are valid
    #     - attribute reference is valid
    #     - types "match"

All_Classes = []
All_Class_Index = {}
All_MROs = {}
All_Attributes_Index = defaultdict(lambda: defaultdict(list)) # class name/attribute name
All_Class_Names = None


All_Diagnostics = []
Annotation_types = read_annotation_types()
def createBug(obj, category, message) -> Diagnostic:
    return createDiagnostic(obj, category, message, severity="Bug")

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
    
    global All_Classes, All_Class_Index, All_Attributes_Index, All_Class_Names
    All_Classes = get_all_classes(model)
    # All_Classes = []

    All_Class_Index = {str(c.name): c for c in All_Classes}
    # now add all plural forms to the index
    
    All_Class_Names = set(str(c.name) for c in All_Classes)

    print("All class names are", All_Class_Names)
    
    for c in All_Classes:
        derive_presumed_plural(c)
        derive_plural(c)
    plural_names =  set(str(c.plural) for c in All_Classes)
    All_Class_Names = All_Class_Names.union(plural_names)
    print("all plural names are ", plural_names)

    print("All classes names (singular and plural are: ")
    for cn in sorted(All_Class_Names):
        print(f"\t\"{cn}\",")

    for cls in All_Classes:
        cname = cls.name.content
        for att in cls.attributes:
            aname = att.name.content
            All_Attributes_Index[cname][aname] = att
            
            
    print("Attributes Index = \n", All_Attributes_Index)
    for cname, att_names in All_Attributes_Index.items():
        print("Class: ", cname)
        for aname in att_names:
            print("\t", aname)
    model.hello = "Hello"
    
    calc_dependents()
    calc_subtypings()
    
    # to calculate overrides...
    calc_mros()
    # Note. Needed to avoid duplication of all classes in yaml file
    # but what sets classes??
    print(len(model.classes), " classes in final model")
    # model.classes = []
    print(len(model.classes), " classes in final model")


# derivation of Dependents from basedOn

def calc_dependents():
    All_Based_Ons = []
    print("Calc Dependents")
    # calc derivation: dependents = inverse(based_on)
    dependents = defaultdict(list)
    for c in All_Classes:
        if c.based_on:
            for b in c.based_on:
                print("b is ", b)
                bsimple = b.content
                print(f"{c.name} is based on {bsimple}")
                dependents[bsimple].append(str(c.name))
    
    for base, deps in dependents.items():
        print("Dependents of ", base, " are ", deps)
        base_class = All_Class_Index.get(base, None)
        if not base_class:
            print("Class not found")
            continue
        dependents_list = [ClassReference(d) for d in deps]
        # print("And the list is ", dependents_list)
        base_class.dependents = dependents_list

def calc_subtypings():
    
    All_Subtypings = defaultdict(lambda: defaultdict(list))


    for c in All_Classes:
        if not c.subtype_of:
            continue
        supers = getattr(c, "subtype_of", None)
        for pair in supers:
            subtyping = pair.subtyping_name
            supertype = pair.class_name
            print(f"{c} is subtype of {supertype} via {subtyping}")
            All_Subtypings[str(supertype)][str(subtyping)].append(str(c.name))
            
    print("All Subtypings")
    for supertype, subtypings in All_Subtypings.items():
        print(supertype, " => ")
        for subtyping, subtypes in subtypings.items():
            print(f"\t{subtyping}: {subtypes}")
            
            subtypes_list = [ClassReference(c) for c in subtypes]
            subtyping_obj = Subtyping(name = SubtypingName(subtyping), 
                                    #   is_exclusive = IsExclusive("exclusive"),
                                    #   is_exhaustive = IsExclusive("non exhaustive"),
                                      subtypes = subtypes_list)
            print("Subtyping object is ", subtyping_obj)
            the_class = All_Class_Index.get(supertype, None)
            if not the_class:
                print("No place to put subtypings for: ", supertype)
                continue
            the_class.subtypings.append(subtyping_obj)
            
        
def calc_mros():
    global All_MROs
    
    print("CALC MROS - index has ", All_Class_Index)
    for cname, c in All_Class_Index.items():
        print("Calc MRO for ", cname)
        mro = calc_mro(cname)
        print("\tMRO is: ", mro)
        
def calc_mro(cname):
    mro = All_MROs.get(cname, None)
    if mro is not None:
        return mro
    
    c = All_Class_Index.get(cname, None)
    if not c:
        All_MROs[cname] = []
        return []
    supers = getattr(c, "subtype_of", None)
    if not supers:
        All_MROs[cname] = []
        return []
    
    if len(supers) > 1:
        print(f"> 1 supers for {cname} - {supers}")
    # Note only taking the first! TODO
    for supertype in supers:
        super_name = str(supertype.class_name)
        # print(cname, "\thas super: ", super_name)
        All_MROs[cname] = [super_name] + calc_mro(super_name)
        print(f"MRO for {cname} => ", All_MROs[cname])
        return All_MROs[cname]

def calc_component(obj):
    for annotation in obj.annotations:
        # print("Calcing annotation: ", annotation)
        label = str(annotation.label)
        atype = Annotation_types.get(label, None)
        if not atype:
            print("Unregoistered annotation type: ", label)
            continue
        emoji_symbol = atype["Emoji"]
        # print(f"\tlabel = {label}, emoji = {emoji_symbol}")
        annotation.emoji = Emoji(emoji_symbol)
    
def calc_class(cls):
    derive_presumed_plural(cls)
    derive_plural(cls)
    
    for attribute in cls.attributes:
        calc_attribute(cls, attribute)

# calc derivation: presumed plural
def derive_presumed_plural(cls):
    # print("Calcing presumed_plural")
    class_name = str(cls.name)
    cls.presumed_plural = fmk.pluralize(class_name)
    # print(f"Set presumed plural for {cls}: name is {class_name}, presuming {cls.presumed_plural}")

# calc derivation: plural
def derive_plural(cls):
    plural = cls.plural
    if plural is not None:
        plural = plural.strip()
        cls.plural = plural
        return
    # print(f"Using presumed plural for {cls}")

    cls.plural = cls.presumed_plural

def find_value_types():
    print("finding value types...")
    # for cname, cls in All_Class_Index.items():
    #     print(cname, " => ", cls)
    vtypes = []
    for cls in All_Classes:
        # print(cls)
        if str(cls).startswith("Valuetype"):
            vtypes.append(cls.name.content)
    # print("found value types are: ", vtypes)
    return vtypes
    

def calc_attribute(cls, attribute: Attribute):
    # Note overrides
    cname = cls.name.content
    aname = attribute.name.content
    print("in calc attribute, attname is ", repr(attribute.name))
    mros = All_MROs[cname]
    for mro in mros:
        parent_att = All_Attributes_Index.get(mro, {}).get(aname, None)
        if not parent_att:
            continue
        print(f"Found override for {cname}.{aname} in {mro}")
        print("Attribute name = ", attribute.name)
        
        newname = AttributeName(aname)
        print(".. and as AName: ", repr(newname))
        attribute.overrides = AttributeReference(ClassReference(mro), newname)
        break
        
    ValueTypes = find_value_types()

    # imply inverse
    print(f"Considering {cname}.{aname} for inversion... ")
    dtc = attribute.data_type_clause
    dt = dtc.data_type
    dtpytype = type(dt).__name__
    print("\tdtc = ", dtc)
    print("\tdt  = ", dt, " -- ", type(dt))
    if "Mapping" in dtpytype:
        print("\tskipping Mapping Data type")
        return
    coretype = None
    if "Base" in dtpytype:
        print("\ta base data type2")

        coretype = dt.class_name

    elif "ListDataType" in dtpytype or "SetDataType" in dtpytype:
        coretype = dt.element_type
    
    print("\tcore type is [", coretype, "]")
    if not coretype:
        print("\tSKIPPING no core type")
        return
    coretype = str(coretype).strip()
    print(f"is {coretype} in Valuetypes?")
    if coretype in ValueTypes:
        print(f"\tSKIPPING {cname}.{aname}, a {dt}. core type {coretype} is a value type")
        return

    print(f"\tInverting {cname}.{aname}, a {dt}. core type {coretype} not a value type")

@faculty_class
class Validators(Faculty):
    """Faculty for adding validation methods to LDM classes."""
    
    def validate_object(self, obj: Any, method_name: str = "validate"):
        """Validate an object using the appropriate patched method."""
        if not obj:
            return

        patched_func = self.resolve_patched_method(obj, method_name)
        if patched_func:
            patched_func(obj)
        
        # Always do field validation
        validate_fields(obj)
    
    def call_super_validate(self, obj, current_class_name: str = None):
        """Helper to call super().validate() equivalent."""
        return self.call_super_method(obj, "validate", current_class_name)
    
    @patch_on(Component, "validate")
    def validate_component(self):
        calc_component(self)
        """Base validation for all Components"""
        if len(str(self.one_liner)) > 90:
            createWarning(self, "Style", f"oneLiner is too long. ({len(str(self.one_liner))} chars).")
        if len(str(self.name)) > 30:
            createWarning(self, "Style", f"name is too long. ({len(str(self.name))} chars).")

    @patch_on(LiterateModel, "validate")
    def validate_literate_model(self):
        calc_model(self)

        # Call super validator with explicit class name
        print("Validating LiterateModel")
        _validation_faculty.call_super_validate(self, 'LiterateModel')
        print("Call to Validating references...")
        print("Before validating: ", len(self.classes), " classes in model")
        validate_references(self)
        print("After validating: ", len(self.classes), " classes in model")
        # self.classes = []   # Don't know why this is necessary, but it is!
        

    @patch_on(SubjectE, "validate")  # lowest level Subject
    def validate_subject_e(self):
        # Call super validator with explicit class name
        _validation_faculty.call_super_validate(self, 'SubjectE')

        classes_count = len(getattr(self, 'classes', []))
        subjects_count = len(getattr(self, 'subjects', []))
        
        obj_type = type(self).__name__
        validate_each(getattr(self, 'classes', []))
        validate_each(getattr(self, 'subjects', []))

    @patch_on(Class, "validate")
    def validate_class(self):
        """Validate Class instances."""
        # Call super validator with explicit class name
        _validation_faculty.call_super_validate(self, 'Class')
        
        calc_class(self)
        validate_each(getattr(self, 'constraints', []))
        validate_each(getattr(self, 'attributes', []))
        validate_each(getattr(self, 'attribute_sections', []))

    @patch_on(AttributeSection, "validate")
    def validate_attribute_section(self):
        """Validate AttributeSection instances."""
        _validation_faculty.call_super_validate(self, 'AttributeSection')
        
        if not hasattr(self, "attributes") or self.attributes is None:
            createError(self, "Empty AttributeSection", "Missing list of Attributes")
        
        validate_each(getattr(self, 'attributes', []))

    @patch_on(Attribute, "validate")
    def validate_attribute(self):
        """Validate Attribute instances."""
        _validation_faculty.call_super_validate(self, 'Attribute')
        
        _validation_faculty.validate_object(getattr(self, 'data_type_clause', None))
        _validation_faculty.validate_object(getattr(self, 'derivation', None))
        _validation_faculty.validate_object(getattr(self, 'default', None))
        validate_each(getattr(self, 'constraints', []))

    
    @patch_on(DataTypeClause, "validate")
    def validate_data_type_clause(self):
        """Validate DataTypeClause instances."""
        validate_presence(self, "data_type")
        _validation_faculty.validate_object(getattr(self, 'data_type', None))
        
    @patch_on(DataType, "validate")
    def validate_data_type(datatype:DataType):
        """Validate DataType instances."""
        print("validating datatype: ", datatype)
        base_types = datatype.base_type_names()
        print("... base types are: ", base_types)
        for base_type in base_types:
            if base_type in All_Class_Names:
                print("\tno problem with ", base_type)
                continue
            print("Base type error for ", base_type, " in dt ", datatype)
        
    
    @patch_on(Formula, "validate")
    def validate_formula(self):
        """Validate Formula instances."""
        one_liner = getattr(self, "one_liner", "")
        if len(str(one_liner)) > 90:
            createWarning(self, "Style", f"Formula one_liner is too long ({len(str(one_liner))} chars)")
        

    @patch_on(Constraint, "validate")
    def validate_constraint(self):
        """Validate Constraint instances."""
        _validation_faculty.call_super_validate(self, 'Constraint')
        createError(self, "Tester", "Let's see how Constraints handle diagnostics")
        validate_presence(self, "ocl")

# Helper functions
def validate_each(objects: List):
    if not objects:
        return
    for i, obj in enumerate(objects):
        _validation_faculty.validate_object(obj)

def validate_presence(obj, attribute):
    value = getattr(obj, attribute, None)
    if value:
        return
    createError(obj, "NonPresence", f"Missing value for required field: '{attribute}'")

# Create the validators instance
_validation_faculty = Validators()
print("Created Validators() = ", _validation_faculty)
show_patches(_validation_faculty.all_patches)

def validate_model(the_model):
    """Validate an entire LDM model."""
    _validation_faculty.validate_object(the_model)
    return All_Diagnostics

# Reference validation functions (unchanged)
ClassListAttributes = ["based_on", "dependents"]

def validate_references(model):
    """Validate all references within a model."""
    all_classes = get_all_classes(model)
    class_names = set(str(c.name) for c in all_classes)
    print("Validating references")
    for c in all_classes:
        for att in ClassListAttributes:
            attrefs = getattr(c, att, [])
            print("Validation class refs for ", c.name, "with att = ", att, " - ", attrefs)
            for ref in attrefs:
                ref_name = str(ref)
                if ref_name not in class_names:
                    createError(c, "Invalid class reference", f"Invalid reference to '{ref}' in {att}")

def get_all_classes(subject: SubjectB) -> List[Class]:
    all_classes = []
    all_classes.extend(subject.classes)
    # note: following causes subject.classes to be extended with all below!!
    # all_classes = subject.classes
    for sub in subject.subjects:
        all_classes.extend(get_all_classes(sub))
    return all_classes