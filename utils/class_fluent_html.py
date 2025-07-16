# fluent_html.py
from bs4 import BeautifulSoup, Tag
import bs4
import builtins

# Patch global __str__ for all bs4.Tag instances
Tag.__str__ = lambda self: self.prettify()

TAGS_TO_EXPORT = [
    "html", "head", "link", "script", "title", "body", "div", "table",
    "img", "span", "h1", "p", "a", "b",
    "figure", "figcaption", "pre"
]

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

_shared_soup = BeautifulSoup("", "html.parser")

def make_tag(name, *children, **attrs):
    tag = _shared_soup.new_tag(name)
    return FluentTag(tag)(*children, **attrs)

def export_tags_globally(names):
    for name in names:
        def make_factory(n):
            def fn(*args, **kwargs):
                return make_tag(n, *args, **kwargs)
            return fn
        builtins.__dict__[name] = make_factory(name)

def retarget_soup(tag_like, new_soup):
    if isinstance(tag_like, FluentTag):
        tag = tag_like.tag
    elif isinstance(tag_like, Tag):
        tag = tag_like
    else:
        return

    tag._formatter = new_soup.builder.formatter
    for child in tag.contents:
        retarget_soup(child, new_soup)

def wrap_deep(tag_like):
    if isinstance(tag_like, FluentTag):
        tag = tag_like.tag
    elif isinstance(tag_like, Tag):
        tag = tag_like
    else:
        raise TypeError("wrap_deep expects a Tag or FluentTag")

    for i, child in enumerate(tag.contents):
        if isinstance(child, FluentTag):
            tag.contents[i] = child.tag
            child = child.tag
        if isinstance(child, Tag):
            wrap_deep(child)

    retarget_soup(tag, _shared_soup)
    return FluentTag(tag)

def unify_soup_tree(tag_like):
    if isinstance(tag_like, FluentTag):
        html_str = tag_like.tag.decode()
    elif isinstance(tag_like, Tag):
        html_str = tag_like.decode()
    else:
        raise TypeError("Expected Tag or FluentTag")

    fragment = BeautifulSoup(html_str, "html.parser")
    if len(fragment.contents) == 1 and isinstance(fragment.contents[0], Tag):
        return FluentTag(fragment.contents[0])
    else:
        container = _shared_soup.new_tag("div")
        for el in fragment.contents:
            container.append(el)
        return FluentTag(container)

def create_html_root():
    html_tag = _shared_soup.new_tag("html")
    _shared_soup.append(html_tag)
    return FluentTag(html_tag)

class FluentTag:
    def __init__(self, tag: Tag):
        self.tag = tag

    def __call__(self, *children, **attrs):
        for child in children:
            if isinstance(child, FluentTag):
                self.tag.append(child.tag)
            elif isinstance(child, Tag):
                self.tag.append(child)
            elif isinstance(child, str):
                self.tag.append(child)

        for k, v in attrs.items():
            if k.endswith("_") and k[:-1] in {"class", "for", "id"}:
                k = k[:-1]
            self.tag[k] = v

        return self

    def __getattr__(self, name):
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

        if name in VALID_HTML_TAGS and self.tag.builder is not None:
            new_tag = self.tag.builder.new_tag(name)
            self.tag.append(new_tag)
            return FluentTag(new_tag)

        raise AttributeError(f"'FluentTag' object has no attribute or tag '{name}'")

    def attr(self, **attrs):
        for k, v in attrs.items():
            self.tag[k] = v
        return self
    
    def parent_tag(self):
        result = self.tag.parent 
        return FluentTag(result) if result else None


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
        try:
            return self.tag.prettify()
        except Exception:
            import traceback
            print("⚠️ Falling back to decode() with formatter='html'")
            traceback.print_exc()
            try:
                return self.tag.decode(formatter="html")
            except Exception:
                return repr(self.tag)

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
    
    # generalized call for append()
    # - filters out None items
    # - takes a list of items as arguments; appends each
    # - eliiminates empty spans/divs
    # - takes a list as an argument; recurses into it
    
    def append_all(self, *items, warn_on_retarget=True):
        for item in items:
            if item is None:
                continue
            if isinstance(item, list):
                self.append_all(*item, warn_on_retarget=warn_on_retarget)
                continue
            self.append(item, warn_on_retarget=warn_on_retarget)
        return self
            
            

    def append(self, item, warn_on_retarget=True):
        if item is None:
            return self
        if not isinstance(item, FluentTag):
            self.tag.append(bs4.NavigableString(str(item)))
            return self
        if isinstance(item, FluentTag):
            item = item.tag
        if isinstance(item, Tag):
            if item.soup is not self.tag.soup:
                if warn_on_retarget:
                    print("⚠️ Retargeting tag from different soup before append.")
                retarget_soup(item, self.tag.soup)
        self.tag.append(item)
        return self

    def extend(self, items):
        for item in items:
            self.append(item)
        return self

    def add_class(self, classname):
        currents = self.get("class", [])
        if isinstance(currents, str):
            currents = [currents]
        clean_classes = list(set(currents + [classname]))
        self["class"] = clean_classes
# def create_html_fragment(html_text):
#     div_tag = _shared_soup.new_tag("div")
#     div_tag.append("Content to come later")
#     return FluentTag(div_tag)

def parse_fragment(html_str):
    """Parse an HTML string into a Tag using the shared soup."""
    fragment = BeautifulSoup(html_str, "html.parser")
    # clone its children into the shared soup
    container = _shared_soup.new_tag("div")
    for el in fragment.contents:
        container.append(el)
    return FluentTag(container)

# Export tags globally on import
export_tags_globally(TAGS_TO_EXPORT)  # html(), head(), etc.
