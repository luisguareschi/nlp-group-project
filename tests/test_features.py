from src.features import extract_features, features_only_classify


def test_bot_phrase_detection():
    f = extract_features(
        "gpt_user",
        ["As an AI language model, I cannot provide medical advice."],
    )
    assert f.bot_phrase_hits >= 1
    label, conf, cues = features_only_classify(f)
    assert label == "bot"
    assert conf > 0


def test_human_short_comment_cap():
    f = extract_features("x", ["lol"])
    label, conf, _ = features_only_classify(f)
    assert conf <= 55
