# Labeling Guidelines

Use these definitions when creating or reviewing gold labels in `data/eval/participants.jsonl`.

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
