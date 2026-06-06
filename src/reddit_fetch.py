from __future__ import annotations

import re
import ssl
import urllib.error
import urllib.request
from html import unescape

import certifi

REDDIT_POST_URL = re.compile(
    r"https?://(?:www\.|old\.|np\.)?reddit\.com/r/(?P<sub>[^/]+)/comments/(?P<id>[a-z0-9]+)",
    re.IGNORECASE,
)

USER_AGENT = "DeadInternetDetector/1.0 (NLP course project; +https://github.com)"

THING_RE = re.compile(
    r'<div[^>]*class="[^"]*\bthing id-(t3|t1)_[^"]*"[^>]*data-author="([^"]*)"[^>]*>'
    r'(.*?)(?=<div[^>]*class="[^"]*\bthing id-(?:t3|t1)_|\Z)',
    re.DOTALL | re.IGNORECASE,
)
TITLE_RE = re.compile(
    r'<a[^>]*class="title[^"]*"[^>]*>(.*?)</a>',
    re.DOTALL | re.IGNORECASE,
)
MD_RE = re.compile(r'<div class="md">(.*?)</div>', re.DOTALL | re.IGNORECASE)
TIMESTAMP_RE = re.compile(r'data-timestamp="(\d+)"', re.IGNORECASE)


class RedditFetchError(Exception):
    """Raised when a Reddit thread cannot be fetched or parsed."""


def reddit_thread_url(post_url: str) -> str:
    """Build an old.reddit.com URL for a post link."""
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
    return f"https://old.reddit.com/r/{sub}/comments/{post_id}/"


def reddit_json_url(post_url: str) -> str:
    """Deprecated alias kept for tests; returns the HTML thread URL."""
    return reddit_thread_url(post_url)


def _request(url: str) -> urllib.request.Request:
    return urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )


def _fetch_html(url: str) -> str:
    req = _request(url)
    ssl_ctx = ssl.create_default_context(cafile=certifi.where())
    try:
        with urllib.request.urlopen(req, timeout=20, context=ssl_ctx) as resp:
            return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RedditFetchError("Post not found (404).") from e
        if e.code == 403:
            raise RedditFetchError(
                "Reddit blocked this request (HTTP 403). "
                "Try again in a minute, or paste the thread manually."
            ) from e
        if e.code == 429:
            raise RedditFetchError("Reddit rate-limited this request. Try again in a minute.") from e
        raise RedditFetchError(f"Reddit returned HTTP {e.code}.") from e
    except urllib.error.URLError as e:
        raise RedditFetchError(f"Could not reach Reddit: {e.reason}") from e


def _strip_html(html: str) -> str:
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)
    text = re.sub(r"</p>\s*<p>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


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


def reddit_html_to_paste(
    html: str, *, max_comments: int = 200
) -> tuple[str, bool, dict[str, list[int]]]:
    """Convert an old.reddit.com comments page to u/username paste format.

    Returns (paste_text, truncated, timestamps) where timestamps maps each
    author to a list of Unix timestamps (ms) for their comments.
    """
    lines: list[str] = []
    timestamps: dict[str, list[int]] = {}
    comment_count = 0
    truncated = False

    for match in THING_RE.finditer(html):
        kind, author, block = match.group(1), match.group(2), match.group(3)
        ts_match = TIMESTAMP_RE.search(match.group(0))
        ts = int(ts_match.group(1)) if ts_match else None

        if kind == "t3":
            title_match = TITLE_RE.search(block)
            title = _strip_html(title_match.group(1)) if title_match else ""
            md_match = MD_RE.search(block)
            body = _strip_html(md_match.group(1)) if md_match else ""
            if body:
                op_body = f"{title}\n\n{body}" if title else body
            else:
                op_body = title
            line = _format_comment_line(author, op_body)
            if line:
                lines.append(line)
                if ts and author not in ("[deleted]", "[removed]", "deleted"):
                    timestamps.setdefault(author, []).append(ts)
            continue

        if comment_count >= max_comments:
            truncated = True
            break
        md_match = MD_RE.search(block)
        if not md_match:
            continue
        line = _format_comment_line(author, _strip_html(md_match.group(1)))
        if line:
            lines.append(line)
            comment_count += 1
            if ts and author not in ("[deleted]", "[removed]", "deleted"):
                timestamps.setdefault(author, []).append(ts)

    if not lines:
        raise RedditFetchError("No comment text found in this post.")

    return "\n".join(lines), truncated, timestamps


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


def fetch_reddit_thread(
    post_url: str, *, max_comments: int = 200
) -> tuple[str, bool, dict[str, list[int]]]:
    """Fetch a Reddit post URL and return (paste-ready text, truncated, timestamps)."""
    thread_url = reddit_thread_url(post_url)
    html = _fetch_html(thread_url)
    return reddit_html_to_paste(html, max_comments=max_comments)
