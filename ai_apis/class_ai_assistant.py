from pathlib import Path
import json

from typing import Dict, Tuple
from together import Together
from ai_apis.class_ai_keys import FMK_Together_API
import utils.util_all_fmk as fmk

AI_CONFIGS = "ai_configs"


class AI_Assistant:
    def __new__(cls, gateway, llm_id):
        if gateway == "Together":
            instance = super().__new__(TogetherAssistant)
            return instance
        elif gateway == "OpenRouter":
            from ai_apis.class_ai_openrouter import OpenRouterAssistant

            instance = super().__new__(OpenRouterAssistant)
            return instance

        else:
            print("Only gateway now is Together")
            return None

    def __init__(self, gateway, llm_id):
        self.gateway = gateway
        self.llm_id = llm_id
        self.client = None
        self.llm_params = {}
        try:
            self.llm_params = self.get_llm_params(llm_id)
        except Exception:
            print(f"Can't get llm_parameters for {llm_id}, yet")
        self.docs_dict = None
        self.persistent_context = None

    def get_llm_params(self, llm_id) -> dict:
        pass

    def prepare(self, docs_dir, doc_files, initial_message):
        self.docs_dict = self.create_docs_dict(docs_dir=docs_dir, doc_files=doc_files)
        self.persistent_context = self.standing_prompt(self.docs_dict, initial_message)

    def create_docs_dict(self, docs_dir: Path, doc_files) -> Dict[str, str]:
        """Load all reference documents"""
        docs = {}
        total_size = 0
        for filename in doc_files:
            file_path = Path(docs_dir) / filename
            if file_path.exists():
                print("loading ... ", file_path)
                docs[filename] = file_path.read_text(encoding="utf-8")
                size = len(docs[filename])
                print("Loading doc: ", filename, ". Length is ", size)
                total_size += size
        print(
            "Total size in bytes is: ",
            total_size,
            " = about ",
            total_size / 4,
            " tokens",
        )
        return docs

    def docs_dict_as_text(self, docs_dict) -> str:
        """Create the persistent system prompt"""
        doc_context = "\n\n".join(
            [
                f"<document name='{name}'>\n{content}\n</document>"
                for name, content in docs_dict.items()
            ]
        )
        return doc_context

    # returns parsed results and calculated usage
    def run_query(self, query) -> Tuple[dict, dict]:
        full_query = self.persistent_context + query
        n_bytes_sent = len(full_query)

        # get raw response, and raw  usage
        (raw_results, raw_usage) = self.run_query_native(full_query)

        # print(response.choices[0].message.content)
        # print(response)
        n_bytes_received = len(str(raw_results))

        costs = self.calc_costs(raw_usage, n_bytes_sent, n_bytes_received)

        results = self.parse_json_results(raw_results=raw_results)

        return (costs, results)

    def calc_costs(self, raw_usage, n_bytes_sent, n_bytes_received):
        print("\nUSAGE:")
        print(raw_usage)

        usage = raw_usage
        bytes_per_token = 4.0
        prompt_ppm = self.llm_params["prompt_ppm"]
        completion_ppm = self.llm_params["completion_ppm"]
        context_length = self.llm_params["context_length"]

        costs = {}
        prompt_tokens = usage["prompt_tokens"]
        completion_tokens = usage["completion_tokens"]
        costs["bytes_per_token_assumed"] = bytes_per_token
        costs["bytes_sent"] = n_bytes_sent
        costs["est_tokens_sent"] = n_bytes_sent / bytes_per_token
        costs["prompt_tokens"] = prompt_tokens

        costs["bytes_received"] = n_bytes_received
        costs["est_completion_tokens"] = n_bytes_received / bytes_per_token
        costs["completion_tokens"] = completion_tokens
        costs["total_cost"] = (
            prompt_tokens * prompt_ppm + completion_tokens * completion_ppm
        ) / 1000000.0
        costs["max_context"] = context_length
        print(json.dumps(costs, indent=2))

    def run_query_native(self, full_query):
        pass

    def parse_json_results(self, raw_results: str):
        pruned = raw_results.replace("```json", "")
        pruned = pruned.replace("```", "")
        if pruned != raw_results:
            print("PRUNING NEEDED")

        try:
            jresults = json.loads(pruned)

            print(json.dumps(jresults, indent=2))
            return jresults
        except Exception:
            print("Parsing failed")
            return {}

    def standing_prompt(self, docs_dict, iniial_message):

        return f"""{iniial_message} 

    ## Reference Documents:
    {self.docs_dict_as_text(docs_dict=docs_dict)}
    """


class TogetherAssistant(AI_Assistant):

    def __init__(self, gateway, llm_id):
        super().__init__(gateway, llm_id=llm_id)
        self.client = Together(
            api_key=FMK_Together_API
        )  # auth defaults to os.environ.get("TOGETHER_API_KEY")

    def get_llm_params(self, llm_id) -> dict:
        llm_details = self.get_together_llm(llm_id)
        return {
            "prompt_ppm": llm_details["pricing"]["input"],
            "completion_ppm": llm_details["pricing"]["output"],
            "context_length": llm_details["context_length"],
        }

    def get_together_llm(self, llm_id) -> dict:

        together_models = fmk.read_json_file(f"{AI_CONFIGS}/together_models.json")
        return together_models[llm_id]

    def run_query_native(self, full_query):
        response = self.client.chat.completions.create(
            model=self.llm_id, messages=[{"role": "user", "content": full_query}]
        )
        raw_results = response.choices[0].message.content
        raw_usage = response.usage
        return (raw_results, raw_usage)


# Not in Class
def update_together_models():
    client = Together(
        api_key=FMK_Together_API
    )  # auth defaults to os.environ.get("TOGETHER_API_KEY")
    models = client.models.list()
    # print(type(models), " is type")
    # Convert each ModelObject to a dictionary using model_dump()
    model_dicts = [model.model_dump() for model in models]
    models_dict = {m["id"]: m for m in model_dicts}
    # print(json.dumps(models_dict, indent=2))
    fmk.write_json(models_dict, f"{AI_CONFIGS}/together_models.json")
    print(f"Together models saved in: {AI_CONFIGS}/together_models.json")
