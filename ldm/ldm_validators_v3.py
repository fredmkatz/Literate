from typing import List, Any
from collections import defaultdict

from faculty_base_v3 import Faculty, faculty_class, patch_on, show_patches
from ldm.ldm_validators_generic import validate_fields
from ldm.Literate_01 import *
import ldm.Literate_01 as Literate_01
from utils.util_fmk import id_for, ids_for

from utils.util_excel import read_annotation_types

# Precalcs
#     Calculate mro per class - OK but need to handle multiple parent TODO
#     List of class names OK
#       check for dups
#     - plurals and presumed plurals

# Fleshing out
#     derive subtpings and subtypes
#     - default values for exclusive, exhaustive
#     check for cycles in subtype of/based on
#     derive dependents - OK

# Per Attribute
# - check for overrides by asceneding thru MRO
# - create Implied attributes
#     - baseX and containingX
#     - inverses (Check of exists)
#     - and note inverseOf on original and implied
#     - derive datatype, cardinality
#     - derive name, oneliner
#     - Att1 overrides Att2
#         for derivation, default
#         adds constraint
#         refines data type (check aa subtype)


# Validation

# Global
#     basic structural - generic field tests. OK
#         - for data type clauses
#     missing values for required attributes - OK
#     Uniqueness of class names


# Per Class
# - uniqueness of attribute names within a Class
# - check class references
#     - for based on, subtypes, etc

# Per Attribute
#   Check overrides type
#   check base types


# - Check that inverses are valid
#     - attribute reference is valid
#     - types "match"

#     Also
#     - output error counts
#     - get faculty working


The_Model: LiterateModel = None



All_Diagnostics = []
Annotation_types = read_annotation_types()


def createBug(
    obj, category, message, constraint_name=None
) -> Diagnostic:
    return createDiagnostic(
        obj,
        category,
        message,
        severity="Bug",
        constraint_name=constraint_name,
    )


def createError(
    obj, category, message, constraint_name=None
) -> Diagnostic:
    return createDiagnostic(
        obj,
        category,
        message,
        severity="Error",
        constraint_name=constraint_name,
    )


def createWarning(
    obj, category, message, constraint_name=None
) -> Diagnostic:
    return createDiagnostic(
        obj,
        category,
        message,
        severity="Warning",
        constraint_name=constraint_name,
    )


def createDiagnostic(
    obj,
    category,
    message,
    severity="Error",
    constraint_name=None,
) -> Diagnostic:
    oname_str = ""
    oname = getattr(obj, "name", None)
    if oname:
        oname_str = oname.content

    d = Diagnostic(
        severity=severity,
        category=category,
        message=message,
        object_type=obj._type,
        object_name=oname_str,
        constraint_name=constraint_name or "NoConstraintName",
    )

    All_Diagnostics.append(d)
    derived_target = obj.containing(MinorComponent) # the broadest class that "takes" diagnostics

    if not hasattr(derived_target, "diagnostics"):
        print(f"BUG: {id_for(derived_target)} can't handle diagnostics")
        return d

    derived_target.diagnostics.append(d)
    return d


def calc_model(model):

    # calculate indexes and list for navigating the model
    precalc_model(model)

    # invert some relationships
    # - dependents from based_on
    calc_dependents(model)

    # subtypings from subtype_of
    calc_subtypings(model)


def precalc_model(model: LiterateModel):


    # now add all plural forms to the index


    print("All classes names (singular and plural are: ")
    for cn in sorted(model.all_class_names()):
        break
        # print(f'\t"{cn}",')





# derivation of Dependents from basedOn
def calc_dependents(model: LiterateModel):

    print("Calc Dependents")
    # calc derivation: dependents = inverse(based_on)
    all_dependents = defaultdict(list)
    for c in model.all_classes():
        if c.based_on:
            for b in c.based_on:
                # print("b is ", b)
                bsimple = b.content
                # print(f"{c.name} is based on {bsimple}")
                all_dependents[bsimple].append(str(c.name))

    for base, deps in all_dependents.items():
        # print("Dependents of ", base, " are ", deps)
        base_class = model.class_named(base)
        if not base_class:
            print(f"BUG: Base Class {base} not found when deriving dependents")
            continue
        dependents_list = [ClassReference(d) for d in deps]
        # print("And the list is ", dependents_list)
        base_class.dependents = dependents_list


