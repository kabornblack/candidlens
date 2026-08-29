# Human Reference Ranking — CandidLens

Human reviewer scoring sheet. Score each category **1–5** (5 = strong, 1 = weak).
Fill in scores and notes yourself; leave blank until reviewed.

Scoring categories (from `jd.md`):

1. Python/Go proficiency
2. REST API design
3. SQL / data modeling
4. Cloud infrastructure experience
5. Ownership & collaboration

---

## Candidate 01 — Priya Raghunathan

Python/Go: 4.5 / 5

REST API design: 4.5 / 5

SQL / data modeling: 5 / 5

Cloud infrastructure: 4 / 5

Ownership & collaboration: 5 / 5

Overall: 4.5 / 5

Notes (discrepancies / flags): NO discrepancy. All claims corroborated; schema redesign explained end-to-end with real tradeoff reasoning (event sourcing rejected, composite index choice, p95 drop from 900→210 ms). Go listed on CV but interview focused on Python — not a contradiction, just untested in that language. Strongest candidate in the set; clear mid‑senior hire.

---

## Candidate 02 — Dylan Prewitt

Python/Go: 1.5 / 5

REST API design: 1 / 5

SQL / data modeling: 1 / 5

Cloud infrastructure: 1 / 5

Ownership & collaboration: 3.5 / 5

Overall: 1.5 / 5

Notes (discrepancies / flags): YES — experience level inflated relative to reality. ~13 months total professional work (bootcamp + internship + FT), mostly bug fixes and Django template work, not backend API development. CV’s “familiar with AWS” is contradicted by interview (never deployed, only console clicks). Coachable and honest about gaps, but this is a junior candidate clearly mismatched to a mid‑level 3–5 yr req.

---

## Candidate 03 — Marcus Delgado-Finn

Python/Go: 3.5 / 5

REST API design: 2.5 / 5

SQL / data modeling: 3 / 5

Cloud infrastructure: 3 / 5

Ownership & collaboration: 2 / 5

Overall: 2.5 / 5

Notes (discrepancies / flags): YES — primary contradiction case. CV claims “designed the core API architecture from the ground up” and “led a team of 5”; interview shows he couldn’t substantiate architecture decisions (“docs would have that”), and his own submitted reference names a different person as tech lead and describes Marcus as a solid IC on the ETA module. Technically competent as an individual contributor, but leadership/ownership claims are not credible. Overall scored below raw average (2.8) due to unresolved credibility flags, consistent with the rule that integrity issues cap the Overall.

---

## Candidate 04 — Yuki Abernathy

Python/Go: 4 / 5

REST API design: 3 / 5

SQL / data modeling: 5 / 5

Cloud infrastructure: 1.5 / 5

Ownership & collaboration: 4 / 5

Overall: 3.5 / 5

Notes (discrepancies / flags): NO contradiction. CV claims are corroborated — SQL/query tuning is genuinely deep (caught rounding drift, cut batch from 6 hrs to 40 min). REST is adequate but shallow (internal APIs only, no versioned external experience). Cloud is a clear, admitted weakness (on‑prem background, minimal AWS/GCP). This is a genuine gap, not a false claim; scored accordingly. Strong hire if cloud isn’t a hard requirement; otherwise a conditional yes.

---

## Candidate 05 — Tomasz Wrenfield

Python/Go: 5 / 5

REST API design: 4.5 / 5

SQL / data modeling: 4 / 5

Cloud infrastructure: 5 / 5

Ownership & collaboration: 2 / 5

Overall: 4 / 5

Notes (discrepancies / flags): NO CV contradiction — all technical claims (p99 400→60 ms, Terraform/EKS ownership) are supported by specific, correct answers. Raw ability is outstanding. However, collaboration is a serious red flag: dismissive of past teammates, interrupts, “I tell them the right way.” This is a behavioral weakness, not a credibility issue, so it doesn’t trigger the “integrity cap” rule, but it pulls the Overall below the arithmetic average (4.1 → 4.0) to reflect that team‑fit risk. Hire only if paired with a strong lead and a culture that can handle blunt ICs.

---

## Candidate 06 — Amara Okonkwo-Bright

Python/Go: 4 / 5

REST API design: 4 / 5

