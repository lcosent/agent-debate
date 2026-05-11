"""Run the advocate/skeptic/judge debate."""

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
    advocate: str
    skeptic: str


@dataclass
class Verdict:
    stronger_argument: str
    advocate_score: float
    skeptic_score: float
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
            out.append(
                f"### Round {r.number}\n\n**ADVOCATE:** {r.advocate}\n\n**SKEPTIC:** {r.skeptic}\n"
            )
        return "\n".join(out)


def run_debate(thesis: str, model: str = "local", rounds: int = 3) -> DebateResult:
    advocate_template = (ROLES_DIR / "advocate.txt").read_text()
    skeptic_template = (ROLES_DIR / "skeptic.txt").read_text()
    judge_template = (ROLES_DIR / "judge.txt").read_text()

    result = DebateResult(thesis=thesis)
    prior = ""
    for i in range(1, rounds + 1):
        advocate_prompt = advocate_template.format(
            round=i, total_rounds=rounds, prior_transcript=prior, thesis=thesis
        )
        advocate = call(
            model, [{"role": "user", "content": advocate_prompt}], max_tokens=900
        )

        skeptic_prompt = skeptic_template.format(
            round=i,
            total_rounds=rounds,
            prior_transcript=prior + f"\nADVOCATE ROUND {i}: {advocate}\n",
            thesis=thesis,
        )
        skeptic = call(model, [{"role": "user", "content": skeptic_prompt}], max_tokens=900)

        result.rounds.append(Round(number=i, advocate=advocate, skeptic=skeptic))
        prior += f"\n## Round {i}\nADVOCATE: {advocate}\nSKEPTIC: {skeptic}\n"

    # Judge
    judge_prompt = judge_template.format(thesis=thesis, transcript=result.transcript())
    raw = call(
        model, [{"role": "user", "content": judge_prompt}], max_tokens=600, temperature=0.1
    )
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
        advocate_score=float(data.get("advocate_score", 0)),
        skeptic_score=float(data.get("skeptic_score", 0)),
        key_uncalled_risks=list(data.get("key_uncalled_risks", [])),
        decision_recommendation=str(data.get("decision_recommendation", "UNKNOWN")).upper(),
        rationale=str(data.get("rationale", "")),
    )
