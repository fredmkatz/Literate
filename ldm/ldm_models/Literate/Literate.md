# Literate Data Model



## Preliminaries - the basic structure of the model


In Literate Data Modeling, the main components of interest are typically Classes, Attributes, Models, and Subjects. However, to streamline the model and promote reusability, we introduce a supertype called Component. By defining common attributes and behaviors in the Component class, we can inherit them in the subclasses, ensuring consistency and reducing duplication throughout the model.  

We present the Component class first because it is a best practice in modeling to introduce supertypes before their subtypes. This approach allows readers to understand the general concepts and shared properties before delving into the specifics of each specialized component.


_ **Component** - An element or building block of the literate data model 
- **normalName** - the name of the component, not in camel case (*String*)
⚠️ Warning: This is a warning with emoji
- **name** - The name of the component (CamelName)



- **qualifiedName** - (*QualifiedCamel*)
- **abbreviatedName** - a short form of the component's name, used for cross references and improved readability. (*CamelName*)
	***Example***: "LDM" is the short form of "Literate Data Model".

	***Default***: name -  how do you say name in english?
  python: x.name == y

  constraint: the abbreviated name should be shorter than the actual name
  python: len(abbreviatedName) < len(name)
  severity: Warning
  message:  Why have an abbreviation longer than the name?
  Note: Does this annotation find it's way to the Constraint? YES! It's fixed!


- **oneLiner** - A brief, one-line definition or description of the component, suitable for use in a descriptive table of contents. _(OneLiner)_  

- **elaboration** - A more detailed explanation or discussion of the component _(RichText)_  

__  ***For Machinery*** - mechanical attributes
- **isEmbellishment** - Indicates whether this component is an embellishment added during post-parsing processing _(Boolean)_
  🔄 ***Default***: false
  ℹ️ ***Note***: This attribute is set to true for components that are automatically generated or added during the fleshing out, review, or rendering processes, such as implied attributes or suggested model elements. It helps distinguish embellishments from the core model elements defined in the original LDM source.
	

_ **AnnotationType** - a kind of note, or aside, used to call attention to additional information about some Component. 
***Based on*** : LiterateModel
***Note***: Each LDM declares a set of Annotation Types, with defined labels, emojis, and clearly documented purposes. These are *recognized* or *registered* Annotation Types. 
But, if none of these fit, you can  introduce an Annotation with any label. It would have an *ad hoc* Annotation Type. 
- **emoji** - an emoji (Emoji)
- **emojiName** - an emoji (String)
- **emojiUnicode** - the Unicode for the emoji (String)
- **label** - A short label to indicate the purpose of the annotation _(LowerCamel)_  
- **plural** - the plural form of the label (*UpperCamel*).  
    Default: based on label
 - **Purpose** - the intended reason for the annotation. (OneLiner)



_ **Annotation**  - A note or comment associated with a model element  
***Based on***: Component 
- **annotationType** - (optional Annotation Type) 
Note: An Annotation is considered to *recognized* if the label is associated with an Annotation Type. otherwise it is *ad hoc*.  
Note: Should be a Value  Type

- **label** - A short label to indicate the purpose of the annotation _(CamelName)_  

     
     But any short label is valid. 
   Default: from annotationType

- **Emoji** - (optional Emoji)
	Default: from annotation type


- **content** - The content or body of the annotation (*RichText*)​​​​​​​  
__***For Machinery***
- **isEmbellishment** - Indicates whether this annotation is an embellishment added during post-parsing processing _(Boolean)_
  🔄 ***Default***: false
  ℹ️ ***Note***: This attribute is set to true for annotations that are automatically generated or added during the fleshing out, review, or rendering processes, such as suggestions, issues, or diagnostic messages. It helps distinguish embellishment annotations from the annotations defined in the original LDM source.
  




## The Model and its Subjects


_ **LiterateModel** - A representation of a domain's entities, attributes, and relationships, 
along with explanatory text and examples  
***Abbreviation***: LDM
Plural: LiterateModels 
Subtype of: Component  


