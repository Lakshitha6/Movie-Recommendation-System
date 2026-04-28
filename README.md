# 🎬 CineMatch — AI-Powered Movie Recommendation System

A production-grade movie recommendation system combining **Knowledge Graph** (Neo4j) and **Semantic Search** (vector embeddings) with a conversational LLM interface. Built with LangChain, Groq/Gemini, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-latest-green?style=flat-square)
![Neo4j](https://img.shields.io/badge/Neo4j-AuraDB-blue?style=flat-square&logo=neo4j)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red?style=flat-square&logo=streamlit)
![Langfuse](https://img.shields.io/badge/Langfuse-Tracing-purple?style=flat-square)
![CI](https://github.com/yourusername/movie-recommendation-system/actions/workflows/ci.yml/badge.svg)

---

## ✨ Features

- **Hybrid Retrieval** — combines structured Knowledge Graph queries with semantic vector search for richer, more accurate results
- **Multi-LLM Support** — switch between Groq (Llama) and Google Gemini via a single config change
- **Conversational UI** — dark-themed Streamlit interface with chat history, quick prompts, and streaming responses
- **Structured Entity Extraction** — automatically extracts actor, director, genre, and semantic intent from natural language queries
- **Observability** — full LLM tracing with Langfuse (latency, token usage, cost per query)
- **Tested** — pytest suite covering config, embeddings, LLM client, and end-to-end pipeline
- **CI/CD** — GitHub Actions runs the full test suite on every push

---

## 🏗 Architecture

```
User Query
    │
    ▼
┌─────────────────────────────┐
│   Extraction Chain (LLM)    │  ← Extracts actor / director / genre / semantic_query
└─────────────┬───────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌─────────┐     ┌─────────────┐
│  Neo4j  │     │  Vector DB  │
│   KG    │     │  (Embeddings│
│ Search  │     │   Search)   │
└────┬────┘     └──────┬──────┘
     └────────┬─────────┘
              ▼
     Merged & Ranked Results
              │
              ▼
┌─────────────────────────────┐
│     Final LLM Response      │  ← Groq / Gemini
└─────────────────────────────┘
              │
              ▼
     Streamlit UI (Streaming)
```

---

## 🗂 Project Structure

```
movie-recommendation-system/
├── config/
│   └── settings.yaml           # LLM provider, paths config
├── data/                        # Movie dataset (CSV)
├── src/
│   ├── app/
│   │   └── main_pipeline.py    # Hybrid retriever + LangChain chain
│   ├── schemas/                 # Pydantic models (QueryExtract)
│   ├── services/
│   │   ├── llm_client.py       # Groq / Gemini LLM singleton
│   │   ├── embeddings.py       # HuggingFace embeddings singleton
│   │   ├── neo4j_client.py     # Neo4j graph connection
│   │   └── langfuse_client.py  # Langfuse tracing handler
│   └── utils/
│       ├── config_loader.py    # YAML config singleton
│       └── graph_search_helper.py  # vector_search, kg_search, format_movie
├── tests/
│   ├── test_config_loader.py
│   ├── test_embedding.py
│   ├── test_llm_client.py
│   └── test_main_pipeline.py
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI
├── main.py                     # Streamlit UI entry point
├── .env                        # secrets (not committed)
├── .gitignore
├── requirements.txt
└── pyproject.toml
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- A [Neo4j AuraDB](https://neo4j.com/cloud/aura/) instance (free tier works)
- A [Groq](https://console.groq.com) or [Google AI Studio](https://aistudio.google.com) API key
- A [HuggingFace](https://huggingface.co/settings/tokens) token
- A [Langfuse](https://cloud.langfuse.com) account (free tier works)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/movie-recommendation-system.git
cd movie-recommendation-system

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Create a `.env` file in the project root:

```properties
# LLM
GROQ_API=gsk_...
GEMINI_API_KEY=AIza...

# HuggingFace
HF_TOKEN=hf_...

# Neo4j
NEO4J_URI=neo4j+ssc://...
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=...
NEO4J_DB=neo4j

# Langfuse
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

### Configuration

Edit `config/settings.yaml` to switch LLM providers:

```yaml
llm:
  active_provider: "groq"   # or "gemini"
```

### Run the App

```bash
streamlit run main.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## ⚙️ Configuration Reference

| Key | Description | Default |
|-----|-------------|---------|
| `llm.active_provider` | Active LLM — `groq` or `gemini` | `groq` |
| `llm.groq.model` | Groq model name | `llama-3.3-70b-versatile` |
| `llm.gemini.model` | Gemini model name | `gemini-3-flash-preview` |
| `llm.*.temperature` | LLM temperature | `0.0` |
| `llm.*.max_tokens` | Max response tokens | `1024` |
| `paths.data_dir` | Path to data directory | `data` |

---

## 🧪 Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run a specific test file
python -m pytest tests/test_main_pipeline.py -v

# Skip integration tests (no API calls)
python -m pytest tests/ -v -m "not integration"
```

### Test Coverage

| File | What it tests |
|------|--------------|
| `test_config_loader.py` | YAML loading, dot-notation get, validation, singleton |
| `test_embedding.py` | Real HuggingFace embedding API, vector dimensions, singleton |
| `test_llm_client.py` | LLM response quality, singleton behaviour |
| `test_main_pipeline.py` | End-to-end pipeline with various query types |

---

## 🔁 CI/CD

GitHub Actions runs the full test suite on every push to `main` or `develop` and on all pull requests.

**Required GitHub Secrets** (Settings → Secrets and variables → Actions):

```
GROQ_API
GEMINI_API_KEY
HF_TOKEN
NEO4J_URI
NEO4J_USERNAME
NEO4J_PASSWORD
NEO4J_DB
LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY
LANGFUSE_BASE_URL
```

---

## 📡 Observability

Every query is traced in [Langfuse](https://cloud.langfuse.com) with:

- Full chain trace (extraction + retrieval + generation)
- Token usage and estimated cost per query
- Latency breakdown per step
- User ID and session ID for conversation grouping

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq (Llama 3.3 70B) / Google Gemini |
| Embeddings | HuggingFace — `all-MiniLM-L6-v2` |
| Graph DB | Neo4j AuraDB |
| Orchestration | LangChain |
| UI | Streamlit |
| Tracing | Langfuse |
| Testing | pytest |
| CI | GitHub Actions |

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.