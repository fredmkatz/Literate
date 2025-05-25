import markdown

import utils_pom.util_all_fmk as fmk


def md_to_html(markdown_string) -> str:
    
    # translate to html text
    html_str = markdown.markdown(markdown_string, extensions=['extra',  'toc'])
    


    return html_str


if __name__ == "__main__":

    input_path = r"ldm\ldm_models\Literate.md"

    input_path = r"ldm\ldm_models\LiterateTester.md"
    input_path = "mdtestdocs/mdtest_doc.md"
    input_path = r"ldm\ldm_models\LiterateTester\LiterateTester.md"

    
    output_path = f"{input_path}_2.html"

    markdown_string = fmk.read_text(input_path)
    html = md_to_html(markdown_string)

    # html = markdown.markdown(markdown_string, extensions=['extra', 'codehilite', 'toc'])
    fmk.write_text(output_path,  html)