- name (UpperCamel )
- allSubjects - list of all classes in the model, as ordered in the 
                definition of the model. (List of Classes)
    Derivation: gathering s.allSubjects over s in subjectAreas
    
    ***Constraint***: Subject names must be unique across the model.
- allClasses - list of all classes in the model, as ordered in the definition of the model. (List of Classes)
    Derivation: gathering s.allClasses over s in allSubjects.  
***Constraint***: Class names must be unique across the model.  

__ 	***Modeling Configuration***
- **annotationTypes** - (List of AnnotationTypes)
- **Preferred Coding Language** - the recommended lanquage  for expressing derivation, defaults, and constraints (Coding Language). 
   Default: Python
- **alternate Coding Languages** -  (optional List of Coding Languages).  
- **Preferred Template Language** - the recommended lanquage  for expressing derivation, defaults, and constraints (Template Language). 
   Default: Handlebars
- **alternate Template Languages** -  (optional List of Template Languages). 
- **aiFunctions** - A list of functions that require sophisticated AI-powered implementation *(List of String)*
  Derivation: ['aiEnglishPlural()']
  
	
_ **Subject**  - A specific topic or theme within the model  
Plural: Subjects  
Subtype of: Component  
based on: LiterateModel

Subjects are the chapters an sections of the model. 
A subject need not contain any Classes if it’s just expository.  

- name (UpperCamel )
- **parentSubject** - The parent subject, if any, under which this subject is nested _(optional Subject)_  

- **Classes** - The major classes related to this subject, in the order in which they should be presented _(ListOf Classes)_  
  ***Issue***: define chapter, section, subsection as levels?  
	***DSL***: Generally, it is best to present the classes within a Subject in top down order...
    * Each Class should be followed first by the classes that are dependent on it, and then
    * By its subtype classes.

    
- **childSubjects** - Any child subjects nested under this subject, in the order in which they should be presented _(ListOf Subjects)_  
	inverse of: Subject.parentSubject. 

    ***DSL***:  the Classes within a Subject are always displayed before the childSubjects.  

	
_ **SubjectArea**  - A main topic or area of focus within the model, containing related subjects and classes  
Plural: SubjectAreas  
Subtype of: Subject  
Where: parentSubject is absent
based on: Literate Model


### Classes


_ **Class** - A key entity or object type in the model, often corresponding to a real-world concept 

Plural: Classes  
Subtype of: Component  
***Constraint***: Within each Class, attribute names must be unique.  
- **pluralForm** - the normal English plural form of the name of the Class (UpperCamel)  

    Might be Books for the Book class or other regular plurals. 
    But also might be People for Person. 
   
    Note: When inputting a model, you will rarely need to specify the plural form. The input program will just look it up. 
   
    The exception is when a common noun has two plural forms, like People and Persons. But this is unusual.  
	***Default***: the regular plural, formed by adding "s" or "es".  
- **basedOn** - the Class or Classes on which this class is dependent (SetOf Class).  


  	This is solely based on **Existence Dependency**. A true dependent entity cannot logically exist without the related parent entity. For instance, an Order Item cannot exist without an Order. If removing the parent entity logically implies removing the dependent entity, then it is a dependent entity.  
  	
  	Note: that basedOn and dependentOf are being used synonymousle in this metamodel.  
  	ToDo - fix that


- **supertypes** - The parent class or classes from which this class inherits attributes (ListOf Classes)

- **subtypings** - the criteria, or dimensions, by which the class can be divided into subtypes (list of Subtypings).
	
     Example: in a library model, the `Book` class could have subtypings based on genre (e.g., Fiction, Non-fiction), format (e.g., Hardcover, Paperback), or subject (e.g., Science, History).   
   
	
- **subtypes** - Any subtypes or specializations of this class based on it’s subtypings. (ListOf Classes)

    
    Example: For instance, using the `Book` example, the subtypes could include `FictionBook`, `Non-fictionBook`, `HardcoverBook`, `PaperbackBook`, `ScienceBook`, and `HistoryBook`.



