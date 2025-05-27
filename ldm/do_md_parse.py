import markdown
from bs4 import BeautifulSoup
from utils.util_plantweb import render_puml

import utils.util_all_fmk as fmk
from dull_dsl.dull_build import the_model_assets_dir
from utils.class_fluent_html import wrap_deep

n_pumls = 0


def as_prose_html(markdown_string):

    # translate to html text
    html_str = markdown.markdown(markdown_string, extensions=["extra", "toc"])

    # parse the html, to make repairs
    # html_soup = BeautifulSoup(html_str, "html.parser")
    
    from utils.class_fluent_html import parse_fragment
    html_soup = parse_fragment(html_str)

    # make repairs
    for codeblock in html_soup.find_all("code"):
        print("Starting codeblock")
        print(codeblock)
        print("and Starting codeblock parent for")
        print(codeblock.parent)

        current_classes = codeblock.get("class")
        if current_classes and "language-mermaid" in current_classes:
            newclasses = current_classes + ["mermaid"]
            codeblock["class"] = newclasses
            continue

        if current_classes and "language-csv" in current_classes:
            csv = codeblock.get_text()
            table_html = fmk.csv2html(csv)
            # table_soup = BeautifulSoup(table_html, "html.parser")
            table_soup = parse_fragment(table_html)
            table_soup["class"] = "codes-table"
            print("table follows", table_soup)
            codeblock.append(table_soup)
            continue
        if current_classes and "language-puml" in current_classes:
            puml = codeblock.get_text()
            puml = puml.replace("@startuml", "")
            puml = puml.replace("@enduml", "")
            global n_pumls
            n_pumls += 1
            png_file_name = f"diagram{n_pumls}.png"
            png_file_path = f"{the_model_assets_dir}/{png_file_name}"
            print(f"creating png in {png_file_path}")
            pngurl = render_puml(puml, "png", png_file_path)
            svg_file_name = f"diagram{n_pumls}.svg"
            svg_file_path = f"{the_model_assets_dir}/{svg_file_name}"
            print(f"creating svg in {svg_file_path}")
            svgurl = render_puml(puml, "svg", svg_file_path)

            pngdiv = div(class_="diagram png puml", string="PNG Diagram")
            png_image_element = img(src=f"assets/{png_file_name}")
            pngdiv.append(png_image_element)
            
            svgdiv = div(class_="diagram svg puml", string="SVG Diagram")
            svg_image_element = img(src=f"assets/{svg_file_name}")
            svgdiv.append(svg_image_element)
            
            print("SVG div for PUML")
            print(svgdiv)

            codeblock.append(svgdiv)
            codeblock.append(pngdiv)
            
            print("Finished codeblock for PUML")
            print(codeblock)
            print("and Finished codeblock parent for PUML")
            print(codeblock.parent)
            continue

    return html_soup

