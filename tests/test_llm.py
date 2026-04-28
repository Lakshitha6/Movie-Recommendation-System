import pytest
from src.services.llm_client import get_llm, _llm_instance

@pytest.fixture(autouse=True)
def reset_singleton():
    import src.services.llm_client as llm_module
    llm_module._llm_instance = None
    yield
    llm_module._llm_instance = None


# ── Groq Tests ────────────────────────────────────────────────────────────────

def test_groq_llm_returns_response():
    llm = get_llm()
    response = llm.invoke("Say hello in one word")
    assert response.content is not None
    assert isinstance(response.content, str)
    assert len(response.content) > 0

def test_groq_llm_response_is_relevant():
    llm = get_llm()
    response = llm.invoke("What is 2 + 2? Reply with just the number.")
    assert "4" in response.content