from __future__ import annotations

import json
import re
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from pathlib import Path

from src.features import UserFeatures, extract_features, features_only_classify
from src.parse_thread import format_thread_for_prompt
from src.schemas import LABELS, ClassificationResult, Label

PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "classify_user.txt"

OLLAMA_TIMEOUT_SECONDS = 40
SHORT_COMMENT_CHAR_LIMIT = 20
LOW_EVIDENCE_THRESHOLD = 40
SHORT_COMMENT_CONF_CAP = 60


def load_system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        return json.loads(m.group(0))
    raise ValueError("No JSON object in model response")


def _apply_confidence_rules(
    result: ClassificationResult,
    features: UserFeatures,
) -> ClassificationResult:
    low = result.confidence < LOW_EVIDENCE_THRESHOLD
    if features.comment_count == 1 and features.avg_chars < SHORT_COMMENT_CHAR_LIMIT:
        result.confidence = min(result.confidence, SHORT_COMMENT_CONF_CAP)
        low = True
    result.low_evidence = low
    return result


def classify_with_ollama(
    username: str,
    comments: list[str],
    thread_context: dict[str, list[str]],
    *,
    model: str = "llama3.2:3b",
    temperature: float = 0.2,
    mode: str = "hybrid",
    timestamps: list[int] | None = None,
) -> ClassificationResult:
    import ollama

    features = extract_features(username, comments, timestamps=timestamps)
    feat_label, feat_conf, feat_cues = features_only_classify(features)

    system = load_system_prompt()
    thread_text = format_thread_for_prompt(thread_context)
    user_block = "\n".join(f"  - {c}" for c in comments)

    user_msg = f"""## Full thread (all participants)
{thread_text}

## Target participant: u/{username}
Comments:
{user_block}

## Stylometric signals (heuristic, not ground truth)
{features.to_summary()}
Heuristic-only guess: {feat_label} ({feat_conf}%)

Signal interpretation hints:
- High generic_opener_score + low type_token_ratio in long comments → likely bot_imitating_human
- bot_phrase_hits > 0 + list_pattern_score > 0 → likely bot
- High all_caps_rate with no bot phrases → likely human_imitating_bot (ironic)
- Low scores across all signals, idiosyncratic phrasing → likely human

Classify u/{username}. Return JSON only."""

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]
    options = {"temperature": temperature}
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(ollama.chat, model=model, messages=messages, options=options)
        try:
            response = future.result(timeout=OLLAMA_TIMEOUT_SECONDS)
        except FuturesTimeoutError:
            raise RuntimeError(f"Ollama timed out after {OLLAMA_TIMEOUT_SECONDS}s")
    raw = response["message"]["content"]
    data = _extract_json(raw)

    label = data.get("label", feat_label)
    if label not in LABELS:
        label = feat_label

    result = ClassificationResult(
        username=username,
        label=label,  # type: ignore[arg-type]
        confidence=int(data.get("confidence", feat_conf)),
        reasoning=str(data.get("reasoning", "No reasoning provided.")),
        cues=list(data.get("cues", feat_cues))[:6],
        mode=mode,
    )
    return _apply_confidence_rules(result, features)


def classify_features_only(
    username: str,
    comments: list[str],
    timestamps: list[int] | None = None,
) -> ClassificationResult:
    features = extract_features(username, comments, timestamps=timestamps)
    label, conf, cues = features_only_classify(features)
    result = ClassificationResult(
        username=username,
        label=label,  # type: ignore[arg-type]
        confidence=conf,
        reasoning=(
            f"Heuristic classification from stylometric signals only. "
            f"{features.to_summary()}"
        ),
        cues=cues,
        mode="features_only",
    )
    return _apply_confidence_rules(result, features)


def classify_participant(
    username: str,
    comments: list[str],
    thread_context: dict[str, list[str]],
    *,
    mode: str = "hybrid",
    model: str = "llama3.2:3b",
    temperature: float = 0.2,
    timestamps: list[int] | None = None,
) -> ClassificationResult:
    if mode == "features_only":
        return classify_features_only(username, comments, timestamps=timestamps)

    if mode == "llm_only":
        try:
            return classify_with_ollama(
                username,
                comments,
                thread_context,
                model=model,
                temperature=temperature,
                mode="llm_only",
                timestamps=timestamps,
            )
        except Exception as e:
            r = classify_features_only(username, comments, timestamps=timestamps)
            r.reasoning = f"Ollama unavailable ({e}). Fallback heuristics used."
            r.mode = "llm_only_fallback"
            return r

    # hybrid: try Ollama, fallback features
    try:
        return classify_with_ollama(
            username,
            comments,
            thread_context,
            model=model,
            temperature=temperature,
            mode="hybrid",
            timestamps=timestamps,
        )
    except Exception:
        return classify_features_only(username, comments, timestamps=timestamps)


def analyze_thread(
    participants: dict[str, list[str]],
    *,
    mode: str = "hybrid",
    model: str = "llama3.2:3b",
    temperature: float = 0.2,
    on_progress: Callable[[int, int], None] | None = None,
    timestamps_dict: dict[str, list[int]] | None = None,
) -> list[ClassificationResult]:
    total_comments = sum(len(comments) for comments in participants.values())
    completed_comments = 0
    if on_progress is not None:
        on_progress(0, total_comments)

    results: list[ClassificationResult] = []
    for user, comments in participants.items():
        user_timestamps = (timestamps_dict or {}).get(user)
        results.append(
            classify_participant(
                user,
                comments,
                participants,
                mode=mode,
                model=model,
                temperature=temperature,
                timestamps=user_timestamps,
            )
        )
        completed_comments += len(comments)
        if on_progress is not None:
            on_progress(completed_comments, total_comments)
    return results


def ollama_available() -> bool:
    try:
        import ollama

        ollama.list()
        return True
    except Exception:
        return False

def list_ollama_models() -> list[str]:
    if ollama_available():
        import ollama
        models = ollama.list()
        return [model.model for model in models.models]
    return []