- **attributes** - The attributes or properties of the class, in the order in which they should be presented _(ListOf Attributes)_  
- **attributeSections** - additional attributes or properties of the class, grouped for clarity and elaboration.  _(ListOf AttributeSections)_  
 
- **constraints** - Any constraints, rules, or validations specific to this class _(ListOf Constraints)_  
    Note: Constraints may be expressed on either the Class or the Attribute. Always?
    Add examples where clarity would favor one or the other.   Sometimes just a matter of taste. 
- **methods** - Any behaviors or operations associated with this class _(ListOf Methods)_  

__  ***Implied Attributes*** 
- **dependents** - the Classes which are basedOn this Class (optional SetOf Classes).  

     ***Inverse of***: Class.basedOn
- UniqueKeys - (optional Set of UniqueKeys).  

        ***Inverse of***:
        UniqueKey.basedOn
  

_ **Subtyping** - a way in which subtypes of a Class may be classified (Subtype of Component).  
    ***based on:*** Class
- **name** (LowerCamel). 
    Usually ByThis or ByThat
- **is exclusive** (Boolean).  
    Default: true
- **is exhaustive** (Boolean).  
    Default: true
- **classes** (List of Classes).  

	***DSL***:  Shown in the DSL as  
	> Subbtypes: byBrand - Brand1, Brand2,... (non exclusive, exhaustive)
	on the super class. And as
	> Subtype of: SuperClass byBrand
	on the subclass.  
	
	Note: every class can have an unnamed subtyping.
	Also,  each subtyping is by default Exclusive and  Exhaustive. So those stipulations may be omitted.

ValueType - A class that is presumed to be used a value, rather than a reference

Subtype of: Class
	
_ **Reference Type** - A class that is presumed to be used as a reference, rather than a value
Subtype of: Class

ValueType:  **CodeType**   - A data type or enumeration used in the model  

- isCaptive - the code type was implied by use in an attribute and is only used for that attribute (Boolean)

ValueType:  **Code Value** - A possible value for an enumerated data class  
based on: CodeType

- **code** - A short code or abbreviation for the value _(String)_
- **description** - an explanation of what the code means (*RichText*)
Note: Often, a CodeType will be assigned to just one attribute in the model.  In such cases, there's no need to declare a new Code Type and invent a name for it.  Instead:
   * List the code values as a bulletted list inside the description of the attribute in the form
	   ‘**code**: description’
   * A Code Type will be created with the name [class][attribute]Code and the code values listed. That CodeType will be marked as isCaptive. 


_ **Key** - a list of attributes of a class
Subtype of: Component 
basedOn: Class
- keyAttributes - the attributes of the base Class. (List of Attributes ).  

Constraint: each attribute must be a direct or inherited of the base class.  
Constraint: no repetitions allowed in keyAttributes   
> 👍 **Issue**: introduce PureLists?
    
    
Issue: need ascending descending to support index keys or ordering keys. 

_ **UniqueKey** - a list of attributes on which instances of the base class may be keyed.  
Subtype of: Key 

Note: order unimportant for Unique Keys. 

## Attributes

_ **Attribute Section** - a group of attributes for a class that merit a shared explanation.  
***SubtypeOf***: Component.  
***Based on***: Class
-	isOptional - whether the attributes in this section, taken together, are optional. (Boolean)

	 If the Attribute Section is required,then each Attribute within the sectional is optional ot required, depending on how it is marked.  
	&nbsp;
	But if the Arrribute Section is optional each attribute in the section is only required if any attribute in the section is ptresent.


_ **Attribute**  - A property or characteristic of a class  
Plural: Attributes  
Subtype of: Component  
*Based on*: AttributeSection
- **name** - (Lower Camel).   
- **dataType** - The kind of object to which the attribute refers.  _(DataType)_  
  H
     In the simplest cases, the data type will be a class. And the specifier is the just the name of that class.   
  
     But,
    * List of Editions
    * Set of Edition
    * ... and more complicated cases.  
    ***See***: the section below on Data Type Specifiers.  
    
