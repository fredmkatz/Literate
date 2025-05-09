import pathlib

import pymupdf # imports the pymupdf library
import pymupdf4llm


def convert_pdf_to_md(pdf_path, md_path):
    doc = pymupdf.open(pdf_path)

    for page in doc: # iterate the document pages
        text = page.get_text() # get plain text encoded as UTF-8
        print(text)

def convert_pdf2md(pdf_path, md_path):
    # convert the document to markdown
    md_text = pymupdf4llm.to_markdown(pdf_path)

    # Write the text to some file in UTF8-encoding
    pathlib.Path(md_path).write_bytes(md_text.encode())
    
if __name__ == "__main__":
    sample_path = "ldm/LDMMeta_results/LDMMeta.pdf"
    md_path =  "ldm/LDMMeta_results/LDMMeta.pdf.md"
    convert_pdf2md(sample_path, md_path)

