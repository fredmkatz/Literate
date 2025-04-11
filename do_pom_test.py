from pom_grammar import PresentableGrammar
from utils_pom.util_fmk_pom import read_text
from utils_pom.util_flogging import flogger
from util_lark import pretty_print_parse_tree
from util_text_markup import markup_text_lines

def test_pom():
    flogger.info("Starting to test POM")
    
    lark_config = {  "case_sensitive": True,
                "ambiguity": "resolve",
                "debug": False}

    g = PresentableGrammar("Lit_01", format_name = "dull", config = lark_config)
    flogger.info("Grammar created")
    print(g)

    path = "models/Lit_01/SamplerClass.md"
    flogger.infof(f"Trying file {path}")
    try_file(g, path)
    flogger.info("Done testing POM")

def try_file(g, path):
    text = read_text(path)
    print("Text is: ", text)
    
    lines = text.split("\n")
    
    print(f"\nLines are: ({len(lines)})")
    for line in lines:
        print("\n", line)
    marked_lines = markup_text_lines(lines)
    
    print(f"\nMarkedLines are: ({len(marked_lines)})")
    trimmed_lines = []
    for line in marked_lines:
        trimmed = line.replace(" ; \n", "")
        trimmed_lines.append(trimmed)
        print("\t", line)
        
    print(f"\nTrimmed lines are: ({len(trimmed_lines)})")
    for line in trimmed_lines:
        print("\t", line)
        
        
    marked_text = "\n".join(trimmed_lines) + "ZZZ"
    marked_text = marked_text.replace("<<<ZZZ", "")
    print("\nMarked text is: \n", marked_text)

    result = g.parse(text)
    print("parse tree = ", result.parse_tree)
    print("parse tree = ", result.parse_tree.pretty())
    print("Original text  is: ", text)
    
    print("---- Prettier Parse Tree ----")
    print(pretty_print_parse_tree(result.parse_tree, max_text_length=30, text_column_width=35))
    print("-----------------------------")
    
    
test_pom()
