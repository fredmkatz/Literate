
# Introduction

These are instructions - directed to an AI -  to help in developing a Literate Data Models (LDMs).

The LDM notation is designed to support clear, concise, and self-documenting data models. This involves defining data types, attributes, classes, and their relationships within the model, ensuring that each component is comprehensively described and adheres to the schema.

The AI support will be orchestrated by a Python script that:
1. Supplies the AI with the working documents, including:
	- A JSON schema for LDMs
	- A target model, provided as a JSON/YAML instance of that schema
	- These instructions, describing the process and the expectations  for how  the AI is expected to help
2. Sends a series of specific requests. ("Improve the definitions of classes in this section of the model", "Supply the python versions of all constraints and derivations", or just "Review this Class")  Each request will refer to the model supplied in step 1.  The AI should respond by:
	- Making changes to the target model initially provided
	- Replying with a list of the changes made (probably a diff of the original to the updated model
3. The script will display the changes to me, save the response, and update the model "on my side".  Or, request a fresh copy of target model in JSON/YAML form
	

# Review instructions

A "full review" includes looking for several kinds of improvements.  (Keep in mind that the model you receive should already have been checked for "formal problems", like duplicate class names or references to undefined classes or attributes.  If such problems have not been fixed, there will already be Diagnostics in the model itself.)

Here are *some* of the things to check for and to correct.  More later.
## What to check for

### One Liners
One liners for Components should always take the form of a noun phrase.  The one liner itself may include an extra sentence, but usually any addition info should be placed in the elaboration.
### Elaborations
### Derivations, Defaults and Constraints
Each Derivation, Default, and Constraint should have a English language description (this is the one liner) and a Python code expression.  If either is missing, supply it, based on the other - or based on the name and description of the attribute.


### Inverse Attributes
As part of the processing (before the json file you see is created), inverse attributes are created when appropriate, which is
- when the attribute is found in a reference type and the value of the attribute is a reference type (or list, set, of such)
- and the structure of the data type is "simple enough": either a simple class reference or a list, set, or mapping to a class.  (So, if the type is *List of Set of X*, no inverse will be created.)
But the names and one liners for these implied attributes are never chosen carefully.  You can help by suggesting improvements.

## Reporting suggestions and improvements
Any suggestions should be attached to the smallest component to which they apply.  That is, an Attribute instead of a Class, and so forth.

For now, just an an Annotation. like: ***Suggestion***: change the one liner to ....
Later, we'll work out a way to actually preview the changes as changes.
Mark all suggestions as *is_embellishment*, so they can be styled to stand out in the html


















## Post Parsing
### Derived and default values -- and definitions
Just after parsing, calculate and store the values for attributes with derivations and defaults. 
Some of these are needed to render the model back into the DSL. More on that later. 

But, before you can do that, you might as well clean up the *Defaults* and *Derivations*. 


**Providing OCL and English expressions:** - **aiInstructions**

## Insert OCL Functions.md
Insert OCL Functions.md

## Fleshing Out LDMs
**Note**: there should be a Boolean attribute, isEmbellishment, on all Components and Annotations. 
By default it is false. 
To mark a component or annotation as an embellishment set this attribute to true. 


The fleshing out process enriches the parsed model with additional information and relationships that are not explicitly specified in the LDM source but can be inferred from the defined elements and their connections.

After parsing a model, you need to flesh out your internal representation. Otherwise, much of the processing won't work. This involves create new components of the model ( mostly attributes) and new annotations. 

When you create a new component, set its *isEmbellishment* to true. Similarly for annotations you create. (The embellishment attribute is on both Component and Annotation). This serves two purposes. First it allows the additions you make to be highlighted in the DSL you will be asked to produce. Second, since I will be uploading that output in the next chat, the highlighting will indicate what you’ve already added. 

***And the next thing you should do is get rid of all the old embellishments.*** 

Now that you have an unadorned model, you can add new embellishments. 

### Implied attributes - specs 
The next few sections explain when to add implied attributes to the model.  

First note: 

1. If any implied attributes are created for a class, they should be placed in an ***Implied Attributes*** attribute section for the class to which they belong. This section should be the last attribute section in the class.  And it should be marked as an embellishment.
2. Only the attributes described below should be created and added into the Implied Attribute section.  (I have noticed a temptation to include as implied attributes, some things that you might think are *implied* in a wider sense. But they are not for here.)

### Implied Attributes for Dependencies 

If the class, *TheDependent* is based on another class, *The Base* (specified using the `BasedOn` or `DependentOf` annotation), 
-	Add an implied attribute in TheDependent class that refers to an instance of The it belongs to. The attribute should be named `base<TheBase>` and have TheBase as its data type.
-	Add an implied attribute in TheBase class, that refers to the set of dependent instances. The attribute should be named the `<TheDependent-s>basedOn` using the plural form of the TheDependent and have a data type of `Set of <TheDependent-s>`.


### Implied Attributes for Inverses - specs
If the data type of an attribute in Source class is:
 - a Reference Type, like Person, or
 - ListOf or SetOf (ReferenceType)
Then an inverse attribute should be defined in that ReferenceType.

(So, if an the data type is
- a primitive,
- A value type, or 
- A more complex type, like SetOf(ListOf(People))
Then no inverse attribute should be implied.)

When creating an inverse attribute
- Both the original attribute and the implied inverse should have `inverse=theOther`.
- The original should have `impliedInverse = new inverse`.
- The created inverse should have `impliedInverseOf` set to the original atttibute.

Be careful. Before creating an inverse for an attribute, check to make sure it doesn’t already have one. 
- The model inputted may have specified inverses 
- Or, you may have just created B as an inverse for A. So B will be marked as having the inverse A. If you don’t notice that you might create a new inverse C for B. I have seen this happen. Don’t let it happen to you. 
     
### Annotations for Overrides - specs 

Later.





















