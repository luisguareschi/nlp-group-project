from __future__ import annotations

import re
from collections import defaultdict

# u/name, /u/name, @name, Author: name, [name]:
USER_PREFIX = re.compile(
    r"^(?:"
    r"(?:u/|/u/|@)(?P<user1>[A-Za-z0-9_-]+)"
    r"|(?:Author|User|Poster):\s*(?P<user2>[A-Za-z0-9_-]+)"
    r"|\[(?P<user3>[A-Za-z0-9_-]+)\]"
    r")\s*[:|-]?\s*(?P<body>.*)$",
    re.IGNORECASE,
)

# Reddit score line: "username 42 points ..."
SCORE_LINE = re.compile(
    r"^(?P<user>[A-Za-z0-9_-]+)\s+\d+\s+points?\s*[:|-]?\s*(?P<body>.*)$",
    re.IGNORECASE,
)

# Numbered comment: "1. username: text" or "1) text" with user on prev line
NUMBERED = re.compile(r"^\d+[\.\)]\s*(.*)$")


def _clean_username(name: str) -> str:
    return name.strip().strip("_")


def parse_thread(text: str) -> dict[str, list[str]]:
    """
    Parse pasted thread text into {username: [comments]}.

    Supported formats:
    - u/alice: comment body
    - /u/bob - comment
    - Author: carol: comment
    - [dave]: comment
    - alice 12 points: comment
    - Blank line separates blocks; lines without user prefix attach to last user.
    """
    participants: dict[str, list[str]] = defaultdict(list)
    current_user: str | None = None
    orphan_lines: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line in ("---", "***"):
            continue

        m = USER_PREFIX.match(line)
        if m:
            user = m.group("user1") or m.group("user2") or m.group("user3")
            body = (m.group("body") or "").strip()
            current_user = _clean_username(user)
            if body:
                participants[current_user].append(body)
            elif current_user not in participants:
                participants[current_user] = []
            continue

        m = SCORE_LINE.match(line)
        if m:
            current_user = _clean_username(m.group("user"))
            body = (m.group("body") or "").strip()
            if body:
                participants[current_user].append(body)
            continue

        # "username:" at start without u/ prefix
        if ":" in line and not line.startswith("http"):
            maybe_user, _, rest = line.partition(":")
            if (
                len(maybe_user) <= 32
                and maybe_user.replace("_", "").replace("-", "").isalnum()
                and rest.strip()
            ):
                current_user = _clean_username(maybe_user)
                participants[current_user].append(rest.strip())
                continue

        num = NUMBERED.match(line)
        if num and current_user:
            body = num.group(1).strip()
            if body:
                participants[current_user].append(body)
            continue

        if current_user:
            participants[current_user].append(line)
        else:
            orphan_lines.append(line)

    # If no structure detected, treat each non-empty paragraph as anonymous user_N
    if not participants and orphan_lines:
        buf: list[str] = []
        idx = 1
        for line in orphan_lines:
            if not line and buf:
                participants[f"user_{idx}"] = buf
                buf = []
                idx += 1
            elif line:
                buf.append(line)
        if buf:
            participants[f"user_{idx}"] = buf

    return {k: v for k, v in participants.items() if v}


def format_thread_for_prompt(participants: dict[str, list[str]]) -> str:
    lines: list[str] = []
    for user, comments in participants.items():
        for i, c in enumerate(comments, 1):
            lines.append(f"u/{user} (comment {i}): {c}")
    return "\n".join(lines)
