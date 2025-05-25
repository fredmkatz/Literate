# Direct method attachment
import ldm.Literate_01 as Literate_01
from utils_pom.util_flogging import trace_decorator

import textwrap

# Options - to be formalized for speccing
para_indent = " " * 0
para_width = 80

style_names = True
add_links = True

# utility functions

# @trace_decorator     
def render(obj) -> str:
    otype = getattr(obj, "_type", None)
    if otype is None:
        print(f"ERROR: No _type for {obj}")
        return str
    
    else:
        print(f"Nothing to render {otype} for {obj}")
        return
        

# @trace_decorator     
def render_each(obj_list):
    """Render each object in the list, if it has a render method."""
    result = ""

    for obj in obj_list:
        if hasattr(obj, "render"):
            result += render(obj)
        else:
            result += render_value(obj)
    return result
# @trace_decorator     
def render(obj, attribute_name):
    """Render the attribute with the specified  name, if it exists."""
    if hasattr(obj, attribute_name):
        value = getattr(obj, attribute_name)
        if not value:
            return ""
        if value is not None:
            if isinstance(value, list):
                return ", ".join([render_value(x) for x in value])
            elif hasattr(value, "render"):
                return value.render()           
            else:
                return render_value(value)
    return ""

# @trace_decorator     
def render_value(value):
    """Render the value, if it has a render method."""
    vtype = getattr(value, "_type", None)
    if not vtype:
        return str(value)

    if isinstance(value, str):
        return value
    
    # print(f"RenderValue for {vtype}")
    if isinstance(value, list):
        return "\n".join([render_value(x) for x in value])
    elif "Subject" in vtype:
        return render_subject(value)
    elif isinstance(value, Literate_01.Class):
        return render_class(value)
    elif isinstance(value, Literate_01.Attribute):
        return render_attribute(value)
    elif isinstance(value, Literate_01.Annotation):
        return render_annotation(value)
    elif isinstance(value, Literate_01.Diagnostic):
        return render_diagnostic(value)
    elif vtype == "Diagnostic":
        return render_diagnostic(value)
    
    elif isinstance(value, Literate_01.CodeBlock):
        return render_codeblock(value)
    elif isinstance(value, Literate_01.Paragraph):
        return render_paragraph(value)
    elif isinstance(value, Literate_01.AttributeSection):
        return render_attribute_section(value)
    elif isinstance(value, Literate_01.AttributeReference):
        return render_attribute_reference(value)
    elif isinstance(value, Literate_01.Formula):
        return render_formula(value)
    elif isinstance(value, Literate_01.LiterateModel):
        return render_ldm(value)
    elif isinstance(value, Literate_01.DataTypeClause):
        return render_data_type_clause(value)
    elif isinstance(value, Literate_01.ClassName):
        return render_class_name(value)
    elif isinstance(value, Literate_01.OneLiner):
        return str(value)
    elif isinstance(value, Literate_01.AttributeName):
        return str(value)
    else:
        print(f"WARNING: No render for type {type(value)}")
        return str(value)  

def render_class_name(name) -> str:
    display_name = str(name)
    if style_names:
        display_name = f"_{name}_"
    if add_links:
        display_name = f"[{display_name}]({name})"
    return display_name

def render_data_type_clause(value):
    return str(value)

def as_rest_of_block(content: str) -> str:
    display = textwrap.fill(content, width=para_width, initial_indent='', subsequent_indent=para_indent) + "\n"
    return display

def as_text_block(content: str) -> str:
    display = textwrap.fill(content, width=para_width, initial_indent=para_indent, subsequent_indent=para_indent) + "\n"
    return display

# @trace_decorator     
def render_annotation(self) -> str:
    """Render the annotations for the object."""
    
    label = render(self, "label")
    one_liner = render(self, "content")
    emoji = render(self, "emoji")
    text = f"{label}: {one_liner}\n"
    if emoji:
        text = emoji + " " + text
    return as_text_block(text)

# @trace_decorator
def render_elaboration(self) -> str:
    result = ""
    elaboration = getattr(self, "elaboration", None)
    if elaboration is None:
        return ""
    if not elaboration:
        return ""
    
    parablock = []
    for piece in elaboration:
        if isinstance(piece, Literate_01.Paragraph):
            parablock.append(piece)
            continue
        if isinstance(piece, Literate_01.CodeBlock):
            # first output any gathered Paragraph pieces
            result += cleaned_paras(parablock)
            parablock = []
            # print("adding code block...")
            # print(piece.content)
            result += piece.content + "\n\n"
            
            # then add the code block
    # finally, take care of gathered paras
    result += cleaned_paras(parablock)
    parablock = []

    return result

def cleaned_paras(paras: list[Literate_01.Paragraph])-> str:
    if not paras:
        return ""
    full_text = "\n\n".join( [str(p) for p in paras]) + "\n\n"
    
    from clean_markdown import clean_markdown
    
    clean_text = clean_markdown(full_text)
    return clean_text

    
# Define the rendering methods

def render_ldm(self):
    result = render_component(self, prefix=self.prefix + " ")
    
    subjects = self.subjects
    print(len(subjects), " subjects coming in model")
    result += render_each(self.subjects)
    
    return result