SQL / data modeling: 3 / 5

Cloud infrastructure: 3 / 5

Ownership & collaboration: 5 / 5

Overall: 4 / 5

Notes (discrepancies / flags): NO discrepancy. Honest, solid mid‑level at the low end of the experience range (3 yrs, one company). REST design is strong (cursor pagination, versioning); SQL is average but she was upfront about it; Cloud is real but modest (Cloud Run, Pub/Sub, no IaC). Ownership and collaboration are exceptional (onboarding guide, mentoring, thoughtful on feedback). Overall score rounds up slightly due to team‑fit green flags — a safe, reliable hire who will grow into the role.

---

## Candidate 07 — Sistine Vale

Python/Go: 4.5 / 5

REST API design: 3.5 / 5

SQL / data modeling: 1.5 / 5

Cloud infrastructure: 5 / 5

Ownership & collaboration: 4 / 5

Overall: 3.5 / 5

Notes (discrepancies / flags): NO contradiction — cloud/AWS depth is genuine (IAM, Step Functions, 22% cost reduction). SQL is a clear demonstrated weakness (struggled with join, fully ORM‑reliant), not just absence of evidence — this is an active gap for any role requiring query or schema work. REST is adequate. Score reflects a specialist profile: a strong platform/infra engineer but a risky bet if the role demands data modeling; otherwise a strong yes.

---

## Candidate 08 — Rohan Marchetti

Python/Go: 4 / 5

REST API design: 2.5 / 5

SQL / data modeling: 5 / 5

Cloud infrastructure: 4.5 / 5

Ownership & collaboration: 4 / 5

Overall: 4 / 5

Notes (discrepancies / flags): NO contradiction. SQL/data modeling is genuinely exceptional (SCD, partitioning, 2TB/day pipelines). Cloud/GCP is strong and corroborated. Python is solid but “script‑like” — less service‑oriented. REST is the clear weak spot (thin on versioning/idempotency), acknowledged honestly. If the role is data‑platform or heavily SQL‑oriented, this is a top hire; if it’s pure API‑service work, the gap may be too wide. Score reflects the strong overlap with data/platform needs.

---

## Candidate 09 — Bjorn Castellanos

Python/Go: 4.5 / 5

REST API design: 4.5 / 5

SQL / data modeling: 3 / 5

Cloud infrastructure: 3 / 5

Ownership & collaboration: 3 / 5

Overall: 3.5 / 5

Notes (discrepancies / flags): NO CV contradiction — idempotent payment API and connection‑pooling claims are corroborated with concrete detail. Go/REST are strong; SQL is middling (no schema ownership); cloud is moderate (ECS deploy, light on networking/IaC). Tenure flag (4 jobs in 5 yrs) probed — reasons plausible (two layoffs, one relocation), but worth a reference check; not a contradiction, just a caution flag. Terse communication style, but not rude. Solid mid‑level, safe if references clear.

---

## Candidate 10 — Nadia Kessler

Python/Go: 3.5 / 5

REST API design: 3 / 5

SQL / data modeling: 3 / 5

Cloud infrastructure: 2.5 / 5

Ownership & collaboration: 3.5 / 5

Overall: 3 / 5

Notes (discrepancies / flags): NO contradiction — all claims are modest and match interview: shipped an export API, helped with queue migration. Middle‑of‑the‑road across every category — no demonstrated weakness, no standout strength. “Absence of evidence” is not a flag here; these are genuine but shallow competencies. A borderline candidate: would be a safe low‑mid hire if the bar is modest, but not compelling against the stronger profiles in this batch. Overall is a fair average of demonstrated competence.

---

## Scoring Methodology Final Ranking (Explicit Rules Applied Consistently)

Before the ranking, here are the three weighting rules I applied across every candidate:

Credibility / Integrity Cap – If an interview or reference actively contradicts a CV claim (e.g., claiming leadership when the reference names a different lead), the Overall score is capped below the raw average. This is a hard ceiling—unresolved trust issues override technical arithmetic.

Behavioral / Collaboration Discount – Clear interpersonal red flags (e.g., dismissiveness, interrupting, “I tell them the right way”) can lower the Overall slightly below the raw average. This is a softer penalty than fraud, but culture‑fit matters for long‑term team health.

