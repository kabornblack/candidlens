# Candidate 04 — Yuki Abernathy

## CV Summary

- **Name:** Yuki Abernathy
- **Experience:** 4 years professional backend development
- **Recent roles:**
  - Backend Engineer, Northwind Payments (2.5 yrs) — reconciliation and ledger services in Python
  - Software Engineer, Kettleworth Robotics (1.5 yrs) — on-prem fleet telemetry backend
- **Key skills:** Python (strong), PostgreSQL + advanced query tuning, dimensional and normalized data modeling, some REST (internal APIs), Linux/on-prem ops, minimal cloud
- **Claimed achievements:**
  - Built the double-entry ledger schema and reconciliation queries at Northwind; caught a class of rounding drift that had gone unnoticed for months
  - Cut a nightly batch job from 6 hrs to 40 min through query and index work

## Interview Notes

- SQL is a real strength: nailed the join + window function exercise fast, then optimized it further unprompted, explained the index tradeoff and when a partial index helps. Best SQL of the batch so far.
- Python solid — clean code, good instincts on transactions and isolation levels for the ledger work.
- REST design is adequate but shallow: has only built internal service-to-service endpoints, never a versioned external API. Answers on pagination/versioning were textbook, not lived.
- Cloud is the clear gap: Kettleworth was fully on-prem, Northwind is mid-migration and Yuki hasn't been hands-on with it. Never provisioned AWS/GCP resources. Willing to learn, but starting near zero.
- Communication is calm and precise; collaborates well, described a constructive code-review disagreement resolution. No red flags on attitude.
