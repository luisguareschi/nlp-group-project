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
    run_full_eval_suite,
)

st.set_page_config(page_title="Eval Dashboard", page_icon="📊", layout="wide")
st.title("Evaluation dashboard")
st.caption(f"Gold set: `{EVAL_PATH.relative_to(ROOT)}`")

GOLD_TIER_LEGEND: dict[str, str] = {
    "synthetic": (
        "Team-authored role-play threads covering all four label types; "
        "gold labels are high-confidence by design."
    ),
    "disclosed": (
        "Bots that explicitly disclose automation (AutoMod, wiki bots) "
        "alongside ordinary human replies."
    ),
    "grid": (
        "GRiD-style paired snippets: a casual human comment vs. a GPT reply "
        "on the same topic (clear human/bot contrast)."
    ),
    "expert": (
        "De-identified excerpts from real threads; majority-vote labels, "
        "with `annotator_disagreement` when annotators split."
    ),
    "edge": (
        "Deliberately hard cases: very short comments, sarcasm, copypasta, "
        "multilingual text, helpful mod bots vs. spam, coordinated phrasing."
    ),
}

rows = load_eval()
st.metric("Number of Gold participants", len(rows))

tier_counts: dict[str, int] = {}
for r in rows:
    tier_counts[r.gold_tier] = tier_counts.get(r.gold_tier, 0) + 1

st.subheader("Gold set by tier")
for tier in sorted(tier_counts):
    count = tier_counts[tier]
    desc = GOLD_TIER_LEGEND.get(
        tier,
        "Tier not documented in the dashboard legend — see `docs/LABELING_GUIDELINES.md`.",
    )
    st.markdown(f"**`{tier}`** ({count}) — {desc}")

EVAL_JSON = RESULTS_DIR / "eval_run.json"


def _confusion_matrix_path(mode: str) -> Path:
    return RESULTS_DIR / f"confusion_matrix_{mode}.png"


def _classification_report_table(metrics: dict) -> dict:
    return {
        label: {
            k: round(v, 3) if isinstance(v, float) else v
            for k, v in stats.items()
            if k in ("precision", "recall", "f1-score", "support")
        }
        for label, stats in metrics["classification_report"].items()
        if isinstance(stats, dict) and "f1-score" in stats
    }


def _display_mode_results(mode: str, metrics: dict) -> None:
    if "error" in metrics:
        st.error(f"**{mode}** failed: {metrics['error']}")
        return

    st.subheader(mode.replace("_", " ").title())
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

    cm_path = _confusion_matrix_path(mode)
    if cm_path.exists():
        st.image(str(cm_path), caption=f"Confusion matrix ({mode}, n={metrics.get('n', '?')})")
    else:
        st.warning(f"No confusion matrix image at `{cm_path.relative_to(ROOT)}`.")

    st.markdown("**Classification report**")
    st.dataframe(_classification_report_table(metrics), use_container_width=True)


def _load_precomputed_suite() -> dict | None:
    if not EVAL_JSON.exists():
        return None
    return json.loads(EVAL_JSON.read_text(encoding="utf-8"))


action = st.radio(
    "Action",
    ["Run full suite", "View precomputed results"],
    horizontal=True,
)

if action == "Run full suite":
    model = st.selectbox("Ollama model", list_ollama_models())
    st.caption("Runs **features_only** and **hybrid** on the full gold set; writes `results/eval_run.json` and confusion matrix PNGs.")
    st.warning(f"This will overwrite the precomputed results at `{EVAL_JSON.relative_to(ROOT)}`")
    st.warning(f"This may take a while to run, depending on the model and the size of the gold set.")

    if st.button("Run full suite"):
        progress = st.progress(0, text="Starting full suite…")
        status = st.empty()

        def on_progress(message: str, current: int, total: int) -> None:
            progress.progress(min(current / total, 1.0), text=message)
            status.caption(f"Step {current} of {total}")

        suite = run_full_eval_suite(model=model, on_progress=on_progress)
        progress.progress(1.0, text="Full suite complete")
        status.empty()
        st.success(f"Saved to `{EVAL_JSON.relative_to(ROOT)}`")
        for mode, metrics in suite.items():
            _display_mode_results(mode, metrics)

elif action == "View precomputed results":
    suite = _load_precomputed_suite()
    if suite is None:
        st.info(
            f"No precomputed results at `{EVAL_JSON.relative_to(ROOT)}`. "
            "Run the full suite first."
        )
    else:
        st.caption(f"Loaded from `{EVAL_JSON.relative_to(ROOT)}`")
        for mode, metrics in suite.items():
            _display_mode_results(mode, metrics)
