# Labeling Guidelines

Use these definitions when creating or reviewing gold labels in `data/eval/participants.jsonl`.

## Gold set tiers (`gold_tier`)

Each eval row has a `gold_tier` field. The **Evaluation dashboard** lists counts and descriptions; use this table when authoring or reviewing labels.

| Tier | Meaning |
|------|---------|
| `synthetic` | Team-authored role-play threads covering all four label types; gold labels are high-confidence by design. |
| `disclosed` | Bots that explicitly disclose automation (AutoMod, wiki bots) alongside ordinary human replies. |
| `grid` | GRiD-style paired snippets: a casual human comment vs. a GPT reply on the same topic. |
| `expert` | De-identified excerpts from real threads; majority-vote labels; `annotator_disagreement` when annotators split. |
| `edge` | Hard cases: very short comments, sarcasm, copypasta, multilingual text, helpful mod bots vs. spam, coordinated phrasing. |

## `human`

- Natural variation, typos, personal anecdotes, inconsistent tone
- Reacts specifically to prior comments in the thread
- No template-heavy structure across multiple comments

## `bot`

- Generic, context-light replies; disclosure lines ("I am a bot")
- Highly regular structure; wiki/AutoMod style
- Classic LLM tells: "As an AI language model", numbered lists without prompting

## `human_imitating_bot`

- Obvious performance: "Greetings fellow humans", excessive formality as joke
- Copypasta or meme formats posted knowingly
- Author confirms role-play (synthetic tier)

## `bot_imitating_human`

- Over-casual LLM voice: "Honestly?", "Great question!", engagement bait
- Suspiciously helpful + generic across comments
- Astroturf or spammy enthusiasm without human messiness

## Confidence (for expert tier)

Annotators may add notes when uncertain. Majority vote wins; flag `annotator_disagreement: true` if split 2-1.

## Do not use

- Account karma, age, or profile metadata (not available in paste-only POC)
- Political affiliation or toxicity as bot signals
