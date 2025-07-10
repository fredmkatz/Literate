import docraptor

doc_api = docraptor.DocApi()
doc_api.api_client.configuration.username = 'YOUR_API_KEY_HERE'
# doc_api.api_client.configuration.debug = True

def url_to(file_path) -> str:
    return file_path

def dr_html_to_pdf(html_path, pdf_path):
    
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    response = doc_api.create_doc({
        "test": True,                                                   # test documents are free but watermarked
        "document_content": html_content,    # supply content directly
        # "document_url": url_to(html_path), # or use a url
        "name": "docraptor-python.pdf",                                 # help you find a document later
        "document_type": "pdf",                                         # pdf or xls or xlsx
        # "javascript": True,                                           # enable JavaScript processing
        # "prince_options": {
        #   "media": "screen",                                          # use screen styles instead of print styles
        #   "baseurl": "http://hello.com",                              # pretend URL when using document_content
        # },
        })
    with open(pdf_path, "wb") as f:
            f.write(response)