__ **Cardinalities**.   
- **isOptional** - Indicates whether the attribute must have a value for every instance of the class _(Boolean)_
  
  	***Default:*** False

- **cardinality** - The cardinality of the relationship represented by the attribute _(Cardinality)_
  
  	***Default:***  For a singular attribute, the default cardinality is N:1. If the attribute is 1:1, it must be stated explicitly.
  For a collective attribute, the default is 1:N. If the attribute is N:M, it must be stated explicitly.



	***DSL***: the cardinality of an attribute, if stated explicitly, should be placed just before the class name in the parenthetical data type specification after the one-liner.
```
	For example:
	- author (1:1 Author)
	- books (optional N:M Set of Books)
```
	***Note***: how this works with optionality

__  ***Inverse Attributes***
- **isInvertible** - (Boolean)
	***Derivation***: true if the data type is a class or a simple collection of members of a class.
- **inverseClass** - the class which contains, or would contain the inverse attribute (optional Class)
	***Derivation***: from the data type. Null unless arrribute is invertible.
- **inverseAttribute** - (optional Attribute)
- **inverseIsOptional** - (optional Attribute)

__ ***Formulas*** 

- **default** - The rule or formula for calculating the value, if no value is supplied 
    Now running to a second line with the parenthentical on yet a third line 
    (optional Derivation)
    Note: even when an Attribute has a default derivation, there’s no guarantee that every instance will have an assigned value. Example needed. 
    And let's see if the note can span extra lines, too

    Yes, it handled extra lines.  Let's see about additional paras for an annotation

    Last paragraph here

    
- **derivation** - For derived attributes, the rule or formula for calculating the value _(optional Derivation)_  
    ***Issue***: on insert vs on access?
- **constraints** - Any validation rules specific to this attribute _(ListOf Constraints)_         
    Note: from Class.constraints 
    
__ Override Tracking
- Overrides - the higher level attribute which this one overrides - for type or ... (Attribute)



ValueType:   **Derivation**  - A rule or formula for deriving the value of an attribute  
Plural: Derivations  
- **statement** - An English language statement of the derivation rule _(RichText)_  
- **expression** - The formal expression of the derivation in a programming language _(CodeExpression)_


  

ValueType:    **Constraint**  - A rule, condition, or validation that must be satisfied by the model  
Plural: Constraints  
Subtype of: Component  
- **statement** - An English language statement of the constraint _(RichText)_  
- **expression** - The formal expression of the constraint in a programming language, for example: OCL or Python. _(CodeExpression)_  
- **severity** -  (Code)
```codes
Warning, nothing fatal; just a caution
Error, serious. Fix now
```

ValueType:   **Class Constraint**  
**Subtype of**: Constraint  
***Based on***: Class. 

ValueType:   **Attribute Constraint** 
***Subtype of***: Constraint 
***Based on***: Attribute

## Methods 
_ **Method**  - A behavior or operation associated with a class  
Plural: Methods  
Subtype of: Component  
- **parameters** - The input parameters of the method _(ListOf Parameters)_  
- **returnType** - The data type of the value returned by the method _(DataType )_  

_ **Parameter**  - An input to a method  
Plural: Parameters  
Subtype of: Component  
- **type** - The data type of the parameter (DataType)
- **cardinality** - The cardinality of the parameter. e.g., optional, required. (Cardinality)

## Trivial Data Types
ValueType:  **Message** - (Template)
ValueType:   **CodeExpression**
- **Language** - the programming language (Code)
``` code
OCL, Object Constraint Language
Java, Java 
Python, Python
```
- **Expression** (String)

ValueType: **Data Type**

ValueType:   **Simple Data Type** 
***SubtpeOf***: DataType
- **coreClass** - (Class)


ValueType:   **Complex Data Type**  
- **aggregation** (Aggregating Operator)
- **aggregatedTypes** (List of DataTypes)

ValueType:   **Aggregating Operator**

