from lark.visitors import TraceRule

def debug_parse_with_trace(grammar, text, start_rule='start'):
    """Parse with TraceRule to see which rules get applied"""
    from lark import Lark
    
    parser = Lark(grammar, parser='earley', start=start_rule)
    
    # Create a parser with a tracing mechanism
    tracer = TraceRule()
    parser.parse_tree = tracer.visit_topdown(parser.parse(text))
    
    # The tracer shows which rules were applied
    return parser 

# 2. Create a custom Parser Callback to see state transitions

from lark.parser.earley import Parser as EarleyParser

class DebugParser(EarleyParser):
    def predict(self, nonterm, rule, start, line, column):
        print(f"PREDICT: {nonterm} -> {rule} at {line}:{column}")
        return super().predict(nonterm, rule, start, line, column)
        
    def complete(self, rule, start, end):
        print(f"COMPLETE: {rule} from {start} to {end}")
        return super().complete(rule, start, end)

# 3. Modify your parser to show more tokenization details

def debug_tokens_detailed(self, input_text):
    """More detailed token debugging showing token contexts"""
    from lark import Lark, Token
    
    # Create a simple parser with debug enabled
    parser = Lark(self._lark_grammar, parser='earley', debug=True)
    
    # Try to parse partially
    try:
        result = parser.parse(input_text)
    except Exception as e:
        print(f"Parse error: {e}")
    
    # The debug output will show which state the parser was in when it failed
    
#     1. Check for Symbol Conflicts:
#           Print all the terminal symbols in your grammar to check for conflicts:



#     3. Print the Parse States:
#       This will show what state the parser is in when it fails:

def print_parse_states(parser, input_text):
    """Print all parser states while parsing"""
    from lark.parser.earley import Parser as EarleyParser
    
    class StateTracker(EarleyParser):
        def predict(self, nonterm, rule, start, line, column):
            print(f"STATE: Predicting {nonterm} at line {line}, col {column}")
            return super().predict(nonterm, rule, start, line, column)
    
    # Replace the parser with our state tracker
    original_parser = parser._parser
    parser._parser = StateTracker(parser.grammar, parser.options)
    
    try:
        tree = parser.parse(input_text)
    except Exception as e:
        print(f"Error during parsing: {e}")
    
    # Restore original parser
    parser._parser = original_parser