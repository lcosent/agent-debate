from __future__ import annotations

import json
import time
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from . import debate


console = Console()


@click.group()
def main():
    """agent-debate: multi-agent advocate/skeptic/judge debate for any consequential decision."""


@main.command("run")
@click.argument("thesis_path")
@click.option("--rounds", default=3, show_default=True)
@click.option("--model", default="local")
def run_cmd(thesis_path: str, rounds: int, model: str):
    thesis = Path(thesis_path).read_text()
    title = thesis.splitlines()[0].lstrip("# ").strip() if thesis else "untitled"
    console.print(f"[bold]DECISION:[/bold] {title}")
    console.print(f"[dim]model={model}  rounds={rounds}[/dim]\n")

    result = debate.run_debate(thesis=thesis, model=model, rounds=rounds)

    for r in result.rounds:
        console.print(
            Panel(r.advocate, title=f"ADVOCATE · round {r.number}", border_style="green")
        )
        console.print(
            Panel(r.skeptic, title=f"SKEPTIC · round {r.number}", border_style="red")
        )

    v = result.verdict
    if v:
        console.print(
            Panel(
                f"[bold]Stronger argument:[/bold] {v.stronger_argument}  "
                f"(advocate {v.advocate_score:.1f} / skeptic {v.skeptic_score:.1f})\n\n"
                f"[bold]Key uncalled risks:[/bold]\n"
                + "\n".join(f"  • {r}" for r in v.key_uncalled_risks)
                + f"\n\n[bold]Decision:[/bold] {v.decision_recommendation}\n\n"
                f"[bold]Rationale:[/bold] {v.rationale}",
                title="JUDGE VERDICT",
                border_style="cyan",
            )
        )

    runs = Path("runs")
    runs.mkdir(exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    stem = Path(thesis_path).stem
    md_path = runs / f"{stem}_{ts}.md"
    md_path.write_text(_render_markdown(title, thesis, result))
    json_path = runs / f"{stem}_{ts}.json"
    json_path.write_text(
        json.dumps(
            {
                "decision_title": title,
                "model": model,
                "rounds": [r.__dict__ for r in result.rounds],
                "verdict": v.__dict__ if v else None,
            },
            indent=2,
        )
    )
    console.print(f"\n[dim]saved → {md_path}[/dim]")


def _render_markdown(title: str, thesis: str, result: debate.DebateResult) -> str:
    parts = [f"# Debate: {title}", "", "## Decision", thesis.strip(), "", "## Debate", ""]
    for r in result.rounds:
        parts += [
            f"### Round {r.number}",
            "",
            "**ADVOCATE:**",
            r.advocate,
            "",
            "**SKEPTIC:**",
            r.skeptic,
            "",
        ]
    if result.verdict:
        v = result.verdict
        parts += [
            "## Verdict",
            f"- Stronger argument: **{v.stronger_argument}** (advocate {v.advocate_score:.1f} / skeptic {v.skeptic_score:.1f})",
            f"- Decision: **{v.decision_recommendation}**",
            "- Key uncalled risks:",
            *[f"  - {r}" for r in v.key_uncalled_risks],
            f"- Rationale: {v.rationale}",
        ]
    return "\n".join(parts)
