# None

## Preliminaries - the basic structureof the model

            In Literate Data Modeling, the main components of interest are typically
            Classes, Attributes, Models, and Subjects. However, to streamline the model and
            promote reusability, we introduce a supertype called Component. By defining
            common attributes and behaviors in the Component class, we can inherit them in
            the subclasses, ensuring consistency and reducing duplication throughout the
            model.

            We present the Component class first because it is a best practice in modeling
            to introduce supertypes before their subtypes. This approach allows readers to
            understand the general concepts and shared properties before delving into the
            specifics of each specialized component.

_ Component - An element or building block of the literate data model

            isValueType: False
    - normalName - the name of the component, not in camel case (*String*)

    - name - The name of the component (CamelName)

    - qualifiedName (*QualifiedCamel*)

    - abbreviatedName - a short form of the component's name, used for cross
            references and improved readability. (*CamelName*)

         Example: "LDM" is the short form of "Literate Data Model".
    - oneLiner - A brief, one-line definition or description of the component,
            suitable for use in a descriptive table of contents. _ (RichLine)

    - elaboration - A more detailed explanation or discussion of the component _
            (RichText)

__ For Machinery - mechanical attributes

    - isEmbellishment - Indicates whether this component is an embellishment
            added during post-parsing processing _ (Boolean)

         Note: This attribute is set to true for components that are
            automatically generated or added during the fleshing out, review, or
            rendering processes, such as implied attributes or suggested model
            elements. It helps distinguish embellishments from the core model
            elements defined in the original LDM source.
