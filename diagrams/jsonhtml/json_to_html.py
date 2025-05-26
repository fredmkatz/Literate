from utils.util_all_fmk import write_text


def json_to_html(obj) -> str:
    if isinstance(obj, dict):
        print(f"Found dict: {obj}")
        dict_html = div()
        dict_html.tag["class"] = "Dictionary"
        for key, value in obj.items():
            if key == "_type":
                dict_html["class"] = ["Dictionary", str(value)]
                continue

            pair_html = div()
            pair_html.tag["class"] = "KeyValue"
            key_html = span()
            key_html.tag["class"] = "Key"

            key_html.string = key
            pair_html.append(key_html)

            value_html = div()
            value_html["class"] = "Value"
            value_html.append(json_to_html(value))
            pair_html.append(value_html)
            dict_html.append(pair_html)
        return dict_html

    if isinstance(obj, list):
        print(f"Found list: {obj}")
        list_html = div()
        list_html["class"] = "List"

        for x in obj:
            item_html = json_to_html(x)
            list_html.append(item_html)
        return list_html
    objtype = type(obj)
    if objtype in [str, bool, int, float]:
        print(f"found scalar {objtype}: {obj}")
        scalar_html = span(str(obj), class_="Scalar")
        # scalar_html["class"] = "Scalar"

        # scalar_html.string = str(obj)
        return scalar_html
    print(f"But object type is {objtype} for {obj}")
    return objtype


def new_test():

    page = html(
        head(title("Hello Page")),
        body(
            h1("Welcome!"),
            div("Main block", id="main")(div("Nested content", class_="note")),
        ),
    )

    print(page)  # Pretty print works


def html_test():

    print("Testing html")
    page_html = html()

    print("type of page_html is ", type(page_html))
    print("\fPrettified")
    print(page_html)


def create_html_page(html_path, page_content):
    link_tag = link(rel="stylesheet", href="JSONClaude.css")

    head_html = head(link_tag)
    body_html = body(page_content)
    page_html = html(head_html, body_html)

    page_html_text = str(page_html)
    write_text(html_path, page_html_text)


if __name__ == "__main__":
    print("New test")
    new_test()

    print("\nOLD HTML test")
    html_test()
    # exit(0)
    print("\nJSON to HTML test")

    sample = {
        "the_dict": "My dictionary",
        "_type": "SpecialDictionary",
        "field1": "Value of field1",
        "field2": {
            "NestedF1": "value1",
            "NestedF2": "value2",
        },
        "field3": [
            "item1",
            {
                "NestedF1": "value1",
                "NestedF2": "value2",
            },
        ],
    }

    result = json_to_html(sample)
    print("RESULT is: ")
    pretty_html = str(result)
    print(pretty_html)
    create_html_page("JSONDataSample.html", result)
