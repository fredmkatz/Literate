from utils.class_pom_token import *
from utils.class_casing import *


def test_casings():
    samples = [
        UpperCamel("Gone with the Wind"),
        LowerCamel("Gone with the Wind"),
        SnakeCase("Gone with the Wind"),
    ]

    for sample in samples:
        test_casing(sample)



def test_casing(sample: Casing):
    the_type = type(sample)
    the_type_name = the_type.__name__
    print(f"\nTesting: {the_type_name}({sample.as_entered})")
    print(f"\t       str: {sample}")
    print(f"\tmodel dump: {sample.model_dump()}")
    print(f"\t      repr: {sample.repr()}")
    print(f"\t  __repr__: {sample.__repr__()}")
    print(f"\t    content: {sample.content}")
    # print(f"\t      asdict: {sample.as_dict}")



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
    test_casings()