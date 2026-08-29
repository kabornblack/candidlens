"""
CandidLens agent solution — Stage 1: claim extraction.

Unlike the baseline (one flat prompt -> scores), the agent pipeline first
pulls discrete, structured claims out of each candidate file, keeping CV
claims and interview claims separate so a later stage can cross-check them
against each other.

Output: solution/extracted_claims.json — a list of
    {"candidate": "candidate_03",
     "cv_claims":        [{"text": "...", "category": "..."}, ...],
     "interview_claims": [{"text": "...", "category": "..."}, ...]}

Usage:
    pip install -r requirements.txt
    # put ANTHROPIC_API_KEY in a local .env file
    python solution/extract.py
"""

import json
import pathlib

import anthropic
from dotenv import load_dotenv

# This exact model string must be identical across baseline/baseline.py and
# every solution/*.py stage (extract, score, crosscheck, aggregate) so the
# baseline and the agent solution are compared fairly using the same model.
MODEL = "claude-sonnet-5"

# The 5 scoring categories from data/jd.md, plus "general" for claims that
# don't map to a single category.
CATEGORIES = [
    "python_go",
    "rest_api_design",
    "sql_data_modeling",
    "cloud_infrastructure",
    "ownership_collab",
]
CATEGORY_SLUGS = CATEGORIES + ["general"]

ROOT = pathlib.Path(__file__).resolve().parent.parent
CANDIDATES_DIR = ROOT / "data" / "candidates"
OUT_PATH = ROOT / "solution" / "extracted_claims.json"


def load_candidates():
    """Return a sorted list of (name, text) for each candidate file."""
    candidates = []
    for path in sorted(CANDIDATES_DIR.glob("candidate_*.md")):
        candidates.append((path.stem, path.read_text(encoding="utf-8")))
    return candidates


def build_prompt(candidate_text):
    return f"""You are analysing a backend engineer candidate's file. It has two
sections: a CV summary and Interview Notes.

Extract discrete claims, keeping the two sections separate:
- cv_claims: individual factual claims made in the CV section (experience,
  past roles, skills, achievements). One claim per list item, short string.
- interview_claims: individual observations or statements from the Interview
  Notes section (what the candidate demonstrated, said, or how they came
  across). One observation per list item, short string.

Tag every claim with the JD skill category it relates to, using exactly one
of these slugs:
  python_go, rest_api_design, sql_data_modeling, cloud_infrastructure,
  ownership_collab, general
Use "general" only when a claim does not fit a single category.

CRITICAL BOUNDARY — extract only what was LITERALLY said or observed. Do NOT
judge, score, or reconcile anything. A claim must NOT compare the CV against
the interview, and must NOT contain the words "CV", "contradicts",
"corroborated"/"uncorroborated", "actual level", "in reality", or "does not
match". Comparing the two sections is a LATER stage's job, not yours.

Examples of the difference:
- KEEP  (raw fact from interview): "Reference names a different person as the tech lead"
- KEEP  (raw observation): "Could not explain why services were split where they were"
- KEEP  (direct quote/paraphrase): "Said he does not do the people-management side"
- DROP  (comparative conclusion): "Response contradicts the CV claim of leading a team"
- DROP  (evaluative conclusion): "CV claims of architecture ownership are not corroborated"
- DROP  (judgment): "Actual level looks like a competent mid-level individual contributor"

If an interview note in the source already states a conclusion, extract only
the underlying observation it rests on, not the conclusion.

=== CANDIDATE FILE ===
{candidate_text}

Respond with ONLY a JSON object of this shape:
{{"cv_claims": [{{"text": "3.5 years experience", "category": "general"}}],
  "interview_claims": [{{"text": "Wrote a correct 3-table join unprompted", "category": "sql_data_modeling"}}]}}
"""


def parse_json(reply_text):
    """Pull the JSON object out of the model reply."""
    try:
        return json.loads(reply_text)
    except json.JSONDecodeError:
        start = reply_text.find("{")
        end = reply_text.rfind("}")
        return json.loads(reply_text[start:end + 1])


def extract_candidate(client, name, candidate_text):
    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        messages=[{"role": "user", "content": build_prompt(candidate_text)}],
    )
    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            f"Extraction truncated for {name}: response hit max_tokens limit "
            f"before completing"
        )
    reply_text = "".join(b.text for b in response.content if b.type == "text")
    return parse_json(reply_text)


def main():
    load_dotenv()  # picks up ANTHROPIC_API_KEY from a local .env file if present
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    results = []
    for name, candidate_text in load_candidates():
        print(f"Extracting {name}...")
        extracted = extract_candidate(client, name, candidate_text)
        results.append({
            "candidate": name,
            "cv_claims": extracted.get("cv_claims", []),
            "interview_claims": extracted.get("interview_claims", []),
        })

    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} extractions to {OUT_PATH}")


if __name__ == "__main__":
    main()
