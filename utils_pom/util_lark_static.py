def find_terminal_conflicts(grammar_text):
    """Find potential terminal definition conflicts"""
    import re
    
    # Find all terminal declarations
    terminal_matches = re.findall(r'([A-Z_]+):\s+"([^"]+)"', grammar_text)
    terminals = {}
    print("======================")
    print("  find_terminal_conflicts   ")
    print("======================")

    for name, pattern in terminal_matches:
        if pattern in terminals:
            print(f"CONFLICT: Pattern '{pattern}' is defined for both {name} and {terminals[pattern]}")
        terminals[pattern] = name
        
    return terminals

#     2. Find Rule Ordering Issues:
#           Check if there are overlapping rules that could be causing the parser to choose the wrong rule:

def find_rule_overlaps(grammar_text):
    """Find rules that could overlap in matching"""
    import re
    
    print("======================")
    print("  find_rule_overlaps   ")
    print("======================")

    print("SKIPPING OVERLAPS")
    return
    # Find all rules
    rule_matches = re.findall(r'([a-z_]+):\s+(.+)', grammar_text)

    # Look for rules with common prefixes
    for name1, rule1 in rule_matches:
        for name2, rule2 in rule_matches:
            if name1 != name2 and rule1.split()[0] == rule2.split()[0]:
                print(f"OVERLAP: {name1} and {name2} both start with {rule1.split()[0]}")
