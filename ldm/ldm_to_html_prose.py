import markdown
import os
from bs4 import BeautifulSoup
from utils.util_plantweb import render_puml

import utils.util_all_fmk as fmk
from dull_dsl.dull_build import model_assets_dir
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
    print("Found codeblocks ", len(codeblocks))
    if len(codeblocks) == 1:
        print(" and the soup is ")
        print(html_soup)
    # make repairs
    for codeblock in html_soup.find_all("code"):
        print("Starting codeblock")
        print(codeblock.name)
        print("and Starting codeblock parent for")
        print(codeblock.parent_tag())
        print("and Starting codeblock grandparent for")
        print(codeblock.parent_tag().parent_tag().name)
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
            n_pumls += 1

            png_file_name = f"plant_img{n_pumls}.png"
            png_file_path = os.path.abspath(f"{model_assets_dir}/{png_file_name}")
            print(f"creating png in {png_file_path}")
            pngurl = render_puml(puml, "png", png_file_path)
            
            svg_file_name = f"plant_img{n_pumls}.svg"
            svg_file_path = os.path.abspath(f"{model_assets_dir}/{svg_file_name}")
            svgurl = render_puml(puml, "svg", svg_file_path)


            pngdiv = div(class_="diagram png puml", string="PNG Diagram " + png_file_name)
            png_image_element = img(src=png_file_path, width="500px")
            pngdiv.append(png_image_element)
            
            svgdiv = div(class_="diagram svg puml", string="SVG Diagram"+ svg_file_name)
            
            svg_image_element = img(src=svg_file_path, width="500px")
            svgdiv.append(svg_image_element)
            
            
            # print("SVG div for PUML")
            # print(svgdiv)

            codediv.append(pngdiv)
            codediv.append(svgdiv)
            
            # print("Finished codeblock for PUML")
            # print(codeblock)
            # print("and Finished codeblock parent for PUML")
            # print(codeblock.parent)
            continue
        if current_classes and "language-mermaid" in current_classes:
            newclasses = current_classes + ["mermaid"]
            codeblock["class"] = newclasses
            
            mmd = codeblock.get_text()
            n_pumls += 1
            
            mmd_file_name = f"mermaid_{n_pumls}.txt"

            mmd_path = os.path.abspath(f"{model_assets_dir}/{mmd_file_name}")
            fmk.write_text(mmd_path, mmd)

            png_file_name = f"mermaid_img{n_pumls}.png"
            png_file_path = os.path.abspath(f"{model_assets_dir}/{png_file_name}")
            print(f"creating png  for mermaid in {png_file_path}")
            pngurl = render_mermaid_file(mmd_path, "png", png_file_path)
            
            svg_file_name = f"mermaid_img{n_pumls}.svg"
            svg_file_path = os.path.abspath(f"{model_assets_dir}/{svg_file_name}")
            svgurl = render_mermaid_file(mmd_path, "svg", svg_file_path)


            pngdiv = div(class_="diagram png puml", string="PNG Diagram for Mermaid")
            pngdiv.append(f"Mermaid PNG - {png_file_name}")

            png_image_element = img(src=png_file_path, width="500px")
            pngdiv.append(png_image_element)
            
            svgdiv = div(class_="diagram svg puml", string="SVG Diagram for Mermaid")
            svgdiv.append(f"Mermaid SVG - {svg_file_name}")
            svg_image_element = img(src=svg_file_path, width="500px")
            svgdiv.append(svg_image_element)
            
            
            codediv.append(pngdiv)
            codediv.append(svgdiv)

            continue

    return html_soup

