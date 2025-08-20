from pathlib import Path
import json

from typing import Dict, Tuple
# from together import Together
# from ai_apis.class_ai_keys import FMK_Together_API
import utils.util_all_fmk as fmk

AI_CONFIGS = "ai_configs"


class AI_Assistant:
    def __init__(self, gateway, llm_id):
        # print("AI_Assistant: __init__ for ", gateway, " model = ", llm_id)
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
        return {}

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
                # print("loading ... ", file_path)
                docs[filename] = file_path.read_text(encoding="utf-8")
                size = len(docs[filename])
                # print("Loaded doc: ", file_path, ". Length is ", size)
                total_size += size
        print(
            "\tTotal size in bytes is: ",
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

    def get_api_key(self) -> str:
        import ai_apis.newkeys0808A as PartA
        import ai_apis.newkeys0808B as PartB
        
        
        parta = PartA.NewFMKClaudeKeyAug8_2025
        partb = PartB.NewFMKClaudeKeyAug8_2025

        parta = PartA.OpenRouterFMK
        partb = PartB.OpenRouterFMK

        full_key = parta + partb
        # print("Full key is: ", full_key)
        return full_key
    # returns parsed results and calculated usage
    def run_query(self, query) -> dict:
        import time
        full_query = self.persistent_context + query
        n_bytes_sent = len(full_query)

        # print(f"in run_query calling run_query_native")
        # print(f"run_query_native method: {self.run_query_native}")
        # print(f"Self class: {self.__class__}")
        # print(f"Self module: {self.__class__.__module__}")
        # get raw response, and raw  usage

        start_time = time.perf_counter()
        response_dict = self.run_query_native(full_query)
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        print(f"Elapsed time: {elapsed_time:.4f} seconds")



        return response_dict

    def calc_costs(self, raw_usage):
        # print("calc_costs()...")
        # print("\tRaw usage = ", raw_usage)

        bytes_per_token = 4.0
        prompt_ppm = self.llm_params["prompt_ppm"]
        completion_ppm = self.llm_params["completion_ppm"]
        context_length = self.llm_params["context_length"]

        costs = {}

        if raw_usage.keys():
            prompt_tokens = raw_usage["prompt_tokens"]
            completion_tokens = raw_usage["completion_tokens"]
        else:
            return 0.0
        
        costs = (
            prompt_tokens * prompt_ppm + completion_tokens * completion_ppm
        ) / 1000000.0
        return costs

    def run_query_native(self, full_query):
        pass


    def standing_prompt(self, docs_dict, iniial_message):

        return f"""{iniial_message} 

    ## Reference Documents:
    {self.docs_dict_as_text(docs_dict=docs_dict)}
    """

