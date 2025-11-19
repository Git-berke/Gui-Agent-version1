import uuid
import google.generativeai as genai
from pinecone import Pinecone, ServerlessSpec
from typing import List, Dict, Any, Optional
from src.utils.config import Config

class MemoryManager:
    def __init__(self):
        self.api_key = Config.PINECONE_API_KEY
        self.index_name = Config.PINECONE_INDEX_NAME
        self.gemini_key = Config.GEMINI_API_KEY
        
        self.pc = None
        self.index = None
        
        if self.api_key:
            self.pc = Pinecone(api_key=self.api_key)
            
            # Use Host URL if available (recommended for Serverless)
            if Config.PINECONE_HOST:
                self.index = self.pc.Index(host=Config.PINECONE_HOST)
            else:
                # Fallback to name-based connection (checks existence)
                existing_indexes = [i.name for i in self.pc.list_indexes()]
                if self.index_name not in existing_indexes:
                    try:
                        self.pc.create_index(
                            name=self.index_name,
                            dimension=768, # Dimension for text-embedding-004
                            metric='cosine',
                            spec=ServerlessSpec(cloud='aws', region='us-east-1')
                        )
                    except Exception as e:
                        print(f"Index creation skipped/failed (might be mock mode): {e}")
                
                self.index = self.pc.Index(self.index_name)

        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)

    def _get_embedding(self, text: str) -> List[float]:
        """Generates embedding using Gemini."""
        if not self.gemini_key:
            return [0.0] * 768 # Mock embedding
            
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return result['embedding']

    def upsert_experience(self, goal: str, steps: List[str], result: str):
        """Saves a successful task execution to Pinecone."""
        if not self.index:
            print("Warning: Memory disabled (No Pinecone Key)")
            return

        content_to_embed = f"Goal: {goal} | Result: {result}"
        vector = self._get_embedding(content_to_embed)
        
        metadata = {
            "goal": goal,
            "steps": str(steps),
            "result": result
        }
        
        self.index.upsert(vectors=[
            {
                "id": str(uuid.uuid4()),
                "values": vector,
                "metadata": metadata
            }
        ])
        print(f"Memory: Experience saved for goal '{goal}'")

    def retrieve_relevant_experience(self, query: str, top_k: int = 3, min_score: float = 0.7) -> List[str]:
        """Retrieves relevant past experiences based on the current goal."""
        if not self.index:
            return []

        vector = self._get_embedding(query)
        
        try:
            results = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
            experiences = []
            for match in results['matches']:
                if match['score'] >= min_score:
                    meta = match['metadata']
                    experiences.append(f"Past Goal: {meta.get('goal')} -> Result: {meta.get('result')} (Score: {match['score']:.2f})")
            return experiences
        except Exception as e:
            print(f"Memory Retrieval Error: {e}")
            return []

