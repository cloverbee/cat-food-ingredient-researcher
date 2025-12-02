import os
from llama_index.core import Settings
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding
from src.core.config import settings

def configure_llama_index():
    # Set GOOGLE_API_KEY environment variable for Gemini SDK
    os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
    
    # Configure LLM - using gemini-2.5-flash (fast and cost-effective)
    Settings.llm = Gemini(
        model="models/gemini-2.5-flash",
        api_key=settings.GEMINI_API_KEY
    )
    
    # Configure Embedding Model
    Settings.embed_model = GeminiEmbedding(
        model="models/text-embedding-004",
        api_key=settings.GEMINI_API_KEY
    )

    # Chunk Size (optional, can tune later)
    Settings.chunk_size = 512
