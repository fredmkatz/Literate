# Direct method attachment
import ldm.Literate_01 as Literate_01
from utils_pom.util_flogging import trace_decorator

import textwrap
para_indent = "            "
para_width = 80
# utility functions

# @trace_decorator     
def render_markdown(obj) -> str:
    otype = getattr(obj, "_type", None)
    if otype is None:
        print(f"ERROR: No _type for {obj}")
        return str
    
    else:
        print(f"Nothing to render {otype} for {obj}")
        return
        

# @trace_decorator     
def render_each(obj_list):
    """Render each object in the list, if it has a render_markdown method."""
    result = ""

    for obj in obj_list:
        if hasattr(obj, "render_markdown"):
            result += render_markdown(obj)
        else:
            result += render_value(obj)
    return result
# @trace_decorator     
def render(obj, attribute_name):
    """Render the attribute with the specified  name, if it exists."""
    if hasattr(obj, attribute_name):
        value = getattr(obj, attribute_name)
        if value is not None:
            if isinstance(value, list):
                return ", ".join([render_value(x) for x in value])
            elif hasattr(value, "render_markdown"):
                return value.render_markdown()           
            else:
                return render_value(value)
    return ""

# @trace_decorator     
def render_value(value):
    """Render the value, if it has a render_markdown method."""
    vtype = getattr(value, "_type", None)
    if not vtype:
        return str(value)

    if isinstance(value, str):
        return value
    
    # print(f"RenderValue for {vtype}")
    if isinstance(value, list):
        return "\n".join([render_value(x) for x in value])
    elif "Subject" in vtype:
        return render_markdown_subject(value)
    elif isinstance(value, Literate_01.Class):
        return render_markdown_class(value)
    elif isinstance(value, Literate_01.Class):
        return render_markdown_class(value)
    elif isinstance(value, Literate_01.Attribute):
        return render_markdown_attribute(value)
    elif isinstance(value, Literate_01.Annotation):
        return render_markdown_annotation(value)
    
    elif isinstance(value, Literate_01.CodeBlock):
        return render_markdown_codeblock(value)
    elif isinstance(value, Literate_01.Paragraph):
        return render_markdown_paragraph(value)
    elif isinstance(value, Literate_01.AttributeSection):
        return render_markdown_attribute_section(value)
    elif isinstance(value, Literate_01.AttributeReference):
        return render_markdown_attribute_reference(value)
    elif isinstance(value, Literate_01.Formula):
        return render_markdown_formula(value)
    elif isinstance(value, Literate_01.LDM):
        return render_markdown_ldm(value)
    elif isinstance(value, Literate_01.ClassName):
        return str(value)
    elif isinstance(value, Literate_01.AttributeName):
        return str(value)
    else:
        print(f"WARNING: No render_markdown for type {type(value)}")
        return str(value)  

# @trace_decorator     
def render_markdown_annotation(self) -> str:
    """Render the annotations for the object."""
    result = ""
    
    label = render(self, "label")
    one_liner = render(self, "content")
    emoji = render(self, "emoji")
    text = f"\t{emoji} {label}: {one_liner}\n"
    result = textwrap.fill(text, width=para_width, initial_indent='', subsequent_indent=para_indent) + "\n"


    return result
# @trace_decorator
def render_markdown_elaboration(self) -> str:
    result = ""
    elaboration = getattr(self, "elaboration", None)
    if elaboration is None:
        return ""
    if not elaboration:
        return ""
    if not isinstance(elaboration, list):
        return ""
    for para in elaboration:
        result += render_markdown_paragraph(para) 
    return result

# Define the rendering methods

def render_markdown_ldm(self):
    result = render_markdown_component(self, prefix=self.prefix + " ")
    
    subjects = self.subjects
    print(len(subjects), " subjects coming in model")
    result += render_each(self.subjects)
    
    return result

def render_markdown_subject(self):
    
    result = render_markdown_component(self, prefix=self.prefix + " ")

    
    # Render classes    
    result += render_each(self.classes)
    # Render child subjects
    subjects = self.subjects

    print(len(subjects), " subjects coming in subject")

    result += render_each(self.subjects)

    
    return result



