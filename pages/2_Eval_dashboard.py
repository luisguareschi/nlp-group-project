"""Evaluation dashboard — run harness on gold set."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.classify import list_ollama_models
from src.eval_runner import (
    EVAL_PATH,
    RESULTS_DIR,
    load_eval,
    run_eval,
    run_full_eval_suite,
    save_confusion_matrix,
)

st.set_page_config(page_title="Eval Dashboard", page_icon="📊", layout="wide")
st.title("Evaluation dashboard")
st.caption(f"Gold set: `{EVAL_PATH.relative_to(ROOT)}`")

rows = load_eval()
st.metric("Gold participants", len(rows))

tier_counts: dict[str, int] = {}
for r in rows:
    tier_counts[r.gold_tier] = tier_counts.get(r.gold_tier, 0) + 1
st.json(tier_counts)

mode = st.selectbox("Run mode", ["features_only", "hybrid", "llm_only"])
tier_filter = st.selectbox(
    "Tier filter",
    ["all", "synthetic", "disclosed", "grid", "expert", "edge"],
    format_func=lambda x: "all tiers" if x == "all" else x,
)
model = st.selectbox("Ollama model", list_ollama_models())

if st.button("Run evaluation"):
    filtered = rows
    if tier_filter != "all":
        filtered = [r for r in rows if r.gold_tier == tier_filter]

    with st.spinner("Running..."):
        metrics = run_eval(filtered, mode=mode, model=model)
        cm_path = RESULTS_DIR / f"confusion_matrix_{mode}_{tier_filter}.png"
        save_confusion_matrix(metrics, cm_path)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Accuracy", metrics["accuracy"])
    c2.metric("Macro F1", metrics["macro_f1"])
    c3.metric("Binary macro F1", metrics["binary_macro_f1"])
    c4.metric("High-conf errors", metrics["high_confidence_errors"])

    st.markdown("**Calibration**")
    st.write(
        f"Mean confidence when correct: **{metrics['mean_confidence_when_correct']}** | "
        f"when wrong: **{metrics['mean_confidence_when_wrong']}**"
    )

    st.image(str(cm_path), caption="Confusion matrix")

    st.subheader("Classification report")
    st.dataframe(
        {
            label: {
                k: round(v, 3) if isinstance(v, float) else v
                for k, v in stats.items()
                if k in ("precision", "recall", "f1-score", "support")
            }
            for label, stats in metrics["classification_report"].items()
            if isinstance(stats, dict) and "f1-score" in stats
        },
        use_container_width=True,
    )

if st.button("Run full suite (features + hybrid) → results/eval_run.json"):
    with st.spinner("Running full suite..."):
        suite = run_full_eval_suite(model=model)
    st.success(f"Saved to `{RESULTS_DIR / 'eval_run.json'}`")
    st.json(suite)

precomputed = RESULTS_DIR / "eval_run.json"
if precomputed.exists():
    with st.expander("Precomputed results"):
        st.json(json.loads(precomputed.read_text(encoding="utf-8")))
