# from utils.class_fluent_html import  FluentTag
# todo: why isn't this needed for a(), div(), etc - just because it's imported
# elsewhere?


def anchor_html(css_class, display_name, anchor_name=""):
    if not anchor_name:
        anchor_name = display_name
    anchor_h = a(display_name, class_=css_class, id=f"{anchor_name}")
    return anchor_h


def link_html(css_class, display_name, anchor_name=""):
    if not anchor_name:
        anchor_name = display_name
    anchor_h = a(display_name, class_=css_class, href=f"#{anchor_name}")
    return anchor_h


def spanned_dict_entry(the_dict, attribute):
    """ Retrieves a dict entry based on key, and returns a span() with the contents.
    The span has the key as a class.
    
    If the entry isn't there, or it's None, or its a blank str, nothing (None)
    is returned
    

    Args:
        the_dict (_type_): _The dict from which to obtain a value_
        attribute (_type_): _the key to use_

    Returns:
        _type_: _an HTML span(value obtained), with class = attribute_
    """
    value = the_dict.get(attribute, None)
    if value is None:
        return None
    
    if attribute == "message":
        print("message value is ", value)
    if not value:
        return ""

    if isinstance(value, str):
        value = value.strip()
    return span(value, class_=attribute)


def div_custom(css_class, pieces=[]):
    div_h = div(class_=css_class)
    for piece in pieces:
        div_h.append(piece)
    return div_h


def span_custom(css_class, pieces):
    html_h = span()
    html_h["class"] = css_class
    # print("span Pieces are: ", pieces)
    for piece in pieces:
        html_h.append(piece)

    # print("span returning: ", html_h)
    return html_h
