from src.eval_runner import load_eval, run_eval


def test_eval_set_size():
    rows = load_eval()
    assert len(rows) >= 30


def test_features_only_eval_runs():
    metrics = run_eval(mode="features_only")
    assert metrics["n"] >= 30
    assert 0 <= metrics["macro_f1"] <= 1
