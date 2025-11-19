from typing import List, Dict, Any
import pyautogui
from PIL import Image

class Perceiver:
    """
    Responsible for perceiving the environment (Screen).
    Captures screenshots for the VLM to analyze.
    """
    
    def __init__(self):
        pass

    def analyze_screen(self) -> Dict[str, Any]:
        """
        Captures a screenshot. 
        Returns a dictionary containing the image object (for Gemini) and detected elements (mock for now).
        """
        try:
            screenshot = pyautogui.screenshot()
            # In a full OmniParser setup, we would run the model here.
            # For now, we pass the raw image to Gemini 2.0 Flash (Visual LLM).
            return {
                "image": screenshot,
                "description": "Screenshot captured. Use this visual context to identify UI elements."
            }
        except Exception as e:
            print(f"Perception Error: {e}")
            return {"image": None, "error": str(e)}
