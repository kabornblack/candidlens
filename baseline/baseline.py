"""
CandidLens baseline evaluator.

Intentionally simple: for each candidate, send the job description plus the
full candidate file (CV + interview notes) to Claude in one prompt and ask
for a 1-5 score per skill category and an overall 1-5 score.

No evidence citation, no cross-checking of claims, no discrepancy flagging.
This is the "one direct prompt" baseline the agent solution is measured against.

Usage:
    set ANTHROPIC_API_KEY=...   (do NOT hardcode it here)
    python baseline/baseline.py
"""

import json
import pathlib

import anthropic
from dotenv import load_dotenv

# This exact model string must be reused identically in solution/extract.py,
# solution/score.py, solution/crosscheck.py, and solution/aggregate.py so the
# baseline and the agent solution are compared fairly using the same model.
MODEL = "claude-sonnet-5"

# The 5 scoring categories from data/jd.md
CATEGORIES = [
    "python_go",            # Python/Go proficiency
    "rest_api_design",      # REST API design
    "sql_data_modeling",    # SQL / data modeling
    "cloud_infrastructure", # Cloud infrastructure experience
    "ownership_collab",     # Ownership & collaboration (soft signal)
]

ROOT = pathlib.Path(__file__).resolve().parent.parent
JD_PATH = ROOT / "data" / "jd.md"
CANDIDATES_DIR = ROOT / "data" / "candidates"
RESULTS_PATH = ROOT / "baseline" / "baseline_results.json"


def load_candidates():
    """Return a sorted list of (name, text) for each candidate file."""
    candidates = []
    for path in sorted(CANDIDATES_DIR.glob("candidate_*.md")):
        candidates.append((path.stem, path.read_text(encoding="utf-8")))
    return candidates


def build_prompt(jd_text, candidate_text):
    return f"""You are screening a backend engineer candidate against a job description.

=== JOB DESCRIPTION ===
{jd_text}

=== CANDIDATE FILE (CV + interview notes) ===
{candidate_text}

Score the candidate from 1 (poor) to 5 (excellent) on each of these categories:
- python_go: Python/Go proficiency
- rest_api_design: REST API design
- sql_data_modeling: SQL / data modeling
- cloud_infrastructure: Cloud infrastructure experience
- ownership_collab: Ownership & collaboration

Also give an "overall" score from 1 to 5.

Respond with ONLY a JSON object, like:
{{"python_go": 3, "rest_api_design": 4, "sql_data_modeling": 2, "cloud_infrastructure": 3, "ownership_collab": 4, "overall": 3}}
"""


def parse_scores(reply_text):
    """Pull the JSON object out of the model reply."""
    try:
        return json.loads(reply_text)
    except json.JSONDecodeError:
        start = reply_text.find("{")
        end = reply_text.rfind("}")
        return json.loads(reply_text[start:end + 1])


def score_candidate(client, jd_text, candidate_text):
    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": build_prompt(jd_text, candidate_text)}],
    )
    reply_text = "".join(b.text for b in response.content if b.type == "text")
    return parse_scores(reply_text)


def main():
    load_dotenv()  # picks up ANTHROPIC_API_KEY from a local .env file if present
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment
    jd_text = JD_PATH.read_text(encoding="utf-8")

    results = []
    for name, candidate_text in load_candidates():
        print(f"Scoring {name}...")
        scores = score_candidate(client, jd_text, candidate_text)
        results.append({"candidate": name, "scores": scores})

    RESULTS_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
