from mermaid_cli import render_mermaid_file_sync

def render_mermaid_file(mmd_path, img_format, img_path):
    render_mermaid_file_sync(
        input_file=mmd_path,
        output_file=img_path,
        output_format=img_format
    )


