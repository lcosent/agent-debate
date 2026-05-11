"""Run a quick debate."""

from pathlib import Path

from agent_debate.debate import run_debate


def main():
    thesis = Path("decisions/hire_senior_eng_remote_only.md").read_text()
    result = run_debate(thesis, model="local", rounds=2)
    print(result.transcript())
    if result.verdict:
        print("\nVERDICT:")
        print(f"  stronger: {result.verdict.stronger_argument}")
        print(f"  decision: {result.verdict.decision_recommendation}")
        print(f"  uncalled risks: {result.verdict.key_uncalled_risks}")


if __name__ == "__main__":
    main()
