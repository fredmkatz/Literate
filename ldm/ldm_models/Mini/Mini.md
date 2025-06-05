# Literate Data Model



## Preliminaries - the basic structure of the model


_ **Component** - An element or building block of the literate data model 
- **normalName** - the name of the component, not in camel case (*String*)

- **name** - The name of the component (CamelName)



- **qualifiedName** - (*QualifiedCamel*)
- **abbreviatedName** - a short form of the component's name, used for cross references and improved readability. (*CamelName*)

	***Default***: name
	***Example***: "LDM" is the short form of "Literate Data Model".

- **oneLiner** - A brief, one-line definition or description of the component, suitable for use in a descriptive table of contents. _(RichLine)_  

- **elaboration** - A more detailed explanation or discussion of the component _(RichText)_  

__  ***For Machinery*** - mechanical attributes
- **isEmbellishment** - Indicates whether this component is an embellishment added during post-parsing processing _(Boolean)_
  🔄 ***Default***: false
  ℹ️ ***Note***: This attribute is set to true for components that are automatically generated or added during the fleshing out, review, or rendering processes, such as implied attributes or suggested model elements. It helps distinguish embellishments from the core model elements defined in the original LDM source.
	

_ **AnnotationType** - a kind of note, or aside, used to call attention to additional information about some Component. 
***Based on*** : Literate Data Model
***Note***: Each LDM declares a set of Annotation Types, with defined labels, emojis, and clearly documented purposes. These are *recognized* or *registered* Annotation Types. 
But, if none of these fit, you can  introduce an Annotation with any label. It would have an *ad hoc* Annotation Type. 
- **emoji** - an emoji (Emoji)
- **emojiName** - an emoji (String)
- **emojiUnicode** - the Unicode for the emoji (Unicode)
- **label** - A short label to indicate the purpose of the annotation _(CamelName)_  
- **plural** - the plural form of the label (*UpperCamel*).  
    Default: based on label
 - **Purpose** - the intended reason for the annotation.


