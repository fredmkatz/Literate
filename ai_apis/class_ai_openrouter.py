from openai import OpenAI  # OpenRouter is compatible with the OpenAI SDK
import os  # For environment variables

from ai_apis.class_ai_assistant import AI_Assistant, AI_CONFIGS
from ai_apis.class_ai_keys import FMK_OpenRouter_API
import utils.util_all_fmk as fmk


class OpenRouterAssistant(AI_Assistant):  # Changed class name for clarity

    def __init__(self, gateway, llm_id):
        super().__init__(gateway, llm_id=llm_id)
        
        self.or_model = None
        self.or_generation_id = None
        self.or_usage = None
        self.or_object = None
        self.llm_used = None
        self.api_key = FMK_OpenRouter_API
        
        # OpenRouter uses the OpenAI SDK, but needs a different base_url and API key
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=FMK_OpenRouter_API,
            # Optional: Add default_headers for attribution on OpenRouter leaderboards
            # default_headers={
            #     "HTTP-Referer": "https://your-app-domain.com/",  # Replace with your app's domain
            #     "X-Title": "Your App Name",  # Replace with your app's name
            # },
        )
        print("OR client is ", self.client)

    def get_openrouter_llm(self, llm_id) -> dict:

        or_models = fmk.read_json_file(f"{AI_CONFIGS}/openrouter_models.json")
        return or_models.get(llm_id)


    def run_query_native_original(self, full_query):
        response = self.client.chat.completions.create(
            model=self.llm_id,

            messages=[{"role": "user", "content": full_query}],
            # usage =  {"include": True},
            extra_headers={
                "HTTP-Referer": "https://localhost:3000",
                "X-Title": "Literate Modeling",       # Optional but recommended
            }

        )
        
      
        print("OR Response is: ")
        display_returned_object(response)
        print("End of OR Response")
        
        self.or_generation_id = response.id
        self.or_model = response.model
        self.or_object = response.object
        self.or_usage = response.usage
        
        
        print("Query id = ", self.or_generation_id)
        print("Model = ", self.or_model)
        print("OR object = ", self.or_object)
        print("OR usage = ", self.or_usage)
        
        self.llm_used = self.or_model
        llm_details = self.get_llm_params(self.llm_used)
        print("params for ", self.or_model)
        print(json.dumps(llm_details, indent=2))
        raw_results = response.choices[0].message.content
        raw_usage = response.usage
        return (raw_results, raw_usage)
    
    def run_query_native(self, full_query):
        

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
        "Authorization": f"Bearer {self.api_key}",
        "Content-Type": "application/json"
        }
        payload = {
        "model": self.llm_id,
        "messages": [
            {
            "role": "user",
            "content": full_query
            }
        ],
        
        #   Waiiing to see if these are worth supporting with arguments
        "temperature": 1,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        
        ## Can't really use this - keep getting "No enppoints match"
        # "usage": {
        #     "include": True
        # },

        # "provider": {
        #     "allow_fallbacks": False,
        #     "max_price": {
        #         "prompt": 0.5,
        #         "completion": 0.5
        #     }
        # }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print("Response from new native....")
        print("type of response is ", type(response))
        response_dict = response.json()
        print("type of response.json() is ", type(response.json()))
        print(json.dumps(response_dict, indent=2))     
        
      
        # print("OR Response is: ")
        # display_returned_object(response)
        # print("End of OR Response")
        
        self.or_generation_id = response_dict["id"]
        self.or_model = response_dict["model"]
        self.or_object = response_dict["object"]
        self.or_usage = response_dict["usage"]
        
        
        print("Query id = ", self.or_generation_id)
        print("Model = ", self.or_model)
        print("OR object = ", self.or_object)
        print("OR usage = ", self.or_usage)
        
        self.llm_used = self.or_model
        llm_details = self.get_llm_params(self.llm_used)
        print("params for ", self.or_model)
        print(json.dumps(llm_details, indent=2))
        raw_results = response_dict["choices"][0]["message"]["content"]
        raw_usage = response_dict["usage"]
        print("Raw usagge is ", raw_usage)
        return (raw_results, raw_usage)

                
        
    def get_llm_params(self, llm_id) -> dict:
        or_details = self.get_openrouter_llm(llm_id)
        print("details for model ", llm_id)
        print(json.dumps(or_details, indent=2))

        return {
            "prompt_ppm": float(or_details["pricing"]["prompt"]) * 1000000.,
            "completion_ppm": float(or_details["pricing"]["completion"])  * 1000000.,
            "context_length": or_details["context_length"]  ,
        }

    
import json
def display_returned_object(obj):
    odict = obj.model_dump()
    print(json.dumps(odict, indent = 2))
    
    

import requests
import json

# The OpenRouter API endpoint for models
OPENROUTER_MODELS_URL = "https://openrouter.ai/api/v1/models"

def get_openrouter_models():
    """
    Fetches all available models from OpenRouter and returns them as a JSON object.
    """
    try:
        response = requests.get(OPENROUTER_MODELS_URL)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        models_data = response.json()
        return models_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching models from OpenRouter: {e}")
        return None


def update_openrouter_models():
    models = get_openrouter_models()
    fmk.write_json(models["data"], f"{AI_CONFIGS}/openrouter_models_raw.json")

    # print(type(models), " is type")
    # Convert each ModelObject to a dictionary using model_dump()
    model_dicts = models["data"]
    models_dict = {m["id"]: m for m in model_dicts}
    # print(json.dumps(models_dict, indent=2))
    fmk.write_json(models_dict, f"{AI_CONFIGS}/openrouter_models.json")
    print(f"OpenRouter models saved in: {AI_CONFIGS}/openrouter_models.json")


# Tier 1
#  Claude recommendations
#     **Tier 1: Start Here (Minimal Dev Effort)**

# - **GPT-4o-mini** - Your current setup, great baseline for structured JSON, excellent cost/performance
#       openai/gpt-4.1-mini  $1, 1Million

# - **GPT-4o** - When you need maximum reasoning quality, same API
#       openai/gpt-4.1 - $4, 1M tokens

# - **Claude 3.5 Sonnet** - Worth the API switch, exceptional at structured output and reasoning
#       anthropic/claude-sonnet-4  $8, 200K

# **Tier 2: Easy Additions (OpenAI-Compatible)**

# - **Llama 3.1 70B** (via TogetherAI) - Strong reasoning, much cheaper, test open model viability
#       meta-llama/llama-3.3-70b-instruct  $0.20 131K

# - **Qwen2.5 72B** (via TogetherAI) - Excellent structured output, competitive reasoning
#       qwen/qwen3-235b-a22b-2507:free  $0, 260K

# - **Gemma 2 27B** (via TogetherAI) - Good balance of capability/cost
#       google/gemma-3-12b-it:free  $0, 96K

# **Tier 3: Worth Custom Integration If Promising**

# - **Claude 3.5 Haiku** - Ultra-fast, surprisingly capable for structured tasks, very cost-effective
#       anthropic/claude-3.5-haiku  $2, 200K

# - **Gemini 1.5 Flash** - Strong reasoning, good structured output, competitive pricing
#       google/gemini-flash-1.5-8b  $.05  1M

# - **DeepSeek V3** - Emerging strong performer, very cost-effective
#   deepseek/deepseek-chat-v3-0324  $0.50  164K

