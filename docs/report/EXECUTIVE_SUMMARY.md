# Executive Summary (one page — non-technical)

## The problem

Social feeds increasingly mix real people, automated accounts, and language that *sounds* machine-generated. Readers and moderators struggle to tell who—or what—is behind a comment thread. This erodes trust in online discussion (“the dead internet”).

## Our solution

**Dead Internet Detector** is a prototype web tool. You paste a comment thread (for example from Reddit). For each participant, the tool offers a best-guess label—human, bot, or two “imitation” categories—plus a confidence score and a short explanation citing wording from the thread.

## What we learned

Perfect detection is not possible from text alone. We built a careful evaluation set of 48 labeled examples using role-play, known bots, and team-reviewed excerpts. The tool performs reasonably on obvious cases but struggles when humans joke like bots or when bots sound casually human—exactly where human annotators also disagree.

## How to use it responsibly

Results are **statistical impressions**, not accusations. The tool does not see account history or identity. It is meant for research and demonstration, not automated punishment of users.

## Next steps

Richer context (reply chains, multiple languages), better calibration, and partnerships with platforms or researchers for ethical deployment studies.
