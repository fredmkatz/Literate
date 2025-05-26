from pathlib import Path


def gpath_for(grammar_name, file_suffix):
    return path_for(
        "", grammar_name, "defns", f"{grammar_name}{file_suffix}"
    )

# Add this at the start of Markdown_objectmodel.py, after the imports
def path_for(
    ppass: str, grammar: str, subdir: str, document: str = "", extension: str = ""
):
    path = "HUH"
    grammars_root = Path("grammars")
    grammar_root = grammars_root / grammar
    subdir_path = grammar_root / f"{grammar}_{subdir}"
    if document == "":
        path = subdir_path

    elif subdir == "defns":
        # pass does not matter for  definitions or inputs
        path = subdir_path / f"{document}{extension}"

    elif subdir == "outputs":
        docdir_path = Path("documents") / f"{document}_by_{grammar}"
        docdir_path.mkdir(mode = 0o777, exist_ok=True)
        path = docdir_path / f"{grammar}_{document}_{ppass}{extension}"
    
    else:
        print("path-for called for inputs?")
        print(f"DEBUG: path_for {document}, {ppass}, {extension},{subdir} is {path}")

    return path

def output_docs_path(grammar: str, document: str) -> Path:
    docdir_path = Path("documents") / f"{document}_by_{grammar}"
    return docdir_path

def input_doc_path(docname: str, extension: str):
    docs_root = Path("documents")
    path = docs_root / f"{docname}{extension}"
    return path

def genned_path(grammar: str, stemSuffix: str):
    return f"grammars/{grammar}/generated_for_{grammar}/{grammar}{stemSuffix}"


