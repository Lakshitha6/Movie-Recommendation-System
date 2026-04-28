# main.py (root directory)

import streamlit as st
import uuid
from src.app import run_pipeline, stream_pipeline

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="CineMatch — Movie Recommendations",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State ─────────────────────────────────────────────────────────────

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "is_loading" not in st.session_state:
    st.session_state.is_loading = False

# ── Styling ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Root & Background ── */
:root {
    --bg-primary:    #0a0a0f;
    --bg-secondary:  #111118;
    --bg-card:       #16161f;
    --bg-input:      #1c1c28;
    --accent-gold:   #c9a84c;
    --accent-red:    #e05252;
    --text-primary:  #f0ede8;
    --text-muted:    #7a7a8c;
    --border:        #2a2a3a;
    --border-light:  #333348;
}

html, body, .stApp {
    background-color: var(--bg-primary) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text-primary);
}

/* Film grain overlay */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.4;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Hero Header ── */
.hero {
    background: linear-gradient(180deg, #0d0d14 0%, #0a0a0f 100%);
    border-bottom: 1px solid var(--border);
    padding: 2.5rem 4rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}

.hero::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent-gold), transparent);
}

.hero-logo {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    margin: 0;
}

.hero-title span {
    color: var(--accent-gold);
    font-style: italic;
}

.hero-tagline {
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.25rem;
}

.hero-badge {
    background: rgba(201, 168, 76, 0.1);
    border: 1px solid rgba(201, 168, 76, 0.3);
    color: var(--accent-gold);
    padding: 0.35rem 1rem;
    border-radius: 2rem;
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* ── Main Layout ── */
.main-layout {
    display: grid;
    grid-template-columns: 280px 1fr;
    min-height: calc(100vh - 100px);
}

/* ── Sidebar ── */
.sidebar {
    background: var(--bg-secondary);
    border-right: 1px solid var(--border);
    padding: 2rem 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.sidebar-section-title {
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 0.75rem;
}

.quick-prompt {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.82rem;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    line-height: 1.4;
}

.quick-prompt:hover {
    border-color: var(--accent-gold);
    background: rgba(201, 168, 76, 0.05);
    color: var(--accent-gold);
}

.quick-prompt-icon {
    font-size: 1rem;
    margin-right: 0.5rem;
}

/* ── Chat Area ── */
.chat-area {
    display: flex;
    flex-direction: column;
    padding: 2rem 3rem;
    gap: 1.5rem;
    max-width: 900px;
    margin: 0 auto;
    width: 100%;
}

/* ── Message Bubbles ── */
.message-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    animation: fadeSlideIn 0.3s ease;
}

@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}

.message-label {
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-muted);
    padding-left: 0.25rem;
}

.message-user {
    background: linear-gradient(135deg, #1e1e2e, #252535);
    border: 1px solid var(--border-light);
    border-radius: 12px 12px 4px 12px;
    padding: 1rem 1.25rem;
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--text-primary);
    align-self: flex-end;
    max-width: 75%;
}

.message-assistant {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-gold);
    border-radius: 4px 12px 12px 12px;
    padding: 1.25rem 1.5rem;
    font-size: 0.92rem;
    line-height: 1.75;
    color: var(--text-primary);
    max-width: 90%;
}

.message-assistant h1, .message-assistant h2, .message-assistant h3 {
    font-family: 'Playfair Display', serif;
    color: var(--accent-gold);
    margin-top: 1rem;
}

.message-assistant strong {
    color: var(--text-primary);
    font-weight: 500;
}

.message-assistant ul, .message-assistant ol {
    padding-left: 1.25rem;
}

.message-assistant li {
    margin-bottom: 0.5rem;
}

/* ── Thinking Indicator ── */
.thinking {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent-gold);
    border-radius: 4px 12px 12px 12px;
    max-width: 200px;
    color: var(--text-muted);
    font-size: 0.85rem;
}

.dot-flashing {
    display: flex;
    gap: 4px;
    align-items: center;
}

.dot-flashing span {
    width: 6px;
    height: 6px;
    background: var(--accent-gold);
    border-radius: 50%;
    animation: dotFlash 1.2s infinite;
}

.dot-flashing span:nth-child(2) { animation-delay: 0.2s; }
.dot-flashing span:nth-child(3) { animation-delay: 0.4s; }

@keyframes dotFlash {
    0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
    40%           { opacity: 1;   transform: scale(1); }
}

/* ── Empty State ── */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 50vh;
    text-align: center;
    gap: 1rem;
}