def render_header(self, prefix: str, parenthetical: str = None) -> str:
    """Render the header for the object."""
    headline = f"{prefix}{self.name}"
    one_liner = render(self, "one_liner")
    if one_liner:
        headline += f" - {one_liner}"
    parenthetical = render(self, "parenthetical")
    if parenthetical:
        headline += f" ({parenthetical})"
    result = textwrap.fill(headline, width=para_width, initial_indent='', subsequent_indent=para_indent)

    result += "\n\n"
    return result

from class_casing import UpperCamel, LowerCamel
def render_field(self, field_name: str, label: str = "") -> str:
    """Render the field with the specified name."""
    result = render(self, field_name)
    if label == "":
        label = str(str(LowerCamel(field_name)))
    if result:
        result = f"{para_indent}{label}: {result}\n"
    return result

def render_markdown_component(self, prefix: str = "", parenthetical: str = "" ) -> str:
    """Render the component with the specified prefix."""
    result = render_header(self, prefix, parenthetical)
    
    # Render elaboration and annotations if present
    
    # Render elaboration if present
    result += render_markdown_elaboration(self)
    result += render_each(self.annotations)
    
    return result    
    
def render_markdown_class(self):
    result = render_markdown_component(self, prefix="_ ", parenthetical=None)    
    

    # fields

    result += render_field(self, "plural")
    result += render_field(self, "subtype_of")
    result += render_field(self, "subtypes") 
    result += render_field(self, "based_on")
    result += render_field(self, "dependent_of")
    result += render_field(self, "dependents")
    result += render_field(self, "is_value_type")
    result += render_field(self, "where")
    result += render_each(self.constraints)
    

    # Render attributes
    result += render_each(self.attributes)
    result += render_each(self.attribute_sections)
    
    return result

def render_markdown_attribute_reference(self):
    result = ""
    result += render(self, "class_name")
    result += "_._"
    result += render(self, "attribute_name")
    return result
    
def render_markdown_attribute(self):
    result = render_markdown_component(self, prefix="    - ", parenthetical=self.parenthetical)
    
    result += render_field(self, "data_type")
    result += render_field(self, "data_type_clause")
    result += render_field(self, "overrides")
    result += render_field(self, "inverse")
    result += render_field(self, "inverse_of")
    # result += render_formula_field(self, "derivation")
    # result += render_formula_field(self, "default")
    # result += render_field(self, "default")
    # for constraint in self.constraints:
    #     result += render_markdown_formula(constraint)
        
    return result

def render_markdown_attribute_section(self) -> str:
    result = render_markdown_component(self, prefix="__ ", parenthetical=self.parenthetical)
    
    
    # Render attributes
    result += render_each(self.attributes)
        
    return result
from utils_pom.util_json_pom import as_json
def render_formula_field(self, field_name: str) -> str:
    result = ""
    formula  = getattr(self, field_name, None)
    if not formula:
        result += f"ERROR No formula for {field_name}\n"
        # print(result)
        return result
    result += f"Formula for {field_name}:\n"
    json = as_json(formula)
    result += f"{json}\n"
    result += render_field(formula, "as_entered", getattr(formula, "_type", "as_entered"))
    result += render_field(formula, "english")
    result += render_field(formula, "code")
    
    result += render_markdown_elaboration(formula)
    result += render_each(formula.annotations)

    return result 

def render_markdown_formula(self) -> str:
    """Render the formula for the object."""
    result = render_field(self, "as_entered",  getattr(self, "_type", "as_entered"))
    result += render_field(self, "english")
    result += render_field(self, "code")

    result += render_markdown_elaboration(self)
    result += render_each(self.annotations)
    
    return result

def render_markdown_paragraph(self):
    
    if not hasattr(self, "content"):
        return ""
    lines = textwrap.wrap(self.content, width=para_width)
    rawtext = "\n".join(lines)
    text = textwrap.indent(rawtext, prefix = para_indent)
    
    
    
    return f"{text}\n\n"
def render_markdown_codeblock(self):
    
    if not hasattr(self, "content"):
        return ""
    text = textwrap.indent(self.content, prefix = para_indent)
    
    
    
    return f"{text}\n\n"

