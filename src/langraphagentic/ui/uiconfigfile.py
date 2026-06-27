from configparser import ConfigParser
import os

class Config:
    def __init__(self, config_file=None):
        if config_file is None:
            # Dynamically resolve the absolute path relative to this file's position
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(current_dir, "uniconfigfile.ini")
            
        self.config = ConfigParser()
        # Verify if the file actually exists before reading it
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Configuration file not found at: {os.path.abspath(config_file)}")
            
        self.config.read(config_file)

    def get_llm_options(self):
        val = self.config["DEFAULT"].get("LLM_OPTIONS")
        return val.split(", ") if val else []
    
    def get_usecase_options(self):
        val = self.config["DEFAULT"].get("USECASE_OPTIONS")
        return val.split(", ") if val else []

    def get_groq_model_options(self):
        val = self.config["DEFAULT"].get("GROQ_MODEL_OPTIONS")
        return val.split(",") if val else []
    
    def get_page_title(self):
        return self.config["DEFAULT"].get("PAGE_TITLE", "Agentic Chat")