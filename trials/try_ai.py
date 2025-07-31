import json


from ai_apis.class_ai_assistant import AI_Assistant
from ai_apis.class_ai_openrouter import get_openrouter_models, update_openrouter_models


def run_quick_query(query="Please review the attached model"):
    gateway = "Together"
    llm_id = "Qwen/Qwen3-235B-A22B-Instruct-2507-tput"
    
    gateway = "OpenRouter"
    llm_id = "openrouter/auto"
    
    # llm_id = "google/gemini-flash-1.5-8b"   # $.05 1M
    llm_id = "qwen/qwen3-235b-a22b-2507:free"   #  $0, 260K
    
    llm_id = "deepseek/deepseek-chat-v3-0324"   #   $0.50  164K

    initial_message = (
        "You are an AI assistant specialized in improving Literate Data Models (LDMs)."
    )

    docs_dir = "ai_docs"
    doc_files = [
        "LiterateMetaModel_01_PD_schema.yaml",
        "ReviewingLDM_v0_1.md",
        # Model comes last here - least persistent
        # "Literate_sample.json",
        "Literate_PD_04.v_model.json"
    ]

    assistant = AI_Assistant(gateway, llm_id)
    assistant.prepare(
        docs_dir=docs_dir, doc_files=doc_files, initial_message=initial_message
    )
    (costs, results) = assistant.run_query(query)
    print("Costs are: ", costs)
    print("results are: ", results)
    print("Costs are: ", costs)

    return (costs, results)


if __name__ == "__main__":
    # models = get_openrouter_models()
    # print(json.dumps(models, indent = 2))
    
    # update_openrouter_models()

    # show_models()
    # exit(0)
    (usage, results) = run_quick_query()
    print(json.dumps(usage, indent=2))
    print("\nParsed results are: ")
    print(json.dumps(results, indent=2))
