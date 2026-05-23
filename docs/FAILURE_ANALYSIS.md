# Failure Mode Analysis

Documented failures from `features_only` / hybrid evaluation on `data/eval/participants.jsonl` (n=48). Re-run after prompt changes: `python -m src.eval_runner`.

## Summary metrics (features_only baseline)

See `results/eval_run.json`. Typical pattern: strong **human** recall, weak **bot_imitating_human** recall — engagement-bait voice overlaps with concise human replies.

---

## Case 1: Irony / shitpost classified as bot

| Field | Value |
|-------|-------|
| Thread | `edge_02` / `copypasta` |
| Gold | `human_imitating_bot` |
| Predicted | Often `bot` or `human` |
| Snippet | "Did you know? The average person walks past 36 murderers..." |
| Hypothesis | Template-shaped copypasta triggers `bot_phrase` and list heuristics without irony context |

---

## Case 2: Actual bot with casual slang → human

| Field | Value |
|-------|-------|
| Thread | `grid_*` / short GPT comments |
| Gold | `bot` |
| Predicted | `human` |
| Snippet | "nah the bus was 40 min late" (human) vs formal GPT (bot) — inverted when GPT uses plain tone |
| Hypothesis | Short, informal **human** comments dominate training heuristics; formal bots easier than casual LLM |

---

## Case 3: Single-word comments → overconfident guess

| Field | Value |
|-------|
| Thread | `edge_01` / `short_one`, `short_two` |
| Gold | `human` |
| Predicted | Variable |
| Snippet | `lol`, `this` |
| Hypothesis | Parser works; features thin. Confidence cap at 55 mitigates but label still unstable |

---

## Case 4: human_imitating_bot vs bot_imitating_human confusion

| Field | Value |
|-------|-------|
| Thread | `synthetic_01` / `hib_charlie` vs `bih_dana` |
| Gold | `human_imitating_bot` vs `bot_imitating_human` |
| Predicted | Cross-confusion common |
| Hypothesis | Both use performative register; distinction needs **intent** not in text. Core limitation for report |

---

## Case 5: Copypasta (human) vs LLM template (bot)

| Field | Value |
|-------|-------|
| Thread | `edge_02` |
| Gold | `copypasta` → `human_imitating_bot`; `template_bot` → `bot` |
| Predicted | Both pull toward `bot` |
| Hypothesis | Surface form overlap; thread-level context helps LLM mode |

---

## Case 6: Non-English / mixed language

| Field | Value |
|-------|-------|
| Thread | `edge_03` / `mixed_lang` |
| Gold | `human` |
| Snippet | "no sé honestly the thread went off the rails" |
| Hypothesis | Stylometric features tuned on English; code-switching underrepresented in gold set

---

## Case 7: Moderator bot — right label, wrong nuance

| Field | Value |
|-------|-------|
| Thread | `edge_04` / `mod_helpful` |
| Gold | `bot` |
| Predicted | `bot` (often correct) |
| Snippet | "I am a bot. This action was performed automatically." |
| Failure mode | Reasoning may say "spam" when behavior is **helpful moderation** — label correct, explanation wrong |

---

## Case 8: LLM rationalization (hybrid mode)

| Field | Value |
|-------|-------|
| Thread | Expert-tier ambiguous users |
| Gold | `bot_imitating_human` |
| Predicted | `human` with plausible reasoning |
| Hypothesis | Ollama cites cues post hoc; **hallucinated evidence** risk when JSON reasoning not tied to strict quotes |

---

## Case 9: Coordinated humans → false bot cluster

| Field | Value |
|-------|-------|
| Thread | `edge_04` / `coordinated` |
| Gold | `bot_imitating_human` |
| Snippet | "Great point!" / "Absolutely agree!" |
| Hypothesis | Similar phrasing across users looks like bot coordination; may be human pile-on

---

## Case 10: Nested meme performance

| Field | Value |
|-------|-------|
| Thread | `synthetic_01` / `hib_charlie` |
| Gold | `human_imitating_bot` |
| Note | Recursing "bot imitating human imitating bot" is **out of taxonomy** by design |
| Hypothesis | Collapsed to `human_imitating_bot`; discuss in presentation as cultural layer, not metric class

---

## Mitigations attempted in code

- Confidence cap for single short comments
- `low_evidence` badge when confidence &lt; 40
- Hybrid mode passes stylometric summary into LLM prompt
- Prompt requires cues from user text only

## Recommended future work

- Thread-level context model (reply-to structure)
- Per-language feature normalization
- Calibrated classifier on larger gold set
- Human baseline study (annotator vs tool)
