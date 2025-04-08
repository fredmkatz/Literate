from pom_grammar import PresentableGrammar
from utils_pom.util_fmk_pom import read_text
from utils_pom.util_flogging import flogger

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
    result = g.parse(text)
    print("parse tree = ", result.parse_tree)
    print("parse tree = ", result.parse_tree.pretty())
    print("Text is: ", text)

    
test_pom()