def calc_subtypings(model: LiterateModel):

    all_Subtypings = defaultdict(lambda: defaultdict(list))

    for c in model.all_classes():
        if not c.subtype_of:
            continue
        supers = getattr(c, "subtype_of", None)
        for pair in supers:
            subtyping = pair.subtyping_name
            supertype = pair.class_name
            # print(f"{c} is subtype of {supertype} via {subtyping}")
            all_Subtypings[str(supertype)][str(subtyping)].append(str(c.name))

    print("All Subtypings")
    for supertype, subtypings in all_Subtypings.items():
        # print(supertype, " => ")
        for subtyping, subtypes in subtypings.items():
            # print(f"\t{subtyping}: {subtypes}")

            subtypes_list = [ClassReference(c) for c in subtypes]
            subtyping_obj = Subtyping(
                name=SubtypingName(subtyping),
                #   is_exclusive = IsExclusive("exclusive"),
                #   is_exhaustive = IsExclusive("non exhaustive"),
                subtypes=subtypes_list,
            )
            # print("Subtyping object is ", subtyping_obj)
            the_class = model.class_named(supertype)
            if not the_class:
                print("No place to put subtypings for: ", supertype)
                continue
            the_class.subtypings.append(subtyping_obj)


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

    calc_base_attribute(cls)

    for attribute in cls.attributes:
        calc_attribute(cls, attribute)


def calc_base_attribute(cls: Class):
    based_on_names = getattr(cls, "based_on", None)
    if not based_on_names:
        return
    for base_name in based_on_names:
        # print(repr(base_name))
        based_on_name_str = base_name.content
        att_name = AttributeName(f"base{based_on_name_str}")
        dt = BaseDataType(class_name=base_name, as_value_type=AsValue(False))
        dtc = DataTypeClause(
            data_type=dt,
            is_optional=IsOptional(False),
            cardinality=Cardinality.MANY_ONE,
        )
        one_liner = OneLiner(
            f"A link back to the {based_on_name_str} on which this {cls.name.content} depends."
        )
        # print("AttNam = ", att_name)
        # print("dt = ", dt)
        # print("dtc = ", dtc)
        att = Attribute(name=att_name, one_liner=one_liner, data_type_clause=dtc)
        # print("Creating basedon attribute: ", repr(att))
        add_implied_attribute(cls, att)


def add_implied_attribute(cls: Class, att: Attribute):
    from utils.class_container import show_containers
    cname = cls.name.content
    # print("Adding implied attribute: ", att, " in ", cls)

    implied_atts = att_section_named(
        cls, f"Implied Attributes", create_section=True, one_liner = f"created for {cname}"
    )

    implied_atts.attributes.append(att)
    implied_atts.set_containees_back(verbose=False)
    # print("Added implied attribute: ", att, " in ", cls)
    # print("... Containees of section are: ", ids_for(implied_atts.clean_containees()))
    # print("... Containees of att are: ", ids_for(att.clean_containees()))
    # print("... Chain from name is: ", att.name.up_chain())
    # print("... Chain from attribute is: ", att.up_chain())
    # print("... Chain from section is: ", implied_atts.up_chain())
    # show_containers(att)


def att_section_named(cls: Class, new_section_name: str, create_section=False, one_liner = "No oneliner provided"):
    sections = cls.attribute_sections
    if not sections:
        cls.attribute_sections = []
        sections = cls.attribute_sections
    implied_atts = None
    for section in sections:
        if section.name.content == new_section_name:
            # print("Found section named: ", new_section_name)
            return section

    if not create_section:
        return None
    # nothing found, create new section
    section = AttributeSection(name=AttributeSectionName(new_section_name))
    section.one_liner = OneLiner(one_liner)
    # print(f"Creating section for {cls}: {section}")
    cls.attribute_sections.append(section)
    # cls.set_containees_back(verbose=True)
    cls.set_containees_back(verbose=False)

    return section

def countEmbellishments(model: LiterateModel, caption):
    print("Embellishment counting - ", caption)
    
    compclass = model.class_named("Component")
    attributes = compclass.attributes
    natts = len(attributes)
    print(natts, " attributes in Component")
    
    nembellishments = len( [a  for a in attributes if a.name.content == "isEmbellishment"])
    print(nembellishments, " isEmbellished in Component")

def calc_attribute(cls, attribute: Attribute):

    calc_attribute_override(cls, attribute)

    calc_attribute_inverse(cls, attribute)


