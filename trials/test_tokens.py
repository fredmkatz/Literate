from utils.class_pom_token import *
from utils.class_casing import *

def test_booleans():
    tests = [
        IsExclusive("nonexclusive"),
        IsExclusive("Exhastive"),
        IsExhaustive("Exhaustive"),
        AsValue("reference"),
        AsValue(True),
        # IsOptional(17),
        
    ]
    for test in tests:
        token_type = type(test)
        token_type_name = type(test).__name__
        as_entered = test.as_entered

        print("Test: ", f"{token_type_name}( {as_entered})")
        
        print("\tstr(T): ", str(test))
        print("\trepr(T):", repr(test))
        
        content = test.content
        rtrip = token_type(content)
        print("\trtrip: ", repr(rtrip))
        print("\n")

if __name__ == "__main__":
    test_booleans()