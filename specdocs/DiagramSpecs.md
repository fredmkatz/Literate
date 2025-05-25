# Diagrams

## Objects
- Class
- Value Type? Code Type?
- Subtyping
-- exclusive
-- exhaustive

- Subject
## Relationships
- A is a subtype of B
- ST is subtyping for A
- A is a subtype of ST
- A relates to B via attribute with cardinality
- A is base on B

## Examples
### Literate
Objects are:
- Class Component
--  with exclusive, exhaustive subtypes
- Class Subject
- Class Class
- Class Section ?
- Class Attribute

Relations are:
- Subject subtype of Component
- Class subtype of Component
- Section subtype of Component
- Attribute subtype of Component

- Class based on Subject
- Section based on Class
- Attribute based on Class or Section

#### Mermaid ER
``` mermaid
erDiagram
    CUSTOMER ||--o{ ORDER : places
    CUSTOMER {
        string name
        string custNumber
        string sector
    }
    ORDER ||--|{ LINE-ITEM : contains
    ORDER {
        int orderNumber
        string deliveryAddress
    }
    LINE-ITEM {
        string productCode
        int quantity
        float pricePerUnit
    }
```