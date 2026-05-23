# Installation Guide — Dead Internet Detector

## Prerequisites

- Python 3.10+
- ~500 MB disk for Python packages
- **Optional but recommended:** [Ollama](https://ollama.com/) for hybrid/LLM classification

## 1. Python environment

```bash
cd nlp-group-project
python -m venv .venv          # skip if .venv already exists
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Ollama (local LLM)

```bash
# Install from https://ollama.com/download
ollama pull llama3.2:3b
ollama serve                   # if not already running
```

Verify:

```bash
ollama list
```

**Without Ollama:** the app still runs using `features_only` mode or hybrid with heuristic fallback.

## 3. Run the app

```bash
streamlit run app.py
```

Open the URL shown in the terminal (default `http://localhost:8501`).

## 4. Run evaluation

```bash
python -m src.eval_runner
```

Outputs:

- `results/eval_run.json`
- `results/confusion_matrix_features_only.png`
- `results/confusion_matrix_hybrid.png`

Or use the **Eval dashboard** page in the Streamlit sidebar.

## 5. Regenerate eval dataset

```bash
python scripts/build_eval_jsonl.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: src` | Run from repo root; `app.py` adds root to `sys.path` |
| Ollama connection refused | Start `ollama serve` or use **features_only** mode |
| Slow first LLM call | Model loads on first request; wait 30–60s |
| Streamlit port in use | `streamlit run app.py --server.port 8502` |

## Hardware

- **CPU-only:** supported; `features_only` is fast; Ollama 3B needs ~4 GB RAM
- **GPU:** Ollama uses GPU automatically if available
