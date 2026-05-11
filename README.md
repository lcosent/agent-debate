# agent-debate

A **multi-agent debate** that pressure-tests an investment thesis. Three agents — bull, bear, and judge — argue from explicit roles, then a structured verdict drops out.

```
$ agent-debate run theses/anthropic_secondary_2026.md --rounds 3

THESIS: Buy Anthropic secondary at $300B valuation (March 2026)
─────────────────────────────────────────────────────────────────
ROUND 1
  BULL: Frontier AI is a duopoly. Anthropic + OpenAI capture 60%+
        of enterprise inference; Anthropic's Constitutional AI brand
        gives it disproportionate share of regulated industries...
  BEAR: $300B values Anthropic at 30x trailing revenue. NVIDIA-style
        capex creates structural unprofitability. Foundation-model
        commoditization in 18-24 months erodes margins...

ROUND 2
  BULL: Counter — even at 30x revenue, growth rate of 5x annually
        compresses multiple. AGI optionality is asymmetric...
  BEAR: Counter — 5x growth is unsustainable. Saturation at $20B ARR
        within 24 months is the consensus model...

ROUND 3
  BULL: ...
  BEAR: ...

JUDGE VERDICT
  Stronger argument: BEAR (8.5/10 vs 7.2/10)
  Key uncalled risks:
    1. Capital intensity / runway to FCF positive
    2. Lock-in vs OpenAI on enterprise contracts (incumbency advantage at OpenAI)
    3. Regulatory tailrisk in EU (AI Act enforcement starting Q3 2026)
  Recommendation: PASS — current price requires AGI-scenario underwriting.

[full debate transcript saved → runs/anthropic_secondary_2026.md]
```

## Why this exists

Single-agent LLM reasoning has a well-known weakness: **the model agrees with the framing in the prompt.** Ask it "is this a good investment?" and you get a thoughtful "yes." Ask "what could go wrong?" and you get a thoughtful "many things." The framing dominates the output.

Multi-agent debate forces the model to **argue against itself**, with each side incentivized (via the role prompt and the judge) to find the strongest case it can. The judge then evaluates which side made the better argument.

This is not a stock-picking tool. It is a **structured devil's-advocate generator** — useful for any high-stakes asymmetric decision where you want to surface the strongest counter-argument before deciding.

## How it works

```
            ┌─────────────┐
            │   Thesis    │
            └──────┬──────┘
                   │
          ┌────────┴────────┐
          ▼                 ▼
     ┌────────┐        ┌────────┐
     │  BULL  │◄──────►│  BEAR  │   N rounds of paired argument
     │ agent  │        │ agent  │
     └────────┘        └────────┘
          │                 │
          └────────┬────────┘
                   ▼
              ┌────────┐
              │ JUDGE  │   structured verdict
              │ agent  │   + uncalled risks
              └────────┘
```

Each agent runs as its own prompt against the same model. Round-robin debate, with each side reading the previous round before responding. The judge sees the full transcript and produces a structured verdict.

## Quickstart

```bash
pip install -e .

# bundled example
agent-debate run theses/anthropic_secondary_2026.md

# your own thesis (markdown)
agent-debate run path/to/thesis.md --rounds 3 --model openai:gpt-4o

# compare two models on the same thesis
agent-debate run thesis.md --model openai:gpt-4o
agent-debate run thesis.md --model anthropic:claude-3-5-sonnet
agent-debate diff runs/*.json
```

## Thesis format

Plain markdown. The first H1 is the title; remaining content is context the agents read.

```markdown
# Buy Anthropic secondary at $300B valuation

## Context
- $300B post-money, March 2026
- ARR run rate: ~$10B
- Capex commitments: $9B for compute through 2027
...

## What I'm trying to decide
Whether to participate in a secondary round at this valuation
or wait for the next funding round.
```

## Bundled theses

```
theses/
├── anthropic_secondary_2026.md
├── short_treasury_long_btc.md
├── acquire_stablecoin_issuer.md
└── nvidia_at_4t_valuation.md
```

Use them as templates.

## Configuration

Three role prompts under `agent_debate/roles/`. Edit them for different decision domains (M&A, hiring, product launches). They are intentionally short and aggressive — the goal is to extract genuine disagreement, not collaboration.

| Role | Lives in |
|---|---|
| Bull (argues for the thesis) | `roles/bull.txt` |
| Bear (argues against) | `roles/bear.txt` |
| Judge (structured verdict) | `roles/judge.txt` |

## What this is not

- **Not financial advice.** The output is a structured argument; not a recommendation.
- **Not a research tool.** The agents reason from the context you provide. Garbage in, garbage out.
- **Not a multi-agent framework.** For agent orchestration, use AutoGen or LangGraph. This is one small purpose-built script.

## License

MIT.
