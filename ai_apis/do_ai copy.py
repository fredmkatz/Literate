import json
import os
import sys

# print("=== DEBUG INFO ===")
# print(f"Current working directory: {os.getcwd()}")
# print(f"Python executable: {sys.executable}")
# print(f"Script location: {__file__}")

from ai_apis.class_ai_assistant import AI_Assistant
from ai_apis.class_ai_openrouter import get_openrouter_models, update_openrouter_models, OpenRouterAssistant

# print(f"AI_Assistant module: {AI_Assistant.__module__}")
# print(f"OpenRouterAssistant module: {OpenRouterAssistant.__module__}")
# print("=== END DEBUG INFO ===\n")
parsing_file = None

def run_quick_query(query="Please review the attached model", 
                    gateway = "OpenRouter",
                    llm_id = "qwen/qwen3-235b-a22b-2507", 
                    docs_dir = "ai_docs",
                    doc_files = [],
                    

                    ) :
    
    gateway = "OpenRouter"
    initial_message = (
        "You are an AI assistant specialized in improving Literate Data Models (LDMs)."
    )


    assistant = OpenRouterAssistant(gateway, llm_id)
    assistant.prepare(
        docs_dir=docs_dir, doc_files=doc_files, initial_message=initial_message
    )
    response_dict = assistant.run_query(query)
    raw_usage = response_dict.get("usage", None)
    if raw_usage:
        costs = assistant.calc_costs(raw_usage)
    else:
        costs = 0.0

    # print("run_quick_query - results are: ", results)
    # print("run_quick_query - Costs are: ", costs)
    return (response_dict, costs)

def parse_json_results(raw_results: str):
    import re
    
    notes = ""
    pruned = re.sub(".*```json", "", raw_results, flags=re.DOTALL)
    # pruned = raw_results.replace(".*```json", "")
    pruned = pruned.replace("```", "")
    all_results = {"raw": raw_results}
    if pruned != raw_results:
        print("\tPRUNING NEEDED")
        notes += "Pruned - "
        all_results["pruned"] = pruned
    else:
        print("\tNo PRUNING Needed")
        notes += "UnPruned - "


    try:
        jresults = json.loads(pruned)

        # print(json.dumps(jresults, indent=2))
        return (jresults, notes, pruned)
    except Exception:
        print("Parsing failed - only raw results returned")
        print("Pruned =...")
        print(pruned)
        print("... end of Pruned")
        notes += "Parsing failed - see raw"
        return(None, notes, pruned)

def run_single_query(model_name, task_id, llm_id, run_path):
    import time
    print(f"Single query: {model_name} - {task_id} - {llm_id}")

    doc_files= [
        "LiterateMetaModel_01_PD_schema.yaml",
        "ReviewingLDM_v0_1.md",
        # Model comes last here - least persistent
        # "Literate_sample.json",
        "Literate_PD_04.v_model.json"
    ]

    start_time = time.perf_counter()

    (response_dict, costs) = run_quick_query(gateway="OpenRouter",
                                       llm_id=llm_id,
                                       docs_dir = "ai_docs",
                                       doc_files = doc_files)
    
    end_time = time.perf_counter()
    rkeys = response_dict.keys()

    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.4f} seconds")

    error = response_dict.get("error", None)
    if error:
        error_msg = error.get("message", "No error Message")
        error_code = error.get("code", "No error code")
        changes = []
        n_changes = -1
        parsing_notes = ""
        parsed_reults = None
        raw_usage = None
        raw_result = ""

    else:
        error_msg = ""
        error_code = ""



    
    raw_results = ""

    if not error_code:
        choices = response_dict.get("choices", None)
        if choices:
            raw_results = choices[0]["message"]["content"]
        else:
            raw_results = ""
        n_bytes_received = len(str(raw_results))

        print("Raw results are....")
        print(json.dumps(raw_results, indent=2))
        raw_usage = response_dict.get("usage", {})

        (parsed_reults, parsing_notes, pruned) = parse_json_results(raw_results)
        parsing_file.write(llm_id + "\n")
        parsing_file.write( parsing_notes+ "\n")
        parsing_file.write( pruned+ "\n")
        parsing_file.write("--------"+ "\n")
        parsing_file.flush()
        n_changes = 0
        if parsed_reults:
            changes = parsed_reults.get("changes", [])
            n_changes = len(changes)
            print(f"Got {n_changes} changes from raw results: ")
            print(raw_results)

        else:
            print("Can't parse raw results:")
            print(raw_results)

    run_capsule = {
        "model": model_name,
        "task": task_id,
        "llm": llm_id,
        "elapsed" : round(elapsed_time, 1),
        "results_len": len(raw_results),
        "rkeys": str(rkeys),
        "usage": raw_usage,
        "costs": round(costs, 3),
        "error_msg": error_msg,
        "error_code": error_code, 
        "changes" : n_changes,
        "parseing_notes": parsing_notes,
    }
    full_results = {"run": run_capsule,
                    "costs": round(costs, 3), 
                    
                    "parsed": parsed_reults,
                    "raw_results": raw_results,
                    "response": response_dict
                    }
    from utils.util_all_fmk import write_json
    write_json(full_results, run_path)
    print("\tRun capsule = ", json.dumps( run_capsule, indent=2))

def cheap_enough(candidates, min_cost, max_cost):
    cheaps = []
    total_cost = 0.0
    for c in candidates:
        est = c.get("query", 1000.0)
        if type(est) == str:
            continue
        if est == 1000.0:
            continue
        if est < 0:
            continue
        if est <  min_cost:
            continue
        if est > max_cost:
            continue
        total_cost += est
        cheaps.append(c)
    print("\ttotal est cost - at max = ", max_cost, " = ", total_cost)
    return cheaps

