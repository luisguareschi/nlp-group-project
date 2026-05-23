# Dead Internet Detector

NLP group project (Option 1 — Application Development). Paste a social thread; get per-participant estimates of **human**, **bot**, **human imitating bot**, or **bot imitating human** — with confidence scores, reasoning, and a thread-level **Dead Internet Index**.

> **Disclaimer:** Statistical vibes, not verdicts. Do not use outputs to harass users.

## Quick start

```bash
source .venv/bin/activate
pip install -r requirements.txt

# Optional: local LLM
ollama pull llama3.2:3b

streamlit run app.py
```

See [docs/INSTALL.md](docs/INSTALL.md) and [docs/USER_MANUAL.md](docs/USER_MANUAL.md).

## Features

- Parse Reddit-style pasted threads (`u/name: comment`)
- Hybrid classification: Ollama LLM + stylometric heuristics (fallback when offline)
- `features_only` mode for fast, fully local evaluation
- Custom eval set: **48** gold participant labels ([`data/eval/participants.jsonl`](data/eval/participants.jsonl)) across five tiers (synthetic, disclosed, grid, expert, edge)
- **Evaluation dashboard** Streamlit page: run or view the full `features_only` + `hybrid` suite with progress feedback
- CLI harness: `python -m src.eval_runner` (interactive Ollama model picker, `tqdm` progress)

## Repository layout

```
app.py                 # Main Streamlit UI
pages/2_Evaluation_dashboard.py
src/
  parse_thread.py      # Thread parser
  features.py          # Stylometric signals + heuristic classifier
  classify.py          # Ollama + hybrid pipeline
  aggregate.py         # Dead Internet Index
  eval_runner.py       # Metrics + confusion matrices
prompts/classify_user.txt
data/eval/             # Gold labels
data/examples/         # Demo threads
docs/                  # Install, manual, labeling, failure analysis, report drafts
```

## Evaluation

The harness always runs **`features_only`** then **`hybrid`** on the full gold set (48 participants), writes metrics to `results/eval_run.json`, and saves `results/confusion_matrix_{mode}.png`.

**CLI** (requires Ollama for hybrid; pick a model when prompted):

```bash
python -m src.eval_runner          # tqdm progress → results/eval_run.json
```

**Streamlit** (sidebar → **Evaluation dashboard**): choose **Run full suite** (same as CLI, with a progress bar) or **View precomputed results** without re-running.

```bash
python scripts/build_eval_jsonl.py # regenerate gold set
pytest tests/ -q
```

Precomputed metrics ship in [`results/eval_run.json`](results/eval_run.json) so you can use **View precomputed results** without Ollama.

## Course alignment


| Requirement         | Artifact                                 |
| ------------------- | ---------------------------------------- |
| Functional POC      | `app.py`                                 |
| Custom eval (30–50) | `data/eval/participants.jsonl` (48 rows) |
| User manual         | `docs/USER_MANUAL.md`                    |
| Install guide       | `docs/INSTALL.md`                        |
| Failure analysis    | `docs/FAILURE_ANALYSIS.md`               |
| Report drafts       | `docs/report/`                           |
| Topic brief         | `docs/TOPIC_BRIEF.md`                    |


## Team notes

- Label definitions: [docs/LABELING_GUIDELINES.md](docs/LABELING_GUIDELINES.md)
- Submit instructor approval using [docs/TOPIC_BRIEF.md](docs/TOPIC_BRIEF.md)

## License

See [LICENSE](LICENSE).
