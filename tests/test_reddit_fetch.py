from src.reddit_fetch import (
    RedditFetchError,
    reddit_html_to_paste,
    reddit_json_url,
    reddit_listing_to_paste,
    reddit_thread_url,
)


def test_reddit_thread_url():
    url = (
        "https://www.reddit.com/r/TheBoys/comments/1tl9qqa/"
        "homelander_at_full_power/?sort=new"
    )
    thread_url = reddit_thread_url(url)
    assert thread_url == "https://old.reddit.com/r/TheBoys/comments/1tl9qqa/"
    assert reddit_json_url(url) == thread_url


def test_reddit_json_url_rejects_invalid():
    try:
        reddit_json_url("https://example.com/not-reddit")
        assert False, "expected RedditFetchError"
    except RedditFetchError:
        pass


def test_reddit_listing_to_paste():
    payload = [
        {
            "data": {
                "children": [
                    {
                        "kind": "t3",
                        "data": {
                            "author": "op_user",
                            "title": "Thread title",
                            "selftext": "OP body here",
                        },
                    }
                ]
            }
        },
        {
            "data": {
                "children": [
                    {
                        "kind": "t1",
                        "data": {
                            "author": "alice",
                            "body": "First reply",
                            "replies": "",
                        },
                    },
                    {
                        "kind": "t1",
                        "data": {
                            "author": "bob",
                            "body": "Nested parent",
                            "replies": {
                                "data": {
                                    "children": [
                                        {
                                            "kind": "t1",
                                            "data": {
                                                "author": "carol",
                                                "body": "Nested reply",
                                                "replies": "",
                                            },
                                        }
                                    ]
                                }
                            },
                        },
                    },
                ]
            }
        },
    ]
    text, truncated = reddit_listing_to_paste(payload)
    assert truncated is False
    assert "u/op_user: Thread title" in text
    assert "OP body here" in text
    assert "u/alice: First reply" in text
    assert "u/bob: Nested parent" in text
    assert "u/carol: Nested reply" in text

    parsed = __import__("src.parse_thread", fromlist=["parse_thread"]).parse_thread(text)
    assert "op_user" in parsed
    assert "alice" in parsed
    assert "carol" in parsed
