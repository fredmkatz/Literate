import subprocess

# prince = Prince(r"C:\Program Files\Prince\engine\bin\prince.exe") # Adjust path as needed

# html_string = """
# <html>
# <body>
#   <h1>Hello, PrinceXML!</h1>
#   <p>This is a test conversion from a string.</p>
# </body>
# </html>
# """

prince_exec = r"C:\Program Files\Prince\engine\bin\prince.exe"

def html2pdf_prince(html_file_path, output_pdf_path):
    subprocess.call([prince_exec, html_file_path, "--javascript", "-o", output_pdf_path])
    
if __name__ == "__main__":

    html_file_path = r'ldm\ldm_models\Literate\Literate_results\Literate_PD_08_as_pdf.html'  # Replace with your HTML file path
    output_pdf_path = r'ldm\ldm_models\Literate\Literate_results\Literate_PD_11.pdf'


    # html_file_path = r'ldm\ldm_models\Diagrams\Diagrams_results\Diagrams_PD_08_as_pdf.html'  # Replace with your HTML file path
    # output_pdf_path = r'ldm\ldm_models\Diagrams\Diagrams_results\Diagrams_PD_11pr.pdf'

    # html_file_path = r'utils\prince_sci_example.html'  # Replace with your HTML file path
    # output_pdf_path = r'utils\prince_sci_example.pdf'
    html2pdf_prince(html_file_path, output_pdf_path)