JD‑Critical Category Weighting – The job description explicitly lists “owning data models and writing efficient SQL queries” as a core responsibility, whereas cloud infrastructure and API‑versioning nuance are listed as “hands‑on” or “working knowledge.” Therefore, a demonstrated weakness in SQL/Data Modeling costs more than an equivalent weakness in Cloud or REST design. This is why Sistine’s 3.7 raw average drops to 3.5, while Yuki’s and Rohan’s gaps in Cloud/REST do not incur an extra penalty beyond their raw scores.

## Final Ranking (1–10, best to worst)

1. **Priya Raghunathan** — 4.5 / 5
   Clear #1. No flags, every claim corroborated, top-tier SQL + API design + collaboration. The schema redesign story was concrete (p95 900→210 ms, rejected event sourcing, composite indexes). This is the complete package.

2. **Tomasz Wrenfield** — 4.0 / 5
   _(4.0 tier)_ Highest raw technical ceiling — Go, Cloud, and REST are all 4.5–5/5, and SQL is a solid 4. The 2/5 collaboration score is a real red flag, but it's behavioral, not credibility. For a role with a strong lead and a culture that can handle blunt ICs, his system-ownership upside outweighs the risk. Ranked above Rohan/Amara because his technical breadth matches the job most completely.

3. **Rohan Marchetti** — 4.0 / 5
   _(4.0 tier)_ Exceptional SQL (5/5) and strong GCP (4.5/5) — a perfect fit if the role leans data-platform. The 2.5 REST gap is his weak spot, but since SQL is JD-critical, his core strength carries more weight than Amara's "solid but unexceptional" profile. Ranked below Tomasz because Tomasz has no critical-category gap (his SQL is 4, while Rohan's REST is a clear weak spot for an API-heavy team).

4. **Amara Okonkwo-Bright** — 4.0 / 5
   _(4.0 tier)_ The safest, most team-positive hire. Ownership/collaboration is a 5 — she mentors, writes onboarding guides, and takes feedback gracefully. SQL (3) and Cloud (3) are modest but she was upfront about them. Ranked third in this tier because the other two have sharper spikes that better match critical JD needs.

5. **Yuki Abernathy** — 3.5 / 5
   _(3.5 tier)_ SQL is a 5 — the JD's core requirement — making her a genuine expert where it counts most. Cloud is a clear 1.5 gap, but that category is weighted less critical. Ranked above Bjorn and Sistine because a critical-category strength outweighs being "solid all-round."

6. **Bjorn Castellanos** — 3.5 / 5
   _(3.5 tier)_ Solidly middle-of-the-road across all technicals (Go/REST 4.5, SQL/Cloud 3). No critical gaps, no integrity flags. The tenure flag (4 jobs in 5 yrs) is a caution, not a contradiction. A safer all-rounder than Sistine, who has a critical SQL failure. Ranked below Yuki because her SQL mastery is more valuable than his well-roundedness.

7. **Sistine Vale** — 3.5 / 5
   _(3.5 tier)_ A genuine Cloud/AWS star (5/5) with strong Python, but the 1.5 in SQL is a demonstrated weakness in a JD-critical category — she struggled with a two-table join and is fully ORM-reliant. Ranked last in this tier because a core-skill gap is harder to close quickly than a non-core gap (Yuki's Cloud) or moderate all-round scores (Bjorn).

8. **Nadia Kessler** — 3.0 / 5
   No red flags, but no standouts either — a true "maybe." Scores cluster around 2.5–3.5 across the board. Would be a safe low-mid hire if the bar is modest, but falls to #8 against this batch.

9. **Marcus Delgado-Finn** — 2.5 / 5
   Hard cap applied for integrity/credibility. Raw average is ~2.8, but the contradiction between his CV (architecture owner, team lead of 5) and both the interview and his own submitted reference (solid IC, not tech lead) triggers the credibility rule. Competent as an IC, but trust in his narrative is broken.

10. **Dylan Prewitt** — 1.5 / 5
    Clear mismatch. A junior candidate (13 months real experience, bug-fix/template work) applying to a 3–5 yr mid-level role. Technical scores are 1–1.5 across critical categories. Honest and coachable — a green flag for a junior role, but firmly at the bottom for this one.
