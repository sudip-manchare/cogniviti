# Product Requirements Document
## Cogniviti — Claims Fraud, Waste & Abuse (FWA) Anomaly Detection & Explanation POC

**Status:** Draft for build
**Owner:** Sudip Manchare
**Purpose:** Hackathon proof-of-concept for Cotiviti Intern Assessment (Topic: Clinical Decision Making and Pattern Recognition in Health Care — Agentic Generative AI, Classification, Anomaly Detection for TPO)

---

## 1. Problem Statement

Healthcare fraud, waste, and abuse (FWA) costs the U.S. healthcare system an estimated 3–10% of total spend annually — conservatively tens of billions of dollars, with some estimates exceeding $300B/year. Payers process millions of claims daily and cannot manually review each one, which is why FWA detection has shifted from manual investigation toward advanced analytics and automated triage.

This POC demonstrates a hybrid architecture that mirrors how real payment-integrity products (e.g., Cotiviti's Payment Accuracy suite) approach this problem: a deterministic statistical/ML layer does the actual anomaly detection, and a GenAI layer adds plain-English, policy-cited explanations on top — making flagged claims fast and defensible for a human reviewer to act on.

## 2. Goals

- Demonstrate a working, end-to-end pipeline: synthetic claim → anomaly score → policy retrieval → natural-language rationale → reviewer-facing dashboard.
- Make the **non-GenAI vs GenAI split** visually and narratively clear (this is the core technical story for the video).
- Keep the build fast and demo-reliable over feature-complete.

## 3. Non-Goals (explicitly out of scope for POC)

- No real PHI or production claims data — synthetic data only.
- No authentication, multi-tenancy, or production security hardening.
- No real-time claim ingestion/streaming.
- Not a replacement for human reviewer judgment — decision-support only, framed that way in the UI copy.
- No deployment infrastructure — local run via `uvicorn` is sufficient.

## 4. Target Users / Personas

| Persona | Need |
|---|---|
| Claims / Payment Integrity Analyst (primary) | Fast, plain-English reason a claim was flagged, with a concrete next action |
| SIU Investigator (secondary) | Audit trail — exactly which policy clause and which numeric deviation triggered the flag |
| Health Plan VP of Payment Integrity (buyer persona, for framing in report/slides) | $ value potential, false-positive rate, time-to-flag |

## 5. System Architecture

Three explicit layers — keep this separation visible in the code and in the demo narration:

1. **Detection layer (non-GenAI)** — deterministic, auditable, reproducible. Computes anomaly scores from claim data alone.
2. **GenAI layer** — retrieves relevant policy text and turns a numeric flag into a cited, human-readable explanation. Does NOT decide whether a claim is anomalous.
3. **Interface layer** — dashboard for a reviewer to triage flagged claims.

### Component / Class Breakdown

```
Claim                      — pydantic model: claim record
SyntheticClaimsGenerator   — generates a reproducible batch of claims with seeded anomalies
AnomalyDetector (ABC)
 ├─ PeerZScoreDetector      — z-score vs (specialty, region, CPT) peer group
 └─ IsolationForestDetector — optional secondary/multivariate detector
PolicyExcerpt              — model: a single citable policy clause
PolicyRetriever             — embeds claim context + policy corpus via Gemini Embeddings API, cosine-similarity top-k match
ExplanationAgent            — calls Gemini generateContent with (claim, flag, retrieved policy) → rationale + recommended action
ClaimsReviewService         — orchestrator; FastAPI routes call this only
```

## 6. Tech Stack (finalized)

| Layer | Choice |
|---|---|
| Backend framework | Python 3.11+, FastAPI, Uvicorn |
| Data validation | Pydantic |
| Detection layer | pandas, numpy, scikit-learn (`scipy.stats.zscore`, `IsolationForest`) |
| Persistence | SQLAlchemy ORM + SQLite |
| Embeddings (RAG) | Gemini Embeddings API |
| Generation (explanations) | Gemini API (`generateContent`) |
| Frontend | Jinja2 server-rendered templates, Tailwind CSS via CDN, vanilla JS (fetch + DOM updates only — no JS framework) |
| Config | `.env` for `GEMINI_API_KEY`, loaded via `python-dotenv` |

> Note for implementation: confirm the current Gemini embedding and generation model identifiers at build time — these change over time and should not be hardcoded from memory.

## 7. Data Model

**`claims` table**
- `id` (PK), `provider_id`, `provider_specialty`, `region`, `cpt_code`, `icd10_code`, `billed_amount`, `units`, `date_of_service`, `patient_id`

**`policy_excerpts` table**
- `id` (PK), `source_citation` (e.g., "CMS NCD 123.4"), `text`, `embedding` (stored as serialized vector)

**`anomaly_flags` table**
- `id` (PK), `claim_id` (FK), `method` (e.g., `peer_zscore`), `score`, `is_flagged` (bool), `explanation_text`, `cited_policy_id` (FK, nullable)

## 8. Functional Requirements

| ID | Feature |
|---|---|
| F1 | Generate a reproducible synthetic batch of claims (fixed random seed) with a known number of seeded anomalies |
| F2 | Run peer-group z-score detection across the batch; persist scores |
| F3 | (Stretch) Run Isolation Forest as a secondary multivariate check |
| F4 | Embed a small hand-curated policy corpus (10–15 excerpts) and the flagged claim's context; retrieve top-1–3 matches via cosine similarity |
| F5 | Generate a plain-English explanation per flagged claim, citing the retrieved policy excerpt and recommending an action (pend / deny / auto-pay) |
| F6 | Orchestrate F1–F5 behind a single service class, exposed via FastAPI routes |
| F7 | Dashboard: claims table with flag status badges; click a row to expand the GenAI rationale |
| F8 | "Generate new batch" action for live, repeatable demo on camera |

## 9. API Endpoints

```
POST /claims/generate          → generates a new synthetic batch, returns batch summary
GET  /claims                   → list all claims with flag status
GET  /claims/{id}              → single claim detail
GET  /claims/{id}/explanation  → triggers/returns GenAI rationale for a flagged claim
GET  /claims/flagged           → flagged claims only, for the dashboard default view
```

## 10. UI/UX Requirements

- Single dashboard page, Tailwind CDN for styling — clean table layout, color-coded badges (green = clean, red = flagged, amber = under review).
- Click-to-expand row reveals: anomaly score, method used, GenAI explanation, cited policy excerpt.
- "Generate new batch" button visible at top for demo reproducibility.
- Should look intentional and reviewer-facing — this is the visual the camera will be on, so prioritize clarity over density.

## 11. Acceptance Criteria

- Detector flags all seeded anomalies in the synthetic batch (target: 100% recall on the known seeded set — this is a controlled test, report it honestly on camera).
- False positives, if any, are visible and explainable, not hidden.
- Every flagged claim's explanation cites a specific policy excerpt — never a generic "this seems unusual" output.
- Full pipeline runs locally via `uvicorn main:app --reload` with no external dependencies beyond the Gemini API.
- End-to-end demo flow (generate batch → view dashboard → expand a flagged claim) completes in under 2 minutes.

## 12. Suggested Repo Structure

```
Cogniviti/
├── app/
│   ├── main.py                  # FastAPI app + routes
│   ├── models.py                # SQLAlchemy models
│   ├── schemas.py                # Pydantic schemas
│   ├── detection/
│   │   ├── base.py               # AnomalyDetector ABC
│   │   ├── zscore_detector.py
│   │   └── isolation_forest_detector.py
│   ├── genai/
│   │   ├── policy_retriever.py
│   │   └── explanation_agent.py
│   ├── services/
│   │   └── claims_review_service.py
│   ├── data/
│   │   ├── synthetic_generator.py
│   │   └── policy_corpus.py       # hand-curated, cited CMS policy excerpts
│   └── templates/
│       └── dashboard.html
├── .env.example
├── requirements.txt
└── README.md
```

## 13. Implementation Notes for the Build Agent

- Keep the detection layer's output (score, method, flagged boolean) fully independent of any LLM call — it should be computable and testable with zero network access.
- The policy corpus should be small, hand-picked, and properly cited (real public CMS NCD/LCD excerpts) — do not fabricate policy text.
- Use a fixed random seed in `SyntheticClaimsGenerator` so demo runs are reproducible.
- `GEMINI_API_KEY` must be read from environment, never hardcoded.