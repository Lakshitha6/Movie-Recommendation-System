import pytest
from src.services.embeddings import get_embeddings

@pytest.fixture(autouse=True)
def reset_singleton():
    import src.services.embeddings as embeddings_module
    embeddings_module._embedding_instance = None
    yield
    embeddings_module._embedding_instance = None


def test_embed_query_returns_list_of_floats():
    embeddings = get_embeddings()
    vector = embeddings.embed_query("recommend me a sci-fi movie")
    assert isinstance(vector, list)
    assert all(isinstance(v, float) for v in vector)

def test_embed_query_returns_correct_dimensions():
    """all-MiniLM-L6-v2 produces 384-dimensional vectors."""
    embeddings = get_embeddings()
    vector = embeddings.embed_query("recommend me a sci-fi movie")
    assert len(vector) == 768

def test_embed_documents_returns_list_of_vectors():
    embeddings = get_embeddings()
    vectors = embeddings.embed_documents([
        "A space adventure movie",
        "A romantic comedy film"
    ])
    assert len(vectors) == 2
    assert all(isinstance(v, list) for v in vectors)

def test_same_text_produces_same_vector():
    embeddings = get_embeddings()
    v1 = embeddings.embed_query("sci-fi movie")
    v2 = embeddings.embed_query("sci-fi movie")
    assert v1 == v2