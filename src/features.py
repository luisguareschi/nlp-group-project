from __future__ import annotations

import math
import re
from dataclasses import dataclass

BOT_PHRASES = [
    "as an ai language model",
    "i cannot provide",
    "it's important to note",
    "in conclusion",
    "i hope this helps",
    "feel free to ask",
    "great question",
    "certainly!",
    "hello fellow humans",
    "greetings fellow",
    "i am a bot",
    "this action was performed automatically",
]

HEDGING = ["perhaps", "might", "could be", "it seems", "arguably", "potentially"]

EMOJI_RE = re.compile(
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF]+", flags=re.UNICODE
)


@dataclass
class UserFeatures:
    username: str
    comment_count: int
    avg_chars: float
    type_token_ratio: float
    emoji_density: float
    bot_phrase_hits: int
    hedging_hits: int
    exclamation_rate: float
    list_pattern_score: float
    all_caps_rate: float
    generic_opener_score: float

    def to_summary(self) -> str:
        return (
            f"comments={self.comment_count}, avg_chars={self.avg_chars:.0f}, "
            f"ttr={self.type_token_ratio:.2f}, emoji_density={self.emoji_density:.3f}, "
            f"bot_phrases={self.bot_phrase_hits}, hedging={self.hedging_hits}, "
            f"exclamations={self.exclamation_rate:.2f}, list_score={self.list_pattern_score:.2f}, "
            f"caps_rate={self.all_caps_rate:.2f}, generic_openers={self.generic_opener_score:.2f}"
        )


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z']+", text.lower())


def extract_features(username: str, comments: list[str]) -> UserFeatures:
    joined = " ".join(comments)
    lower = joined.lower()
    words = _tokenize(joined)
    unique = set(words)
    ttr = len(unique) / max(len(words), 1)

    emojis = len(EMOJI_RE.findall(joined))
    emoji_density = emojis / max(len(joined), 1)

    bot_hits = sum(1 for p in BOT_PHRASES if p in lower)
    hedge_hits = sum(1 for h in HEDGING if h in lower)

    exclamations = joined.count("!") / max(len(comments), 1)

    list_score = 0.0
    for c in comments:
        bullets = len(re.findall(r"(?m)^\s*[-*•]\s", c))
        numbers = len(re.findall(r"(?m)^\s*\d+[\.\)]\s", c))
        if bullets + numbers >= 2:
            list_score += 1.0
    list_score /= max(len(comments), 1)

    caps_words = sum(1 for w in joined.split() if len(w) > 2 and w.isupper())
    caps_rate = caps_words / max(len(joined.split()), 1)

    generic_openers = 0
    for c in comments:
        first = c.strip().split()[:3]
        phrase = " ".join(first).lower()
        if phrase.startswith(("honestly", "great question", "so basically", "well,")):
            generic_openers += 1
    generic_score = generic_openers / max(len(comments), 1)

    return UserFeatures(
        username=username,
        comment_count=len(comments),
        avg_chars=sum(len(c) for c in comments) / max(len(comments), 1),
        type_token_ratio=round(ttr, 3),
        emoji_density=round(emoji_density, 4),
        bot_phrase_hits=bot_hits,
        hedging_hits=hedge_hits,
        exclamation_rate=round(exclamations, 2),
        list_pattern_score=round(list_score, 2),
        all_caps_rate=round(caps_rate, 3),
        generic_opener_score=round(generic_score, 2),
    )


def features_only_classify(features: UserFeatures) -> tuple[str, int, list[str]]:
    """Heuristic label + confidence for ablation / Ollama fallback."""
    score_bot = 0.0
    score_hib = 0.0
    score_bih = 0.0
    cues: list[str] = []

    if features.bot_phrase_hits > 0:
        score_bot += 35
        cues.append("Contains known bot/LLM template phrases")
    if features.list_pattern_score >= 0.5:
        score_bot += 15
        cues.append("Heavy bullet/numbered list formatting")
    if features.hedging_hits >= 2:
        score_bot += 10
        cues.append("Frequent hedging language")

    if "fellow humans" in " ".join([]).lower():
        pass
    if features.avg_chars < 25 and features.comment_count <= 2:
        score_bih += 10
        cues.append("Very short comments — low signal")

    if features.generic_opener_score >= 0.5:
        score_bih += 30
        cues.append("Generic engagement-bait openers")
    if features.type_token_ratio < 0.55 and features.avg_chars > 60:
        score_bih += 25
        cues.append("Low lexical diversity in relatively long comments")
    if features.exclamation_rate >= 1.0 and features.hedging_hits >= 1:
        score_bih += 15
        cues.append("Enthusiastic + hedging reply-guy tone")

    if features.exclamation_rate > 1.5 and features.emoji_density > 0.01:
        score_hib -= 5  # more human-like chaos

    # human_imitating_bot: stiff + joke cues
    if features.bot_phrase_hits == 0 and features.all_caps_rate > 0.05:
        score_hib += 15
        cues.append("ALL CAPS performance energy")

    scores = {
        "bot": score_bot,
        "bot_imitating_human": score_bih,
        "human_imitating_bot": score_hib,
        "human": max(5.0, 30 - score_bot - score_bih - score_hib),
    }
    label = max(scores, key=scores.get)  # type: ignore[arg-type]
    raw_conf = min(95, int(scores[label] + 25))
    if features.comment_count == 1 and features.avg_chars < 20:
        raw_conf = min(raw_conf, 55)
        cues.append("Single short comment — confidence capped")
    return label, raw_conf, cues[:4]
