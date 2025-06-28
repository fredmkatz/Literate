from utils.class_pom_token import *
from utils.class_casing import *

def test_token(cls, input_str):
    print(f"\nTesting {cls.__name__} with input = {input_str}")
    token = cls(input_str)
    print(fmk.as_json(token.full_display()))
    
    
def test_casings():
    samples = [
        (UpperCamel, "Gone with the Wind"),
        (LowerCamel, "Gone with the Wind"),
        (SnakeCase, "Gone with the Wind"),
    ]

    for sample in samples:
        test_token(*sample)
        
def test_emojis():

    tests = [
        (Emoji, ":grinning_face:"),
        (Emoji, ":stop-sign:"),
        (Emoji, "❌"),
        (Emoji, "⚠️"),
        (Emoji, ":warning:"),
        (Emoji, "💡"),

    ]

    for test in tests:
        test_token(*test)


def test_booleans():
    tests = [
        (IsExclusive, "nonexclusive"),
        (IsExclusive, "Exhastive"),
        (IsExhaustive, "Exhaustive"),
        (AsValue, "reference"),
        (AsValue, True),
        # (IsOptional, 17),
        
    ]
    for test in tests:
        test_token(*test)

if __name__ == "__main__":
    test_booleans()
    test_emojis()
    # test_casings()