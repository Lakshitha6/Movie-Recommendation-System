# src/app/main_pipeline.py

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda

from src.schemas import QueryExtract
from src.services import get_llm, get_langfuse_handler
from src.utils import vector_search, kg_search, format_movie

from typing import Generator

# ── Prompts ───────────────────────────────────────────────────────────────────

EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert at understanding movie search queries.
    Extract the following from the user's question:
    - actor: a specific actor name if mentioned
    - director: a specific director name if mentioned
    - genre: a specific genre if mentioned (e.g. Action, Drama, Horror)
    - semantic_query: the core movie theme/plot intent for semantic search

    If something is not mentioned, return null for that field."""),
    ("human", "{question}")
])

FINAL_PROMPT = ChatPromptTemplate.from_template("""
You are a knowledgeable movie recommendation assistant.

Use the context below to answer the user's question.
- Prefer movies that strongly match the theme or explicit filters.
- Include year, rating, and a brief reason why each movie fits.
- If a movie appears in both Structured and Semantic results, prioritise it.
- Be specific — avoid vague answers.

Context:
{context}

Question: {question}

Answer:
""")

# ── Chains ────────────────────────────────────────────────────────────────────

def _build_extraction_chain():
    llm = get_llm()
    return EXTRACTION_PROMPT | llm.with_structured_output(QueryExtract)

def _build_final_chain():
    llm = get_llm()
    return (
        RunnableParallel({
            "context": RunnableLambda(hybrid_retriever),
            "question": RunnablePassthrough()
        })
        | FINAL_PROMPT
        | llm
        | StrOutputParser()
    )

# ── Retriever ─────────────────────────────────────────────────────────────────

def hybrid_retriever(question: str) -> str:
    extraction_chain = _build_extraction_chain()
    extract = extraction_chain.invoke({"question": question})

    kg_results     = []
    vector_results = []

    if extract.actor or extract.genre or extract.director:
        kg_results = kg_search(
            actor=extract.actor,
            genre=extract.genre,
            director=extract.director,
        )

    semantic_q     = extract.semantic_query or question
    vector_results = vector_search(semantic_q, k=10)

    # Merge — KG results take priority
    seen   = set()
    merged = []

    for r in kg_results:
        title = r.get("title")
        if title and title not in seen:
            seen.add(title)
            merged.append(("kg", r))

    for r in vector_results:
        title = r.get("title")
        if title and title not in seen:
            seen.add(title)
            merged.append(("vector", r))

    # Build context string
    kg_section = "\n\n".join(
        format_movie(r) for src, r in merged if src == "kg"
    ) or "None"

    vec_section = "\n\n".join(
        format_movie(r) for src, r in merged if src == "vector"
    ) or "None"

    return f"""=== Structured Graph Results (exact matches) ===
{kg_section}

=== Semantic / Thematic Results ===
{vec_section}"""


# ── Calling Final Pipeline ────────────────────────────────────────────────────────────────

def run_pipeline(question: str, user_id: str = None, session_id: str = None) -> str:
    """
    Single entry point for main.py and Streamlit.
    Traces the full pipeline run in Langfuse automatically.
    """
    handler = get_langfuse_handler()

    # Attach optional user/session metadata for Langfuse dashboard
    handler.user_id    = user_id
    handler.session_id = session_id

    chain = _build_final_chain()

    return chain.invoke(
        question,
        config={"callbacks": [handler]}
    )



def stream_pipeline(question: str, user_id: str = None, session_id: str = None) -> Generator:
    """Streaming version for Streamlit to get output as token by token."""
    
    handler            = get_langfuse_handler()
    handler.user_id    = user_id
    handler.session_id = session_id

    chain = _build_final_chain()
    for chunk in chain.stream(
        question,
        config={"callbacks": [handler]}
    ):
        yield chunk