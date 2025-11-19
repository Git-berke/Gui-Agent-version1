import json
import time
import google.generativeai as genai
from typing import List, Dict, Any
from src.utils.config import Config
from src.utils.prompt_loader import PromptLoader
from src.perception.perceiver import Perceiver
from src.memory.manager import MemoryManager
from src.mcp_server.server import LocalMCPServer

class VilAgent:
    def __init__(self, 
                 perceiver: Perceiver, 
                 memory: MemoryManager, 
                 mcp_server: LocalMCPServer):
        
        self.perceiver = perceiver
        self.memory = memory
        self.mcp = mcp_server
        self.system_prompt = PromptLoader.get_system_prompt()
        
        # Configure Gemini
        if Config.GEMINI_API_KEY:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',  # Multimodal Model
                generation_config={"response_mime_type": "application/json"}
            )
        else:
            self.model = None
            print("Warning: Gemini API Key missing. Agent will fail to think.")

    def run(self, goal: str, max_steps: int = 10):
        """
        Main ReAct Loop: Observe -> Recall -> Think -> Act -> Learn
        """
        print(f"\n--- VILAGENT STARTED: {goal} ---\n")
        
        history: List[str] = []
        steps_taken: List[str] = []
        
        for step in range(max_steps):
            print(f"Step {step + 1}/{max_steps}")
            
            # 1. Observe (Multimodal)
            # IMPORTANT: For 429 Error (Rate Limit), we can choose to skip the image 
            # if not strictly necessary, OR wait. 
            # For this prototype, let's wait a bit to be nice to the free tier.
            time.sleep(2) 
            
            perception_data = self.perceiver.analyze_screen()
            screen_image = perception_data.get("image") # PIL Image or None
            
            # 2. Recall (Score > 0.7 is handled in MemoryManager)
            past_experiences = self.memory.retrieve_relevant_experience(goal)
            
            # 3. Think
            tools_schema = self.mcp.list_tools()
            
            prompt_text = self._construct_prompt(
                goal=goal,
                history=history,
                context=past_experiences,
                tools=tools_schema
            )
            
            try:
                # Send Image + Text to Gemini
                inputs = [prompt_text]
                if screen_image:
                    # Resize image to reduce token usage/load
                    try:
                        screen_image.thumbnail((1024, 1024))
                        inputs.append(screen_image)
                    except Exception as e:
                        print(f"Image processing error: {e}")
                
                response = self.model.generate_content(inputs)
                response_text = response.text
                
                # Strict JSON Parsing
                try:
                    decision = json.loads(response_text)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON response: {response_text}")
                    continue

                thought = decision.get("thought", "No thought provided")
                action = decision.get("action", {})
                
                print(f"  Thought: {thought}")
                print(f"  Action: {action}")

                # 4. Act
                tool_name = action.get("tool_name")
                tool_params = action.get("parameters", {})
                
                if not tool_name:
                    print("  No tool selected.")
                    continue

                result = self.mcp.execute_tool(tool_name, tool_params)
                print(f"  Result: {result}")
                
                # Update History
                history.append(f"Step {step+1}: Thought: {thought} | Action: {tool_name} | Result: {result}")
                steps_taken.append(f"Used {tool_name}")

                # 5. Learn (Check for completion)
                if tool_name == "task_complete" or "TASK_COMPLETE" in str(result):
                    print("\n--- TASK COMPLETED SUCCESSFULLY ---")
                    # Upsert to memory
                    final_result = tool_params.get("result", "Completed")
                    self.memory.upsert_experience(goal, steps_taken, final_result)
                    return

            except Exception as e:
                print(f"Critical Agent Error: {e}")
                # Simple exponential backoff for rate limits could be added here
                if "429" in str(e):
                    print("Rate limit hit. Waiting 10 seconds...")
                    time.sleep(10)
                else:
                    break

    def _construct_prompt(self, goal, history, context, tools) -> str:
        """Constructs the prompt for Gemini."""
        
        history_str = "\n".join(history) if history else "Henüz bir adım atılmadı."
        context_str = "\n".join(context) if context else "Benzer geçmiş deneyim yok."
        
        return f"""
{self.system_prompt}

MEVCUT HEDEF: {goal}

MEVCUT ARAÇLAR (Tools):
{json.dumps(tools, indent=2)}

EKRAN GÖRÜNTÜSÜ:
Ekteki resim mevcut ekran durumudur. UI elementlerini görsel olarak analiz et.
Eğer 'execute_python' kullanacaksan, pyautogui veya pywinauto kodlarını ekran koordinatlarına veya görünen öğelere göre üret.

HAFIZA (RAG - Benzer Deneyimler, Skor > 0.7):
{context_str}

GÖREV GEÇMİŞİ (History):
{history_str}

Şimdi düşün ve bir sonraki JSON çıktısını üret.
"""
