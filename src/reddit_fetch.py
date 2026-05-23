from __future__ import annotations

import json
import re
import urllib.error
import urllib.request

REDDIT_POST_URL = re.compile(
    r"https?://(?:www\.|old\.|np\.)?reddit\.com/r/(?P<sub>[^/]+)/comments/(?P<id>[a-z0-9]+)",
    re.IGNORECASE,
)

USER_AGENT = "DeadInternetDetector/1.0 (NLP course project; +https://github.com)"


class RedditFetchError(Exception):
    """Raised when a Reddit thread cannot be fetched or parsed."""


def reddit_json_url(post_url: str) -> str:
    """Build the Reddit JSON API URL for a post link."""
    url = post_url.strip()
    if not url:
        raise RedditFetchError("Enter a Reddit post URL.")
    match = REDDIT_POST_URL.search(url)
    if not match:
        raise RedditFetchError(
            "Not a supported Reddit post URL. "
            "Use a link like https://www.reddit.com/r/subreddit/comments/ID/title/"
        )
    sub, post_id = match.group("sub"), match.group("id")
    return (
        f"https://www.reddit.com/r/{sub}/comments/{post_id}.json"
        f"?limit=500&depth=10&raw_json=1"
    )


def _fetch_json(url: str) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RedditFetchError("Post not found (404).") from e
        if e.code == 429:
            raise RedditFetchError("Reddit rate-limited this request. Try again in a minute.") from e
        raise RedditFetchError(f"Reddit returned HTTP {e.code}.") from e
    except urllib.error.URLError as e:
        raise RedditFetchError(f"Could not reach Reddit: {e.reason}") from e
    except json.JSONDecodeError as e:
        raise RedditFetchError("Invalid response from Reddit.") from e


def _format_comment_line(author: str, body: str) -> str | None:
    author = (author or "[deleted]").strip()
    if author in ("[deleted]", "[removed]"):
        author = "deleted"
    body = (body or "").strip()
    if not body or body in ("[removed]", "[deleted]"):
        return None
    return f"u/{author}: {body}"


def _walk_comments(
    children: list, lines: list[str], *, max_comments: int
) -> bool:
    """Walk comment tree. Return True if stopped early due to max_comments."""
    truncated = False
    for child in children:
        if len(lines) >= max_comments:
            return True
        kind = child.get("kind")
        if kind == "more":
            truncated = True
            continue
        if kind != "t1":
            continue
        data = child.get("data") or {}
        line = _format_comment_line(data.get("author", ""), data.get("body", ""))
        if line:
            lines.append(line)
        replies = data.get("replies")
        if isinstance(replies, dict):
            reply_children = (replies.get("data") or {}).get("children") or []
            if _walk_comments(reply_children, lines, max_comments=max_comments):
                truncated = True
    return truncated or len(lines) >= max_comments


def reddit_listing_to_paste(payload: list, *, max_comments: int = 200) -> tuple[str, bool]:
    """Convert Reddit listing JSON to u/username paste format."""
    if not isinstance(payload, list) or len(payload) < 1:
        raise RedditFetchError("Unexpected Reddit response shape.")

    post_listing = payload[0].get("data", {}).get("children") or []
    if not post_listing or post_listing[0].get("kind") != "t3":
        raise RedditFetchError("Could not find post data in Reddit response.")

    post = post_listing[0].get("data") or {}
    lines: list[str] = []

    author = post.get("author") or "unknown"
    title = (post.get("title") or "").strip()
    selftext = (post.get("selftext") or "").strip()
    if selftext:
        op_body = f"{title}\n\n{selftext}" if title else selftext
    else:
        op_body = title
    if op_body:
        op_line = _format_comment_line(author, op_body)
        if op_line:
            lines.append(op_line)

    truncated = False
    if len(payload) > 1:
        comment_children = (payload[1].get("data") or {}).get("children") or []
        truncated = _walk_comments(comment_children, lines, max_comments=max_comments)

    if not lines:
        raise RedditFetchError("No comment text found in this post.")

    return "\n".join(lines), truncated


def fetch_reddit_thread(post_url: str, *, max_comments: int = 200) -> tuple[str, bool]:
    """Fetch a Reddit post URL and return (paste-ready thread text, truncated)."""
    json_url = reddit_json_url(post_url)
    payload = _fetch_json(json_url)
    return reddit_listing_to_paste(payload, max_comments=max_comments)
