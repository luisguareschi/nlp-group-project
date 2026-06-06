# Individual Reflection — Luis Guareschi

---

## Specific contributions

I built the proof-of-concept end to end: the parsing and classification pipeline (`src/parse_thread.py`, `src/features.py`, `src/classify.py`, `src/aggregate.py`), the Streamlit app and Evaluation dashboard, the evaluation harness (`src/eval_runner.py`) over our 48-participant gold set, and Reddit URL fetching (`src/reddit_fetch.py`). I also defined the four-label taxonomy, contributed to `data/eval/participants.jsonl`, drafted `docs/FAILURE_ANALYSIS.md`, and wrote the install guide, user manual, README, and report outlines.

---

## What I learned

The most important lesson was that **problem framing matters as much as model choice**. "Bot or not?" is too coarse for real threads; the imitation categories (`human_imitating_bot`, `bot_imitating_human`) capture behavior readers actually notice, but they are also the hardest to label and classify. Building a tiered gold set — synthetic, disclosed, GRiD-style, expert, and edge cases — forced me to be honest about where ground truth is strong versus where I am making judgment calls.

Empirically, I learned that **a hybrid pipeline is not automatically better than heuristics alone**. Our `features_only` baseline reached roughly 60% accuracy and 0.51 macro-F1 on 48 labels, with strong human recall but very weak `bot_imitating_human` recall. Adding a local LLM improved some cases but introduced rationalized cues that do not always match the text. That gap between confidence and correctness reinforced why we cap confidence on short comments and frame output as probabilistic, not accusatory.

On process, I learned how to **use AI coding assistants effectively without outsourcing judgment**. Cursor and Claude helped with boilerplate, parser regex, and documentation drafts, but every label definition, eval design choice, failure interpretation, and ethical framing decision was mine to own and defend in Q&A.

Finally, **shipping an early end-to-end POC** made later iteration much more productive — concrete failures in the eval dashboard and confusion matrices were far more useful than planning on paper.
