import os
from playwright.sync_api import sync_playwright


def html2pdf_playwright(html_path, pdf_path):
    with sync_playwright() as p:
        # Launch a Chromium browser in headless mode
        browser = p.chromium.launch()
        page = browser.new_page()

        # Construct the file URL for the local HTML file
        file_url = f"file://{os.path.abspath(html_path)}"

        # Navigate to the local HTML file
        page.goto(file_url)

        # Wait for dynamic content (e.g., PlantUML, Mermaid diagrams) to render
        # You might need to adjust the wait_until or add a specific wait_for_selector if needed
        page.wait_for_load_state("networkidle")

        # Generate the PDF
        page.pdf(path=pdf_path, format="A4")

        # Close the browser
        browser.close()

if __name__ == "__main__":
    # Example usage:
    html_file_path = r"ldm\ldm_models\Literate\Literate_results\Literate_PD_08_as_pdf.html"  # Replace with your HTML file path
    output_pdf_path = r"ldm\ldm_models\Literate\Literate_results\Literate_PD_11.pdf"

    html2pdf_playwright(html_file_path, output_pdf_path)
