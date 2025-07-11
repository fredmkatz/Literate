``` mermaid
erDiagram
    Class_ ||--|| Component : subtype_of
    Class_ |o--o| Class_ : basedOn
    Subtyping }o--|| Class_ : based_on
    ReferenceType ||--|| Class_ : subtype_of
    Key ||--|| Component : subtype_of
    Key }o--|| Class_ : based_on
    AttributeSection ||--|| Component : subtype_of
    AttributeSection }o--|| Class_ : based_on
    Attribute ||--|| Component : subtype_of
    Attribute }o--|| AttributeSection : based_on
    Attribute |o--o| DataType : dataType
    ClassConstraint }o--|| Class_ : based_on
    AttributeConstraint }o--|| Attribute : based_on
```
