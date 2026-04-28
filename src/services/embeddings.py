from langchain_huggingface import HuggingFaceEndpointEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

_embedding_instance = None

def get_embeddings() -> HuggingFaceEndpointEmbeddings:
    global _embedding_instance

    if _embedding_instance is None:
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN is not set in your .env file")

        _embedding_instance = HuggingFaceEndpointEmbeddings(
            repo_id="sentence-transformers/all-mpnet-base-v2",
            huggingfacehub_api_token=hf_token
        )
    return _embedding_instance