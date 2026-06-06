# User Manual — Dead Internet Detector

## What this tool does

Paste a social thread (Reddit-style comments, forum replies, etc.). The app estimates, **for each participant**:

- **Human** — likely genuine human voice
- **Bot** — likely automated or template/LLM output
- **Human imitating bot** — ironic or performative "bot voice"
- **Bot imitating human** — casual engagement-bait or astroturf style

Each user gets a **confidence score (0–100)** and short **reasoning** with linguistic cues.

The **Dead Internet Index** summarizes how much of the thread reads as non-pure-human, weighted by confidence.

## Important disclaimer

Outputs are **statistical vibes, not verdicts**. The tool only sees pasted text — not account history, karma, or identity. Do not use results to harass or accuse real people.

## Supported paste formats

```
u/alice: First comment
u/alice: Second comment from same user
u/bob: Reply
```

Also supported:

- `/u/name: text`
- `Author: name: text`
- `[name]: text`
- `name 42 points: text`

Separate users with new lines. Blank lines are ignored.

## Step-by-step

1. Start the app (`streamlit run app.py` — see [INSTALL.md](INSTALL.md)).
2. Paste your thread into the text area, paste a **Reddit post URL** and click **Load from Reddit**, or click an **example loader** button.
3. Choose **classification mode** in the sidebar:
   - **hybrid** (default): Ollama LLM + heuristics; falls back if Ollama is offline
   - **features_only**: fast stylometric heuristics, no LLM
   - **llm_only**: Ollama only
4. Click **Analyze thread**.
5. Review the summary metrics and per-user table.
6. Expand **detail** sections for full reasoning and cues.

## Understanding results

| Field | Meaning |
|-------|---------|
| Confidence | How strongly the model holds the label (not a legal probability) |
| Low evidence badge | Thin data (e.g. one short comment) or confidence &lt; 40 |
| Dead Internet Index | Higher = more bot-like / performative non-human labels in the thread |
| Cues | Phrases or patterns cited from that user's comments |

## Evaluation dashboard

Open **Evaluation dashboard** in the Streamlit sidebar (not for analyzing pasted threads — coursework / reproducibility only).

At the top you see how many gold participants are in the set and a **tier breakdown** (`synthetic`, `disclosed`, `grid`, `expert`, `edge`) with short descriptions of each source.

Choose an action:

| Action | What it does |
|--------|----------------|
| **View precomputed results** | Loads `results/eval_run.json` and shows metrics for `features_only` and `hybrid` (no Ollama required). Use this for quick review or grading. |
| **Run full suite** | Runs both modes on all 48 gold labels, shows a progress bar, overwrites `results/eval_run.json`, and refreshes confusion matrix PNGs. Pick an Ollama model; hybrid needs Ollama running. |

For each mode you get accuracy, macro-F1, binary macro-F1, high-confidence error count, calibration (mean confidence when correct vs wrong), a confusion matrix image, and a per-label classification report.

Equivalent from the terminal: `python -m src.eval_runner` (interactive model selection and `tqdm` progress). See [INSTALL.md](INSTALL.md).

## Tips for better parsing

- Include consistent `u/username:` prefixes.
- Keep each comment on the same line as its username, or continue on following lines without a new username until the next speaker.
- For very short threads (1 word per user), expect **low evidence** warnings.

## Getting help

See [README.md](../README.md) for repository structure and [LABELING_GUIDELINES.md](LABELING_GUIDELINES.md) for how gold labels are defined in evaluation.
