
# Literate Data Model
!! Error: Missing oneLiner


## Preliminaries - the basic structure of the model
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


_ **Component** - An element or building block of the literate data model
- ***normalName*** - the name of the component, not in camel case (optional
String)
- ***name*** - The name of the component (optional  CamelName)
- ***qualifiedName*** (optional  QualifiedCamel)
!! Error: Missing oneLiner


- ***abbreviatedName*** - a short form of the component's name, used for cross
references and improved readability. (optional  CamelName)None: "LDM" is the short form of "Literate Data Model".

- ***oneLiner*** - A brief, one-line definition or description of the component,
suitable for use in a descriptive table of contents. _ (optional  RichLine)
!! Warning: oneLiner is too long. (116 chars).


- ***elaboration*** - A more detailed explanation or discussion of the component
_ (optional  RichText)
__ _For Machinery_ - mechanical attributes (None)
- ***isEmbellishment*** - Indicates whether this component is an embellishment
added during post-parsing processing _ (optional  Boolean)None: This attribute is set to true for components that are automatically
generated or added during the fleshing out, review, or rendering processes, such
as implied attributes or suggested model elements. It helps distinguish
embellishments from the core model elements defined in the original LDM source.

!! Warning: oneLiner is too long. (91 chars).


_ **AnnotationType** - a kind of note, or aside, used to call attention to
additional information about some Component.None: Each LDM declares a set of Annotation Types, with defined labels, emojis,
and clearly documented purposes. These are *recognized* or *registered*
Annotation Types.

!! Warning: oneLiner is too long. (96 chars).


- ***emoji*** - an emoji (optional  Emoji)
- ***emojiName*** - an emoji (optional  String)
- ***emojiUnicode*** - the Unicode for the emoji (optional  Unicode)
- ***label*** - A short label to indicate the purpose of the annotation _
(optional  CamelName)
- ***plural*** - the plural form of the label (optional  UpperCamel)
- ***purpose*** - the intended reason for the annotation.
!! Error: No value for data_type_clause
!! Error: Required field 'data_type_clause' is missing


_ **ValueTypeAnnotationANoteOrCommentAssociatedWithAModelElement**
!! Error: Missing oneLiner


- ***annotationType*** (optional  AnnotationType)None: An Annotation is considered to *recognized* if the label is associated
with an Annotation Type. otherwise it is *ad hoc*.

!! Error: Missing oneLiner


- ***label*** - A short label to indicate the purpose of the annotation _
(optional  CamelName)
- ***emoji*** (optional  Emoji)
!! Error: Missing oneLiner


- ***content*** - The content or body of the annotation (optional  RichText)
__ _For Machinery_ (None)
!! Error: Missing oneLiner


- ***isEmbellishment*** - Indicates whether this annotation is an embellishment
added during post-parsing processing _ (optional  Boolean)None: This attribute is set to true for annotations that are automatically
generated or added during the fleshing out, review, or rendering processes, such
as suggestions, issues, or diagnostic messages. It helps distinguish
embellishment annotations from the annotations defined in the original LDM
source.

!! Warning: oneLiner is too long. (92 chars).


## The Model and its Subjects
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


_ **LiterateDataModel** - A representation of a domain's entities, attributes,
and relationships, along with explanatory text and examples
!! Warning: oneLiner is too long. (112 chars).
!! Error: For field 'abbreviation' - expected
typing.Optional[utils.class_casing.CamelCase], but got <class 'str'>
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>

_plural_:  LiterateDataModels


- ***name*** (optional  UpperCamel)
!! Error: Missing oneLiner


- ***allSubjects*** - list of all classes in the model, as ordered in the
definition of the model. (optional List of  Classes)
- ***allClasses*** - list of all classes in the model, as ordered in the
definition of the model. (optional List of  Classes)
__ _Modeling Configuration_ (None)
!! Error: Missing oneLiner


- ***annotationTypes*** (optional List of  AnnotationTypes)
!! Error: Missing oneLiner


- ***preferredCodingLanguage*** - the recommended lanquage  for expressing
derivation, defaults, and constraints (optional  CodingLanguage)
- ***alternateCodingLanguages*** (optional List of  CodingLanguages)
!! Error: Missing oneLiner


- ***preferredTemplateLanguage*** - the recommended lanquage  for expressing
derivation, defaults, and constraints (optional  TemplateLanguage)
- ***alternateTemplateLanguages*** (optional List of  TemplateLanguages)
!! Error: Missing oneLiner