- **Name**- (Code)
``` code
SetOf
ListOf
Mapping
```
- **arity** - (Integer)
- **spelling** - (Template)


## Trivial  Low level Data Types

insert Camel Case.md

ValueType: Emoji
ValueType: String

ValueType: **CamelName**  

A short string without punctuation or spaces, suitable for names, labels, or identifiers and presented in camel case.  
***Subtype of***: String
- value: the string (String)
🚫 ***Constraint***: Must follow the camel case naming convention and not be empty.
     Example:  "firstName", "orderDate", "customerID"  

> 📝 ***ModelingNote***: Putting the non-empty constraint on the CamelName value type is effective because it automatically applies to all attributes that use CamelName as their type. This ensures consistency and avoids the need to define the constraint separately for each attribute.

  
*ModelingNote:* *CamelName* is presented here, just after its first usage by another class (Component), to provide context and understanding before it is used further in the model.

ValueType:  **UpperCamel**- a CamelName that begins with a capital letter  
**Subtype of**: CamelName
**Where**: content begins with an upper case letter. 
Example:_ "Customer", "ProductCategory", "PaymentMethod"  


ValueType:   **LowerCamel** - a CamelName that begins with a lower case letter  
**Subtype of**: CamelName
**Where**: content begins with a lower case letter. 

 Example:  "firstName", "orderTotal", "shippingAddress"  

ValueType:   **Qualified Camel** - an expression consisting of Camel Names separated by periods 
***Subtype of***: String
***Constraint***: content consists of CamelNames, separated by periods.  Each of the camel names must be Upper Camel except, possibly, the first. 

ValueType: **RichText** - A string with markup for block level formatting.  
  ***SubtypeOf***: String  
  
  - **value** - the string content (string)  
  - **format** - the rich text coding language used (Code)  
```code
HTML
MarkDown
```
ValueType:  **OneLiner**   - String with markup for line level formatting.  
  ***SubtypeOf***: RichText 
  
  - **value** - the string content (string)  
      ***Constraint***: must not containa line break or new line character
      Message: A line can't span two lines
  
ValueType:  **PrimitiveType**  - A basic, built-in data type  

ValueType: **String**  
SubtypeOf: PrimitiveType

ValueType: **Integer**  
SubtypeOf: PrimitiveType

ValueType: **Decimal**  
SubtypeOf: PrimitiveType

ValueType: **Boolean**  
SubtypeOf: PrimitiveType

ValueType: **Date**  
SubtypeOf: PrimitiveType

ValueType: **Time**  
SubtypeOf: PrimitiveType

ValueType: **DateTime**  
SubtypeOf: PrimitiveType

CodeType: CodingLanguage
CodeType: Cardinality

ValueType: Template Language
ValueType: Template
ValueType: Code


### Annotation Types Used

These are the recognized Annotation Types for the LDM model.

 
And this is how you register the AnnotationTyped for a model. By including this sort of array in the DSL document for the model. 

