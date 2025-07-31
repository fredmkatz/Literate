
# Literate Data Model
!! Warning: oneLiner is too long. (126 chars).


## Preliminaries - the basic structure of the model
!! Warning: oneLiner is too long. (96 chars).


_ **Component** - An element or building block of the literate data model
!! Warning: oneLiner is too long. (116 chars).

_plural_: Components

- ***normalName*** - the name of the component, not in camel case (optional
String (O_O))None: This is a warning with emoji

- ***name*** - The name of the component (optional  CamelName (O_O))
- ***qualifiedName*** (optional  QualifiedCamel (O_O))
- ***abbreviatedName*** - a short form of the component's name, used for cross
references and improved readability. (optional  CamelName (O_O))None: "LDM" is the short form of "Literate Data Model".

- ***oneLiner*** - A brief, one-line definition or description of the component,
suitable for use in a descriptive table of contents. _ (optional  OneLiner
(O_O))
- ***elaboration*** - A more detailed explanation or discussion of the component
_ (optional  RichText (O_O))
- ***isEmbellishment*** - Indicates whether this component is an embellishment
added during post-parsing processing _ (optional  Boolean (O_O))
__ _For Machinery_ - mechanical attributes (None)
!! Warning: oneLiner is too long. (91 chars).


- ***isEmbellishment*** - Indicates whether this component is an embellishment
added during post-parsing processing _ (optional  Boolean (O_O))
_ **AnnotationType** - a kind of note, or aside, used to call attention to
additional information about some Component.None: Each LDM declares a set of Annotation Types, with defined labels, emojis,
and clearly documented purposes. These are *recognized* or *registered*
Annotation Types.
_plural_: AnnotationTypes

- ***emoji*** - an emoji (optional  Emoji (O_O))
- ***emojiName*** - an emoji (optional  String (O_O))
- ***emojiUnicode*** - the Unicode for the emoji (optional  String (O_O))
- ***label*** - A short label to indicate the purpose of the annotation _
(optional  LowerCamel (O_O))
- ***plural*** - the plural form of the label (optional  UpperCamel (O_O))
- ***purpose*** - the intended reason for the annotation. (optional  OneLiner
(O_O))
__ _Implied Attributes_ - created for AnnotationType (None)
- ***baseLiterateModel*** - A link back to the LiterateModel on which this
AnnotationType depends. (optional value LiterateModel (M_1))
- ***inverseOfAnnotationType*** - Inverse attribute for
Annotation.annotationType from which this was implied. (optional value
Annotation (M_1))_inverse_: _._annotationType

_ **Annotation** - A note or comment associated with a model element_plural_: Annotations

- ***annotationType*** (optional  AnnotationType (O_O))None: An Annotation is considered to *recognized* if the label is associated
with an Annotation Type. otherwise it is *ad hoc*.
None: Should be a Value  Type
_inverse_: _._inverseOfAnnotationType

- ***label*** - A short label to indicate the purpose of the annotation _
(optional  CamelName (O_O))
- ***emoji*** (optional  Emoji (O_O))
- ***content*** - The content or body of the annotation (optional  RichText
(O_O))
__ _For Machinery_ (None)
!! Warning: oneLiner is too long. (92 chars).


- ***isEmbellishment*** - Indicates whether this annotation is an embellishment
added during post-parsing processing _ (optional  Boolean (O_O))
__ _Implied Attributes_ - created for Annotation (None)
- ***baseComponent*** - A link back to the Component on which this Annotation
depends. (optional value Component (M_1))
## The Model and its Subjects
!! Warning: oneLiner is too long. (112 chars).


_ **LiterateModel** - A representation of a domain's entities, attributes, and
relationships, along with explanatory text and examples_plural_: LiterateModels

- ***name*** (optional  UpperCamel (O_O))_overrides_: _._name

- ***allSubjects*** - list of all classes in the model, as ordered in the
definition of the model. (optional List of  Classes (O_O))
!! Error: Missing value for required field: 'python'

