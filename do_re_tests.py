import re

##

# Fence pattern
# To match entire code blocks, including the triple backtick fences, use the following regex with the re.DOTALL flag:

#   (?:[^\n]*) — Optionally matches any language specifier after the opening fence.

#   \n — Requires a newline after the opening fence.

#   [\s\S]*? — Lazily matches everything (including newlines) up to the closing fence.

#   `\n```

code_block_pattern = r"```(?:[^\n]*)\n[\s\S]*?\n```"


# TextLines
paragraph = r"(?:^(?:[ \t]*\S.*\n?)+)"
# Explanation:

# ^ — Start of a line (in multiline mode).

# [ \t]*\S.* — Line may start with spaces/tabs, but must contain at least one non-whitespace character.

# \n? — Optionally match the newline at the end (handles last line without a newline).

# (?: ... )+ — One or more such lines in a row.

# The outer non-capturing group ensures you get the whole block as one match.

paragraph_pattern = r"(?:^(?:[ \t]*\S.*\n?)+)"

from utils_pom.util_fmk_pom import read_text

ldmpath = "samples/LDMMeta.md"
ldmtext = read_text(ldmpath)

def block():
    matches = re.findall(paragraph_pattern, ldmtext, re.MULTILINE)
    for block in matches:
        print("Block:")
        print(repr(block))

    code_matches = re.findall(code_block_pattern, ldmtext, re.DOTALL)
    for block in code_matches:
        print("CodeBlock:")
        print(repr(block))


    starts = [
        "Note:",
        "Example:",
        "Default",
        "Subtypes:",
        ".+:",
    ]

    for start in starts:
        pattern = f'\s*{start}{paragraph_pattern}'
        print("matching: ", start, "\t", pattern)
        matches = re.findall(pattern, ldmtext, re.DOTALL)
        for block in matches:
            print("\n", start, ":")
            print(repr(block))


def oldchunk(text, starts):

    full_pattern = re.compile(r'''
        (?P<code>``````)                   # Code blocks (non-greedy)
    | (?P<labeled>^[A-Z]+:.*?(?=\n{2}|\Z))  # Labeled paragraphs (e.g., "KEYWORD: ...")
    | (?P<text>(?:(?!```
    | (?P<blank>^\s*$)                      # Blank lines
    ''', re.MULTILINE | re.DOTALL | re.VERBOSE)


    sections = []
    for match in full_pattern.finditer(ldmtext):
        if match.group('code'):
            sections.append(('code', match.group('code')))
        elif match.group('labeled'):
            sections.append(('labeled', match.group('labeled')))
        elif match.group('text'):
            sections.append(('text', match.group('text').strip()))
        elif match.group('blank'):
            sections.append(('blank', ''))

    for section in sections:
        print(section)

# Output structure:
# [('labeled', 'LABEL: Example Section'),
#  ('text', 'This is a labeled paragraph.'),
#  ('text', 'Some unlabeled text spanning multiple lines.'),
#  ('code', '```\ncode_block = "example"\n```
#  ('text', 'Another unlabeled paragraph.')]



def chunk(text: str):
    # Patterns

    code_block_pat = r'```[\s\S]*?```'
    labeled_para_pat = (
        r'^\s*[A-Za-z][A-Za-z0-9_]*:.*'
        r'(?:\n(?!\n|[A-Z][A-Z0-9_]*:|```).*?)*'
    )
    blank_line_pat = r'^\s*$'

    full_pattern = re.compile(
        rf'(?P<code>{code_block_pat})'
        rf'|(?P<labeled>{labeled_para_pat})'
        rf'|(?P<blank>{blank_line_pat})',
        re.MULTILINE | re.DOTALL
    )

    # Iterate and classify
    pos = 0
    results = []
    for m in full_pattern.finditer(text):
        kind = m.lastgroup
        start, end = m.span()
        if pos < start:
            # Text between matches is unlabeled paragraph(s)
            chunk = text[pos:start].strip('\n')
            if chunk:
                results.append(('unlabeled', chunk))
        if kind != 'blank':
            results.append((kind, m.group()))
        pos = end

    # Catch any trailing text
    if pos < len(text):
        chunk = text[pos:].strip('\n')
        if chunk:
            results.append(('unlabeled', chunk))

    # Print results
    for kind, chunk in results:
        print(f'--- {kind.upper()} ---\n{chunk}\n')

chunk(ldmtext)
