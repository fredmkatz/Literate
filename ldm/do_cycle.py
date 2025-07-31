from utils.util_all_fmk import *
import utils.util_all_fmk as fmk

from utils.util_cycle import reduce_model, post_advice, render_html, render_md

MODELS_PATH = "ldm/ldm_models"
def do_cycle(model_name = "Literate"):
    cycle_no = 0
    
    # fmk.create_fresh_directory(cycles_path)
    
    starting_json = cyfile(model_name, cycle_no, "00", "full.json")
    reduced_json = cyfile(model_name, cycle_no, "01a", "reduced.json")
    reduced_html = cyfile(model_name, cycle_no, "01b", "reduced.html")
    reduced_md = cyfile(model_name, cycle_no, "01c", "reduced.md")
    advice_json = ""
    revised_json = cyfile(model_name, cycle_no, "03a", "revised.json")
    revised_html = cyfile(model_name, cycle_no, "03b", "revised.html")
    revised_md = cyfile(model_name, cycle_no, "03c", "revised.md")
    
    full_revised_json = cyfile(model_name, cycle_no, "04a", "full_revised.json")
    report_html = cyfile(model_name, cycle_no, "05", "report.html")

    # Step 1. Reduce the model; remove elaborations
    show_step("Step 1: Reduce model by removing elaborations")
    reduce_model(starting_json, reduced_json)
    render_md(reduced_json, reduced_md)
    render_html(reduced_json, reduced_html)

    show_step("Step 2: Get advice, post to revised json")

    advice_sample_path = f"{model_path(model_name)}/sample_advice.json"
    advice_files = [advice_sample_path]
    post_advice(reduced_json, advice_files, revised_json)
    render_html(revised_json, revised_html)
    render_md(revised_json, revised_md)
    
    exit(0)
    
    create_cycle_report(model_name, cycle_no, report_html)
    
def cyfile(model_name, cycle_no: int, artifact_no: int,  extension) -> str:
    return f"{cycles_path(model_name)}/{model_name}_{cycle_no:03d}_{artifact_no}_{extension}"

def cycles_path(model_name):
    return  f"{model_path(model_name)}/{model_name}_cycles"

def model_path(model_name):
    return f"{MODELS_PATH}/{model_name}"


def create_cycle_report(model_name, cycle_no, reoort_html):
    print("Creating report")


def show_step(caption: str):
    print(f"\nPhase: {caption}", file=sys.stderr)
    # print(f"\nPhase: {caption}")

if __name__ == "__main__":
    model_name = "Literate"
    do_cycle(model_name)