def calc_attribute_inverse(cls: Class, attribute: Attribute):
    the_model = findTheModel(attribute)
    # imply inverse
    cname = cls.name.content
    aname = attribute.name.content

    # print(f"Considering {cname}.{aname} for inversion... ")
    inverse = attribute.inverse
    if inverse:
        # print("\tSkipping: already has inverse")
        return
    dtc = attribute.data_type_clause
    if not dtc:
        # print("\tSkipping: NO DTC")
        return

    dt = dtc.data_type
    # print("\tdtc = ", dtc)
    # print("\tdt  = ", dt, " -- ", type(dt))

    # Figure out whether the datatype is
    #   a. Simple enough. Either a base type or List, Set, or Mapping with just base types
    #       below
    #   b. Whether the base type is a value or reference type
    target_type0 = calc_inverse_target_type(dt)
    # print(f"\tTarget type0 = {target_type0}")
    
    if not target_type0:
        # print("\tSkipping: datatype to complicated; no target type")
        return None
    # if "Mapping" in dtpytype:
    #     print("\tskipping Mapping Data type")
    #     return

    if target_type0 not in the_model.full_class_index():
        # print("\tSKIPPING inverse for..  No such class as ", target_type0)
        return

    
    the_model = cls.containing(LiterateModel)
    target_type = singularize_class_name(the_model, target_type0)

    realer_target_type = the_model.class_named(target_type)
    # print("\tRealer target type is ", realer_target_type)

    if realer_target_type.is_value_type:
        # print(
        #     f"\tSKIPPING {cname}.{aname}, a {dt}. core type {target_type} is a value type"
        # )
        return

    # print(
    #     f"\tInverting {cname}.{aname}, a {dt}. core type {target_type} not a value type"
    # )

    # so
    # cls is the class of the original attribute
    # aname is the string name of the original

    # target type is the string name of whete the new implied att should go
    # source type is the string name of class in which the old attribute was found

    source_type = cname
    inverse_att_name = AttributeName(f"inverseOf {aname}")

    # will sometimes be set of source_type. If
    dt = BaseDataType(class_name=source_type, as_value_type=AsValue(False))
    dtc = DataTypeClause(
        data_type=dt, is_optional=IsOptional(False), cardinality=Cardinality.MANY_ONE
    )
    one_liner = OneLiner(
        f"Inverse attribute for {source_type}.{aname} from which this was implied."
    )
    # print("\tInvrse AttNam = ", inverse_att_name)
    # print("\tInverse dt = ", dt)
    # print("\tInverse dtc = ", dtc)
    inverse_att = Attribute(
        name=inverse_att_name, one_liner=one_liner, data_type_clause=dtc
    )
    # print("\tCreating inverse attribute: ", repr(inverse_att))
    target_cls = the_model.class_named(target_type)
    add_implied_attribute(target_cls, inverse_att)

    # create inverse attributes for the original and for the implied invers
    inverse_att.inverse = AttributeReference(
        class_name=ClassReference(cname), attribute_name=AttributeName(aname)
    )
    attribute.inverse = AttributeReference(
        class_name=ClassReference(target_type), attribute_name=inverse_att_name
    )

    # And still have to add inverse clauses on both sides


def singularize_class_name(model, cname: str) -> str:
    cls = model.full_class_index().get(cname, None)
    if not cls:
        return None
    singular = str(cls.name)
    # print(f"\tSingular for {cname} is {singular}")
    return singular


def calc_inverse_target_type(dt: DataType) -> str:
    target_type = None
    # print(f"\ttypename of dt is: {typename(dt)}")
    dtname = typename(dt)
    if dtname == "BaseDataType":
        target_type = dt.class_name.content
        return target_type
    if dtname in ["SetDataType", "ListDataType"]:
        element_type = dt.element_type
        if typename(element_type) == "BaseDataType":
            target_type = element_type.class_name.content
            return target_type
    return None


def typename(obj):
    return type(obj).__name__