.empty-icon {
    font-size: 3.5rem;
    opacity: 0.4;
}

.empty-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    color: var(--text-primary);
    opacity: 0.6;
}

.empty-subtitle {
    font-size: 0.88rem;
    color: var(--text-muted);
    max-width: 320px;
    line-height: 1.6;
}

/* ── Input Area ── */
.input-area {
    position: sticky;
    bottom: 0;
    background: linear-gradient(0deg, var(--bg-primary) 80%, transparent);
    padding: 1.5rem 3rem 2rem;
    max-width: 900px;
    margin: 0 auto;
    width: 100%;
}

.input-container {
    background: var(--bg-input);
    border: 1px solid var(--border-light);
    border-radius: 12px;
    display: flex;
    align-items: flex-end;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    transition: border-color 0.2s ease;
}

.input-container:focus-within {
    border-color: var(--accent-gold);
    box-shadow: 0 0 0 3px rgba(201, 168, 76, 0.08);
}

/* Override Streamlit text_area */
.stTextArea textarea {
    background: transparent !important;
    border: none !important;
    color: var(--text-primary) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.92rem !important;
    resize: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.stTextArea textarea:focus {
    box-shadow: none !important;
    border: none !important;
}

.stTextArea > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-gold), #a8832a) !important;
    color: #0a0a0f !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(201, 168, 76, 0.3) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Clear button */
.clear-btn > button {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.78rem !important;
}

.stDivider { border-color: var(--border) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: var(--border-light); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div>
        <div class="hero-logo">
            <h1 class="hero-title">Cine<span>Match</span></h1>
        </div>
        <div class="hero-tagline">AI-Powered Movie Recommendations</div>
    </div>
    <div class="hero-badge">🎬 Knowledge Graph + Semantic Search</div>
</div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────

sidebar_col, main_col = st.columns([1, 3.2])

# ── Sidebar ───────────────────────────────────────────────────────────────────

QUICK_PROMPTS = [
    ("🎭", "Movies directed by Christopher Nolan"),
    ("👻", "Best horror movies from the 90s"),
    ("🚀", "Sci-fi movies with mind-bending plots"),
    ("❤️",  "Romantic movies similar to Titanic"),
    ("💥", "Action movies with Tom Cruise"),
    ("🎨", "Visually stunning artistic films"),
    ("😂", "Feel-good comedy movies"),
    ("🕵️", "Thriller movies with plot twists"),
]

with sidebar_col:
    st.markdown('<div class="sidebar">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section-title">Quick Searches</div>', unsafe_allow_html=True)

    for icon, prompt in QUICK_PROMPTS:
        if st.button(f"{icon}  {prompt}", key=f"quick_{prompt}", use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                response = st.write_stream(stream_pipeline(
                    question=prompt,
                    user_id="streamlit-user",
                    session_id=st.session_state.session_id
                ))
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

    st.divider()
    st.markdown('<div class="sidebar-section-title">Session</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:0.72rem;color:var(--text-muted);word-break:break-all;">ID: {st.session_state.session_id[:18]}...</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="clear-btn">', unsafe_allow_html=True)
        if st.button("🗑 Clear History", use_container_width=True):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ── Chat Area ─────────────────────────────────────────────────────────────────

with main_col:

    # Messages
    if not st.session_state.messages:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">🎬</div>
            <div class="empty-title">What shall we watch?</div>
            <div class="empty-subtitle">
                Ask me anything — by genre, actor, director, mood,
                or describe a vibe and I'll find the perfect match.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="message-wrapper">
                    <div class="message-label">You</div>
                    <div class="message-user">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="message-wrapper">
                    <div class="message-label">CineMatch</div>
                    <div class="message-assistant">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    # ── Input ─────────────────────────────────────────────────────────────────

    st.markdown('<div class="input-area">', unsafe_allow_html=True)

    input_col, btn_col = st.columns([5, 1])

    with input_col:
        user_input = st.text_area(
            label="Movie search input",
            placeholder="Ask for a movie recommendation...",
            key="user_input",
            height=68,
            label_visibility="hidden"
        )

    with btn_col:
        st.markdown("<br>", unsafe_allow_html=True)
        send = st.button("Search →", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Handle Submit ─────────────────────────────────────────────────────────

    if send and user_input.strip():
        question = user_input.strip()
        st.session_state.messages.append({"role": "user", "content": question})

        with st.chat_message("assistant"):
            response = st.write_stream(stream_pipeline(
                question=question,
                user_id="streamlit-user",
                session_id=st.session_state.session_id
            )
            )
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()