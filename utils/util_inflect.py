import inflect

# Initialize the inflect engine
p = inflect.engine()

# Custom overrides for irregular cases
PLURAL_OVERRIDES = {
    "person": "people",
    "child": "children",
    "mouse": "mice",
    "datum": "data",
    "index": "indices",  # Change to "indexes" if needed
}

def pluralize(word):
    """Returns the plural form of a word, with overrides."""
    
    return PLURAL_OVERRIDES.get(word.lower(), p.plural(word))

def show_plurals(word):
    print("Word is: ", word)
    print("Inflect plural is: ", p.plural(word))
    print()
    
# Examples
if __name__ == "__main__":
    show_plurals("person")
    show_plurals("people")
    show_plurals("child")
    show_plurals("children")
    show_plurals("index")
    show_plurals("persona")
    show_plurals("formula")
    show_plurals("table")
