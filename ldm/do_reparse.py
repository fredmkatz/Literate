from class_fluent_html import FluentSoupBuilder, FluentTag
import utils_pom.util_all_fmk as fmk
from do_md2html import md_to_html

def markup_md_html(document_h):
    mark_by_tag(document_h, "h1", "ModelHeader")
    mark_by_tag(document_h, "h2", "Subject1_Header")
    mark_by_tag(document_h, "h3", "Subject2_Header")
    mark_by_tag(document_h, "h4", "Subject3_Header")
    mark_by_tag(document_h, "h4", "Subject3_HeaderB")
    mark_by_tag(document_h, "h5", "Subject4_Header")
    mark_by_tag(document_h, "h6", "Subject4_Header")
    
    mark_paragraphs(document_h)

def mark_paragraphs(element_h: FluentTag):
    for para in element_h.find_all("p"):
        paratext = para.text.strip()
        print("paratext is:", paratext)
        if paratext.startswith("_ "):
            .para(add_class("ClassDefinition")
            new_para = refine_class_para(para)
            print("Refined para is: ", new_para)
            para.insert_after(new_para)


def refine_class_para(para: FluentTag)->FluentTag:
    lines = para.text.split("\n")
    new_para = div(class_ = "RefinedClass")
    for line in lines:
        new_line = refine_line(line)
        new_para.append(new_line)
    return new_para

from typing import Union
def refine_line(line: str) -> Union[FluentTag, str]:
    return line
            
def mark_by_tag(element_h: FluentTag, tagname, class_mark):
    for e in element_h.find_all(tagname):
        e.add_class(class_mark)
        print(f"Marked {tagname} as {class_mark}")
        print(e)

    
def do_reparse(document_h) -> FluentTag:
    pass

if __name__ == "__main__":
    md_docpath = "ldm/ldm_models/LiterateTester/LiterateTester.md"
    mdh_docpath = md_docpath + ".as.html"
    
    md_text = fmk.read_text(md_docpath)
    md_html = md_to_html(md_text)
    # print(md_html)
    builder = FluentSoupBuilder()
    doc_h = builder.from_html(md_html)
    markup_md_html(doc_h)
    # print(doc_h)
    fmk.write_text(mdh_docpath, str(doc_h))
