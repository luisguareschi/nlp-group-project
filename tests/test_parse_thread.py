from src.parse_thread import parse_thread


def test_u_prefix_format():
    text = "u/alice: hello\nu/bob: hi back\nu/alice: again"
    p = parse_thread(text)
    assert "alice" in p
    assert "bob" in p
    assert len(p["alice"]) == 2
    assert p["bob"][0] == "hi back"


def test_author_format():
    text = "Author: mod_bot: This is automated"
    p = parse_thread(text)
    assert "mod_bot" in p


def test_empty_returns_empty():
    assert parse_thread("") == {}
