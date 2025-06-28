import emoji
from utils.class_pom_token import Emoji, IsOptional
# from emoji import emoji_list, replace_emoji, emoji


    
def try_emojis():
    tests = [
        ":grinning_face:",
        ":stop-sign:",
        "❌",
        "⚠️",
        "💡",

    ]

    # for test in tests:
    #     emoji = Emoji(test)
    #     print(f"Test is {test}, Emoji is {emoji}")
    #     print("\tunicode:\t", emoji.as_unicode())
    #     print("\tsmile:\t", emoji.as_smile())
    #     print("\tsymbol\t", emoji.as_symbol())


    tests2 = [
        ":thumbs_up:",
        "❤",
        "👍",
        "❤❤❤",
        'This is a message with emojis :smile: :snake:',
        
        
    ]
    for test in tests + tests2:
        print("test input: ", test)
        if test.startswith(":"):
            print("\tstarts with colon - assuming shortcode...")
            shortcode = test
            symbol = emoji.emojize(shortcode)
            print("\tshortcode: ", shortcode)
            print("\tsymbol: ", symbol)
            
            shortcode2 = emoji.demojize(symbol)
            print("\trt shortcode: ", shortcode2)
            if shortcode2 != shortcode:
                print(f"\tError: {shortcode2} != {shortcode}")

        else:
            print("\tassuming symbol/icon")
            symbol = test
            shortcode = emoji.demojize(symbol)
            print("\tsymbol: ", symbol)

            print("\tshortcode: ", shortcode)
            symbol2 = emoji.emojize(shortcode)
            print("\trt symbol: ", symbol2)
            if symbol2 != symbol:
                print(f"\tError: {symbol2} != {symbol}")


    print(emoji.emojize('Python is :thumbs_up:'))
# Python is 👍
# >>> print(emoji.emojize('Python is :thumbsup:', language='alias'))
# Python is 👍
# >>> print(emoji.demojize('Python is 👍'))
# Python is :thumbs_up:
# >>> print(emoji.emojize("Python is fun :red_heart:"))
# Python is fun ❤
# >>> print(emoji.emojize("Python is fun :red_heart:", variant="emoji_type"))
# Python is fun ❤️ #red heart, not black heart
# >>> print(emoji.is_emoji("👍"))
# True
if __name__ == "__main__":
    # try_epedia()
    try_emojis()