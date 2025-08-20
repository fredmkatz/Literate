import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
from typing import List, Dict, Any

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
parsing_file_lock = threading.Lock()

class RateLimiter:
    """Simple rate limiter for API calls"""
    def __init__(self, calls_per_minute=60):
        self.calls_per_minute = calls_per_minute
        self.min_interval = 60.0 / calls_per_minute
        self.last_call = 0
        self.lock = threading.Lock()
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit"""
        with self.lock:
            now = time.time()
            time_since_last = now - self.last_call
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                print(f"Rate limiting: sleeping {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
            self.last_call = time.time()

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
        # print("Pruned =...")
        # print(pruned)
        # print("... end of Pruned")
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

        # print("Raw results are....")
        # print(json.dumps(raw_results, indent=2))
        raw_usage = response_dict.get("usage", {})

        (parsed_reults, parsing_notes, pruned) = parse_json_results(raw_results)
        with parsing_file_lock:
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
            # print(raw_results)

        else:
            print("Can't parse raw results:")
            # print(raw_results)

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

def run_single_query_task(args):
    """Wrapper function for concurrent execution of run_single_query"""
    model_name, task_id, llm_id, run_path, candidate_info = args
    try:
        run_single_query(model_name, task_id, llm_id, run_path)
        return {"success": True, "llm_id": llm_id, "estimate": candidate_info.get("query", 0)}
    except Exception as e:
        print(f"Error processing {llm_id}: {str(e)}")
        return {"success": False, "llm_id": llm_id, "error": str(e), "estimate": candidate_info.get("query", 0)}

def run_query_suite_concurrent(model_name, task_id, max_workers=3, delay_between_submissions=1.0):
    """
    Concurrent version of run_query_suite with throttling
    
    Args:
        model_name: Name of the model
        task_id: Task identifier
        max_workers: Maximum number of concurrent threads (default: 3)
        delay_between_submissions: Delay in seconds between query submissions (default: 1.0)
    """
    import pandas as pd
    
    max_runs = 3  # 3000
    min_est_cost = 0.00000
    max_est_cost = 0.01  # 48 for 0.15
    
    # Get the list of candidate models 
    file_path = "ai_configs/all_models.xlsx" 
    df = pd.read_excel(file_path, sheet_name="OpenRouter Pruned")
    candidates = df.to_dict('records')

    print(len(candidates), " initial candidates")
    
    candidates = cheap_enough(candidates, min_est_cost, max_est_cost)
    candidates.reverse()
    print(len(candidates), " cheap candidates", " with max cost per = ", max_est_cost, f" ({max_runs} max runs)")

    model_runs_dir = f"ldm/ldm_models/{model_name}/{model_name}_runs"
    
    # Prepare tasks for concurrent execution
    tasks = []
    for c in candidates[:max_runs]:
        llm_id = c["id"]
        run_file_name = f"{model_name}_{task_id}_{llm_id.replace('/', '_').replace(':', '_')}.json"
        run_path = model_runs_dir + "/" + run_file_name
        
        suffixes = ["", "_A", "_B", "_C"]
        useful_path = None
        for suffix in suffixes:
            suffixed_path = run_path.replace(".json", suffix + ".json")
            if not os.path.exists(suffixed_path):
                useful_path = suffixed_path
                break

        if useful_path:
            tasks.append((model_name, task_id, llm_id, useful_path, c))
    
    print(f"Prepared {len(tasks)} tasks for concurrent execution with {max_workers} workers")
    
    start_time = time.perf_counter()
    completed_tasks = 0
    total_est = 0.0
    successful_runs = 0
    failed_runs = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks with throttling
        future_to_task = {}
        for i, task in enumerate(tasks):
            if i > 0 and delay_between_submissions > 0:
                time.sleep(delay_between_submissions)
            
            future = executor.submit(run_single_query_task, task)
            future_to_task[future] = task
            print(f"Submitted task {i+1}/{len(tasks)}: {task[2]}")
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            result = future.result()
            completed_tasks += 1
            total_est += result.get("estimate", 0)
            
            if result["success"]:
                successful_runs += 1
                print(f"✓ Completed ({completed_tasks}/{len(tasks)}): {result['llm_id']} - estimate: {result['estimate']}")
            else:
                failed_runs += 1
                print(f"✗ Failed ({completed_tasks}/{len(tasks)}): {result['llm_id']} - error: {result.get('error', 'Unknown')}")
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    print(f"Concurrent run completed:")
    print(f"  Total tasks: {len(tasks)}")
    print(f"  Successful: {successful_runs}")
    print(f"  Failed: {failed_runs}")
    print(f"  Estimated cost: ${total_est:.3f}")
    print(f"  Total time: {elapsed_time:.1f} seconds")
    print(f"  Average time per task: {elapsed_time/len(tasks):.1f} seconds")

def run_query_suite_advanced(model_name, task_id, max_workers=3, calls_per_minute=30):
    """
    Advanced concurrent version with rate limiting
    
    Args:
        model_name: Name of the model
        task_id: Task identifier
        max_workers: Maximum number of concurrent threads (default: 3)
        calls_per_minute: Rate limit for API calls (default: 30)
    """
    import pandas as pd
    
    rate_limiter = RateLimiter(calls_per_minute)
    
    max_runs = 30  # 3000
    min_est_cost = 0.00000
    max_est_cost = 0.01  # 48 for 0.15
    
    # Get the list of candidate models 
    file_path = "ai_configs/all_models.xlsx" 
    df = pd.read_excel(file_path, sheet_name="OpenRouter Pruned")
    candidates = df.to_dict('records')

    print(len(candidates), " initial candidates")
    
    candidates = cheap_enough(candidates, min_est_cost, max_est_cost)
    candidates.reverse()
    print(len(candidates), " cheap candidates", " with max cost per = ", max_est_cost, f" ({max_runs} max runs)")

    model_runs_dir = f"ldm/ldm_models/{model_name}/{model_name}_runs"
    
    def run_single_query_with_rate_limit(args):
        """Enhanced wrapper with rate limiting"""
        model_name, task_id, llm_id, run_path, candidate_info = args
        try:
            rate_limiter.wait_if_needed()
            run_single_query(model_name, task_id, llm_id, run_path)
            return {"success": True, "llm_id": llm_id, "estimate": candidate_info.get("query", 0)}
        except Exception as e:
            print(f"Error processing {llm_id}: {str(e)}")
            return {"success": False, "llm_id": llm_id, "error": str(e), "estimate": candidate_info.get("query", 0)}
    
    # Prepare tasks for concurrent execution
    tasks = []
    for c in candidates[:max_runs]:
        llm_id = c["id"]
        run_file_name = f"{model_name}_{task_id}_{llm_id.replace('/', '_').replace(':', '_')}.json"
        run_path = model_runs_dir + "/" + run_file_name
        
        suffixes = ["", "_A", "_B", "_C"]
        useful_path = None
        for suffix in suffixes:
            suffixed_path = run_path.replace(".json", suffix + ".json")
            if not os.path.exists(suffixed_path):
                useful_path = suffixed_path
                break

        if useful_path:
            tasks.append((model_name, task_id, llm_id, useful_path, c))
    
    print(f"Prepared {len(tasks)} tasks for advanced concurrent execution")
    print(f"Rate limit: {calls_per_minute} calls/minute, Max workers: {max_workers}")
    
    start_time = time.perf_counter()
    completed_tasks = 0
    total_est = 0.0
    successful_runs = 0
    failed_runs = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks at once - rate limiting happens in the worker function
        futures = [executor.submit(run_single_query_with_rate_limit, task) for task in tasks]
        
        # Process completed tasks as they finish
        for future in as_completed(futures):
            result = future.result()
            completed_tasks += 1
            total_est += result.get("estimate", 0)
            
            if result["success"]:
                successful_runs += 1
                print(f"✓ Completed ({completed_tasks}/{len(tasks)}): {result['llm_id']} - estimate: {result['estimate']}")
            else:
                failed_runs += 1
                print(f"✗ Failed ({completed_tasks}/{len(tasks)}): {result['llm_id']} - error: {result.get('error', 'Unknown')}")
    
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    
    print(f"Advanced concurrent run completed:")
    print(f"  Total tasks: {len(tasks)}")
    print(f"  Successful: {successful_runs}")
    print(f"  Failed: {failed_runs}")
    print(f"  Estimated cost: ${total_est:.3f}")
    print(f"  Total time: {elapsed_time:.1f} seconds")
    print(f"  Average time per task: {elapsed_time/len(tasks):.1f} seconds")
    print(f"  Effective rate: {successful_runs/(elapsed_time/60):.1f} completions/minute")

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
    if True:
        with open("trace_parsings.txt", "a", encoding="utf-8") as parsing_file:
            
            # Choose one of the following execution modes:
            
            # Original sequential execution (default)
            # run_query_suite("Literate", "T01")
            
            # Basic concurrent execution with simple throttling
            # run_query_suite_concurrent("Literate", "T01", max_workers=3, delay_between_submissions=1.0)
            
            # Advanced concurrent execution with rate limiting
            run_query_suite_advanced("Literate", "T01", max_workers=3, calls_per_minute=30)
    
    create_run_spread("Literate")
