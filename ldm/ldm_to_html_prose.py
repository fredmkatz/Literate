import markdown
import os
from bs4 import BeautifulSoup
from utils.util_plantweb import render_puml

import utils.util_all_fmk as fmk
from dull_dsl.dull_build import model_assets_dir, model_diagrams_dir
from utils.class_fluent_html import wrap_deep
from utils.util_mermaid import render_mermaid_file

n_pumls = 0


def as_prose_html(markdown_string):

    # translate to html text
    html_str = markdown.markdown(markdown_string, extensions=["extra", "toc"])

    # parse the html, to make repairs
    # html_soup = BeautifulSoup(html_str, "html.parser")
    
    from utils.class_fluent_html import parse_fragment
    html_soup = parse_fragment(html_str)
    global n_pumls

    codeblocks = html_soup.find_all("code")
    # print("Found codeblocks ", len(codeblocks))
    # if len(codeblocks) == 1:
    #     print(" and the soup is ")
    #     print(html_soup)
    # make repairs
    for codeblock in html_soup.find_all("code"):
        # print("Starting codeblock")
        # print(codeblock.name)
        # print("and Starting codeblock parent for")
        # print(codeblock.parent_tag())
        # print("and Starting codeblock grandparent for")
        # print(codeblock.parent_tag().parent_tag().name)
        codediv = codeblock.parent_tag().parent_tag()   # the containing div/pre
        # codediv = codeblock.find("code")
        # if codediv:
        #     print("Found codediv in codeblock")
        # else:
        #     print("No codediv in codeblock")
        #     continue
        current_classes = codeblock.get("class")

        if current_classes and "language-csv" in current_classes:
            csv = codeblock.get_text()
            table_html = fmk.csv2html(csv)
            # table_soup = BeautifulSoup(table_html, "html.parser")
            table_soup = parse_fragment(table_html)
            table_soup["class"] = "codes-table"
            # print("table follows", table_soup)
            codeblock.append(table_soup)
            continue
        if current_classes and "language-puml" in current_classes:
            puml = codeblock.get_text()
            puml = puml.replace("@startuml", "")
            puml = puml.replace("@enduml", "")
            
            suite_h = diagram_suite("PlantUML Diagram", puml, "puml")

            codediv.clear()
            codediv.append(suite_h)
            
            continue
        if current_classes and "language-mermaid" in current_classes:
            newclasses = current_classes + ["mermaid"]
            codeblock["class"] = newclasses
            
            mmd = codeblock.get_text()
            suite_h = diagram_suite("Mermaid Diagram", mmd, "mermaid")

            codediv.clear()
            codediv.append(suite_h)

            continue

    return html_soup

def diagram_suite(title: str, diagram_code: str, flavor: str):
    suite_h = div(class_ = "diagram_suite")
    
    # first, the inert raw code
    rawfigure = figure(
        figcaption(f"{title} - Inert"),
        div(diagram_code,  class_ = "raw-diagram-code")
    )

    suite_h.append(rawfigure)

    # only produce a live section for mermaid; can't use it for PlantUML
    if flavor == "mermaid":
        # then, the live version of the code
        live_figure = figure(
            figcaption(f"{title} - Live!"),
            div(diagram_code, class_ =  f"language-{flavor} {flavor}")
        )
        suite_h.append(live_figure)

        # then, the png/svg

    global n_pumls
    n_pumls += 1
    
    diagram_code_file_name = f"diagram_{n_pumls}_{flavor}.txt"

    diagram_code_path = os.path.abspath(f"{model_diagrams_dir}/{diagram_code_file_name}")
    fmk.write_text(diagram_code_path, diagram_code)

    



    PNGING = True
    if PNGING:
        png_file_name = f"diagram_{n_pumls}_{flavor}.png"
        png_file_path = os.path.abspath(f"{model_diagrams_dir}/{png_file_name}")
        print(f"creating png  for {flavor} in {png_file_path}")

        if flavor == "puml":
            pngurl = render_puml(diagram_code, "png", png_file_path)
        else:
            pngurl = render_mermaid_file(diagram_code_path, "png", png_file_path)

        pngfigure = figure(
            figcaption(f"{title} - PNG for {flavor}"),
            img(src=png_file_path, width="500px"), 
            class_="diagram png puml"
        )

        suite_h.append(pngfigure)

    SVGING = False
    if SVGING:
        svg_file_name = f"diagram_{n_pumls}_{flavor}.svg"
        svg_file_path = os.path.abspath(f"{model_diagrams_dir}/{svg_file_name}")

        if flavor == "puml":
            svgurl = render_puml(diagram_code, "svg", svg_file_path)
        else:
            svgurl = render_mermaid_file(diagram_code_path, "svg", svg_file_path)

        svgfigure = figure(
            figcaption(f"{title} - SVG for {flavor}"),
            img(src=svg_file_path, width="500px"), 
            class_="diagram svg puml"
        )

        suite_h.append(svgfigure)

        
    return suite_h
