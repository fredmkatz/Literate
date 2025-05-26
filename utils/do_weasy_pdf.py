import os
import sys

from pathlib import Path


class suppress_stdout_stderr(object):
    """
    A context manager for doing a "deep suppression" of stdout and stderr in Python,
    i.e. will suppress all print, even if the print originates in a compiled C/Fortran sub-function.
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for _ in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close all file descriptors
        for fd in self.null_fds + self.save_fds:
            os.close(fd)


# Usage:
# with suppress_stdout_stderr():
#     # Place your WeasyPrint code here
#     # For example:
#     # weasyprint.HTML('input.html').write_pdf('output.pdf')
#     pass


def generate_weasy_pdf(html_path, css_path, output_path):
    #   css = CSS("ldm/Literate.css")
    #   html = HTML(filename="ldm/LDMMeta_results/LDMMeta.html")
    with suppress_stdout_stderr():

        from weasyprint import CSS, HTML

        html = HTML(filename=html_path)
        css = CSS(css_path)
        out_path = output_path
        print(f"PDFing for {html_path} written to {out_path}")

        html.write_pdf(target=out_path, stylesheets=[css])

    print(f"PDF for {html_path} written to {out_path}")
    return out_path


from html_to_markdown import convert_to_markdown
from utils.util_fmk import write_text, read_text


def gen_markdown_to_html(html_path, md_path):

    html = read_text(html_path)
    markdown = convert_to_markdown(html)
    write_text(md_path, markdown)
    print(f"Markdown for {html_path} written to {md_path}")
    return md_path


if __name__ == "__main__":
    # HTML('https://weasyprint.org/').write_pdf('weasyprint-website.pdf')
    html_path = "ldm/LDMMeta_results/LDMMeta.html"
    css_path = "ldm/Literate.css"
    out_path = "ldm/LDMMeta_results/LDMMeta.pdf"
    md_path = "ldm/LDMMeta_results/LDMMeta.html.md"

    pdf_path = generate_weasy_pdf(
        html_path=html_path, css_path=css_path, output_path=out_path
    )

    md_path_new = gen_markdown_to_html(html_path=html_path, md_path=md_path)
    print(md_path_new)
