import re

def parse_dt_phrase(phrase):
    # Initialize return values
    qualifier = None
    typeA = None
    typeB = None
    
    # Convert to string in case another type is passed
    phrase = str(phrase).strip()
    
    # Pattern for list/set - case insensitive
    list_set_pattern = re.compile(r'^(list\s*of|listof|set\s*of|setof)\s+(.+)$', re.IGNORECASE)
    
    # Pattern for mapping - case insensitive
    mapping_pattern = re.compile(r'^(mapping\s+from)\s+(.+?)\s+to\s+(.+)$', re.IGNORECASE)
    
    # Check for list/set pattern
    list_set_match = list_set_pattern.match(phrase)
    if list_set_match:
        qualifier_raw = list_set_match.group(1).lower()
        if qualifier_raw.replace(' ', '') == 'listof':
            qualifier = 'ListOf'
        elif qualifier_raw.replace(' ', '') == 'setof':
            qualifier = 'SetOf'
        
        typeA = list_set_match.group(2).strip()
        return (qualifier, typeA, typeB)
    
    # Check for mapping pattern
    mapping_match = mapping_pattern.match(phrase)
    if mapping_match:
        qualifier = 'Mapping'
        typeA = mapping_match.group(2).strip()
        typeB = mapping_match.group(3).strip()
        return (qualifier, typeA, typeB)
    
    # If no match, return None for qualifier and the original phrase for typeA
    return (qualifier, phrase.strip(), typeB)

if __name__ == "__main__":
    # Test cases
    test_phrases = [
        "List of Things",
        "list of Other Items",
        "listof Items",
        "SET OF Values",
        "SetOf Numbers",
        "Mapping from Keys to Values",
        "mapping from X to Y",
        "Random Text",
        "List of",  # Edge case
    ]

    for phrase in test_phrases:
        result = parse_dt_phrase(phrase)
        print(f"Phrase: '{phrase}'")
        print(f"Result: {result}")
        print()