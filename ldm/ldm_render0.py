# In a file like render_markdown.py
from ldm.Literate_01 import LDM, SubjectE, Class, Attribute, Component, Paragraph

def render_markdown_component(self: Component):
    result = ""
    if self.elaboration:
        result =  "\n\t".join([x.render_markdown() for x in self.elaboration])
    return result    

def render_markdown_paragraph(self: Paragraph): 
    return self.content

def render_markdown_ldm(self: LDM):
    # Render the LDM
    result = f"# {self.name}\n\n"

    # result += super().render_markdown()
    result += render_markdown_component(self)

    # Recursively render each subject
    for subject in self.subjects:
        result += subject.render_markdown()
    return result

def render_markdown_subject(self: SubjectE):
    # Render a subject
    result = f"{self.prefix} {self.name}\n\n"
    # result += super().render_markdown_component()
    result += render_markdown_component(self)

    # Render classes in this subject
    for cls in self.classes:
        result += cls.render_markdown()
    return result

def render_markdown_class(self: Class):
    # Render a class
    result = f"Class: {self.name}\n\n"
    # result += super().render_markdown()
    result += render_markdown_component(self)

    # Render attributes
    for attr in self.attributes:
        result += attr.render_markdown()
    return result

def render_markdown_attribute(self: Attribute):
    # Render an attribute
    result = f" Attribute: {self.name}\n\n"
    # result += super().render_markdown()
    result += render_markdown_component(self)

    # Add any specific details about the attribute here
    return result
# Apply the methods

LDM.render_markdown = render_markdown_ldm
SubjectE.render_markdown = render_markdown_subject
Class.render_markdown = render_markdown_class
Attribute.render_markdown = render_markdown_attribute
Component.render_markdown = render_markdown_component
Paragraph.render_markdown = render_markdown_paragraph
# ... and so on

def render_model(ldm: LDM) -> str:
    """Render the LDM as a markdown string."""
    return ldm.render_markdown()

if __name__ == "__main__":
    # Example usage
    ldm = LDM(name="Example LDM")
    subject = SubjectB(name="Example Subject")
    cls = Class(name="Example Class")
    attr = Attribute(name="Example Attribute")

    ldm.subjects.append(subject)
    subject.classes.append(cls)
    cls.attributes.append(attr)

    print(ldm.render_markdown())