- ***aiFunctions*** - A list of functions that require sophisticated AI-powered
implementation * (optional List of  String)
_ **SubjectASpecificTopicOrThemeWithinTheModel**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>

_plural_:  Subjects


- ***name*** (optional  UpperCamel)
!! Error: Missing oneLiner


- ***parentSubject*** - The parent subject, if any, under which this subject is
nested _ (optional  Subject)
- ***classes*** - The major classes related to this subject, in the order in
which they should be presented _ (optional List of  Classes)None: define chapter, section, subsection as levels?

!! Warning: oneLiner is too long. (91 chars).


- ***eachClassShouldBeFollowedFirstByTheClassesThatAreDependentOnItAndThen***
!! Error: Missing oneLiner
!! Error: No value for data_type_clause
!! Error: Required field 'data_type_clause' is missing


- ***byItsSubtypeClasses***
!! Error: Missing oneLiner
!! Error: No value for data_type_clause
!! Error: Required field 'data_type_clause' is missing


- ***childSubjects*** - Any child subjects nested under this subject, in the
order in which they should be presented _ (optional List of  Subjects)
!! Warning: oneLiner is too long. (94 chars).

_inverse_: [_Subject_](_Subject_)_._parentSubject

_ **SubjectAreaAMainTopicOrAreaOfFocusWithinTheModelContainingRelatedSubjectsAnd
Classes**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>
!! Error: For field 'where' - expected typing.Optional[Literate_01.OneLiner],
but got <class 'str'>

_plural_:  SubjectAreas

_where_:  parentSubject is absent


### Classes
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


_ **Class** - A key entity or object type in the model, often corresponding to a
real-world concept_plural_:  Classes

_Constraint_:  Within each Class, attribute names must be unique.

_english_: 



- ***pluralForm*** - the normal English plural form of the name of the Class
(optional  UpperName)None: When inputting a model, you will rarely need to specify the plural form.
The input program will just look it up.

- ***basedOn*** - the Class or Classes on which this class is dependent
(optional Set of  Classes)None: that basedOn and dependentOf are being used synonymousle in this
metamodel.

- ***supertypes*** - The parent class (optional  Es)
- ***subtypings*** - the criteria, or dimensions, by which the class can be
divided into subtypes (optional List of  Subtypings)None: in a library model, the `Book` class could have subtypings based on genre
(e.g., Fiction, Non-fiction), format (e.g., Hardcover, Paperback), or subject
(e.g., Science, History).

- ***subtypes*** - Any subtypes or specializations of this class based on it’s
subtypings. _ (optional List of  Classes)None: For instance, using the `Book` example, the subtypes could include
`FictionBook`, `Non-fictionBook`, `HardcoverBook`, `PaperbackBook`,
`ScienceBook`, and `HistoryBook`.

- ***attributes*** - The attributes or properties of the class, in the order in
which they should be presented _ (optional List of  Attributes)
- ***attributeSections*** - additional attributes or properties of the class,
grouped for clarity and elaboration.  _ (optional List of  AttributeSections)
- ***constraints*** - Any constraints, rules, or validations specific to this
class _ (optional List of  Constraints)None: Constraints may be expressed on either the Class or the Attribute. Always?

- ***methods*** - Any behaviors or operations associated with this class _
(optional List of  Methods)
__ _Implied Attributes_ (None)
- ***dependents*** - the Classes which are basedOn this Class (optional Set of
Classes)_inverse_: [_Class_](_Class_)_._basedOn

- ***uniqueKeys*** (optional Set of  UniqueKeys)_inverse_: [_UniqueKey_](_UniqueKey_)_._basedOn

_ **Subtyping** - a way in which subtypes of a Class may be classified
- ***name*** (optional  UpperName)
- ***isExclusive*** (optional  Boolean)
- ***isExhaustive*** (optional  Boolean)
- ***classes*** (optional List of  Classes)None: every class can have an unnamed subtyping.

_ **ValueType**
_ **ReferenceType**
_ **CodeTypeADataTypeOrEnumerationUsedInTheModel**None: Often, a CodeType will be assigned to just one attribute in the model.  In
such cases, there's no need to declare a new Code Type and invent a name for it.
Instead:

- ***listTheCodeValuesAsABullettedListInsideTheDescriptionOfTheAttributeInTheFor
mCodeDescription***
- ***aCodeTypeWillBeCreatedWithTheNameClassAttributeCodeAndTheCodeValuesListedTh
atCodeTypeWillBeMarkedAsIsCaptive***
- ***isCaptive*** - the code type was implied by use in an attribute and is only
used for that attribute (optional  Boolean)
_ **CodeValue**None: CodeType

