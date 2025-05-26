def pretty_print_parse_tree(
    tree, max_text_length=30, indent=0, indent_size=2, text_column_width=35
):
    """
    Pretty prints a Lark parse tree with full token and text information in a fixed-width column.

    Args:
        tree: The Lark parse tree (Tree or Token)
        max_text_length: Maximum length of text to display
        indent: Current indentation level (used in recursion)
        indent_size: Number of spaces per indentation level
        text_column_width: Width of the text column

    Returns:
        String representation of the parse tree
    """
    result = []
    indent_str = ". " * indent_size * indent

    if hasattr(tree, "data"):  # It's a Tree node
        # Get the full text of this subtree
        tree_text = get_full_text(tree)
        tree_text_display = tree_text.replace("\n", "\\n")
        if len(tree_text_display) > max_text_length:
            tree_text_display = tree_text_display[:max_text_length] + "..."

        # Format with fixed-width column for text
        text_column = f"'{tree_text_display}'".ljust(text_column_width)
        result.append(f"{text_column} {indent_str}Rule: {tree.data}")

        # Process children
        for child in tree.children:
            result.append(
                pretty_print_parse_tree(
                    child, max_text_length, indent + 1, indent_size, text_column_width
                )
            )
    else:  # It's a Token
        # Get token type and text, truncating text if necessary
        token_type = tree.type if hasattr(tree, "type") else "TOKEN"
        token_value = str(tree)

        # Replace newlines for display
        token_value_display = token_value.replace("\n", "\\n")

        # Truncate if needed
        if len(token_value_display) > max_text_length:
            token_value_display = token_value_display[:max_text_length] + "..."

        # Format with fixed-width column for text
        text_column = f"'{token_value_display}'".ljust(text_column_width)
        result.append(f"{text_column} {indent_str}Token: {token_type}")

    return "\n".join(result)


def get_full_text(tree):
    """
    Recursively extracts the full text of a parse tree.

    Args:
        tree: The Lark parse tree (Tree or Token)

    Returns:
        String representation of the tree's text
    """
    if not hasattr(tree, "data"):  # It's a Token
        return str(tree)

    # It's a Tree, collect text from all children
    text_parts = []
    for child in tree.children:
        text_parts.append(get_full_text(child))

    return "".join(text_parts)


def pretty_print_lark_tree(tree, max_text_length=30, text_column_width=35):
    """
    Wrapper function to pretty print a Lark parse tree.

    Args:
        tree: The Lark parse tree
        max_text_length: Maximum length of text to display for tokens
        text_column_width: Width of the text column

    Returns:
        None (prints to console)
    """
    print("---- Prettier Parse Tree ----")
    print(
        pretty_print_parse_tree(
            tree, max_text_length, text_column_width=text_column_width
        )
    )
    print("-----------------------------")


import lark


def lark_to_dict(tree: lark.Tree) -> dict:
    """
    Converts a Lark parse tree to a JSON-like dictionary.

    Args:
        tree: The Lark parse tree

    Returns:
        Dictionary representation of the parse tree
    """
    if hasattr(tree, "data"):  # It's a Tree node
        rule_name = str(tree.data)
        print(f"Rule name: {rule_name}")
        # first_element = tree.children[0] if tree.children else None
        # print(f"First element: {first_element}")
        # first_token = first_element.data
        # print(f"First token: {first_token}")
        return {rule_name: [lark_to_dict(child) for child in tree.children]}
    else:  # It's a Token
        print(f"Token type: {tree.type}")
        return {tree.type: str(tree)}


def lark_to_json_pretty(tree, indent=2):
    """
    Converts a Lark parse tree to a pretty-printed JSON string.

    Args:
        tree: The Lark parse tree
        indent: Number of spaces for indentation

    Returns:
        Pretty-printed JSON string representation of the parse tree
    """
    import json

    return json.dumps(lark_to_dict(tree), indent=indent)


def lark_to_yaml_pretty(tree, indent=2):
    """
    Converts a Lark parse tree to a pretty-printed JSON string.

    Args:
        tree: The Lark parse tree
        indent: Number of spaces for indentation

    Returns:
        Pretty-printed JSON string representation of the parse tree
    """
    from utils.util_fmk import as_yaml

    return as_yaml(lark_to_dict(tree))
