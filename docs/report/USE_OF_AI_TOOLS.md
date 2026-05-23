# Use of AI Tools (report section draft)

## Tools used

- **Cursor / Claude** — repository scaffolding, boilerplate for Streamlit app, parser, evaluation runner, documentation drafts
- **Team judgment** — label taxonomy, all gold labels in `data/eval/participants.jsonl`, failure mode interpretations, synthetic role-play threads

## What AI assisted with

- Python module structure matching the project plan
- Regex parser heuristics and pydantic schemas
- Initial prompt template in `prompts/classify_user.txt` (edited by team)
- README, INSTALL, USER_MANUAL, failure analysis templates

## What the team owns

- Problem framing and Dead Internet narrative
- Evaluation methodology (tiered ground truth)
- Synthetic thread authorship and expert-tier label decisions
- Final prompt wording, metric thresholds, and presentation narrative
- Decision to cap confidence on short comments (transparent rule in code)

## Verification

All team members can explain parser behavior, label definitions, and eval metrics. Reproducibility: `pip install -r requirements.txt`, `python -m src.eval_runner`, `streamlit run app.py`.
