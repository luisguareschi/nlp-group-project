"""Dead Internet Detector — Streamlit entry point."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.aggregate import build_thread_analysis
from src.classify import analyze_thread, list_ollama_models, ollama_available
from src.parse_thread import parse_thread
from src.reddit_fetch import RedditFetchError, fetch_reddit_thread

st.set_page_config(
    page_title="Dead Internet Detector",
    page_icon="🌐",
    layout="wide",
)

EXAMPLES_DIR = ROOT / "data" / "examples"

LABEL_DISPLAY = {
    "human": "Human",
    "bot": "Bot",
    "human_imitating_bot": "Human imitating bot",
    "bot_imitating_human": "Bot imitating human",
}


def load_example(name: str) -> str:
    path = EXAMPLES_DIR / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


st.title("Dead Internet Detector")
st.caption(
    "Statistical vibes, not verdicts. Paste a thread; get per-user labels with confidence and reasoning."
)

with st.sidebar:
    st.header("Settings")
    mode = st.selectbox(
        "Classification mode",
        ["hybrid", "features_only", "llm_only"],
        help="hybrid: Ollama + heuristics fallback; features_only: no LLM",
    )
    model = st.selectbox("Ollama model", list_ollama_models())
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2, 0.05)
    strict = st.checkbox("Strict mode (temp 0.1)", value=False)
    if strict:
        temperature = 0.1

    if ollama_available():
        st.success("Ollama detected")
    else:
        st.warning("Ollama not running — hybrid/llm_only will use heuristics")

    st.divider()
    st.markdown("**Format help**")
    st.code(
        "u/alice: First comment\n"
        "u/alice: Second comment\n"
        "u/bob: Reply here",
        language="text",
    )

st.warning(
    "This tool estimates rhetorical 'bot-voice' from pasted text only. "
    "It is not proof of account type. Do not use outputs to harass users."
)

if "thread_text" not in st.session_state:
    st.session_state.thread_text = ""

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Load example: mixed thread"):
        st.session_state.thread_text = load_example("mixed_thread.txt")
with col2:
    if st.button("Load example: disclosed bots"):
        st.session_state.thread_text = load_example("disclosed_bots.txt")
with col3:
    if st.button("Load example: irony/shitpost"):
        st.session_state.thread_text = load_example("irony_thread.txt")

st.write("Reddit post URL")
reddit_col, load_col = st.columns([4, 1], vertical_alignment="bottom")
with reddit_col:
    reddit_url = st.text_input(
        "reddit_url",
        label_visibility="collapsed",
        placeholder="https://www.reddit.com/r/subreddit/comments/…",
    )
with load_col:
    load_reddit = st.button("Load from Reddit", use_container_width=True)

if load_reddit:
    if not reddit_url.strip():
        st.error("Enter a Reddit post URL first.")
    else:
        try:
            pasted, truncated = fetch_reddit_thread(reddit_url.strip())
            st.session_state.thread_text = pasted
            st.success("Thread loaded from Reddit. Review below, then analyze.")
            if truncated:
                st.warning(
                    "Only the first ~200 comments were loaded. "
                    "Edit the text area or paste more manually for a longer thread."
                )
        except RedditFetchError as e:
            st.error(str(e))

st.text_area(
    "Paste thread",
    height=280,
    placeholder="u/user1: comment\nu/user2: comment",
    key="thread_text",
)

if st.button("Analyze thread", type="primary"):
    thread_text = st.session_state.thread_text
    if not thread_text.strip():
        st.error("Paste a thread first.")
        st.stop()

    participants = parse_thread(thread_text)
    if len(participants) < 1:
        st.error("Could not parse any participants. Check format in sidebar.")
        st.stop()

    total_comments = sum(len(comments) for comments in participants.values())
    progress = st.progress(
        0.0,
        text=f"Classifying 0 / {total_comments} comments…",
    )

    def report_progress(done: int, total: int) -> None:
        fraction = done / total if total else 1.0
        progress.progress(
            fraction,
            text=f"Classifying {done} / {total} comments…",
        )

    results = analyze_thread(
        participants,
        mode=mode,
        model=model,
        temperature=temperature,
        on_progress=report_progress,
    )
    progress.empty()
    analysis = build_thread_analysis(results)

    st.subheader("Thread summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Dead Internet Index", f"{analysis.dead_internet_index}%")
    m2.metric("Participants", len(results))
    m3.metric("Mode", mode)

    st.subheader("Per-participant results")
    rows = []
    for r in analysis.participants:
        badge = " ⚠️ low evidence" if r.low_evidence else ""
        rows.append(
            {
                "User": f"u/{r.username}",
                "Label": LABEL_DISPLAY.get(r.label, r.label) + badge,
                "Signal Strength": r.confidence,
                "Reasoning": r.reasoning,
                "Cues": "; ".join(r.cues) if r.cues else "—",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)
    st.caption(
        "Signal Strength reflects stylometric or LLM signal intensity (0–100). "
        "It is not a calibrated probability — see the Evaluation dashboard for calibration metrics."
    )

    with st.expander("Label breakdown"):
        st.json(analysis.label_counts)

    for r in analysis.participants:
        with st.expander(f"u/{r.username} — detail"):
            st.markdown(f"**Label:** {LABEL_DISPLAY.get(r.label, r.label)}")
            st.markdown(f"**Confidence:** {r.confidence}%")
            st.markdown(f"**Reasoning:** {r.reasoning}")
            if r.cues:
                st.markdown("**Cues:**")
                for c in r.cues:
                    st.markdown(f"- {c}")
            st.markdown("**Comments in thread:**")
            for c in participants.get(r.username, []):
                st.markdown(f"> {c}")
