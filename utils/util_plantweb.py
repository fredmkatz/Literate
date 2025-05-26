from plantweb.render import render, render_cached

def render_puml(puml_text, format, output_file):

    print(f'==> INPUT to render_puml in {format}:')
    print(puml_text)

    plantuml_server_url = "http://www.plantuml.com/plantuml"
    try:
        (puml_output, sha)= render_cached(plantuml_server_url, format, puml_text)
        
        
        with open(output_file,"wb") as f:
            f.write(puml_output)

        print(f"PUML {format} file saved to: {output_file}")
    except Exception:
        print(f"PUML {format} Failed with input ", puml_text, " - ", output_file)
    return output_file
