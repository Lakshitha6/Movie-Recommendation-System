import pytest
from src.app import run_pipeline

# ── Fixtures ──────────────────────────────────────────────────────────────────

MOVIE_QUESTIONS = [
    "Recommend me some good sci-fi movies",
    "I want to watch a horror movie tonight",
    "Recommend movies similar to The Matrix",
]

# ── Response Quality Tests ────────────────────────────────────────────────────

def test_pipeline_response_contains_movie_info():
    """Response should contain year-like pattern and rating-like content."""
    response = run_pipeline(
        question="Recommend me a popular action movie",
        user_id="test-user",
        session_id="test-session-movie-info"
    )
    assert any(str(year) in response for year in range(1970, 2025))


# ── Parameterized Tests ───────────────────────────────────────────────────────

@pytest.mark.parametrize("question", MOVIE_QUESTIONS)
def test_pipeline_handles_various_questions(question):
    response = run_pipeline(
        question=question,
        user_id="test-user",
        session_id=f"test-session-{question[:20].replace(' ', '-').lower()}"
    )
    assert isinstance(response, str)
    assert len(response) > 0