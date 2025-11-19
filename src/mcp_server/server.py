import os
import math
import time
import pyautogui
import pywinauto
from typing import Dict, Any, Callable, List

class LocalMCPServer:
    """
    Implements a local Model Context Protocol (MCP) server.
    Handles tool definitions and execution.
    """
    def __init__(self):
        self.tools: Dict[str, Callable] = {
            "write_file": self.write_file,
            "calculate": self.calculate,
            "execute_python": self.execute_python,
            "task_complete": self.task_complete
        }

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns the schema of available tools for the Agent."""
        return [
            {
                "name": "write_file",
                "description": "Writes text content to a specific file path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "content": {"type": "string", "description": "Text content"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "calculate",
                "description": "Evaluates a mathematical expression safely.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression (e.g., '25 * 4')"}
                    },
                    "required": ["expression"]
                }
            },
            {
                "name": "execute_python",
                "description": "Executes Python code to interact with the GUI (pyautogui, pywinauto).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Python code using pyautogui/pywinauto"}
                    },
                    "required": ["code"]
                }
            },
            {
                "name": "task_complete",
                "description": "Signals that the user's goal has been achieved.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "result": {"type": "string", "description": "Summary of the result"}
                    },
                    "required": ["result"]
                }
            }
        ]

    def execute_tool(self, name: str, params: Dict[str, Any]) -> str:
        """Executes a tool by name with provided parameters."""
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        
        try:
            return self.tools[name](**params)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"

    # --- Tools Implementation ---

    def write_file(self, path: str, content: str) -> str:
        try:
            # Ensure directory exists
            directory = os.path.dirname(path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Success: File written to {path}"
        except Exception as e:
            raise e

    def calculate(self, expression: str) -> str:
        # Security: Limit scope of eval
        allowed_names = {"abs": abs, "round": round, "math": math}
        try:
            result = eval(expression, {"__builtins__": None}, allowed_names)
            return str(result)
        except Exception as e:
            return f"Calculation Error: {e}"

    def execute_python(self, code: str) -> str:
        """Executes GUI automation code."""
        print(f"\n[EXECUTING GUI CODE]:\n{code}\n")
        try:
            # Define a limited safe environment, but allow GUI libs
            exec_globals = {
                "pyautogui": pyautogui,
                "pywinauto": pywinauto,
                "time": time,
                "print": print
            }
            exec(code, exec_globals)
            return "Success: Code executed."
        except Exception as e:
            return f"Execution Error: {e}"

    def task_complete(self, result: str) -> str:
        return f"TASK_COMPLETE: {result}"

