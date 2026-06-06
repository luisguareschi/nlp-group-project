"""Dead Internet Detector — Streamlit entry point."""

from __future__ import annotations

import base64
import csv
import gzip
import io
import re
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

LABEL_COLOR = {
    "human": "#4CAF50",
    "bot": "#F44336",
    "human_imitating_bot": "#FF9800",
    "bot_imitating_human": "#9C27B0",
}

# Matches the leading "u/name:", "/u/name:", "@name:", or "name:" pattern
_USER_LINE_RE = re.compile(r"^(?:u/|/u/|@)?([A-Za-z0-9_-]+)\s*[:|-]", re.IGNORECASE)


def load_example(name: str) -> str:
    path = EXAMPLES_DIR / name
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _encode_thread(text: str) -> str:
    return base64.urlsafe_b64encode(gzip.compress(text.encode())).decode().rstrip("=")


def _decode_thread(encoded: str) -> str:
    padding = "=" * (-len(encoded) % 4)
    return gzip.decompress(base64.urlsafe_b64decode(encoded + padding)).decode()


# ── Page header ──────────────────────────────────────────────────────────────

st.title("Dead Internet Detector")
st.caption(
    "Statistical vibes, not verdicts. Paste a thread; get per-user labels with confidence and reasoning."
)

# ── Sidebar ───────────────────────────────────────────────────────────────────

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

    st.divider()
    compare_modes = st.checkbox(
        "Compare features_only vs hybrid",
        value=False,
        help="Run both modes side-by-side and highlight where they disagree. Requires Ollama for hybrid.",
    )

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

# ── Disclaimer ────────────────────────────────────────────────────────────────

st.warning(
    "This tool estimates rhetorical 'bot-voice' from pasted text only. "
    "It is not proof of account type. Do not use outputs to harass users."
)

# ── Session state — pre-populate from URL on first load ──────────────────────

if "thread_text" not in st.session_state:
    raw_param = st.query_params.get("t", "")
    if raw_param:
        try:
            st.session_state.thread_text = _decode_thread(raw_param)
        except Exception:
            st.session_state.thread_text = ""
    else:
        st.session_state.thread_text = ""

if "thread_timestamps" not in st.session_state:
    st.session_state.thread_timestamps = {}

# ── Example loaders ───────────────────────────────────────────────────────────

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Load example: mixed thread"):
        st.session_state.thread_text = load_example("mixed_thread.txt")
        st.session_state.thread_timestamps = {}
with col2:
    if st.button("Load example: disclosed bots"):
        st.session_state.thread_text = load_example("disclosed_bots.txt")
        st.session_state.thread_timestamps = {}
with col3:
    if st.button("Load example: irony/shitpost"):
        st.session_state.thread_text = load_example("irony_thread.txt")
        st.session_state.thread_timestamps = {}

# ── Reddit fetch ──────────────────────────────────────────────────────────────

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
            pasted, truncated, ts_dict = fetch_reddit_thread(reddit_url.strip())
            st.session_state.thread_text = pasted
            st.session_state.thread_timestamps = ts_dict
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

