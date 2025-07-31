class AI_Assistant():
    def __new__(cls, gateway, llm_id):
        if gateway == "Together":
            instance = super().__new__(TogetherAssistant)  # Corrected line
            return instance 
        else:
            print("Only gateway now is Together")
            return None

    def __init__(self, gateway, llm_id):
        self.gateway = gateway
        self.client = None
        self.llm_params = self.get_llm_params(llm_id)
        self.docs_dict = None
        self.persistent_context = None


class TogetherAssistant(AI_Assistant):
    
    def __init__(self, gateway, llm_id):
        super().__init__(gateway, llm_id=llm_id)
        self.client = Together(api_key=FMK_Together_API) 
