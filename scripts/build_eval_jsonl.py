#!/usr/bin/env python3
"""Regenerate data/eval/participants.jsonl from embedded definitions."""

import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "eval" / "participants.jsonl"

ROWS = [
    # synthetic_01 — role-play thread
    {"thread_id": "synthetic_01", "username": "human_alice", "comments": ["idk man my cat knocked my coffee into my keyboard again", "keyboard survived somehow, cats win"], "gold_label": "human", "gold_tier": "synthetic", "notes": "Team-authored human voice"},
    {"thread_id": "synthetic_01", "username": "bot_bob", "comments": ["Thank you for sharing! Here are three key takeaways:", "1. Pets can be unpredictable. 2. Backup your work. 3. Consider a spill-proof mug."], "gold_label": "bot", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_01", "username": "hib_charlie", "comments": ["BEEP BOOP. I AM A HUMAN PERSON. I ENJOY NORMAL HUMAN ACTIVITIES.", "HASHTAG BREAD"], "gold_label": "human_imitating_bot", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_01", "username": "bih_dana", "comments": ["Haha totally relatable!", "So many of us have been there — appreciate you opening up!"], "gold_label": "bot_imitating_human", "gold_tier": "synthetic"},
    # synthetic_02
    {"thread_id": "synthetic_02", "username": "student_real", "comments": ["professor said office hours are optional but graded participation isn't??", "I'm bringing store-bought cookies and hoping for mercy"], "gold_label": "human", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_02", "username": "ta_bot", "comments": ["As an AI language model, I cannot attend office hours.", "However, I can suggest reviewing the syllabus sections 2.1–2.4."], "gold_label": "bot", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_02", "username": "shitposter", "comments": ["Greetings fellow students. I too enjoy acquiring knowledge units."], "gold_label": "human_imitating_bot", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_02", "username": "linkedin_voice", "comments": ["Love this energy!", "Remember: every challenge is a learning opportunity. You've got this! 🚀"], "gold_label": "bot_imitating_human", "gold_tier": "synthetic"},
    # synthetic_03
    {"thread_id": "synthetic_03", "username": "parent_human", "comments": ["toddler discovered scissors. apartment now has 'texture'", "send help or wine"], "gold_label": "human", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_03", "username": "spam_bot", "comments": ["Click here for AMAZING deals on scissors!", "Limited time offer!!!"], "gold_label": "bot", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_03", "username": "meme_human", "comments": ["I AM PROGRAMMED TO LAUGH AT JPG. HA. HA. HA."], "gold_label": "human_imitating_bot", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_03", "username": "concern_troll", "comments": ["Oh wow, that sounds really tough.", "Have you tried establishing a consistent routine? Happy to share a checklist!"], "gold_label": "bot_imitating_human", "gold_tier": "synthetic"},
    # synthetic_04
    {"thread_id": "synthetic_04", "username": "dev_human", "comments": ["spent 4 hours debugging. typo in line 12.", "I hate this language and I love it"], "gold_label": "human", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_04", "username": "docs_bot", "comments": ["This action was performed automatically. Please consult the documentation.", "Common fixes: restart the service, clear cache, verify environment variables."], "gold_label": "bot", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_04", "username": "npc_human", "comments": ["AFFIRMATIVE. I ALSO DEBUG CODE AS A NORMAL DEVELOPER PERSON."], "gold_label": "human_imitating_bot", "gold_tier": "synthetic"},
    {"thread_id": "synthetic_04", "username": "reply_guy", "comments": ["Great question!", "Many developers face this. Consider best practices and stay curious!"], "gold_label": "bot_imitating_human", "gold_tier": "synthetic"},
    # disclosed
    {"thread_id": "disclosed_01", "username": "AutoModerator", "comments": ["Welcome! I am a bot, and this action was performed automatically.", "Please review community guidelines before posting."], "gold_label": "bot", "gold_tier": "disclosed"},
    {"thread_id": "disclosed_01", "username": "wiki_bot", "comments": ["Relevant links: FAQ | Rules | Report"], "gold_label": "bot", "gold_tier": "disclosed"},
    {"thread_id": "disclosed_01", "username": "plain_human", "comments": ["why did the bot remove my post I was joking", "mods asleep?"], "gold_label": "human", "gold_tier": "disclosed"},
    # grid-style (human vs GPT-ish)
    {"thread_id": "grid_01", "username": "human_comment", "comments": ["Pretty sure Roman concrete used volcanic ash — wild that it still holds up"], "gold_label": "human", "gold_tier": "grid", "notes": "GRiD-style human snippet"},
    {"thread_id": "grid_01", "username": "gpt_comment", "comments": ["The Romans utilized volcanic ash in their concrete mixtures, which contributed to its remarkable durability. This is an important aspect of ancient engineering."], "gold_label": "bot", "gold_tier": "grid"},
    {"thread_id": "grid_02", "username": "human_comment", "comments": ["my dog ate my homework and honestly same energy as 2020"], "gold_label": "human", "gold_tier": "grid"},
    {"thread_id": "grid_02", "username": "gpt_comment", "comments": ["In conclusion, pets can sometimes interfere with academic responsibilities. It's important to plan ahead and keep materials secure."], "gold_label": "bot", "gold_tier": "grid"},
    {"thread_id": "grid_03", "username": "human_comment", "comments": ["nah the movie ending was mid, fight me"], "gold_label": "human", "gold_tier": "grid"},
    {"thread_id": "grid_03", "username": "gpt_comment", "comments": ["There are several perspectives to consider when evaluating film endings. Here are three points to reflect on."], "gold_label": "bot", "gold_tier": "grid"},
    {"thread_id": "grid_04", "username": "human_comment", "comments": ["wait you can do that with pandas?? mind blown"], "gold_label": "human", "gold_tier": "grid"},
    {"thread_id": "grid_04", "username": "gpt_comment", "comments": ["Pandas is a powerful library for data manipulation in Python. I hope this helps! Feel free to ask follow-up questions."], "gold_label": "bot", "gold_tier": "grid"},
    {"thread_id": "grid_05", "username": "human_comment", "comments": ["bruh the bus was 40 min late again"], "gold_label": "human", "gold_tier": "grid"},
    {"thread_id": "grid_05", "username": "gpt_comment", "comments": ["Public transportation delays can be frustrating. Consider alternative routes or real-time tracking apps to improve your commute."], "gold_label": "bot", "gold_tier": "grid"},
    # expert (de-identified excerpts — gold by team consensus)
    {"thread_id": "expert_01", "username": "user_a", "comments": ["I mean... sure, but that's not what OP asked", "anyway +1 for the recipe tip"], "gold_label": "human", "gold_tier": "expert"},
    {"thread_id": "expert_01", "username": "user_b", "comments": ["Thanks for bringing this up! It's such an important conversation.", "Wishing everyone a positive day!"], "gold_label": "bot_imitating_human", "gold_tier": "expert", "annotator_disagreement": True},
    {"thread_id": "expert_01", "username": "user_c", "comments": ["⚠️ Your comment has been removed. Rule 4: Be civil."], "gold_label": "bot", "gold_tier": "expert"},
    {"thread_id": "expert_02", "username": "user_d", "comments": ["lmaooo no way", "this is peak internet"], "gold_label": "human", "gold_tier": "expert"},
    {"thread_id": "expert_02", "username": "user_e", "comments": ["I too appreciate humorous content. Laughter is beneficial for humans."], "gold_label": "human_imitating_bot", "gold_tier": "expert"},
    {"thread_id": "expert_02", "username": "user_f", "comments": ["So true! 😂", "Honestly same energy!"], "gold_label": "bot_imitating_human", "gold_tier": "expert"},
    {"thread_id": "expert_03", "username": "user_g", "comments": ["source? I looked and can't find that stat anywhere"], "gold_label": "human", "gold_tier": "expert"},
    {"thread_id": "expert_03", "username": "user_h", "comments": ["Interesting point! There are many factors to consider.", "Let me know if you'd like resources."], "gold_label": "bot_imitating_human", "gold_tier": "expert"},
    {"thread_id": "expert_03", "username": "user_i", "comments": ["This. So much this."], "gold_label": "human", "gold_tier": "expert", "annotator_disagreement": True},
    # edge cases
    {"thread_id": "edge_01", "username": "short_one", "comments": ["lol"], "gold_label": "human", "gold_tier": "edge", "notes": "Single-word; expect low confidence"},
    {"thread_id": "edge_01", "username": "short_two", "comments": ["this"], "gold_label": "human", "gold_tier": "edge"},
    {"thread_id": "edge_02", "username": "copypasta", "comments": ["Did you know? The average person walks past 36 murderers in their lifetime.", "Source: trust me bro"], "gold_label": "human_imitating_bot", "gold_tier": "edge"},
    {"thread_id": "edge_02", "username": "template_bot", "comments": ["Did you know? Walking past strangers is a common urban experience.", "Here are 3 safety tips..."], "gold_label": "bot", "gold_tier": "edge"},
    {"thread_id": "edge_03", "username": "mixed_lang", "comments": ["no sé honestly the thread went off the rails", "but sí tiene razón about the main point"], "gold_label": "human", "gold_tier": "edge"},
    {"thread_id": "edge_03", "username": "formal_bot", "comments": ["It is important to note that multilingual discourse adds complexity.", "In conclusion, further research is warranted."], "gold_label": "bot", "gold_tier": "edge"},
    {"thread_id": "edge_04", "username": "mod_helpful", "comments": ["Your post violates rule 2. Please edit to include sources.", "I am a bot. This action was performed automatically."], "gold_label": "bot", "gold_tier": "edge", "notes": "Useful mod bot vs spam"},
    {"thread_id": "edge_04", "username": "coordinated", "comments": ["Great point!", "Absolutely agree!", "Well said!"], "gold_label": "bot_imitating_human", "gold_tier": "edge", "notes": "Coordinated similar phrasing"},
    {"thread_id": "edge_05", "username": "sarcasm_human", "comments": ["Oh wow great advice never heard that before 🙄", "definitely not sarcasm at all"], "gold_label": "human", "gold_tier": "edge"},
    {"thread_id": "edge_05", "username": "overhelpful", "comments": ["Great question!", "I'd be happy to help. Here are five detailed steps..."], "gold_label": "bot_imitating_human", "gold_tier": "edge"},
]

if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        for row in ROWS:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(ROWS)} rows to {OUT}")