def render_subject(self):
    
    result = render_component(self, prefix=self.prefix + " ")

    
    # Render classes    
    result += render_each(self.classes)
    # Render child subjects
    subjects = self.subjects

    # print(len(subjects), " subjects coming in subject")

    result += render_each(self.subjects)

    
    return result

from Literate_01 import ClassName, AttributeName, AttributeSectionName, Label
def style_for_header(prefix, name) -> str:
    display_name = str(name)
    
    style_mark = ""
    if style_names or True:
        if isinstance(name, ClassName) or prefix == "_ " or  "Value" in prefix or "Code" in prefix:
            style_mark = "**"
        elif isinstance(name, AttributeSectionName) or prefix == "__ ":
            style_mark = "_"
        elif isinstance(name, AttributeName) or prefix == "- ":
            style_mark = "***"
    display_name = f"{style_mark}{name}{style_mark}"
    # print("Prefix is [", prefix, "] dislay is ", display_name)
    return display_name

def render_header(self, prefix: str, parenthetical: str = None) -> str:
    """Render the header for the object."""
    
    # print("Render header:", f"[{prefix}] {self.name} ({parenthetical}) ")
    displayed_name = style_for_header(prefix, str(self.name))

    headline = f"{prefix}{displayed_name}"
    one_liner = render(self, "one_liner")
    if one_liner:
        headline += f" - {one_liner}"
    if parenthetical:
        phrase = render_value(parenthetical)
        if parenthetical:
            headline += f" ({phrase})"
        

    result = textwrap.fill(headline, width=para_width, initial_indent='', subsequent_indent=para_indent)

    result += "\n\n"
    return result

from class_casing import UpperCamel, LowerCamel
def render_field(self, field_name: str, label: str = "") -> str:
    """Render the field with the specified name."""
    from do_build_ldm import handle_subtype_of

    result = ""
    if field_name == "subtype_of":
        value = getattr(self, field_name, None)
        if not value:
            return ""
        result = handle_subtype_of.render(value)
    else:
        result = render(self, field_name)
    # print(f"Field [{field_name}] render result is {result}")
    if not result:
        return ""
    if label == "":
        label = str(str(LowerCamel(field_name)))
    if label and style_names:
        label = f"_{label}_"
    if result:
        result = f"{para_indent}{label}: {result}\n"
    return result

def render_component(self, prefix: str = "", parenthetical: str = "" ) -> str:
    """Render the component with the specified prefix."""
    result = render_header(self, prefix, parenthetical)
    
    # Render elaboration and annotations if present
    
    # Render elaboration if present
    result += render_elaboration(self)
    result += render_each(self.annotations)
    if self.diagnostics: # so, block df diagnostics, surrounded by blank lines
        result += "\n"
        result += render_each(self.diagnostics)
        result += "\n"

    return result    

def render_diagnostic(d) -> str:
    return as_text_block(f"!! {d.severity}: {d.message}\n")
    
def render_class(self):
    the_prefix = "_ "
    if isinstance(self, Literate_01.CodeType):
        the_prefix = "Code Type: "
    elif isinstance(self, Literate_01.ValueType):
        the_prefix = "Value Type: "

    result = render_component(self, prefix= the_prefix, parenthetical=None)    
    

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

def render_attribute_reference(self):
    result = ""
    result += render(self, "class_name")
    result += "_._"
    result += render(self, "attribute_name")
    return result
    
def render_attribute(self):
    result = render_component(self, prefix="- ", parenthetical=self.data_type_clause)
    
    # result += render_field(self, "data_type")
    # result += render_field(self, "data_type_clause")
    result += render_field(self, "overrides")
    result += render_field(self, "inverse")
    result += render_field(self, "inverse_of")
    # result += render_formula_field(self, "derivation")
    # result += render_formula_field(self, "default")
    # result += render_field(self, "default")
    # for constraint in self.constraints:
    #     result += render_formula(constraint)
        
    return result

def render_attribute_section(self) -> str:
    result = render_component(self, prefix="__ ", parenthetical=self.is_optional)
    
    
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
    result += render_field(formula, "one_liner", getattr(formula, "_type", "one_liner"))
    result += render_field(formula, "english")
    result += render_field(formula, "code")
    
    result += render_elaboration(formula)
    result += render_each(formula.annotations)

    return result 

def render_formula(self) -> str:
    """Render the formula for the object."""
    result = render_field(self, "one_liner",  getattr(self, "_type", "one_liner"))
    result += render_field(self, "english")
    result += render_field(self, "code")

    result += render_elaboration(self)
    result += render_each(self.annotations)
    
    return result

def render_paragraph(self):
    
    if not hasattr(self, "content"):
        return ""
    lines = textwrap.wrap(self.content, width=para_width)
    rawtext = "\n".join(lines)
    text = textwrap.indent(rawtext, prefix = para_indent)
    
    
    
    return f"{text}\n\n"
def render_codeblock(self):
    
    if not hasattr(self, "content"):
        return ""
    text = textwrap.indent(self.content, prefix = para_indent)
    
    
    
    return f"{text}\n\n"

