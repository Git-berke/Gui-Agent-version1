import yaml
from typing import Dict, Any
import os

class PromptLoader:
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """
        Loads a YAML file from the given path safely.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt file not found at: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML file {file_path}: {e}")

    @staticmethod
    def get_system_prompt(prompts_dir: str = "prompts") -> str:
        """
        Loads and constructs the full system prompt from system.yaml.
        """
        system_path = os.path.join(prompts_dir, "system.yaml")
        data = PromptLoader.load_yaml(system_path)
        
        identity = data.get("identity", "")
        strategies = data.get("strategies", "")
        output_format = data.get("output_format", "")
        
        return f"{identity}\n\nSTRATEJİLER VE İPUÇLARI:\n{strategies}\n\nKURALLAR VE FORMAT:\n{output_format}"