_inverse_: _._inverseOfAllSubjects

- ***allClasses*** - list of all classes in the model, as ordered in the
definition of the model. (optional List of  Classes (O_O))
!! Error: Missing value for required field: 'python'

_inverse_: _._inverseOfAllClasses

__ _Modeling Configuration_ (None)
- ***annotationTypes*** (optional List of  AnnotationTypes (O_O))
- ***preferredCodingLanguage*** - the recommended lanquage  for expressing
derivation, defaults, and constraints (optional  CodingLanguage (O_O))
- ***alternateCodingLanguages*** (optional List of  CodingLanguages (O_O))
- ***preferredTemplateLanguage*** - the recommended lanquage  for expressing
derivation, defaults, and constraints (optional  TemplateLanguage (O_O))
- ***alternateTemplateLanguages*** (optional List of  TemplateLanguages (O_O))
- ***aiFunctions*** - A list of functions that require sophisticated AI-powered
implementation * (optional List of  String (O_O))
_ **Subject** - A specific topic or theme within the model
!! Warning: oneLiner is too long. (91 chars).
!! Warning: oneLiner is too long. (94 chars).

_plural_: Subjects

- ***name*** (optional  UpperCamel (O_O))_overrides_: _._name

- ***parentSubject*** - The parent subject, if any, under which this subject is
nested _ (optional  Subject (O_O))_inverse_: _._inverseOfParentSubject

- ***classes*** - The major classes related to this subject, in the order in
which they should be presented _ (optional List of  Classes (O_O))None: define chapter, section, subsection as levels?
_inverse_: _._inverseOfClasses

- ***childSubjects*** - Any child subjects nested under this subject, in the
order in which they should be presented _ (optional List of  Subjects (O_O))_inverse_: _._parentSubject

__ _Implied Attributes_ - created for Subject (None)
- ***baseLiterateModel*** - A link back to the LiterateModel on which this
Subject depends. (optional value LiterateModel (M_1))
- ***inverseOfParentSubject*** - Inverse attribute for Subject.parentSubject
from which this was implied. (optional value Subject (M_1))_inverse_: _._parentSubject

_ **SubjectArea** - A main topic or area of focus within the model, containing
related subjects and classes_plural_: SubjectAreas
_where_:  parentSubject is absent


__ _Implied Attributes_ - created for SubjectArea (None)
- ***baseLiterateModel*** - A link back to the LiterateModel on which this
SubjectArea depends. (optional value LiterateModel (M_1))
### Classes
_ **Class** - A key entity or object type in the model, often corresponding to a
real-world concept
!! Error: Missing value for required field: 'python'
!! Warning: oneLiner is too long. (91 chars).

_plural_: Classes
_Constraint_:  Within each Class, attribute names must be unique.


- ***pluralForm*** - the normal English plural form of the name of the Class
(optional  UpperCamel (O_O))None: When inputting a model, you will rarely need to specify the plural form.
The input program will just look it up.

- ***basedOn*** - the Class or Classes on which this class is dependent
(optional Set of  Class (O_O))None: that basedOn and dependentOf are being used synonymousle in this
metamodel.
_inverse_: _._inverseOfBasedOn

- ***supertypes*** - The parent class or classes from which this class inherits
attributes (optional List of  Classes (O_O))_inverse_: _._inverseOfSupertypes

- ***subtypings*** - the criteria, or dimensions, by which the class can be
divided into subtypes (optional List of  Subtypings (O_O))None: in a library model, the `Book` class could have subtypings based on genre
(e.g., Fiction, Non-fiction), format (e.g., Hardcover, Paperback), or subject
(e.g., Science, History).
_inverse_: _._inverseOfSubtypings

- ***subtypes*** - Any subtypes or specializations of this class based on it’s
subtypings. (optional List of  Classes (O_O))None: For instance, using the `Book` example, the subtypes could include
`FictionBook`, `Non-fictionBook`, `HardcoverBook`, `PaperbackBook`,
`ScienceBook`, and `HistoryBook`.
_inverse_: _._inverseOfSubtypes

