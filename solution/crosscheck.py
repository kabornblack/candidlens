"""
CandidLens agent solution — Stage 2: crosscheck.

This is the stage extract.py deliberately deferred. It compares each
candidate's CV claims against their interview claims and flags discrepancies:
  - corroborated   : interview claims support the CV claim
  - uncorroborated  : no interview claim addresses the CV claim either way
  - contradicted    : an interview claim conflicts with the CV claim

Input:  solution/extracted_claims.json   (Stage 1 output — the ONLY input;
        the raw candidate files are never read here, so no outside judgment
        can be smuggled in)
Output: solution/crosscheck_results.json — a list of
    {"candidate": "candidate_03",
     "claim_checks": [{"cv_claim": "...", "status": "contradicted",
                       "conflicting_interview_claims": ["..."]}, ...],
     "discrepancy_summary": ["..."]}

Usage:
    pip install -r requirements.txt
    # put ANTHROPIC_API_KEY in a local .env file
    python solution/crosscheck.py
"""

import json
import pathlib

import anthropic
from dotenv import load_dotenv

# This exact model string must be identical across baseline/baseline.py and
# every solution/*.py stage (extract, score, crosscheck, aggregate) so the
# baseline and the agent solution are compared fairly using the same model.
MODEL = "claude-sonnet-5"

ROOT = pathlib.Path(__file__).resolve().parent.parent
IN_PATH = ROOT / "solution" / "extracted_claims.json"
OUT_PATH = ROOT / "solution" / "crosscheck_results.json"


def load_extractions():
    """Return the list of Stage 1 extraction objects."""
    return json.loads(IN_PATH.read_text(encoding="utf-8"))


def build_prompt(cv_claims, interview_claims):
    cv_json = json.dumps(cv_claims, indent=2)
    interview_json = json.dumps(interview_claims, indent=2)
    return f"""You are cross-checking a backend engineer candidate. You are given two
lists of already-extracted claims: claims from their CV, and observations
from their interview. Work ONLY from these lists — do not use outside
knowledge and do not score or rate the candidate.

Go through every CV claim and classify it as exactly one of:
- "corroborated": one or more interview claims support or confirm it.
- "uncorroborated": no interview claim addresses it either way (simple
  silence — the interview neither supports nor conflicts with it).
- "contradicted": one or more interview claims conflict with it (the
  interview evidence points the other way).

Do not mark a claim "contradicted" just because it is unsupported — that is
"uncorroborated". "contradicted" requires an actual conflict.

"contradicted" requires evidence of actual INABILITY to do the thing, or
something ACTIVELY INCOMPATIBLE with the claim. It does NOT apply when the
interview merely shows limited depth, needing a hint, partial ability, or
the candidate being modest about their skill level. "Can do the basics but
isn't deep" is not a contradiction of a skill claim.

Before marking any claim "contradicted", check whether ANY interview claim
also SUPPORTS that same skill or claim, even partially. If at least one
interview claim supports it and the only negative evidence is about
depth/scope/seniority (not inability), the correct status is "corroborated"
(if the support is real) or "uncorroborated" — NOT "contradicted".

Worked example:
- CV claim: "Lists PostgreSQL as a skill"
- Interview claims: "Got a SQL join right" AND "Needed a hint on a window
  function" AND "Said deep query tuning isn't her strong area yet"
- Correct status: "corroborated" — basic ability is demonstrated ("got a
  join right"); the hint and the modesty are about depth, not inability.
- WRONG: "contradicted" (there is no evidence she cannot use PostgreSQL).

For every claim you mark "contradicted", list the specific interview
claim(s) that conflict with it, quoted or closely paraphrased from the
interview list.

Then produce a discrepancy_summary: a short list (0-4 items) of the most
significant contradictions, phrased as one-line findings. Use an empty list
if there are no contradictions.

=== CV CLAIMS ===
{cv_json}

=== INTERVIEW CLAIMS ===
{interview_json}

Respond with ONLY a JSON object of this shape:
{{"claim_checks": [
    {{"cv_claim": "Led a team of 5 engineers",
      "status": "contradicted",
      "conflicting_interview_claims": ["Reference names a different person as the tech lead"]}},
    {{"cv_claim": "5 years professional backend development",
      "status": "uncorroborated",
      "conflicting_interview_claims": []}}
  ],
  "discrepancy_summary": ["CV claims leading a team of 5; interview reference names someone else as tech lead and describes candidate as an IC"]}}
"""


def parse_json(reply_text):
    """Pull the JSON object out of the model reply."""
    try:
        return json.loads(reply_text)
    except json.JSONDecodeError:
        start = reply_text.find("{")
        end = reply_text.rfind("}")
        return json.loads(reply_text[start:end + 1])


def crosscheck_candidate(client, name, cv_claims, interview_claims):
    response = client.messages.create(
        model=MODEL,
        max_tokens=8192,
        messages=[{
            "role": "user",
            "content": build_prompt(cv_claims, interview_claims),
        }],
    )
    if response.stop_reason == "max_tokens":
        raise RuntimeError(
            f"Crosscheck truncated for {name}: response hit max_tokens limit "
            f"before completing"
        )
    reply_text = "".join(b.text for b in response.content if b.type == "text")
    return parse_json(reply_text)


def main():
    load_dotenv()  # picks up ANTHROPIC_API_KEY from a local .env file if present
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from the environment

    results = []
    for entry in load_extractions():
        name = entry["candidate"]
        print(f"Cross-checking {name}...")
        checked = crosscheck_candidate(
            client, name, entry["cv_claims"], entry["interview_claims"]
        )
        results.append({
            "candidate": name,
            "claim_checks": checked.get("claim_checks", []),
            "discrepancy_summary": checked.get("discrepancy_summary", []),
        })

    OUT_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Wrote {len(results)} crosscheck results to {OUT_PATH}")


if __name__ == "__main__":
    main()
