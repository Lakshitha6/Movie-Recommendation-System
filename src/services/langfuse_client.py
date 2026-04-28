# src/services/langfuse_client.py

import os
from dotenv import load_dotenv
from langfuse.langchain import CallbackHandler

load_dotenv()

_langfuse_handler = None

def get_langfuse_handler() -> CallbackHandler:
    global _langfuse_handler

    if _langfuse_handler is None:
        if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
            raise ValueError("LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY must be set in .env")

        # v4 reads keys from env automatically
        _langfuse_handler = CallbackHandler()

    return _langfuse_handler