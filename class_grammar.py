from lark import ParseTree
from lark import Lark, ParseError


class ParseResult:
    parse_tree: ParseTree
    pretty_tree: str
    
    errors: List[ParseError]
    
class Grammar():
    # rules
    # visitor
    # renderer / templates
    pass

def save_rules():
    # stores syntax rules in a text file (lark), rules_file
    pass

def save_templates():
    pass

def save_visitor():
    # saves any generated visitors
    pass

def parse(self, text: str) -> ParseResult:
    pass

def createObject(self, parseResult: ParseResult) -> Any:
    pass

def render(self, the_object) -> str:
    # renders the object, using the templates  or renderer associated with the grammar
    pass
    


def present_object(self, rule, text_content, marked_invalid = False) -> str:
    
    brief_text = text_content[:50].replace("\n", " ")   
    presentation = f"### Round trip for **{rule}** -- _[{brief_text} ..._]\n"
    presentation += self.presented_block("Input", f"{rule} -> : \n" + text_content)

    
    parse_result = self.parse(text_content)
    status = "Parsed well"
    presentation += self.presented_block(f"ParseTree -  ", parse_result.pretty_tree + "\n" + status)
    
    if parse_result.pretty_errors != "No errors":
        presentation += self.presented_block("Parsing errors", parse_result.pretty_errors)
        
    the_object = self.create_object(parse_tree)
    object_dict = the_object

    presentation += self.presented_block("Object", as_json(the_object))
    
    renderer = self.get_renderer()

    rendered = self.render_object(object_dict)

    presentation += self.presented_block("Rendered", rendered)



    return presentation
def presented_block(self, caption: str, text: str) -> str:
    return f"~~~\n{caption} ...\n{text}\n~~~\n"




class Document:
    def __init__(self, grammar: Grammar, name: str):
        """
        Initialize a Document instance.

        Args:
            grammar: The Grammar for this document
            name: The name of the document.
        """
        self.name = name
        self.grammar = grammar

    def path_for(self, ppass: str, subdir: str, extension: str = "") -> Path:
        """Get a path for a file related to this grammar."""
        return self.grammar.path_for(ppass, subdir, self.name, extension)
