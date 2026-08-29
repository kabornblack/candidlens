# Candidate 01 — Priya Raghunathan

## CV Summary

- **Name:** Priya Raghunathan
- **Experience:** 4.5 years professional backend development
- **Recent roles:**
  - Backend Engineer, Meridian Freight Systems (2.5 yrs) — Python/FastAPI services for shipment tracking, ~4k req/s peak
  - Backend Engineer, Lumen Cartography (1.5 yrs) — Go microservices for a mapping tile API
  - Software Engineer Intern → Junior Engineer, Halcyon Data Co. (0.5 yr)
- **Key skills:** Python (primary), Go (production), REST API design, PostgreSQL + schema design, AWS (ECS, RDS, S3, CloudWatch), Docker, GitHub Actions CI
- **Claimed achievements:**
  - Redesigned the shipment-events schema and query layer at Meridian, cutting p95 latency on the tracking endpoint from 900 ms to 210 ms
  - Introduced contract tests and a staged rollout process for the public tracking API, reducing breaking-change incidents to zero over 18 months

## Interview Notes

- Walked through the Meridian schema redesign end to end — explained the composite index choice, why they denormalized the carrier lookup, and the tradeoff they rejected (event sourcing, too heavy for the team). Clearly did the work.
- REST design: gave a clean answer on versioning, idempotency keys for the create-shipment endpoint, and pagination via cursors over offsets. Unprompted, mentioned how they'd deprecate a field.
- SQL live exercise: wrote a correct 3-table join with a window function for "latest status per shipment" without hints. Reasoned about the query plan out loud.
- Cloud: described their ECS + RDS setup, blue/green deploys via GitHub Actions, and how they handle DB migrations safely. Comfortable, not hand-wavy.
- Green flag: talks about mentoring two juniors at Meridian, running their team's code review norms doc. Calm, concise communicator. No red flags.