- ***attributes*** - The attributes or properties of the class, in the order in
which they should be presented _ (optional List of  Attributes (O_O))_inverse_: _._inverseOfAttributes

- ***attributeSections*** - additional attributes or properties of the class,
grouped for clarity and elaboration.  _ (optional List of  AttributeSections
(O_O))_inverse_: _._inverseOfAttributeSections

- ***constraints*** - Any constraints, rules, or validations specific to this
class _ (optional List of  Constraints (O_O))None: Constraints may be expressed on either the Class or the Attribute. Always?

- ***methods*** - Any behaviors or operations associated with this class _
(optional List of  Methods (O_O))_inverse_: _._inverseOfMethods

__ _Implied Attributes_ (None)
- ***dependents*** - the Classes which are basedOn this Class (optional Set of
Classes (O_O))_inverse_: _._basedOn

- ***uniqueKeys*** (optional Set of  UniqueKeys (O_O))_inverse_: _._basedOn

- ***inverseOfAllSubjects*** - Inverse attribute for LiterateModel.allSubjects
from which this was implied. (optional value LiterateModel (M_1))_inverse_: _._allSubjects

- ***inverseOfAllClasses*** - Inverse attribute for LiterateModel.allClasses
from which this was implied. (optional value LiterateModel (M_1))_inverse_: _._allClasses

- ***inverseOfClasses*** - Inverse attribute for Subject.classes from which this
was implied. (optional value Subject (M_1))_inverse_: _._classes

- ***inverseOfBasedOn*** - Inverse attribute for Class.basedOn from which this
was implied. (optional value Class (M_1))_inverse_: _._basedOn

- ***inverseOfSupertypes*** - Inverse attribute for Class.supertypes from which
this was implied. (optional value Class (M_1))_inverse_: _._supertypes

- ***inverseOfSubtypes*** - Inverse attribute for Class.subtypes from which this
was implied. (optional value Class (M_1))_inverse_: _._subtypes

- ***inverseOfClasses*** - Inverse attribute for Subtyping.classes from which
this was implied. (optional value Subtyping (M_1))_inverse_: _._classes

- ***inverseOfCoreClass*** - Inverse attribute for
SimpleDataTypeSubtpeOfDataType.coreClass from which this was implied. (optional
value SimpleDataTypeSubtpeOfDataType (M_1))_inverse_: _._coreClass

_ **Subtyping** - a way in which subtypes of a Class may be classified_plural_: Subtypings

- ***name*** (optional  LowerCamel (O_O))
- ***isExclusive*** (optional  Boolean (O_O))
- ***isExhaustive*** (optional  Boolean (O_O))
- ***classes*** (optional List of  Classes (O_O))None: every class can have an unnamed subtyping.
_inverse_: _._inverseOfClasses

__ _Implied Attributes_ - created for Subtyping (None)
- ***inverseOfSubtypings*** - Inverse attribute for Class.subtypings from which
this was implied. (optional value Class (M_1))_inverse_: _._subtypings

- ***baseClass*** - A link back to the Class on which this Subtyping depends.
(optional value Class (M_1))
_ **ReferenceType** - A class that is presumed to be used as a reference, rather
than a value_plural_: ReferenceTypes

_ **Key** - a list of attributes of a class_plural_: Keys

- ***keyAttributes*** - the attributes of the base Class. (optional List of
Attributes (O_O))
!! Error: Missing value for required field: 'python'
!! Error: Missing value for required field: 'python'

_inverse_: _._inverseOfKeyAttributes

__ _Implied Attributes_ - created for Key (None)
- ***baseClass*** - A link back to the Class on which this Key depends.
(optional value Class (M_1))
_ **UniqueKey** - a list of attributes on which instances of the base class may
be keyed.None: order unimportant for Unique Keys.
_plural_: UniqueKeys

