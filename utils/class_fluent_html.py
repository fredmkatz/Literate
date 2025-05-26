# fluent_html.py
from bs4 import BeautifulSoup, Tag
import builtins

# Patch global __str__ for all bs4.Tag instances
Tag.__str__ = lambda self: self.prettify()

TAGS_TO_EXPORT =  ["html", "head", "link", "script", "title", "body", "div", "table",
                   "img", "span", "h1", "p", "a", "b"]

VALID_HTML_TAGS = {
    "a", "abbr", "address", "area", "article", "aside", "audio",
    "b", "base", "bdi", "bdo", "blockquote", "body", "br", "button",
    "canvas", "caption", "cite", "code", "col", "colgroup",
    "data", "datalist", "dd", "del", "details", "dfn", "dialog", "div", "dl", "dt",
    "em", "embed",
    "fieldset", "figcaption", "figure", "footer", "form",
    "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hr", "html",
    "i", "iframe", "img", "input", "ins",
    "kbd", "label", "legend", "li", "link",
    "main", "map", "mark", "meta", "meter",
    "nav", "noscript",
    "object", "ol", "optgroup", "option", "output",
    "p", "param", "picture", "pre", "progress",
    "q",
    "rp", "rt", "ruby",
    "s", "samp", "script", "section", "select", "small", "source", "span", "strong", "style", "sub", "summary", "sup", "svg",
    "table", "tbody", "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track",
    "u", "ul",
    "var", "video",
    "wbr"
}

class FluentTag:
    def __init__(self, tag: Tag):
        self.tag = tag

    # def __call__(self, *children, **attrs):
    #     for child in children:
    #         if isinstance(child, FluentTag):
    #             self.tag.append(child.tag)
    #         elif isinstance(child, Tag):
    #             self.tag.append(child)
    #         elif isinstance(child, str):
    #             self.tag.append(child)
    #     for k, v in attrs.items():
    #         self.tag[k] = v
    #     return self
    def __call__(self, *children, **attrs):
        for child in children:
            if isinstance(child, FluentTag):
                self.tag.append(child.tag)
            elif isinstance(child, Tag):
                self.tag.append(child)
            elif isinstance(child, str):
                self.tag.append(child)

        # Translate class_ → class
        for k, v in attrs.items():
            if k.endswith("_") and k[:-1] in {"class", "for", "id"}:
                k = k[:-1] 
            self.tag[k] = v

        return self

    def __getattr__(self, name):
        # Forward known attributes/methods to the underlying Tag
        if hasattr(self.tag, name):
            attr = getattr(self.tag, name)
            if callable(attr):
                def wrapped(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    if isinstance(result, Tag):
                        return FluentTag(result)
                    elif isinstance(result, list):
                        return [FluentTag(r) if isinstance(r, Tag) else r for r in result]
                    return result
                return wrapped
            return attr

        # Only create new tag if it's a valid HTML tag name
        if name in VALID_HTML_TAGS and self.tag.builder is not None:
            new_tag = self.tag.builder.new_tag(name)
            self.tag.append(new_tag)
            return FluentTag(new_tag)

        raise AttributeError(f"'FluentTag' object has no attribute or tag '{name}'")

    def attr(self, **attrs):
        for k, v in attrs.items():
            self.tag[k] = v
        return self

    def find(self, *args, **kwargs):
        result = self.tag.find(*args, **kwargs)
        return FluentTag(result) if result else None

    def find_all(self, *args, **kwargs):
        return [FluentTag(t) for t in self.tag.find_all(*args, **kwargs)]

    def select(self, selector):
        return [FluentTag(t) for t in self.tag.select(selector)]

    def unwrap(self):
        return self.tag

    def __str__(self):
        return self.tag.prettify()

    def __repr__(self):
        return f"FluentTag({repr(self.tag)})"

    def __getitem__(self, key):
        return self.tag[key]

    def __setitem__(self, key, value):
        if key == "class_":
            key = "class"
        self.tag[key] = value

    def __delitem__(self, key):
        del self.tag[key]

    def __contains__(self, key):
        return key in self.tag

    def append(self, item):
        if isinstance(item, FluentTag):
            item = item.tag
        self.tag.append(item)
        return self

    def extend(self, items):
        for item in items:
            self.append(item)
        return self
    
    def add_class(self, classname):
        currents = self.get("class", [])
        clean_classes = list( set(currents + [classname]))
        self["class"] = clean_classes


class FluentSoupBuilder:
    def __init__(self):
        self.soup = BeautifulSoup("", "html.parser")
        self.export_tags(TAGS_TO_EXPORT)


    def tag(self, name, *children, **attrs):
        t = self.soup.new_tag(name)
        t.builder = self  # allow chaining to access soup
        return FluentTag(t)(*children, **attrs)

    def export_tags(self, names):
        for name in names:
            def make_factory(n):
                def fn(*args, **kwargs):
                    return self.tag(n, *args, **kwargs)
                return fn
            builtins.__dict__[name] = make_factory(name)

    def to_fluent(self, tag: Tag):
        return FluentTag(tag)

    def from_html(self, html: str):
        soup = BeautifulSoup(html, "html.parser")
        return self.to_fluent(soup)

builder = FluentSoupBuilder()   # needed on import to get html tag routines exported

### Usage examples
# from class_fluent_html import FluentSoupBuilder

# builder.export_tags(["html", "head", "title", "body", "div", "span", "h1", "p", "a", "b"])

# page = html(
#     head(title("Hello Page")),
#     body(
#         h1("Welcome!"),
#         div("Main block", id="main")(
#             div("Nested content", class_="note")
#         )
#     )
# )

# print(page)  # Pretty print works

# ## on imported html
# from bs4 import BeautifulSoup
# from class_fluent_html import FluentSoupBuilder

# soup = BeautifulSoup("<div id='main'><p>Hello</p></div>", "html.parser")
# builder = FluentSoupBuilder()

# main = builder.to_fluent(soup.find(id="main"))
# main(" World!", div("New block"))

# print(main)
