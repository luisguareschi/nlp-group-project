# Field Review: Online Discourse Authenticity

**Project:** Dead Internet Detector (Option 1 — Application Development)  
**Scope:** The industry and practice of detecting bots, LLM-generated text, and performative "imitation" voices in social comment threads.

---

## Scope and motivation

Online forums, comment sections, and social feeds are central infrastructure for public conversation. Readers and moderators routinely ask a version of the same question: *who—or what—is actually speaking here?* The "Dead Internet" narrative captures a growing epistemic worry: that much of what looks like organic discussion may be automated, templated, or LLM-assisted fill.

This field sits at the intersection of **platform trust & safety**, **computational social science**, and **NLP detection research**. Platforms operate large-scale moderation pipelines; researchers build classifiers and benchmarks; ordinary users develop informal heuristics ("that reply feels like ChatGPT"). Our project targets a narrower but real gap: **thread-level, participant-level auditing** when you only have pasted text—no account graph, no posting history, no API access to the platform's internal signals.

---

## Trends

### Pre-LLM social bots

For years, "bot detection" meant identifying **automated accounts**: spam pipelines, astroturf campaigns, political influence operations, and engagement farms. Signals included posting rate, follower ratios, retweet networks, and repetitive phrasing. Tools like **Botometer** (formerly BotOrNot) popularized public-facing bot scores for Twitter/X accounts. Academic work produced simulators and shared tasks (e.g. **BotSim**) to stress-test detectors under adversarial adaptation.

The dominant framing was **binary**: bot account vs. human account, often at the profile level rather than the comment level.

### Post-2022 generative fill

Large language models changed the threat model. Bots no longer need to sound like 2016 spam templates. A single prompt can produce **casual, empathetic, on-topic replies**—the "reply guy" voice that blends into normal threads. At the same time, humans increasingly perform **ironic bot voices**: copypasta, "hello fellow humans" memes, NPC dialogue bits. The relevant distinction is no longer only *automated vs. not* but *what register is being performed*.

Research benchmarks such as **GRiD** (human vs. GPT snippet pairs) reflect this shift toward **text-level** AI detection. Commercial and open tools (OpenAI classifiers, **GLTR**, various "AI detector" sites) target whether a passage was machine-generated—again mostly binary.

### From account graphs to voice-level reading

Three converging trends define the current landscape:

1. **Text-first auditing** — Readers judge individual comments without access to account metadata.
2. **Imitation layers** — Both humans and machines deliberately mimic the other's voice.
3. **Disclosed automation** — Moderation bots (e.g. Reddit AutoModerator) are labeled bots but serve legitimate functions, not spam.

Platform-internal systems still rely heavily on **account-level graphs** (device fingerprints, IP clusters, behavior timelines). Public-facing or paste-only tools cannot replicate that and must lean on **linguistic and stylometric cues**.

---

## Challenges

**Intent is invisible from text alone.** A human posting copypasta and a template bot posting "Did you know?" facts can share surface form. Distinguishing `human_imitating_bot` from `bot` requires cultural context the text may not encode.

**Surface-form overlap.** Engagement-bait phrases ("Great question!", "Love this energy!") appear in both genuine human pile-ons and astroturf. Short informal comments ("lol", "nah the bus was late") carry little signal for stylometric classifiers.

**English-centric tooling.** Most open detectors and feature sets assume English prose. Code-switching and multilingual threads degrade performance; this is underrepresented in many public benchmarks.

**Adversarial adaptation.** Detectors that publish their signals get gamed. Platforms face an arms race; research prototypes face rapid obsolescence as models and prompting styles evolve.

**Ethical and deployment risk.** False accusations harm real users. Automated moderation at scale has documented bias against marginalized dialects. Any reader-facing authenticity tool must frame output as **probabilistic impressions**, not verdicts—a constraint we adopt explicitly in our POC.

**Probe access.** Unlike Option 2 (system audit), application builders often lack API access to deployed moderation stacks. Rate limits, paywalls, and closed models make it hard to benchmark against production systems directly.

---

## Major players

### Platforms (mostly closed)

| Actor | Role |
|-------|------|
| **Reddit** | AutoModerator, spam filtering, crowd moderation; disclosed bot accounts in many subreddits |
| **Meta** (Facebook, Instagram) | Coordinated inauthentic behavior teams; content + graph signals (not public) |
| **X / Twitter** | Historical bot research hub; post-acquisition moderation changes; limited third-party API access |
| **YouTube, TikTok** | Comment filtering, spam detection; ML pipelines largely proprietary |

These systems optimize for **platform safety at scale**, not for a moderator pasting a thread into an external audit tool.

### Research and open tools

| Tool / line of work | Focus |
|---------------------|--------|
| **Botometer** | Account-level bot likelihood (primarily Twitter/X) |
| **BotSim** and related simulators | Adversarial bot–detector dynamics |
| **GRiD** and similar benchmarks | Human vs. GPT text snippets |
| **GLTR, RoBERTa-based detectors** | Token-probability / classifier approaches to AI text |
| **Stylometry / authorship attribution** | Writing-style fingerprints across documents |
| **"Bot or Not?" studies** | Human baseline performance on bot identification tasks |

### Adjacent industry

Content moderation vendors (e.g. **Spectrum Labs**, **Crisp**, **ActiveFence**) sell classifiers to gaming, dating, and brand platforms—typically for **harm categories** (hate, grooming, spam) rather than Dead Internet-style authenticity labels. LLM guardrail products focus on **model output safety**, not retrospective thread auditing.

---

## Existing solutions and gaps

**Binary classification dominates.** Deployed and research systems usually output human vs. bot, or human-written vs. AI-generated. That matches some moderation workflows but not how readers actually experience threads—where irony, memes, and casual-tone bots create a blurrier picture.

**Few tools expose imitation categories.** Labels like "human performing bot voice" or "bot performing casual human" are discussed informally but rarely appear in public APIs or consumer tools.

**Account signals vs. paste-only auditing.** Botometer-style tools need handles and network context. Paste-only analysis (our use case) must infer everything from **comment text and thread structure**, a strictly harder problem.

**Explanation quality varies.** Some LLM-based demos produce plausible rationales that are not tightly grounded in quoted evidence—a known failure mode we document in our eval.

**Gap our POC addresses:** A **local, research-oriented** Streamlit tool that parses a pasted thread, classifies each participant into a **four-label taxonomy**, returns **confidence and cited cues**, and aggregates a thread-level **Dead Internet Index**. It is a proof of concept for transparent, participant-level reading—not a replacement for platform moderation or account-level bot scores.

---

## Implications for Dead Internet Detector

The field review suggests our design choices:

- **Hybrid pipeline** (stylometric heuristics + local LLM via Ollama) balances offline reproducibility with richer reasoning when a model is available.
- **Four-label taxonomy** ([TOPIC_BRIEF.md](TOPIC_BRIEF.md)) maps closer to reader perception than binary bot/human alone—at the cost of harder ground truth ([LABELING_GUIDELINES.md](LABELING_GUIDELINES.md)).
- **Tiered evaluation** (synthetic, disclosed, GRiD-style, expert, edge) acknowledges that perfect labels are impossible for arbitrary paste; we separate high-confidence cases from deliberately hard edge tiers ([FAILURE_ANALYSIS.md](FAILURE_ANALYSIS.md)).
- **Probabilistic framing** aligns with industry ethics: statistical vibes, not accusations.

For academic depth on methods and citations, see the technical report outline §2 Related work ([report/TECHNICAL_REPORT_OUTLINE.md](report/TECHNICAL_REPORT_OUTLINE.md)).
