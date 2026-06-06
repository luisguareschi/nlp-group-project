# Topic Brief: Dead Internet Detector

**Course:** NLP Group Project — Option 1 (Application Development)  
**Status:** Pending instructor approval

## One-line pitch

A Streamlit app that parses pasted social threads and estimates, per participant, whether they read as human, bot, human-imitating-bot, or bot-imitating-human — with confidence scores and cited linguistic cues.

## Label taxonomy

| Label | Definition |
|-------|------------|
| `human` | Likely genuine human participant |
| `bot` | Likely automated or LLM-generated without casual-human mimicry |
| `human_imitating_bot` | Human deliberately performing "bot voice" (irony, copypasta, etc.) |
| `bot_imitating_human` | Bot performing casual human voice (engagement bait, astroturf) |

## Evaluation approach

30–50 participant-level gold labels across tiered sources: team synthetic role-play threads, disclosed bots, GRiD-style human/GPT snippets, and expert-consensus excerpts. Metrics: macro-F1, calibration, ablation (LLM vs features vs hybrid).

## Ethics

Output is framed as probabilistic "vibes," not accusations. No live account targeting or moderation automation in the POC.
