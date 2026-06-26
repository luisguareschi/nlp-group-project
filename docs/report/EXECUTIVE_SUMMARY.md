# Executive Summary: Dead Internet Detector

## The problem we set out to address

A growing share of online conversation is no longer purely human. Automated accounts post in comment sections, and language that reads as machine-written now appears alongside genuine replies. The reverse also happens, where people deliberately write in a stiff, robotic style as a joke. For everyday readers and for the moderators who manage online communities, it is increasingly difficult to tell who, or what, is behind a given comment. This uncertainty is sometimes described as the "dead internet" effect, and it slowly wears down trust in public discussion.

## What we built

The Dead Internet Detector is a working web application. A user pastes a comment thread, for example from Reddit, or supplies a link to one. The tool then reviews each participant and offers a best-guess label drawn from four categories: a genuine human, an automated bot, a human writing in a deliberately bot-like voice, and a bot trying to pass as a casual human. Alongside each label it reports a confidence score, a short plain-language explanation, and the specific wording from the thread that informed the guess. It also produces a single thread-level figure, the Dead Internet Index, which summarises how much of the conversation appears to be non-human.

## How it works

The application combines two approaches. The first measures observable writing patterns, such as repetitive phrasing, list formatting, generic openers, and the regularity of posting times. This method runs entirely on a local machine and needs no internet connection. The second layer adds a language model, also running locally, which reads the full thread for context and refines the assessment. The tool can run either approach on its own, which let us measure how much the language model adds. If the language model is unavailable, the application falls back to the pattern-based method so it always returns a result.

## What the results show

We assembled a carefully labelled test set of 48 participants drawn from five sources, including role-play threads written by the team, openly disclosed bots, and excerpts reviewed for agreement among team members. On this set, the combined approach correctly identified roughly 71 percent of participants, compared with about 60 percent for the pattern-only method. Performance was strong on clear cases, such as obvious bots and plainly human replies. It was much weaker on the two imitation categories, where a person mimics a machine or a machine mimics a person. These are exactly the cases where the team members themselves often disagreed, which suggests the limitation reflects the genuine difficulty of the task rather than a fixable flaw in the tool.

## Responsible use and limitations

The results are best understood as statistical impressions, not verdicts. The tool reads only the text of a thread and has no access to account history, identity, or any private information. We designed it for research and demonstration, and we explicitly discourage using its output to accuse, punish, or harass anyone.

## Where this could go next

Promising directions include reading the reply structure of a thread rather than each comment in isolation, supporting languages other than English, improving how confidence scores are calibrated, and partnering with platforms or researchers to study ethical use in a real setting.
