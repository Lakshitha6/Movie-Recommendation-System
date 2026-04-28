import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils import get_config

load_dotenv()

_llm_instance = None


def get_llm():
    global _llm_instance

    if _llm_instance is None:
        config = get_config()
        provider = config.get("llm.active_provider")
        llm_config = config.active_llm_config

        if provider == "groq":
            api_key = os.getenv("GROQ_API")
            if not api_key:
                raise ValueError("GROQ_API is not set in your .env file")

            _llm_instance = ChatGroq(
                api_key=api_key,
                model=llm_config["model"],
                temperature=llm_config["temperature"],
                max_tokens=llm_config["max_tokens"],
                timeout=llm_config["timeout"],
            )

        elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not set in your .env file")

            _llm_instance = ChatGoogleGenerativeAI(
                google_api_key=api_key,
                model=llm_config["model"],
                temperature=llm_config["temperature"],
                max_tokens=llm_config["max_tokens"],
                timeout=llm_config["timeout"],
            )

        else:
            raise ValueError(f"Unsupported LLM provider: '{provider}'. Choose 'groq' or 'gemini' in settings.yaml")

    return _llm_instance