"""Run the bull/bear/judge debate."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .model import call


ROLES_DIR = Path(__file__).parent / "roles"


@dataclass
class Round:
    number: int
    bull: str
    bear: str


@dataclass
class Verdict:
    stronger_argument: str
    bull_score: float
    bear_score: float
    key_uncalled_risks: list[str]
    decision_recommendation: str
    rationale: str


@dataclass
class DebateResult:
    thesis: str
    rounds: list[Round] = field(default_factory=list)
    verdict: Verdict | None = None

    def transcript(self) -> str:
        out = []
        for r in self.rounds:
            out.append(f"### Round {r.number}\n\n**BULL:** {r.bull}\n\n**BEAR:** {r.bear}\n")
        return "\n".join(out)


def run_debate(thesis: str, model: str = "local", rounds: int = 3) -> DebateResult:
    bull_template = (ROLES_DIR / "bull.txt").read_text()
    bear_template = (ROLES_DIR / "bear.txt").read_text()
    judge_template = (ROLES_DIR / "judge.txt").read_text()

    result = DebateResult(thesis=thesis)
    prior = ""
    for i in range(1, rounds + 1):
        bull_prompt = bull_template.format(
            round=i, total_rounds=rounds, prior_transcript=prior, thesis=thesis
        )
        bull = call(model, [{"role": "user", "content": bull_prompt}], max_tokens=900)

        bear_prompt = bear_template.format(
            round=i,
            total_rounds=rounds,
            prior_transcript=prior + f"\nBULL ROUND {i}: {bull}\n",
            thesis=thesis,
        )
        bear = call(model, [{"role": "user", "content": bear_prompt}], max_tokens=900)

        result.rounds.append(Round(number=i, bull=bull, bear=bear))
        prior += f"\n## Round {i}\nBULL: {bull}\nBEAR: {bear}\n"

    # Judge
    judge_prompt = judge_template.format(thesis=thesis, transcript=result.transcript())
    raw = call(model, [{"role": "user", "content": judge_prompt}], max_tokens=600, temperature=0.1)
    result.verdict = _parse_verdict(raw)
    return result


def _parse_verdict(raw: str) -> Verdict:
    m = re.search(r"\{.*\}", raw, re.DOTALL)
    if not m:
        return Verdict("UNKNOWN", 0, 0, [], "UNKNOWN", raw[:300])
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return Verdict("UNKNOWN", 0, 0, [], "UNKNOWN", raw[:300])
    return Verdict(
        stronger_argument=str(data.get("stronger_argument", "UNKNOWN")).upper(),
        bull_score=float(data.get("bull_score", 0)),
        bear_score=float(data.get("bear_score", 0)),
        key_uncalled_risks=list(data.get("key_uncalled_risks", [])),
        decision_recommendation=str(data.get("decision_recommendation", "UNKNOWN")).upper(),
        rationale=str(data.get("rationale", "")),
    )