def run_query_suite(model_name, task_id):
    import pandas as pd
    import time
    
    max_runs =  3 # 3000
    min_est_cost = 0.00000
    max_est_cost = 0.0
    max_est_cost = 0.01 # 48 for 0.15
    # max_est_cost = 0.05 # 92 for $1
    # max_est_cost = 0.1 # 113 for $3
    # max_est_cost = 0.25 # 128 for $5
    # max_est_cost = 0.5 # 150 for $12
    # max_est_cost = 1. # 165 for $22
    # max_est_cost = 100. # 174 for $63
    # max_est_cost = 100000.
    # Get the list of candidate models 
    file_path = "ai_configs/all_models.xlsx" 
    df = pd.read_excel(file_path, sheet_name="OpenRouter Pruned")
    candidates = df.to_dict('records')

    print(len(candidates), " initial candidates")
    
    candidates = cheap_enough(candidates, min_est_cost, max_est_cost)
    candidates.reverse()
    print(len(candidates), " cheap candidates", " with max cost per = ", max_est_cost, f" ({max_runs} max runs)")

    # return
    model_runs_dir = f"ldm/ldm_models/{model_name}/{model_name}_runs"
    
    start_time = time.perf_counter()

    n_runs = 0
    total_est = 0.0
    for c in candidates:
        # print(c)
        est = c.get("query", 1000.0)
        print("\t", n_runs, "\t", c["id"], " - estimate = ", est)
        
        llm_id = c["id"]

        run_file_name =  f"{model_name}_{task_id}_{llm_id.replace("/", "_").replace(":", "_")}.json"
        run_path = model_runs_dir + "/"  + run_file_name
        
        suffixes = [ "", "_A", "_B", "_C"]
        useful_path = None
        for suffix in suffixes:
            suffixed_path = run_path.replace(".json", suffix + ".json")
            if not os.path.exists(suffixed_path):
                # print("Skipping ", llm_id, " - alrady have file")
                useful_path = suffixed_path
                break

        if not useful_path:
            continue

        print("Useful path = ", useful_path)

        run_single_query(model_name, task_id, llm_id, useful_path)

        n_runs += 1
        print("\t", n_runs, "\t", c["id"], " - estimate = ", est)
        total_est += est
        if n_runs >= max_runs:
            break
    end_time = time.perf_counter()

    elapsed_time = end_time - start_time
    print(f"Full run: {n_runs} runs; estimated cost = {total_est}, total time = {round(elapsed_time, 1)} seconds")

def prune_models(raw_models):
    pruned_models = []
    for raw in raw_models:
        pruned = {}
        pruned["name"] = raw["name"]
        pruned["id"] = raw["id"]
        pruned["provider"] = raw['name'].split(":", 1)[0]
        pruned["context"] = raw["context_length"]
        pruned["description"] = raw["description"]
        pruned["canonical_slug"] = raw["canonical_slug"]
        pruned["pr_prompt"] = float(raw["pricing"]["prompt"]) * 1000000
        pruned["pr_completion"] = float(raw["pricing"]["completion"]) * 1000000
        pruned["supported_parameters"] = raw["supported_parameters"]
        if "structured_outputs" in pruned["supported_parameters"]:
            pruned['structured'] = "Structured"
        else:
            pruned['structured'] = "Nope"
        if pruned["context"] < 150000:
            continue
        
        prompt_ppm = pruned["pr_prompt"]
        completion_ppm = pruned["pr_completion"]
        prompt_tokens = 80000
        completion_tokens = 20000
        # print(pruned["name"])
        # print(pruned["name"], "\t", prompt_ppm)
        # print(pruned["name"], "\t", completion_ppm)
        pruned["query_est"] = (
            prompt_tokens * prompt_ppm + completion_tokens * completion_ppm
        ) / 1000000.0
        # print("Estimate is ", pruned["query_est"])
        # print("\n")

        pruned_models.append(pruned)
    
    return pruned_models

def update_model_spread():
    from utils.util_spread import create_spread
    
    models = update_openrouter_models()
    # print(models)
    create_spread(models["data"], "ai_configs/all_models.xlsx", "OpenRouter Models")
    pruned_models = prune_models(models["data"])
    create_spread(pruned_models, "ai_configs/all_models.xlsx", "OpenRouter Pruned")

def create_run_spread(model_name):
    from utils.util_spread import create_spread

    import utils.util_all_fmk as fmk
    model_runs_dir = f"ldm/ldm_models/{model_name}/{model_name}_runs"
    spread_path = model_runs_dir + "/all_results.xlsx"
    
    runs = []
    for p in os.listdir(model_runs_dir):
        if not p.endswith("json"):
            continue
        results = fmk.read_json_file(model_runs_dir + "/" + p)
        run_capsule = results.get("run", {})
        runs.append(run_capsule)
    create_spread(runs, spread_path, "All Result")

if __name__ == "__main__":
    
    # fix to only run daily
    # update_model_spread()
    # exit(0)
    # llm_id = "qwen/qwen3-235b-a22b-2507"
    
    # run_single_query("Literate", "T01", llm_id=llm_id)
    with open("trace_parsings.txt", "a", encoding="utf-8") as parsing_file:

        run_query_suite("Literate", "T01")
    
    create_run_spread("Literate")