__ Markdown Support

    - mdPrefix (*[String](#string)

    - mdSuffix (*[String](#string)

    - mdTopLine (*[String](#string)

_ AnnotationType - a kind of note, or aside, used to call attention to
            additional information about some Component.

         Note: Each LDM declares a set of Annotation Types, with defined labels,
            emojis, and clearly documented purposes. These are *recognized* or
            *registered* Annotation Types.But, if none of these fit, you can
            introduce an Annotation with any label. It would have an *ad hoc*
            Annotation Type.
            basedOn: Literate Data Model
            isValueType: False
    - emoji - an emoji (Emoji)

    - emojiName - an emoji (String)

    - emojiUnicode - the Unicode for the emoji (Unicode)

    - label - A short label to indicate the purpose of the annotation _
            (CamelName)

    - plural - the plural form of the label (*UpperCamel*)

    - Purpose - the intended reason for the annotation.

_ ValueType: AnnotationA note or comment associated with a model element

            basedOn: Component
            isValueType: False
    - annotationType (optional Annotation Type)

         Note: An Annotation is considered to *recognized* if the label is
            associated with an Annotation Type. otherwise it is *ad hoc*.
    - label - A short label to indicate the purpose of the annotation _
            (CamelName)

            But any short label is valid.

    - Emoji (optional Emoji)

    - content - The content or body of the annotation (*RichText*)

__ For Machinery

    - isEmbellishment - Indicates whether this annotation is an embellishment
            added during post-parsing processing _ (Boolean)

         Note: This attribute is set to true for annotations that are
            automatically generated or added during the fleshing out, review, or
            rendering processes, such as suggestions, issues, or diagnostic
            messages. It helps distinguish embellishment annotations from the
            annotations defined in the original LDM source.
## The Model and its Subjects

_ LiterateDataModel - A representation of a domain's entities, attributes, and
            relationships,along with explanatory text and examples

            plural:  LiterateDataModels
            subtypeOf: Component
            isValueType: False
    - name (UpperCamel)

    - allSubjects - list of all classes in the model, as ordered in
            thedefinition of the model. (List of Classes)

    - allClasses - list of all classes in the model, as ordered in the
            definition of the model. (List of Classes)

__ Modeling Configuration

    - annotationTypes (List of AnnotationTypes)

    - Preferred Coding Language - the recommended lanquage  for expressing
            derivation, defaults, and constraints (Coding Language)

    - alternate Coding Languages (optional List of Coding Languages)

    - Preferred Template Language - the recommended lanquage  for expressing
            derivation, defaults, and constraints (Template Language)

    - alternate Template Languages (optional List of Template Languages)

    - aiFunctions - A list of functions that require sophisticated AI-powered
            implementation * (List of String)

__ Markdown Support

    - mdPrefix (*[String](#string)

    - mdTopLine (*[String](#string)

_ SubjectA specific topic or theme within the model

            Subjects are the chapters an sections of the model.  + A subject need not
            contain any Classes if it’s just expository.

            plural:  Subjects
            subtypeOf: Component
            dependentOf: LiterateDataModel
            isValueType: False
    - name (UpperCamel)

    - parentSubject - The parent subject, if any, under which this subject is
            nested _ (Subject, optional)

    - Classes - The major classes related to this subject, in the order in which
            they should be presented _ (ListOf Classes)

         Issue: define chapter, section, subsection as levels?***DSL***:
            Generally, it is best to present the classes within a Subject in top
            down order:
    - Each Class should be followed first by the classes that are dependent on
            it, and then

    - By its subtype classes.

    - childSubjects - Any child subjects nested under this subject, in the order
            in which they should be presented _ (ListOf Subjects)

            ***DSL***:  the Classes within a Subject are always displayed before the
            childSubjects.

            inverse: Subject_._parentSubject
__ Markdown Support

    - mdPrefix (*[String](#string)

    - mdTopLine (*[String](#string)

_ SubjectAreaA main topic or area of focus within the model, containing related
            subjects and classes

            plural:  SubjectAreas
            subtypeOf: Subject
            isValueType: False
            where:  parentSubject is absent
### Classes

_ Class - A key entity or object type in the model, often corresponding to a
            real-world concept

            plural:  Classes
            subtypeOf: Component
            isValueType: False
            Constraint:  Within each Class, attribute names must be unique.
    - pluralForm - the normal English plural form of the name of the Class
            (UpperName)

            Might be Books for the Book class or other regular plurals.  + But also might be
            People for Person.

         Note: When inputting a model, you will rarely need to specify the
            plural form. The input program will just look it up.
    - basedOn - the Class or Classes on which this class is dependent (SetOf
            Classes)

            This is solely based on **Existence Dependency**. A true dependent entity cannot
            logically exist without the related parent entity. For instance, an Order Item
            cannot exist without an Order. If removing the parent entity logically implies
            removing the dependent entity, then it is a dependent entity.

         Note: that basedOn and dependentOf are being used synonymousle in this
            metamodel.ToDo - fix that
    - supertypes - The parent class (es)

    - subtypings - the criteria, or dimensions, by which the class can be
            divided into subtypes (list of Subtypings)

         Example: in a library model, the `Book` class could have subtypings
            based on genre (e.g., Fiction, Non-fiction), format (e.g.,
            Hardcover, Paperback), or subject (e.g., Science, History).
    - subtypes - Any subtypes or specializations of this class based on it’s
            subtypings. _ (ListOf Classes)

         Example: For instance, using the `Book` example, the subtypes could
            include `FictionBook`, `Non-fictionBook`, `HardcoverBook`,
            `PaperbackBook`, `ScienceBook`, and `HistoryBook`.
    - attributes - The attributes or properties of the class, in the order in
            which they should be presented _ (ListOf Attributes)

    - attributeSections - additional attributes or properties of the class,
            grouped for clarity and elaboration.  _ (ListOf AttributeSections)

    - constraints - Any constraints, rules, or validations specific to this
            class _ (ListOf Constraints)

         Note: Constraints may be expressed on either the Class or the
            Attribute. Always?Add examples where clarity would favor one or the
            other.   Sometimes just a matter of taste.
    - methods - Any behaviors or operations associated with this class _ (ListOf
            Methods)

__ Implied Attributes

    - dependents - the Classes which are basedOn this Class (optional SetOf
            Classes)

            inverse: Class_._basedOn
    - UniqueKeys (optional Set of UniqueKeys)

            inverse: UniqueKey_._basedOn
_ Subtyping - a way in which subtypes of a Class may be classified (Subtype of
            Component)

            dependentOf: Class
            isValueType: False
    - name (Upper Name)

    - is exclusive (Boolean)

    - is exhaustive (Boolean)

    - classes (List of Classes)

            ***DSL***:  Shown in the DSL as  + > Subbtypes: byBrand - Brand1, Brand2,...
            (non exclusive, exhaustive)  + on the super class. And as  + > Subtype of:
            SuperClass byBrand  + on the subclass.

         Note: every class can have an unnamed subtyping.Also,  each subtyping
            is by default Exclusive and  Exhaustive. So those stipulations may
            be omitted.
_ ValueType

            subtypeOf: Class.
            isValueType: False
__ Markdown Support

    - mdPrefix (*[String](#string)

_ Reference Type

            subtypeOf: Class.
            isValueType: False
_ CodeTypeA data type or enumeration used in the model

         Note: Often, a CodeType will be assigned to just one attribute in the
            model.  In such cases, there's no need to declare a new Code Type
            and invent a name for it.  Instead:
            subtypeOf: ValueType.
            isValueType: False
    - List the code values as a bulletted list inside the description of the
            attribute in the form:‘code: description’

    - A Code Type will be created with the name [class][attribute]Code and the
            code values listed. That CodeType will be marked as isCaptive.

    - isCaptive - the code type was implied by use in an attribute and is only
            used for that attribute (Boolean)

_ Code Value

         A possible value for an enumerated data class  DependentOf: CodeType
            isValueType: False
    - code - A short code or abbreviationi for the value _ (NameString)

    - description - an explanation of what the code means (*RichText*)

_ Key - a list of attributes of a class

            subtypeOf: Component
            dependentOf: Class
            isValueType: False
    - keyAttributes - the attributes of the base Class. (List of Attributes)

         Issue: need ascending descending to support index keys or ordering
            keys.
_ UniqueKey - a list of attributes on which instances of the base class may be
            keyed.

         Note: order unimportant for Unique Keys.
            subtypeOf: Key
            isValueType: False
## Attributes

_ Attribute Section - a group of attributes for a class that merit a shared
            explanation.

            subtypeOf: Component.
            basedOn: Class
            isValueType: False
    - isOptional - whether the attributes in this section, taken together, are
            optional. (Boolean)

            If the Attribute Section is required,then each Attribute within the sectional is
            optional ot required, depending on how it is marked.  + &nbsp;  + But if the
            Arrribute Section is optional each attribute in the section is only required if
            any attribute in the section is ptresent.

__ Markdown Support

    - mdPrefix (*[String](#string)

    - mdTopLine (*[String](#string)

_ AttributeA property or characteristic of a class

            plural:  Attributes
            subtypeOf: Component
            basedOn: AttributeSection
            isValueType: False
    - name (Lower Camel)

            overrides: CamelName_._
    - dataType - The kind of object to which the attribute refers.  _ (DataType)

            But,

    - List of Editions

    - Set of Edition

    - ... and more complicated cases.

         See: the section below on Data Type Specifiers.
__ Cardinalities.

    - isOptional - Indicates whether the attribute must have a value for every
            instance of the class _ (Boolean)

    - cardinality - The cardinality of the relationship represented by the
            attribute _ (CardinalityCode)

         For example:
    - author (1:1 Author)

    - books (optional N:M Set of Books)

         Note: how this works with optionality
__ Inverse Attributes

    - isInvertible (Boolean)

    - inverseClass - the class which contains, or would contain the inverse
            attribute (optional Class)

    - inverseAttribute (optional Attribute)

    - inverseIsOptional (optional Attribute)

_ Formulas

            isValueType: False
    - default - The rule or formula for calculating the value, if no value is
            suppliedNow running to a second line with the parenthentical on yet
            a third line  - (Derivation, optional)

         Note: even when an Attribute has a default derivation, there’s no
            guarantee that every instance will have an assigned value. Example
            needed.And let's see if the note can span extra lines, too
    - derivation - For derived attributes, the rule or formula for calculating
            the value _ (Derivation, optional)

         Issue: on insert vs on access?
    - constraints - Any validation rules specific to this attribute _ (ListOf
            Constraints)

         Note: from Class.constraints
__ Override Tracking

    - Overrides

_ ValueType: DerivationA rule or formula for deriving the value of an attribute

            plural:  Derivations
            isValueType: False
    - statement - An English language statement of the derivation rule _
            (RichText)

    - expression - The formal expression of the derivation in a programming
            language _ (CodeExpression)

_ ValueType: ConstraintA rule, condition, or validation that must be satisfied
            by the model

            plural:  Constraints
            subtypeOf: Component
            isValueType: False
    - statement - An English language statement of the constraint _ (RichText)

    - expression - The formal expression of the constraint in a programming
            language (e.g., OCL _(CodeExpression)

    - severity (Code)

    -  - **Warning** - nothing fatal; just a caution

    -  - **Error** - serious. Fix now

    - Message (Template)

_ Class Constraint

            subtypeOf: Constraint
            basedOn: Class.
            isValueType: False
_ Attribute Constraint

            subtypeOf: Constraint
            basedOn: Attribute
            isValueType: False
_ CodeExpression

            isValueType: False
    - Language - the programming language (Code)

    -  - OCL: Object Constraint Language

    -  - Java: Java

    - Expression (String)

## Methods

_ MethodA behavior or operation associated with a class

            plural:  Methods
            subtypeOf: Component
            isValueType: False
    - parameters - The input parameters of the method _ (ListOf Parameters)

    - returnType - The data type of the value returned by the method _
            (DataType)

_ ParameterAn input to a method

            plural:  Parameters
            subtypeOf: Component
            isValueType: False
    - type - The data type of the parameter _ (DataType)

    - cardinality - The cardinality of the parameter (e.g., optional, required)

## Data Types

            *ValueType*:**Data Type**

_ Simple Data TypeSubtpeOf: DataType

            isValueType: False
    - coreClass (Class)

_ Complex Data Type

            isValueType: False
    - aggregation (Aggregating Operator)

    - aggregatedTypes (List of DataTypes)

_ Aggregating Operator

            isValueType: False
    - Name (Code)

    -  - **SetOf**

    -  - **ListOf**

    -  - **Mapping**

    - arity (Integer)

    - spelling (Template)

## Low level Data Types

            insert Camel Case.md

_ ValueType: CamelName

            A short string without punctuation or spaces, suitable for names, labels, or
            identifiers and presented in camel case.

            subtypeOf: String
            isValueType: False
    - value: the string (String)

         Example: "firstName", "orderDate", "customerID"
         ModelingNote: * *CamelName* is presented here, just after its first
            usage by another class (Component), to provide context and
            understanding before it is used further in the model.
_ UpperCamel - a CamelName that begins with a capital letter

         Example: _ "Customer", "ProductCategory", "PaymentMethod"
            subtypeOf: CamelName
            isValueType: False
            where:  content begins with an upper case letter.
_ LowerCamel - a CamelName that begins with a lower case letter

         Example: "firstName", "orderTotal", "shippingAddress"
            subtypeOf: CamelName
            isValueType: False
            where:  content begins with a lower case letter.
_ Qualified Camel - an expression consisting of Camel Names separated by periods

            subtypeOf: String
            isValueType: False
            Constraint:  content consists of CamelNames, separated by periods.  Each of the camel names must be Upper Camel except, possibly, the first.
_ RichText.  A string with markup for block level formatting.

            subtypeOf: String
            isValueType: False
    - value - the string content (string)

    - format - the rich text coding language used (Code)

    - HTML

    - MarkDown

_ RichLine - String with markup for line level formatting.

            subtypeOf: RichText
            isValueType: False
    - value - the string content (string)

_ PrimitiveType

         Values: **String**
            subtypeOf: ValueTypeA basic, built-in data type
            isValueType: False
## AppendicesInsert More Sidebars.md - Insert Overrides.md  - insert LDM
            Intro.md  - Insert OCL.md  - Insert Camel Case.md

### Annotation Types Used

            These are the recognized Annotation Types for the LDM model.

            And this is how you register the AnnotationTyped for a model. By including this
            sort of array in the DSL document for the model.

            ```typescriptinterface AnnotationType {  - label: string;  - emoji: string;  -
            emojiName: string;  - emojiUnicode: string;  - purpose: string;  - }  - // LINK:
            LiterateDataModel.annotationTypes  - const annotationTypes: AnnotationType[] = [
            - {  - label: "Error",  - emoji: "",  - emojiName: "cross_mark",  -
            emojiUnicode: "U+274C",  - purpose: "Indicates a critical error or failure in
            the model."  - },  - {  - label: "Warning",  - emoji: "",  - emojiName:
            "warning",  - emojiUnicode: "U+26A0",  - purpose: "Indicates a potential issue
            or warning in the model."  - },  - {  - label: "Note",  - emoji: "",  -
            emojiName: "blue_book",  - emojiUnicode: "U+1F4D8",  - purpose: "Provides
            additional context, explanations, or clarifications for the annotated element."
            - },  - {  - label: "Issue",  - emoji: "",  - emojiName: "warning",  -
            emojiUnicode: "U+26A0",  - purpose: "Highlights a potential issue or error that
            needs to be addressed or resolved."  - },  - {  - label: "Question",  - emoji:
            "",  - emojiName: "question",  - emojiUnicode: "U+2753",  - purpose: "Raises a
            question or seeks further clarification about the annotated element."  - },  - {
            - label: "Suggestion",  - emoji: "",  - emojiName: "bulb",  - emojiUnicode:
            "U+1F4A1",  - purpose: "Provides a suggestion or recommendation for improving
            the model or the annotated element."  - },  - {  - label: "Info",  - emoji: "",
            - emojiName: "information_source",  - emojiUnicode: "U+2139",  - purpose:
            "Offers relevant information, facts, or details about the annotated element."  -
            },  - {  - label: "Todo",  - emoji: "",  - emojiName: "pushpin",  -
            emojiUnicode: "U+1F4CC",  - purpose: "Indicates a pending task, action item, or
            future work related to the annotated element."  - },  - {  - label: "Reference",
            - emoji: "",  - emojiName: "globe_with_meridians",  - emojiUnicode: "U+1F310",
            - purpose: "Provides a reference or link to an external resource or
            documentation."  - },  - {  - label: "See",  - emoji: "",  - emojiName: "mag",
            - emojiUnicode: "U+1F50D",  - purpose: "Indicates a cross-reference to another
            relevant element within the model."  - }  - ];  - ```

            ===

## AppendicesInsert More Sidebars.md - Insert Overrides.md  - insert LDM
            Intro.md  - Insert OCL.md  - Insert Camel Case.md

