from utils.class_pom_token import Emoji, IsOptional, MarkedText
# from emoji import emoji_list, replace_emoji, emoji

import emoji
import emojis


tests = [
    "ABC",
    ":smile",
    "❌",
    "⚠️",
    "💡",

]

print(IsOptional("optional"))
print(IsOptional("required"))
print(MarkedText("Content without marks"))
print(MarkedText("<<<Content with marks>>>"))
for test in tests:
    emoji = Emoji(test)
    print(f"Test is {test}, Emoji is {emoji}")
    print("\tunicode:\t", emoji.as_unicode())
    print("\tsmile:\t", emoji.as_smile())
    print("\tsymbol\t", emoji.as_symbol())


tests2 = [
    ":thumbs_up:",
    "❤",
    "👍",
    "👍❤❤❤",
    'This is a message with emojis :smile: :snake:',
    
    
]
for test in tests2:
    print("test input: ", test)
    print("\tdecoded: ", emojis.decode(test))
    print("\tencoded: ", emojis.encode(test))
    


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