- ***code*** - A short code or abbreviationi for the value _ (optional
NameString)
- ***description*** - an explanation of what the code means (optional  RichText)
_ **Key** - a list of attributes of a class
- ***keyAttributes*** - the attributes of the base Class. (optional List of
Attributes)None: need ascending descending to support index keys or ordering keys.

_ **UniqueKey** - a list of attributes on which instances of the base class may
be keyed.None: order unimportant for Unique Keys.

## Attributes
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


_ **AttributeSection** - a group of attributes for a class that merit a shared
explanation.
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>


- ***isOptional*** - whether the attributes in this section, taken together, are
optional. (optional  Boolean)
_ **AttributeAPropertyOrCharacteristicOfAClass**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>

_plural_:  Attributes


- ***name*** (optional  LowerCamel)
!! Error: Missing oneLiner

_overrides_: CamelName_._

- ***dataType*** - The kind of object to which the attribute refers.  _
(optional  DataType)None: the section below on Data Type Specifiers.

__ _Cardinalities_ (None)
!! Error: Missing oneLiner


- ***isOptional*** - Indicates whether the attribute must have a value for every
instance of the class _ (optional  Boolean)
- ***cardinality*** - The cardinality of the relationship represented by the
attribute _ (optional  CardinalityCode)None:

- ***author*** (optional value InventedName)
!! Error: Missing oneLiner


- ***books*** (optional value InventedName)None: how this works with optionality

!! Error: Missing oneLiner


__ _Inverse Attributes_ (None)
!! Error: Missing oneLiner


- ***isInvertible*** (optional  Boolean)
!! Error: Missing oneLiner


- ***inverseClass*** - the class which contains, or would contain the inverse
attribute (optional  Class)
- ***inverseAttribute*** (optional  Attribute)
!! Error: Missing oneLiner


- ***inverseIsOptional*** (optional  Attribute)
!! Error: Missing oneLiner


_ **Formulas**
!! Error: Missing oneLiner


- ***default*** - The rule or formula for calculating the value, if no value is
supplied Now running to a second line with the parenthentical on yet a third
line (optional  Derivation)None: even when an Attribute has a default derivation, there’s no guarantee that
every instance will have an assigned value. Example needed.

!! Warning: oneLiner is too long. (143 chars).


- ***derivation*** - For derived attributes, the rule or formula for calculating
the value _ (optional  Derivation)None: on insert vs on access?

- ***constraints*** - Any validation rules specific to this attribute _
(optional List of  Constraints)None: from Class.constraints

__ _Override Tracking_ (None)
!! Error: Missing oneLiner


- ***overrides***
!! Error: Missing oneLiner
!! Error: No value for data_type_clause
!! Error: Required field 'data_type_clause' is missing


_ **ValueTypeDerivationARuleOrFormulaForDerivingTheValueOfAnAttribute**
!! Error: Missing oneLiner

_plural_:  Derivations


- ***statement*** - An English language statement of the derivation rule _
(optional  RichText)
- ***expression*** - The formal expression of the derivation in a programming
language _ (optional  CodeExpression)
_ **ValueTypeConstraintARuleConditionOrValidationThatMustBeSatisfiedByTheModel**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>

_plural_:  Constraints


- ***statement*** - An English language statement of the constraint _ (optional
RichText)
- ***expression*** - The formal expression of the constraint in a programming
language (optional value InventedName)
- ***severity*** (optional  Code)
!! Error: Missing oneLiner


- ***None*** - **Warning** - nothing fatal; just a caution
!! Error: Name is missing
!! Error: No value for data_type_clause
!! Error: Required field 'name' is missing
!! Error: Required field 'data_type_clause' is missing


- ***None*** - **Error** - serious. Fix now
!! Error: Name is missing
!! Error: No value for data_type_clause
!! Error: Required field 'name' is missing
!! Error: Required field 'data_type_clause' is missing


- ***message*** (optional  Template)
!! Error: Missing oneLiner


_ **ClassConstraint**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>


_ **AttributeConstraint**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>


_ **CodeExpression**
!! Error: Missing oneLiner


- ***language*** - the programming language (optional  Code)
- ***None*** - OCL: Object Constraint Language
!! Error: Name is missing
!! Error: No value for data_type_clause
!! Error: Required field 'name' is missing
!! Error: Required field 'data_type_clause' is missing


