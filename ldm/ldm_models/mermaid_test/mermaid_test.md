# This is my first Mermaid test

## Mermaid Class Diagram

```mermaid


classDiagram
    class Component
    class Literate
    class Subject
    class Class
    class Attrribute Section
    class Attribute

    Component  <|-- Literate
    Subject  <|-- Literate
    Class  <|-- Literate
    AttributeSection  <|-- Literate
    Attribute  <|-- Literate

classDef default fill:yellow,stroke:#000, color:black, stroke-width:4px
```


## Mermaid Flowchart

``` mermaid
%%{init: {
  "flowchart": {
    "curve": "stepAfter",
    "useMaxWidth": true
  }
}}%%

flowchart TB
    subgraph Component["Component - Base class"]
        direction TB
        
        Literate["Literate<br>Core implementation"]
        
        subgraph Subtypes["Component Subtypes"]
            direction LR
            Subject["Subject<br>Domain entity"]
            Class["Class<br>Schema definition"]
            AttributeSection["AttributeSection<br>Property group"]
            Attribute["Attribute<br>Individual property"]
        end
        
        Subject ==> Literate
        Class ==> Literate
        AttributeSection ==> Literate
        Attribute ==> Literate
    end
    
    %% Styling with border-radius only
    classDef container fill:#e3f2fd,stroke:#1565c0,stroke-width:3px,color:#0d47a1,border-radius:10px
    classDef subcontainer fill:#f5f5f5,stroke:#78909c,stroke-width:2px,color:#37474f,border-radius:8px
    classDef default fill:white,stroke:#90a4ae,stroke-width:1px,color:#455a64,border-radius:5px
    
    class Component container
    class Subtypes subcontainer
    
    %% Edge styling
    linkStyle default stroke:#546e7a,stroke-width:2px, border-radius: 20px
```
## PlantUML jsondata

``` puml
@startjson
<style>
  .h1 {
    BackGroundColor green
    FontColor white
    FontStyle italic
  }
  .h2 {
    BackGroundColor red
    FontColor white
    FontStyle bold
  }
</style>
#highlight "lastName"
#highlight "address" / "city" <<h1>>
#highlight "phoneNumbers" / "0" / "number" <<h2>>
{
  "firstName": "John",
  "lastName": "Smith",
  "isAlive": true,
  "age": 28,
  "address": {
    "streetAddress": "21 2nd Street",
    "city": "New York",
    "state": "NY",
    "postalCode": "10021-3100"
  },
  "phoneNumbers": [
    {
      "type": "home",
      "number": "212 555-1234"
    },
    {
      "type": "office",
      "number": "646 555-4567"
    }
  ],
  "children": [],
  "spouse": null
}
@endjson
```

## PlantUML UML
``` puml

@startuml

rectangle Component
rectangle Literate
rectangle Subject
rectangle Class
rectangle Attribute
rectangle a

Literate -u->  a
Subject -u-> a
Class -u-> a
Attribute -u-> a
a -u-> Component
skinparam linetype ortho
@enduml
```


```mermaid
block-beta
columns 3
a:3
block:group1:2
columns 2
h i j k
end
g
block:group2:3
%% columns auto (default)
l m n o p q r
end
```

## Mermaid ER Diagram
``` mermaid

erDiagram

    CAR {

        string registrationNumber

        string make

        string model

    }

    PERSON {

        string firstName

        string lastName

        int age

    }

    style CAR fill: red,stroke:navy,stroke-width:3px

    style PERSON color: white, fill: navy,stroke:yellow ,stroke-width:2px

```

## Mermaid ER Diagram

``` mermaid
erDiagram

    class Subject Component

    class Section Component

    class Attribute Component

    class Classe Component

    Subject ||--|{ Subject : contains

    Subject ||--|{ Classe : contains

  

    Classe ||--|{ Section : contains

    Classe ||--|{ Attribute : contains

    Section ||--|{ Attribute : contains

```
## Captioned figure
<figure>
  <img src="../FMKNYIDFrontIMG_1141.jpg" alt="Trulli" style="width:30%">
  <figcaption>Fig.1 - Trulli, Puglia, Italy.</figcaption>
</figure>
And the same figure with figure/caption markup

<figure title="A Drivers License">
	<img src="../FMKNYIDFrontIMG_1141.jpg" style="width:20%">
	<figcaption>My Non-Drivers License</figcaption>
</figure>

## List of Codes

```csv
eFormat, Description
E-Book, 'Kindle or Apple books - etc'
PDF, formatted for printing and direct delivery

```

## UML
``` puml

@startuml

nwdiag {

  network {

    Component;

    Literate;

    Subject;

    Attribute;

    AttributeSection;

    Class;

    Component -- Literate;

    Component -- Subject;

    Component -- Class;

    Component -- AttributeSection;

    Component -- Attribute;

  

    Subject [description = "Domain entity"];

    Literate [description = "Core implementation"];

    AttributeSection [description = "Property group"];

    Attribute [description = "Individual property"];

    Class [description = "Schema definition"];

  
  

  }

}

@enduml
```

## Russian UML
``` puml
@startuml
'hide empty description
'!pragma layout elk
skinparam rectangleBorderThickness 1
skinparam defaultTextAlignment center
skinparam lifelineStrategy solid
skinparam monochrome false
skinparam style strictuml
hide empty members
skinparam Linetype ortho

rectangle "Базовые модули" as base {

class "Базовые объекты" as baseobjects
class "Делопроизводство\n4.5" as takeoffice
class "Управление\nпроцессами" as workflow
class "Windows-клиент" as windowsclient

class "Управление\nдокументами" as documentmanagement
class "Конструктор\nсогласований" as approvaldesigner

class "Платформа" as platform
class "Служба\n фоновых операций" as worker

}

platform <-- baseobjects
platform <-- workflow
platform <-- takeoffice
platform <-- windowsclient
platform <-- documentmanagement
platform <-- approvaldesigner

windowsclient -up-> approvaldesigner
windowsclient -up-> documentmanagement
windowsclient -up-> baseobjects
windowsclient -up-> takeoffice
windowsclient -up-> workflow

worker <-- approvaldesigner
worker <-- baseobjects
@enduml

```
## Car diagram
``` puml
@startuml
class Car

Driver - Car : drives >
Car *- Wheel : have 4 >
Car -- Person : < owns
@enduml
```

## and a dummy section