# ── Analysis ──────────────────────────────────────────────────────────────────

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
    timestamps = st.session_state.get("thread_timestamps", {})

    # ── Compare mode ──────────────────────────────────────────────────────────
    if compare_modes:
        progress = st.progress(0.0, text="Running features_only…")

        def _prog_feat(d: int, t: int) -> None:
            progress.progress((d / t / 2) if t else 0.0, text=f"features_only: {d}/{t}")

        results_feat = analyze_thread(
            participants,
            mode="features_only",
            model=model,
            temperature=temperature,
            on_progress=_prog_feat,
            timestamps_dict=timestamps,
        )

        def _prog_hyb(d: int, t: int) -> None:
            progress.progress(0.5 + (d / t / 2 if t else 0.0), text=f"hybrid: {d}/{t}")

        results_hyb = analyze_thread(
            participants,
            mode="hybrid",
            model=model,
            temperature=temperature,
            on_progress=_prog_hyb,
            timestamps_dict=timestamps,
        )
        progress.empty()

        analysis_feat = build_thread_analysis(results_feat)
        analysis_hyb = build_thread_analysis(results_hyb)

        feat_map = {r.username: r for r in results_feat}
        hyb_map = {r.username: r for r in results_hyb}
        agree_count = sum(1 for u in feat_map if feat_map[u].label == hyb_map.get(u, feat_map[u]).label)
        agreement_pct = round(100 * agree_count / len(feat_map)) if feat_map else 0

        st.subheader("Mode comparison")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Agreement", f"{agreement_pct}%")
        mc2.metric("features_only DII", f"{analysis_feat.dead_internet_index}%")
        mc3.metric("hybrid DII", f"{analysis_hyb.dead_internet_index}%")

        comp_rows = []
        for u in feat_map:
            fr = feat_map[u]
            hr = hyb_map.get(u, fr)
            agrees = fr.label == hr.label
            comp_rows.append(
                {
                    "User": f"u/{u}",
                    "features_only": LABEL_DISPLAY.get(fr.label, fr.label),
                    "hybrid": LABEL_DISPLAY.get(hr.label, hr.label),
                    "feat signal": fr.confidence,
                    "hybrid signal": hr.confidence,
                    "Agree": "✓" if agrees else "✗",
                }
            )
        st.dataframe(comp_rows, use_container_width=True, hide_index=True)

        disagreements = [r for r in comp_rows if r["Agree"] == "✗"]
        if disagreements:
            with st.expander(f"Disagreements ({len(disagreements)} users)"):
                for r in disagreements:
                    uname = r["User"][2:]
                    fr = feat_map[uname]
                    hr = hyb_map.get(uname, fr)
                    st.markdown(f"**u/{uname}** — features_only: `{fr.label}` / hybrid: `{hr.label}`")
                    st.markdown(f"- features_only reasoning: {fr.reasoning}")
                    st.markdown(f"- hybrid reasoning: {hr.reasoning}")

        # Use hybrid results for the shared downstream sections
        results = results_hyb
        analysis = analysis_hyb

    # ── Single mode ───────────────────────────────────────────────────────────
    else:
        progress = st.progress(0.0, text=f"Classifying 0 / {total_comments} comments…")

        def report_progress(done: int, total: int) -> None:
            progress.progress(
                done / total if total else 1.0,
                text=f"Classifying {done} / {total} comments…",
            )

        results = analyze_thread(
            participants,
            mode=mode,
            model=model,
            temperature=temperature,
            on_progress=report_progress,
            timestamps_dict=timestamps,
        )
        progress.empty()
        analysis = build_thread_analysis(results)

        st.subheader("Thread summary")
        m1, m2, m3 = st.columns(3)
        m1.metric("Dead Internet Index", f"{analysis.dead_internet_index}%")
        m2.metric("Participants", len(results))
        m3.metric("Mode", mode)

    # ── Per-participant results (shared) ──────────────────────────────────────
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

    # ── Feature 1: Export ─────────────────────────────────────────────────────
    exp_col1, exp_col2 = st.columns(2)
    with exp_col1:
        buf = io.StringIO()
        writer = csv.DictWriter(
            buf, fieldnames=["User", "Label", "Signal Strength", "Reasoning", "Cues"]
        )
        writer.writeheader()
        writer.writerows(rows)
        st.download_button(
            "Download CSV",
            buf.getvalue(),
            "dead_internet_results.csv",
            "text/csv",
            use_container_width=True,
        )
    with exp_col2:
        st.download_button(
            "Download JSON",
            analysis.model_dump_json(indent=2),
            "dead_internet_results.json",
            "application/json",
            use_container_width=True,
        )

    with st.expander("Label breakdown"):
        st.json(analysis.label_counts)

    # ── Feature 5: Annotated thread ───────────────────────────────────────────
    label_map = {r.username: r.label for r in analysis.participants}
    with st.expander("Annotated thread"):
        st.caption("Each comment line is color-coded by the speaker's predicted label.")
        for line in thread_text.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            m = _USER_LINE_RE.match(stripped)
            username = m.group(1) if m else None
            label = label_map.get(username) if username else None
            color = LABEL_COLOR.get(label, "#888888") if label else "#888888"
            display_label = LABEL_DISPLAY.get(label, "") if label else ""
            badge_html = (
                f' <span style="background:{color};color:white;border-radius:3px;'
                f'padding:1px 5px;font-size:0.75em;">{display_label}</span>'
                if label
                else ""
            )
            st.markdown(
                f'<span style="color:{color};">{stripped}</span>{badge_html}',
                unsafe_allow_html=True,
            )

    # ── Feature 6: Share link ─────────────────────────────────────────────────
    with st.expander("Share this thread"):
        try:
            encoded = _encode_thread(thread_text)
            if len(encoded) > 8000:
                st.warning(
                    "Thread text is too long to encode in a URL (~8 KB limit). "
                    "Share the raw text manually instead."
                )
            else:
                st.caption(
                    "Append this parameter to the app URL to share a pre-loaded thread "
                    "(e.g. http://localhost:8501?t=…)."
                )
                st.code(f"?t={encoded}", language="text")
        except Exception:
            st.warning("Could not generate share link.")

    # ── Per-participant detail expanders ──────────────────────────────────────
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