## Attributes
_ **AttributeSection** - a group of attributes for a class that merit a shared
explanation._plural_: AttributeSections

- ***isOptional*** - whether the attributes in this section, taken together, are
optional. (optional  Boolean (O_O))
__ _Implied Attributes_ - created for AttributeSection (None)
- ***inverseOfAttributeSections*** - Inverse attribute for
Class.attributeSections from which this was implied. (optional value Class
(M_1))_inverse_: _._attributeSections

- ***baseClass*** - A link back to the Class on which this AttributeSection
depends. (optional value Class (M_1))
_ **Attribute** - A property or characteristic of a class_plural_: Attributes

- ***name*** (optional  LowerCamel (O_O))_overrides_: _._name

- ***dataType*** - The kind of object to which the attribute refers.  _
(optional  DataType (O_O))None: the section below on Data Type Specifiers.

__ _Cardinalities_ (None)
- ***isOptional*** - Indicates whether the attribute must have a value for every
instance of the class _ (optional  Boolean (O_O))
- ***cardinality*** - The cardinality of the relationship represented by the
attribute _ (optional  Cardinality (O_O))
!! Warning: Formula one_liner is too long (220 chars)


__ _Inverse Attributes_ (None)
- ***isInvertible*** (optional  Boolean (O_O))
- ***inverseClass*** - the class which contains, or would contain the inverse
attribute (optional  Class (O_O))
- ***inverseAttribute*** (optional  Attribute (O_O))
- ***inverseIsOptional*** (optional  Attribute (O_O))
__ _Formulas_ (None)
!! Warning: oneLiner is too long. (143 chars).


- ***default*** - The rule or formula for calculating the value, if no value is
supplied Now running to a second line with the parenthentical on yet a third
line (optional  Derivation (O_O))None: even when an Attribute has a default derivation, there’s no guarantee that
every instance will have an assigned value. Example needed.

- ***derivation*** - For derived attributes, the rule or formula for calculating
the value _ (optional  Derivation (O_O))None: on insert vs on access?

- ***constraints*** - Any validation rules specific to this attribute _
(optional List of  Constraints (O_O))None: from Class.constraints

__ _Override Tracking_ (None)
- ***overrides*** - the higher level attribute which this one overrides - for
type or ... (optional  Attribute (O_O))
__ _Implied Attributes_ - created for Attribute (None)
- ***inverseOfAttributes*** - Inverse attribute for Class.attributes from which
this was implied. (optional value Class (M_1))_inverse_: _._attributes

- ***inverseOfKeyAttributes*** - Inverse attribute for Key.keyAttributes from
which this was implied. (optional value Key (M_1))_inverse_: _._keyAttributes

- ***baseAttributeSection*** - A link back to the AttributeSection on which this
Attribute depends. (optional value AttributeSection (M_1))
## Methods
_ **Method** - A behavior or operation associated with a class_plural_: Methods

- ***parameters*** - The input parameters of the method _ (optional List of
Parameters (O_O))_inverse_: _._inverseOfParameters

- ***returnType*** - The data type of the value returned by the method _
(optional  DataType (O_O))
__ _Implied Attributes_ - created for Method (None)
- ***inverseOfMethods*** - Inverse attribute for Class.methods from which this
was implied. (optional value Class (M_1))_inverse_: _._methods

_ **Parameter** - An input to a method_plural_: Parameters

- ***type*** - The data type of the parameter (optional  DataType (O_O))
- ***cardinality*** - The cardinality of the parameter. e.g., optional,
required. (optional  Cardinality (O_O))
__ _Implied Attributes_ - created for Parameter (None)
- ***inverseOfParameters*** - Inverse attribute for Method.parameters from which
this was implied. (optional value Method (M_1))_inverse_: _._parameters

## Trivial Data Types
## Trivial Low level Data Types
### Annotation Types Used
### Annotation types as CSV
## Appendices - various sidebars to include Insert More Sidebars.md Insert
Overrides.md insert LDM Intro.md Insert OCL.md Insert Camel Case.md