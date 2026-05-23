from __future__ import annotations

import json
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ProgressCallback = Callable[[str, int, int], None]

# Writable matplotlib cache inside repo (CI/sandbox friendly)
_MPL_DIR = Path(__file__).resolve().parents[1] / "results" / ".matplotlib"
_MPL_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(_MPL_DIR))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

from src.classify import classify_participant, list_ollama_models
from src.schemas import LABELS

EVAL_PATH = Path(__file__).resolve().parents[1] / "data" / "eval" / "participants.jsonl"
RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


@dataclass
class EvalRow:
    thread_id: str
    username: str
    comments: list[str]
    gold_label: str
    gold_tier: str
    notes: str = ""
    annotator_disagreement: bool = False


def load_eval(path: Path | None = None) -> list[EvalRow]:
    path = path or EVAL_PATH
    rows: list[EvalRow] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            rows.append(
                EvalRow(
                    thread_id=d["thread_id"],
                    username=d["username"],
                    comments=d["comments"],
                    gold_label=d["gold_label"],
                    gold_tier=d.get("gold_tier", "unknown"),
                    notes=d.get("notes", ""),
                    annotator_disagreement=d.get("annotator_disagreement", False),
                )
            )
    return rows


def _binary(label: str) -> str:
    return "human" if label == "human" else "non_human"


def run_eval(
    rows: list[EvalRow] | None = None,
    *,
    mode: str = "features_only",
    model: str = "llama3.2:3b",
    tier_filter: str | None = None,
    on_progress: ProgressCallback | None = None,
) -> dict:
    rows = rows or load_eval()
    if tier_filter:
        rows = [r for r in rows if r.gold_tier == tier_filter]

    # Build thread context per thread_id for realistic classification
    thread_participants: dict[str, dict[str, list[str]]] = {}
    for r in rows:
        thread_participants.setdefault(r.thread_id, {})[r.username] = r.comments

    y_true: list[str] = []
    y_pred: list[str] = []
    confidences: list[int] = []
    correct_flags: list[bool] = []

    total = len(rows)
    for i, r in enumerate(rows, start=1):
        if on_progress:
            on_progress(
                f"{mode}: classifying {r.username} ({i}/{total})",
                i,
                total,
            )
        ctx = thread_participants[r.thread_id]
        pred = classify_participant(
            r.username,
            r.comments,
            ctx,
            mode=mode,
            model=model,
        )
        y_true.append(r.gold_label)
        y_pred.append(pred.label)
        confidences.append(pred.confidence)
        correct_flags.append(pred.label == r.gold_label)

    labels_present = sorted(set(y_true) | set(y_pred))
    macro_f1 = f1_score(y_true, y_pred, average="macro", labels=labels_present, zero_division=0)
    acc = accuracy_score(y_true, y_pred)

    conf_correct = np.mean([c for c, ok in zip(confidences, correct_flags) if ok]) if any(correct_flags) else 0
    conf_wrong = (
        np.mean([c for c, ok in zip(confidences, correct_flags) if not ok])
        if not all(correct_flags)
        else 0
    )
    high_conf_wrong = sum(
        1 for c, ok in zip(confidences, correct_flags) if not ok and c >= 70
    )

    y_true_bin = [_binary(y) for y in y_true]
    y_pred_bin = [_binary(y) for y in y_pred]
    binary_f1 = f1_score(y_true_bin, y_pred_bin, average="macro", zero_division=0)

    report = classification_report(
        y_true, y_pred, labels=labels_present, zero_division=0, output_dict=True
    )

    return {
        "mode": mode,
        "n": len(rows),
        "accuracy": round(acc, 4),
        "macro_f1": round(macro_f1, 4),
        "binary_macro_f1": round(binary_f1, 4),
        "mean_confidence_when_correct": round(float(conf_correct), 2),
        "mean_confidence_when_wrong": round(float(conf_wrong), 2),
        "high_confidence_errors": high_conf_wrong,
        "classification_report": report,
        "y_true": y_true,
        "y_pred": y_pred,
        "labels": labels_present,
    }


def save_confusion_matrix(metrics: dict, out_path: Path) -> None:
    cm = confusion_matrix(metrics["y_true"], metrics["y_pred"], labels=metrics["labels"])
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(len(metrics["labels"])))
    ax.set_yticks(range(len(metrics["labels"])))
    ax.set_xticklabels(metrics["labels"], rotation=45, ha="right")
    ax.set_yticklabels(metrics["labels"])
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Gold")
    ax.set_title(f"Confusion matrix ({metrics['mode']}, n={metrics['n']})")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center", color="black")
    fig.colorbar(im)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def run_full_eval_suite(
    model: str = "llama3.2:3b",
    on_progress: ProgressCallback | None = None,
) -> dict:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    modes = ("features_only", "hybrid")
    rows = load_eval()
    n = len(rows)
    total_steps = len(modes) * (n + 1) + 1

    def report(message: str, step: int) -> None:
        if on_progress:
            on_progress(message, step, total_steps)

    suite: dict = {}
    step = 0
    for mode in modes:
        try:

            def mode_progress(message: str, current: int, _local_total: int) -> None:
                report(message, step + current)

            m = run_eval(mode=mode, model=model, on_progress=mode_progress)
            step += n
            suite[mode] = {
                k: v for k, v in m.items() if k not in ("y_true", "y_pred", "labels")
            }
            save_confusion_matrix(
                m, RESULTS_DIR / f"confusion_matrix_{mode}.png"
            )
            step += 1
            report(f"Saved confusion matrix ({mode})", step)
        except Exception as e:
            step += n + 1
            suite[mode] = {"error": str(e)}

    step += 1
    report("Writing eval_run.json", step)
    out = RESULTS_DIR / "eval_run.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(suite, f, indent=2)
    return suite


if __name__ == "__main__":
    from tqdm import tqdm

    _progress_bar: list[tqdm | None] = [None]

    def on_progress(message: str, current: int, total: int) -> None:
        bar = _progress_bar[0]
        if bar is None:
            bar = tqdm(total=total, unit="step", dynamic_ncols=True)
            _progress_bar[0] = bar
        if bar.total != total:
            bar.reset(total=total)
        bar.n = current
        bar.set_description(message, refresh=False)
        bar.refresh()

    print("Available models:")
    available_models = list_ollama_models()
    for i, model in enumerate(available_models):
        print(f"{i+1}. {model}")
    if not available_models:
        print("No models available. Please install Ollama and try again.")
        exit(1)
    selected_model = int(input("Enter the number of the model you want to use: "))
    selected_model = available_models[selected_model - 1]
    try:
        suite = run_full_eval_suite(model=selected_model, on_progress=on_progress)
    finally:
        if _progress_bar[0] is not None:
            _progress_bar[0].close()
    print(json.dumps(suite, indent=2))
    print("Evaluation complete!")
    print(f"Results saved to {RESULTS_DIR / 'eval_run.json'}")
    print("You can now view the results in the browser by running the Streamlit app and navigating to the Evaluation dashboard page.")
