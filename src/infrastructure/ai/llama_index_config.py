from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from src.core.config import settings

def configure_llama_index():
    # Configure LLM
    Settings.llm = OpenAI(
        model="gpt-4o",
        temperature=0.1,
        api_key=settings.OPENAI_API_KEY
    )
    
    # Configure Embedding Model
    Settings.embed_model = OpenAIEmbedding(
        model="text-embedding-3-small",
        api_key=settings.OPENAI_API_KEY
    )

    # Chunk Size (optional, can tune later)
    Settings.chunk_size = 512