```puml
@startjson

[
  {
    "label": "Error",
    "emoji": "❌",
    "emojiName": "cross_mark",
    "emojiUnicode": "U+274C",
    "purpose": "Indicates a critical error or failure in the model."
  },
  {
    "label": "Warning",
    "emoji": "⚠️",
    "emojiName": "warning",
    "emojiUnicode": "U+26A0",
    "purpose": "Indicates a potential issue or warning in the model."
  },
  {
    "label": "Note",
    "emoji": "📘",
    "emojiName": "blue_book",
    "emojiUnicode": "U+1F4D8",
    "purpose": "Provides additional context, explanations, or clarifications for the annotated element."
  },
  {
    "label": "Issue",
    "emoji": "⚠️",
    "emojiName": "warning",
    "emojiUnicode": "U+26A0",
    "purpose": "Highlights a potential issue or error that needs to be addressed or resolved."
  },
  {
    "label": "Question",
    "emoji": "❓",
    "emojiName": "question",
    "emojiUnicode": "U+2753",
    "purpose": "Raises a question or seeks further clarification about the annotated element."
  },
  {
    "label": "Suggestion",
    "emoji": "💡",
    "emojiName": "bulb",
    "emojiUnicode": "U+1F4A1",
    "purpose": "Provides a suggestion or recommendation for improving the model or the annotated element."
  },
  {
    "label": "Info",
    "emoji": "ℹ️",
    "emojiName": "information_source",
    "emojiUnicode": "U+2139",
    "purpose": "Offers relevant information, facts, or details about the annotated element."
  },
  {
    "label": "Todo",
    "emoji": "📌",
    "emojiName": "pushpin",
    "emojiUnicode": "U+1F4CC",
    "purpose": "Indicates a pending task, action item, or future work related to the annotated element."
  },
  {
    "label": "Reference",
    "emoji": "🌐",
    "emojiName": "globe_with_meridians",
    "emojiUnicode": "U+1F310",
    "purpose": "Provides a reference or link to an external resource or documentation."
  },
  {
    "label": "See",
    "emoji": "🔍",
    "emojiName": "mag",
    "emojiUnicode": "U+1F50D",
    "purpose": "Indicates a cross-reference to another relevant element within the model."
  }
]
@endjson

```


### Annotation types as CSV

``` csv
label,emoji,emojiName,emojiUnicode,purpose
Error,❌,cross_mark,U+274C,Indicates a critical error or failure in the model.
Warning,⚠️,warning,U+26A0,Indicates a potential issue or warning in the model.
Note,📘,blue_book,U+1F4D8,"Provides additional context, explanations, or clarifications for the annotated element."
Issue,⚠️,warning,U+26A0,Highlights a potential issue or error that needs to be addressed or resolved.
Question,❓,question,U+2753,Raises a question or seeks further clarification about the annotated element.
Suggestion,💡,bulb,U+1F4A1,Provides a suggestion or recommendation for improving the model or the annotated element.
Info,ℹ️,information_source,U+2139,"Offers relevant information, facts, or details about the annotated element."
Todo,📌,pushpin,U+1F4CC,"Indicates a pending task, action item, or future work related to the annotated element."
Reference,🌐,globe_with_meridians,U+1F310,Provides a reference or link to an external resource or documentation.
See,🔍,mag,U+1F50D,Indicates a cross-reference to another relevant element within the model.

```
## Appendices - various sidebars to include
Insert More Sidebars.md
Insert Overrides.md
insert LDM Intro.md
Insert OCL.md
Insert Camel Case.md





== content to add
- minor component
- embellishment
- words and phrases


``` mermaid
erDiagram
    Component ||--|LiterateModel : inherits
    Component ||--|Subject : inherits
    Subject ||--|SubjectArea : inherits
    Component ||--|Class : inherits
    Class ||--|ReferenceType : inherits
    Component ||--|Key : inherits
    Key ||--|UniqueKey : inherits
    Component ||--|AttributeSection : inherits
    Component ||--|Attribute : inherits
    Component ||--|Constraint : inherits
    Constraint ||--|ClassConstraint : inherits
    Constraint ||--|AttributeConstraint : inherits
    Component ||--|Method : inherits
    Component ||--|ParameterAnInputToAMethod : inherits
    AnnotationType }|--|} LiterateModel : based_on
    Annotation }|--|} Component : based_on
    Annotation ||--|| AnnotationType : annotationType
    Subject }|--|} LiterateModel : based_on
    Subject ||--|| Subject : parentSubject
    Class ||--|| Class : basedOn
    Subtyping }|--|} Class : based_on
    CodeValue }|--|} CodeType : based_on
    Key }|--|} Class : based_on
    AttributeSection }|--|} Class : based_on
    Attribute }|--|} AttributeSection : based_on
    Attribute ||--|| DataType : dataType
    ClassConstraint }|--|} Class : based_on
    AttributeConstraint }|--|} Attribute : based_on
    Method ||--|| DataType : returnType
    ParameterAnInputToAMethod ||--|| DataType : type
    ```