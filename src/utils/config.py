import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENV = os.getenv("PINECONE_ENV", "gcp-starter")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "vilagent-memory")
    PINECONE_HOST = os.getenv("PINECONE_HOST") # Added support for Host URL

    @staticmethod
    def validate():
        """Validates that essential environment variables are set."""
        missing = []
        if not Config.GEMINI_API_KEY:
            missing.append("GEMINI_API_KEY")
        if not Config.PINECONE_API_KEY:
            missing.append("PINECONE_API_KEY")
        
        if missing:
            print(f"Warning: Missing environment variables: {', '.join(missing)}. Functionality will be limited.")
