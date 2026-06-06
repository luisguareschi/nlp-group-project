from __future__ import annotations

from src.schemas import ClassificationResult, ThreadAnalysis

NON_HUMAN_LABELS = {"bot", "human_imitating_bot", "bot_imitating_human"}


def compute_dead_internet_index(results: list[ClassificationResult]) -> float:
    """
    Weighted share of non-pure-human participants.
    Each non-human label contributes confidence/100; humans contribute 0.
    """
    if not results:
        return 0.0
    total = 0.0
    for r in results:
        if r.label in NON_HUMAN_LABELS:
            total += r.confidence / 100.0
    return round(100.0 * total / len(results), 1)


def build_thread_analysis(results: list[ClassificationResult]) -> ThreadAnalysis:
    counts: dict[str, int] = {}
    for r in results:
        counts[r.label] = counts.get(r.label, 0) + 1
    return ThreadAnalysis(
        participants=results,
        dead_internet_index=compute_dead_internet_index(results),
        label_counts=counts,
    )
