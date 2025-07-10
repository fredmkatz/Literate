``` mermaid
erDiagram
    AnnotationType }o--|| LiterateDataModel : based_on
    Annotation }o--|| Component : based_on
    Annotation |o--o| AnnotationType : annotationType
    LiterateDataModel ||--|| Component : subtype_of
    Subject ||--|| Component : subtype_of
    Subject }o--|| LiterateDataModel : based_on
    Subject |o--o| Subject : parentSubject
    SubjectArea ||--|| Subject : subtype_of
    Classy ||--|| Component : subtype_of
    Classy |o--o| Classy : basedOn
    Subtyping }o--|| Classy : based_on
    ReferenceType ||--|| Classy : subtype_of
    CodeValue }o--|| CodeType : based_on
    Key ||--|| Component : subtype_of
    Key }o--|| Classy : based_on
    UniqueKey ||--|| Key : subtype_of
    AttributeSection ||--|| Component : subtype_of
    AttributeSection }o--|| Classy : based_on
    Attribute ||--|| Component : subtype_of
    Attribute }o--|| AttributeSection : based_on
    Attribute |o--o| DataType : dataType
    Constraint ||--|| Component : subtype_of
    ClassConstraint ||--|| Constraint : subtype_of
    ClassConstraint }o--|| Classy : based_on
    AttributeConstraint ||--|| Constraint : subtype_of
    AttributeConstraint }o--|| Attribute : based_on
    Method ||--|| Component : subtype_of
    Method |o--o| DataType : returnType
    ParameterAnInputToAMethod ||--|| Component : subtype_of
    ParameterAnInputToAMethod |o--o| DataType : type
```