- ***None*** - Java: Java
!! Error: Name is missing
!! Error: No value for data_type_clause
!! Error: Required field 'name' is missing
!! Error: Required field 'data_type_clause' is missing


- ***expression*** (optional  String)
!! Error: Missing oneLiner


## Methods
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


_ **MethodABehaviorOrOperationAssociatedWithAClass**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>

_plural_:  Methods


- ***parameters*** - The input parameters of the method _ (optional List of
Parameters)
- ***returnType*** - The data type of the value returned by the method _
(optional  DataType)
_ **ParameterAnInputToAMethod**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>

_plural_:  Parameters


- ***type*** - The data type of the parameter _ (optional  DataType)
- ***cardinality*** - The cardinality of the parameter (optional value
InventedName)
## Data Types
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


_ **SimpleDataTypeSubtpeOfDataType**
!! Error: Missing oneLiner


- ***coreClass*** (optional  Class)
!! Error: Missing oneLiner


_ **ComplexDataType**
!! Error: Missing oneLiner


- ***aggregation*** (optional  AggregatingOperator)
!! Error: Missing oneLiner


- ***aggregatedTypes*** (optional List of  DataTypes)
!! Error: Missing oneLiner


_ **AggregatingOperator**
!! Error: Missing oneLiner


- ***name*** (optional  Code)
!! Error: Missing oneLiner


- ***None*** - **SetOf**
!! Error: Name is missing
!! Error: No value for data_type_clause
!! Error: Required field 'name' is missing
!! Error: Required field 'data_type_clause' is missing


- ***None*** - **ListOf**
!! Error: Name is missing
!! Error: No value for data_type_clause
!! Error: Required field 'name' is missing
!! Error: Required field 'data_type_clause' is missing


- ***None*** - **Mapping**
!! Error: Name is missing
!! Error: No value for data_type_clause
!! Error: Required field 'name' is missing
!! Error: Required field 'data_type_clause' is missing


- ***arity*** (optional  Integer)
!! Error: Missing oneLiner


- ***spelling*** (optional  Template)
!! Error: Missing oneLiner


## Low level Data Types
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


_ **ValueTypeCamelName**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>


- ***valueTheString*** (optional  String)None: "firstName", "orderDate", "customerID"
None: * *CamelName* is presented here, just after its first usage by another
class (Component), to provide context and understanding before it is used
further in the model.

!! Error: Missing oneLiner


_ **UpperCamel** - a CamelName that begins with a capital letterNone: _ "Customer", "ProductCategory", "PaymentMethod"

!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>
!! Error: For field 'where' - expected typing.Optional[Literate_01.OneLiner],
but got <class 'str'>

_where_:  content begins with an upper case letter.


_ **LowerCamel** - a CamelName that begins with a lower case letterNone: "firstName", "orderTotal", "shippingAddress"

!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>
!! Error: For field 'where' - expected typing.Optional[Literate_01.OneLiner],
but got <class 'str'>

_where_:  content begins with a lower case letter.


_ **QualifiedCamel** - an expression consisting of Camel Names separated by
periods
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>

_Constraint_:  content consists of CamelNames, separated by periods.  Each of the camel names must be Upper Camel except, possibly, the first.

_english_: 



_ **RichTextAStringWithMarkupForBlockLevelFormatting**
!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>


- ***value*** - the string content (optional  String)
- ***format*** - the rich text coding language used (optional  Code)
- ***html***
!! Error: Missing oneLiner
!! Error: No value for data_type_clause
!! Error: Required field 'data_type_clause' is missing


- ***markDown***
!! Error: Missing oneLiner
!! Error: No value for data_type_clause
!! Error: Required field 'data_type_clause' is missing


_ **RichLine** - String with markup for line level formatting.
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>


- ***value*** - the string content (optional  String)
_ **PrimitiveType**None:

!! Error: Missing oneLiner
!! Error: For field 'subtype_of' - expected
typing.Optional[typing.List[Literate_01.SubtypeBy]], but got <class 'list'>


## Appendices Insert More Sidebars md Insert Overrides md insert LDM Intro md
Insert OCL md Insert Camel Case md
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


### Annotation Types Used
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


### Annotation types as CSV
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>


## Appendices Insert More Sidebars md Insert Overrides md insert LDM Intro md
Insert OCL md Insert Camel Case md
!! Error: Missing oneLiner
!! Error: For field 'name' - expected <class 'utils.class_casing.CamelCase'>,
but got <class 'Literate_01.SubjectName'>

