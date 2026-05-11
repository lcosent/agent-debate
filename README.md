# agent-debate

A **multi-agent debate** that pressure-tests any consequential decision — hiring, product strategy, policy, acquisitions, architecture choices, investment theses. Three agents — `advocate`, `skeptic`, and `judge` — argue from explicit roles, then a structured verdict drops out.

```
$ agent-debate run decisions/hire_senior_eng_remote_only.md --rounds 3

DECISION: Hire Senior Engineer A — remote-only candidate, no overlap with team timezone
─────────────────────────────────────────────────────────────────────────────────
ROUND 1
  ADVOCATE: Strong technical signal — three letters of recommendation from
            principal engineers, three-year track record shipping in async cultures.
            Async-first hire is a forcing function for better written docs.
  SKEPTIC: Real-time architectural decisions in this team happen on a daily 1-hour
            call. Zero overlap means the candidate becomes a follower, not a leader.
            We are not async-mature enough to absorb the operational cost.

ROUND 2
  ADVOCATE: ...
  SKEPTIC: ...

JUDGE VERDICT
  Stronger argument: SKEPTIC (8.0/10 vs 7.0/10)
  Key uncalled risks:
    1. No one on the team has hired async-only before — performance management gap
    2. Visa/contractor structure for the candidate's jurisdiction
    3. Team-culture impact: 6th remote hire vs first in this timezone
  Recommendation: WAIT — solve async operating model first, then hire.
```

## Why this exists

Single-agent LLM reasoning has a well-known weakness: **the model agrees with the framing in the prompt.** Ask it "is this a good hire?" and you get a thoughtful "yes." Ask "what are the risks?" and you get a thoughtful "many." The framing dominates the output.

Multi-agent debate forces the model to **argue against itself**, with each side incentivized (via the role prompt and the judge) to find the strongest case it can. The judge then evaluates which side made the better argument and surfaces risks neither side raised.

This is not a decision-making tool. It is a **structured devil's-advocate generator** — useful for any high-stakes asymmetric decision where you want to surface the strongest counter-argument before committing.

## What it works on

Any decision you can describe in a paragraph of markdown. Examples:

- **Hiring** — should we extend an offer? to whom? at what level?
- **Product strategy** — should we ship feature X? kill feature Y? consolidate two SKUs?
- **Architecture** — monolith vs services, build vs buy, language migration
- **M&A** — acquire vs partner, target valuation, integration approach
- **Policy** — return-to-office, comp philosophy, performance review changes
- **Investments** — capital allocation, vendor selection, secondary tender participation

The roles are intentionally generic. Override `roles/advocate.txt` and `roles/skeptic.txt` if you want domain-specific personas (e.g., "skeptic-CFO" for capital decisions, "skeptic-PM" for product).

## How it works

```
            ┌─────────────┐
            │  Decision   │
            └──────┬──────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
     ┌─────────┐       ┌─────────┐
     │ADVOCATE │◄─────►│ SKEPTIC │   N rounds of paired argument
     │  agent  │       │  agent  │
     └─────────┘       └─────────┘
          │                 │
          └────────┬────────┘
                   ▼
              ┌────────┐
              │ JUDGE  │   structured verdict
              │ agent  │   + uncalled risks
              └────────┘
```

Each agent is its own prompt against the same model. Round-robin debate, with each side reading the previous round before responding. The judge sees the full transcript and produces a structured JSON verdict.

## Quickstart

```bash
pip install -e .

# bundled examples (multiple domains)
agent-debate run decisions/hire_senior_eng_remote_only.md
agent-debate run decisions/migrate_to_kotlin.md
agent-debate run decisions/acquire_stablecoin_issuer.md
agent-debate run decisions/return_to_office_5_days.md

# your own decision (markdown)
agent-debate run path/to/decision.md --rounds 3 --model openai:gpt-4o

# compare verdicts across models
agent-debate run decision.md --model openai:gpt-4o
agent-debate run decision.md --model anthropic:claude-3-5-sonnet
agent-debate diff runs/*.json
```

## Decision format

Plain markdown. The first H1 is the title; remaining content is the context the agents read.

```markdown
# Should we hire Senior Engineer A as a remote-only contributor with no timezone overlap?

## Context
- 12-person engineering team, all in PST timezone
- Candidate is in CET, ~9 hour offset
- Team rituals: daily 1-hour standup, weekly architectural review
- Strong technical signal: ex-Stripe, ex-Plaid, three principal-engineer references
- We have never hired async-only before

## What I'm trying to decide
Whether to extend an offer, or restart the search for a same-timezone candidate.
```

## Bundled decisions

```
decisions/
├── hire_senior_eng_remote_only.md      # hiring
├── migrate_to_kotlin.md                # architecture
├── return_to_office_5_days.md          # policy
├── acquire_stablecoin_issuer.md        # M&A / investment
└── kill_feature_y_to_focus.md          # product
```

Use them as templates. The bundled examples are deliberately not personally identifying.

## Configuration

Three role prompts under `agent_debate/roles/`. Edit them for different decision domains. They are intentionally short and aggressive — the goal is to extract genuine disagreement, not collaboration.

| Role | Lives in |
|---|---|
| Advocate (argues for the decision as stated) | `roles/advocate.txt` |
| Skeptic (argues against) | `roles/skeptic.txt` |
| Judge (structured verdict) | `roles/judge.txt` |

## What this is not

- **Not advice.** The output is a structured argument; not a recommendation.
- **Not a research tool.** The agents reason from the context you provide. Garbage in, garbage out.
- **Not a multi-agent framework.** For agent orchestration, use AutoGen or LangGraph. This is one small purpose-built script.

## License

MIT.
