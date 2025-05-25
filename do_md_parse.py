import markdown
from bs4 import BeautifulSoup 

from utils_pom.util_plantweb import render_puml

import utils_pom.util_all_fmk as fmk
from dull_dsl.dull_build import the_model_assets_dir
n_pumls = 0
def as_prose_html(markdown_string):
    
    # translate to html text
    html_str = markdown.markdown(markdown_string, extensions=['extra',  'toc'])
    
    # parse the html, to make repairs
    html_soup = BeautifulSoup(html_str, 'html.parser')

    
    # make repairs
    for codeblock in html_soup.find_all("code"):
        current_classes = codeblock.get("class")
        if current_classes and "language-mermaid" in current_classes:
            newclasses = current_classes + ["mermaid"]
            codeblock['class'] = newclasses

        if current_classes and "language-csv" in current_classes:
            csv = codeblock.get_text()
            table_html = fmk.csv2html(csv)
            table_soup = BeautifulSoup(table_html, 'html.parser')
            table_soup["class"] = "codes-table"
            print("table follows", table_soup)
            codeblock.parent.insert_after(table_soup)
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
            pngdiv = div(class_ = "diagram png puml", string="PNG Diagram")
            png_image_element = img(src = f"assets/{png_file_name}")
            pngdiv.append(png_image_element)
            svgdiv = div(class_ = "diagram svg puml", string="SVG Diagram")
            svg_image_element = img(src = f"assets/{svg_file_name}")
            svgdiv.append(svg_image_element)
            codeblock.insert_after(svgdiv)
            codeblock.insert_after(pngdiv)
            continue

    # html = markdown.markdown(markdown_string, extensions=['extra', 'codehilite', 'toc'])
    return html_soup