def calc_attribute_override(cls: Class, attribute):
    # Note overrides
    cname = cls.name.content
    aname = attribute.name.content
    # print("in calc attribute, attname is ", attribute.name)
    the_model = cls.containing(LiterateModel)
    # print(f"the_model = {the_model}")
    mros = cls.class_mro()
    # print("calc attribute override; mro for ", cls, " is ", mros)
    for mro in mros:
        parent_class = the_model.class_named(mro)
        parent_att = parent_class.attribute_named(aname)
        if not parent_att:
            continue
        # print(f"Found override for {cname}.{aname} in {mro}")
        # print("Attribute name = ", attribute.name)

        newname = AttributeName(aname)
        # print(".. and as AName: ", repr(newname))
        attribute.overrides = AttributeReference(ClassReference(mro), newname)
        break


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
            createWarning(
                self,
                "Style",
                f"oneLiner is too long. ({len(str(self.one_liner))} chars).",
                constraint_name="componentOneLinerLength",
            )
        if len(str(self.name.content)) > 30:
            createWarning(
                self, "Style", f"name is too long. ({len(str(self.name))} chars).",
                constraint_name="NameTooLong",
            )

    @patch_on(LiterateModel, "validate")
    def validate_literate_model(self):

        global The_Model

        The_Model = self
        calc_model(self)

        # call precalc a second time to include all the implied attributes
        precalc_model(self)

        # Call super validator with explicit class name
        print("Validating LiterateModel")
        _validation_faculty.call_super_validate(self, "LiterateModel")
        print("Call to Validating references...")
        # print("Before validating: ", len(self.classes), " classes in model")
        validate_references(self)
        # print("After validating: ", len(self.classes), " classes in model")

    @patch_on(SubjectE, "validate")  # lowest level Subject
    def validate_subject_e(self):
        # Call super validator with explicit class name
        _validation_faculty.call_super_validate(self, "SubjectE")

        classes_count = len(getattr(self, "classes", []))
        subjects_count = len(getattr(self, "subjects", []))

        obj_type = type(self).__name__
        validate_each(getattr(self, "classes", []))
        validate_each(getattr(self, "subjects", []))

    @patch_on(Class, "validate")
    def validate_class(self):
        """Validate Class instances."""
        # Call super validator with explicit class name
        _validation_faculty.call_super_validate(self, "Class")

        calc_class(self)
        validate_each(getattr(self, "constraints", []))
        validate_each(getattr(self, "attributes", []))
        validate_each(getattr(self, "attribute_sections", []))
        
        countEmbellishments(The_Model, f"After validating class {self}")

    @patch_on(AttributeSection, "validate")
    def validate_attribute_section(self):
        """Validate AttributeSection instances."""
        _validation_faculty.call_super_validate(self, "AttributeSection")

        if not hasattr(self, "attributes") or self.attributes is None:
            createError(self, "EmptyAttributeSection", "Missing list of Attributes")

        validate_each(getattr(self, "attributes", []))

    @patch_on(Attribute, "validate")
    def validate_attribute(self):
        """Validate Attribute instances."""
        _validation_faculty.call_super_validate(self, "Attribute")

        dtc = getattr(self, "data_type_clause", None)
        if dtc:
            validate_data_type_clause(dtc, target=self)

        _validation_faculty.validate_object(getattr(self, "derivation", None))
        _validation_faculty.validate_object(getattr(self, "default", None))
        validate_each(getattr(self, "constraints", []))

    @patch_on(Formula, "validate")
    def validate_formula(self):
        """Validate Formula instances."""
        one_liner = getattr(self, "one_liner", "")
        if len(str(one_liner)) > 90:
            createWarning(
                self,
                "Style",
                f"Formula one_liner is too long ({len(str(one_liner))} chars)",
                constraint_name="FormulaOneLinerLength"
            )

    @patch_on(Constraint, "validate")
    def validate_constraint(self):
        """Validate Constraint instances."""
        _validation_faculty.call_super_validate(self, "Constraint")
        validate_presence(self, "python")


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
    createError(obj, "MissingValue", f"Missing value for required field: '{attribute}'",
                constraint_name=f"Missing attribute: {attribute}")


def validate_data_type_clause(dtc, target=None):
    """Validate DataTypeClause instances."""
    validate_presence(dtc, "data_type")
    data_type = getattr(dtc, "data_type", None)
    if data_type:
        validate_data_type(data_type, target=target)


def findTheModel(obj) -> LiterateModel:
    the_model = None
    if hasattr(obj, "containing"):
        # print("obj has containing: ", obj)
        # print(f"Value of 'containing': {datatype.containing}")

        the_model = obj.containing(LiterateModel)
    if not the_model:
        print("BUG: obj lacks something, resorting to The_Model for ",  type(obj).__name__, " = ", obj)

        the_model = The_Model
    return the_model

def validate_data_type(datatype: DataType, target=None):
    """Validate DataType instances."""
    # print("validating datatype: ", datatype)
    if not datatype:
        return

    # print("type of datatype is ", type(datatype))
    the_model = findTheModel(datatype)
    base_types = datatype.base_type_names()
    # print("... base types are: ", base_types)
    for base_type in base_types:
        if base_type in the_model.all_class_names():
            # print("\tno problem with ", base_type)
            continue
        print("\t!!! Base type error for ", base_type, " in dt ", datatype)
        createError(
            datatype,
            "InvalidBaseType",
            f"{base_type} is not a class name - or plural",
            constraint_name="checkClassReference",
        )


# Create the validators instance
_validation_faculty = Validators()
# print("Created Validators() = ", _validation_faculty)
# show_patches(_validation_faculty.all_patches)


def validate_model(the_model):
    """Validate an entire LDM model."""
    _validation_faculty.validate_object(the_model)
    return All_Diagnostics


# Reference validation functions (unchanged)
ClassListAttributes = ["based_on", "dependents"]


def validate_references(model: LiterateModel):
    """Validate all references within a model."""
    all_classes = model.all_classes()

    class_names = set(str(c.name) for c in all_classes)
    print("Validating references")
    for c in all_classes:
        for att in ClassListAttributes:
            attrefs = getattr(c, att, [])
            # print(
            #     "Validation class refs for ", c.name, "with att = ", att, " - has ", len(attrefs)
            # )
            for ref in attrefs:
                ref_name = str(ref)
                if ref_name not in class_names:
                    createError(
                        c,
                        "InvalidClassReference",
                        f"Invalid reference to '{ref}' in {att}",
                        constraint_name="checkListedClassReference",
                    )
