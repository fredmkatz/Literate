import utils.util_all_fmk as fmk

from utils.util_json_path_update import JSONPathUpdater

def reduce_model(full_start_json, reduced_json):
    print(f"\treduce_model {full_start_json} to {reduced_json}")
    full_json_data = fmk.read_json_file(full_start_json)
    
    reduced_json_data = remove_keys_recursively(full_json_data, ["elaboration"])
    # print(fmk.as_yaml(reduced_json_data))
    fmk.write_json(reduced_json_data, reduced_json)

def render_html(model_dict_path, html_path):

    import ldm.Literate_01 as Literate_01
    from ldm.ldm_htmlers import create_model_html_with_faculty, save_model_html

    print(f"\trender_html: {model_dict_path} to {html_path}")

    the_dict = fmk.read_json_file(model_dict_path)
    the_model = Literate_01.LiterateModel.from_typed_dict(the_dict)

    web_css_path = "../../ldm_assets/Literate.css"

    model_h = create_model_html_with_faculty(the_model, diagrams = False)

    save_model_html(model_h, web_css_path, html_path)

def render_md(model_dict_path, md_path):
    import ldm.ldm_renderers as ldm_renderers
    import ldm.Literate_01 as Literate_01

    print(f"\trender_md {model_dict_path} to {md_path}")

    the_dict = fmk.read_json_file(model_dict_path)
    the_model = Literate_01.LiterateModel.from_typed_dict(the_dict)

    markdown_output = ldm_renderers.render_ldm(the_model)

    fmk.write_text(md_path, markdown_output)
    print("\t\tsaved markdown to: ", md_path)


def post_advice(reduced_json, advice_files, revised_json):
    print("\tpost_advice from...")
    the_dict = fmk.read_json_file(reduced_json)
    for path in advice_files:
        print("\t\t\t", path)
        advice_dict = fmk.read_json_file(path)
        post_to_dict(advice_dict, the_dict)
        # print(advice_dict)
    fmk.write_json(the_dict, revised_json)


def post_to_dict(advice, target_dict):
    changes = advice.get("changes", [])
    if not changes:
        print('\t\tNo changes found')
    for change in changes:
        print("\t\t\t", change)
        c_type = change.get("type", "")
        c_path = change.get("path", "")
        c_old = change.get("old_value", "")
        c_new = change.get("new_value", "")
        c_reason = change.get("reason", "")
        print("\t\t", c_type)
        print("\t\t", c_path)
        print("\t\t", c_old)
        print("\t\t", c_new)
        print("\t\t", c_reason)
        print("\t\t", "=" * 20)

    

def remove_keys_recursively(obj, keys_to_remove):
    if isinstance(obj, dict):
        # Create a copy of the keys to avoid "RuntimeError: dictionary changed size during iteration"
        for key in list(obj.keys()):
            if key in keys_to_remove:
                del obj[key]
            else:
                # Recursively call on the value, as it could be another dict or a list
                remove_keys_recursively(obj[key], keys_to_remove)
    elif isinstance(obj, list):
        # Iterate through the list and recursively call on each item
        for item in obj:
            remove_keys_recursively(item, keys_to_remove)
    return obj


