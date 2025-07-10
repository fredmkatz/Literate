from pikepdf import Pdf, Name

def set_pdf_viewing(pdf_path, output_path):
    with Pdf.open(pdf_path) as pdf:
        # Set the page layout to TwoPageLeft
        pdf.Root.PageLayout = Name.TwoPageLeft
        pdf.Root.PageMode = Name.UseAttachments


        pdf.save(output_path)
