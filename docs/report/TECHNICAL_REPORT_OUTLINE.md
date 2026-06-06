# Technical Report Outline (draft)

Expand each section for PDF submission. Target length: appropriate to project scope (~8–15 pages).

## 1. Introduction

- Dead Internet theory and epistemic distrust in online discourse
- Problem: moderators and readers cannot audit every participant at scale
- Contribution: Dead Internet Detector POC with tiered evaluation methodology

## 2. Related work

- Social bot detection (BotSim, platform moderation)
- LLM-generated text detection (GRiD, GPT detectors)
- Human performance studies ("Bot or Not?" style experiments)
- Stylometry and authorship attribution

## 3. System design

- Architecture diagram (parser → features → Ollama → aggregate)
- Label taxonomy with examples
- Prompt design (`prompts/classify_user.txt`)
- Hybrid vs features-only vs llm-only modes

## 4. Evaluation methodology

- Why perfect ground truth is impossible for arbitrary paste
- Tier 1: synthetic, disclosed, GRiD-style (high confidence)
- Tier 2: expert consensus (de-identified excerpts)
- Tier 3: edge cases (analyzed separately)
- Metrics: macro-F1, binary collapse, calibration
- Ablation table from `results/eval_run.json` (`features_only` vs `hybrid` on full n=48)
- Human baseline (optional): one annotator on held-out set
- Reproducibility: `python -m src.eval_runner` or Streamlit **Evaluation dashboard** → **Run full suite**

## 5. Results

- Include tables from `results/eval_run.json`
- Confusion matrices (`results/confusion_matrix_features_only.png`, `results/confusion_matrix_hybrid.png`)
- Per-tier discussion using dashboard tier legend / `gold_tier` field (optional filtered re-runs via `run_eval(..., tier_filter=...)` in code)

## 6. Failure taxonomy

- Summarize `docs/FAILURE_ANALYSIS.md` with 2–3 deepest cases

## 7. Ethics and limitations

- Probabilistic output; harassment risk
- English-centric features; paste-only blindness
- LLM rationalization / hallucinated cues

## 8. Future work

- Reply-tree structure, multilingual models, larger gold set, hosted demo constraints

## 9. Use of AI tools

- Describe Cursor/ChatGPT use for scaffolding, debugging, report drafting
- Substantive decisions: label defs, eval set, failure interpretations — team-owned

## References

- ACL Anthology, GRiD paper, course materials on hallucination/pattern completion
