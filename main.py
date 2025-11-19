import sys
from src.utils.config import Config
from src.perception.perceiver import Perceiver
from src.memory.manager import MemoryManager
from src.mcp_server.server import LocalMCPServer
from src.agent.core import VilAgent

def main():
    print("Başlatılıyor: VILAGENT - GUI Otomasyon Sürümü")
    
    # Validate configuration
    Config.validate()

    # Initialize Components
    try:
        print("Initializing Perception Module (Screenshot/Vision)...")
        perceiver = Perceiver()
        
        print("Initializing Memory Manager (Pinecone)...")
        memory = MemoryManager()
        
        print("Initializing Local MCP Server (GUI Tools)...")
        mcp_server = LocalMCPServer()
        
        print("Initializing Agent Core (Gemini 2.0 Flash Multimodal)...")
        agent = VilAgent(perceiver, memory, mcp_server)
        
    except Exception as e:
        print(f"Initialization Error: {e}")
        sys.exit(1)

    # Get Task from User
    if len(sys.argv) > 1:
        # python main.py "Gorev buraya"
        task = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        print("\n" + "="*50)
        task = input("Lütfen bir görev girin (Örn: Not defterini aç): ")
        print("="*50 + "\n")

    if not task.strip():
        print("Boş görev girildi. Çıkılıyor.")
        sys.exit(0)
    
    print(f"\nAtanan Görev: {task}")
    print("UYARI: Ajan farenizi ve klavyenizi kontrol edecek. Lutfen mudahale etmeyin.")
    print("Cikmak icin CTRL+C yapabilirsiniz.")
    print("-" * 50)
    
    # Run Agent
    agent.run(task)

if __name__ == "__main__":
    main()
