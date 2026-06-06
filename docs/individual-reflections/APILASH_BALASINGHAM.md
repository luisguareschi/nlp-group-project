# Individual Reflection — Apilash Balasingham

---

## Specific contributions

My work focused on extending the application layer once the core pipeline was in place. I added result export (CSV and JSON download), an annotated thread view that colour-codes each comment by its predicted label, a shareable URL that encodes the thread with gzip + base64 so a link opens the app pre-loaded, and a side-by-side mode comparison that runs `features_only` and `hybrid` in parallel and surfaces where they disagree. On the signal side I extended `src/reddit_fetch.py` to capture per-comment timestamps from old.reddit HTML, propagated those timestamps through the classification pipeline, and added `reply_interval_cv` — the coefficient of variation of inter-comment gaps — as a temporal bot signal in `src/features.py`. I also kept the README up to date as features were added.

---

## What I learned

The most concrete lesson was that **UX and interpretability are part of the NLP work, not separate from it**. Adding the annotated thread view made misclassifications immediately visible in a way that confusion matrices did not — you could see at a glance that a sarcastic commenter was being flagged red while an obviously templated reply sat green. That kind of direct feedback loop is more actionable than aggregate F1 scores, and it changed how I thought about what the tool actually needs to communicate.

Working on the mode comparison feature taught me that **disagreement between a heuristic and an LLM is itself a signal worth exposing**. Cases where `features_only` and `hybrid` agree are usually either clear-cut or both wrong in the same way; cases where they diverge are almost always the interesting edge cases from the failure analysis — irony, code-switching, casual-tone bots. Surfacing those disagreements explicitly in the UI turns a limitation into a feature.

The temporal feature work highlighted a gap between what is **theoretically a strong signal and what the data actually supports**. Uniform reply timing is a well-documented bot indicator, but in practice most pasted threads lack timestamps, and Reddit's old HTML only carries them for HTML-fetched threads. The feature is architecturally in place, but it will only matter at scale with richer data — a reminder that signal engineering and data collection are not independent problems.

Finally, I learned that **treating the share link as a clipboard action rather than a copy-paste instruction is a small change with a disproportionate effect on usability**. The difference between showing a user an encoded string and having the button copy a ready-to-send URL is the difference between a feature people actually use and one they ignore. Sweating that detail felt like over-engineering at first, but it reflects the broader principle that a tool is only useful if people can share what they find with it.
