from pathlib import Path

from antlr4 import *

from antlr4.BufferedTokenStream import BufferedTokenStream
from antlr4.tree.Tree import TerminalNodeImpl
from antlr4.tree.Trees import Trees
from antlr4.error.ErrorListener import ErrorListener

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


class MyErrorListener(ErrorListener):

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        print(f"ERROR: line {line}:{column} {msg}", flush=True)

    def reportAmbiguity(
        self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs
    ):
        print(f"Ambiguity: {startIndex}-{stopIndex}", flush=True)

    def reportAttemptingFullContext(
        self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs
    ):
        print(f"Attempting full context: {startIndex}-{stopIndex}", flush=True)


def filter_tokens(tokens, LexerClass):
    """Filter and potentially split tokens before parsing."""
    relex_types = {"CLASS_HEADER", "ATT_SECTION_HEADER", "ATTRIBUTE_HEADER"}

    new_tokens = []
    for token in tokens:
        if token.type >= 0:
            token_name = LexerClass.symbolicNames[token.type]
            if token_name in relex_types:
                # Create a lexer with specific rules disabled
                class RelexLexer(LexerClass):
                    def __init__(self):
                        super().__init__(InputStream(""))
                        # Override the token type map to exclude the rules we're relexing
                        self.ruleNames = [
                            rule for rule in self.ruleNames if rule not in relex_types
                        ]
                        # Set their token types to invalid to prevent matching
                        for rule in relex_types:
                            if hasattr(self, rule):
                                setattr(self, rule, -1)

                text = token.text.rstrip("\r\n")
                mini_lexer = RelexLexer()
                mini_lexer.inputStream = InputStream(text)

                while True:
                    new_token = mini_lexer.nextToken()
                    if new_token.type == Token.EOF:
                        break
                    new_token.line = token.line
                    new_token.column = token.column
                    new_tokens.append(new_token)
            else:
                new_tokens.append(token)
    return new_tokens




def log_tokens(token_stream: BufferedTokenStream, LexerClass, output_path: str):
    """Log all tokens to a file for debugging."""
    with open(output_path, "w", encoding="utf-8") as token_file:
        for i, token in enumerate(token_stream.tokens):
            token_name = (
                LexerClass.symbolicNames[token.type]
                if token.type < len(LexerClass.symbolicNames)
                else f"Unnamed - {str(token.type)}"
            )
            print(
                f"Token {i}: type={token.type} ({token_name}), text='{token.text}'",
                file=token_file,
            )


def pretty_antlr(parser, node, depth=0):
    ruleNames = parser.ruleNames

    freeRules = ["freeLine", "freeRun", "freeText"] 
    result = ""
    depthStr = ". " * depth
    if isinstance(node, TerminalNodeImpl):
        result += f"{depthStr}{node.symbol}" + "\n"
    else:
        rule = Trees.getNodeText(node, ruleNames)
        if rule in freeRules:
            result += f"{depthStr}{rule} = {node.getText()}" + "\n"
            return result

        result += f"{depthStr}{Trees.getNodeText(node, ruleNames)}" + ":\n"
        if node.children:
            for child in node.children:
                sub = pretty_antlr(parser, child, depth + 1)
                if sub:
                    result += sub
    return result


def save_parse_tree(ppass, grammar, document, pretty_tree):
    output_path = path_for(ppass, grammar, "outputs", document, "_03.tree.txt")
    with open(output_path, "w", encoding="utf8") as f:
        f.write(pretty_tree)
