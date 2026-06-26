Pattern Recognition and Agentic AI for Payment Integrity
Detecting Fraud, Waste, and Abuse in Healthcare Claims
1. Defining the Topic
Clinical decision making and pattern recognition in health care covers a family of techniques like classification, prediction, inference, clustering, and time-series anomaly detection that are applied across three intersecting domains: Treatment, Payment, and Operations (TPO). I have chosen to focus on the Payment and Operations dimensions, specifically how pattern recognition combined with agentic generative AI can identify fraud, waste, and abuse (FWA) in healthcare claims before money leaves the building.
FWA is formally distinguished by intent: fraud involves knowingly submitting false claims, waste reflects careless overuse of services without criminal intent, and abuse describes care that fails to meet recognized clinical standards (Centene, 2026). Detecting these patterns at scale requires two capabilities: a deterministic statistical or machine-learning layer flags claims that deviate from expected peer-group, temporal, or coding norms and an agentic generative AI layer that retrieves relevant billing policy, reasons across the available evidence (chain reasoning), and produces a citable, human-readable explanation for why a claim was flagged. Neither layer is sufficient alone: a statistical model lacks the interpretive reasoning needed for actionable inference, and a language model lacks the numerical precision and reproducibility a decision needs once it faces audit or appeal.
2. Industry Trends
The underlying problem is large enough to keep this topic strategically urgent: the National Health Care Anti-Fraud Association estimates that 3 to 10 percent of total U.S. health care spending (potentially exceeding $300 billion annually) is lost to FWA (NHCAA, n.d.). Because payers process millions of claims daily, the industry has steadily shifted from manual investigative review toward advanced analytics and automated detection (Vee Healthtek, 2024).
Generative and agentic AI now sit at the leading edge of that shift. Gartner forecasts that by 2028, 80 percent of ambulatory claims will move through AI-enabled, real-time adjudication (Cohere Health, 2026), and major automation vendors like UiPath and Accenture have launched agentic offerings in 2026 specifically for claim denial prevention, prior authorization, and payment integrity workflows (UiPath, 2026; Accenture, 2026). Industry research from HealthVerity indicates most agentic deployments remain in early pilot stages, concentrated among larger, technology-forward payers, suggesting a near-term window for a fast-moving, well-governed entrant to differentiate (HealthVerity, 2025).
3. Opportunities
For Cotiviti, advancing this capability set offers concrete upside, and the company's own client results already show the value achievable with focused payment-accuracy work: one health plan tripled its projected findings after adopting clinical chart (DRG) validation, and coordination-of-benefits clients realize roughly 80 percent of overpaid findings as actual cost savings (Cotiviti, 2026a). Layering a GenAI explanation capability on top of existing detection models compounds this value by shortening review cycles and Cotiviti already reports cutting time-to-results from over 90 days to under five through integrated pre- and postpay programs (Cotiviti, 2026b), all while producing the auditable rationale regulators increasingly require. A well-explained flag is also a faster flag, reducing both administrative cost and provider abrasion at once.
4. Threats
The same capability carries real regulatory and reputational exposure. As of early 2026, at least 25 states have adopted guidance based on the NAIC's AI Model Bulletin, requiring insurers to document AI oversight, demonstrate explainability for automated decisions, and accept responsibility for third-party AI vendors (KFF, 2026). Several states have gone further: Texas, Arizona, Maryland, and Indiana now prohibit using AI as the sole basis for an adverse claim determination or coding downgrade without human review, and California's SB 1120 has barred fully automated coverage denials since 2025 (Sheppard Mullin, 2026; Holland & Knight, 2026).
Poorly governed AI has already triggered litigation, including allegations that one insurer’s review algorithm had a 90 percent error rate, and that another's automated review system enabled physicians to reject hundreds of thousands of claims in a matter of months at roughly a second of review each (PCMI, 2026). For a vendor whose product is AI-assisted claim review, the central risk is governance, not technical failure: an explanation layer that misapplies a policy citation, or a detection model that drifts as billing behavior adapts to evade it, could expose Cotiviti and its health-plan clients to exactly this kind of scrutiny.
5. Strategic Recommendations for Cotiviti
I suggest exploring three main options. First, I recommend a “detect and explain” approach for our product. We can pair our current data-mining models with a new AI layer that finds the exact policy clause for every flag. This way, we give reviewers a clear reason for each decision and meet state legal requirements for explainability from the start.
Second, I propose building an agentic payment-integrity copilot for our analysts. This tool would automatically pull up the relevant coding and coverage policies for each claim, draft the review rationale, and route it to a human reviewer. This approach saves time while maintaining the human-in-the-loop oversight required by recent state laws.
Third, I believe we should prioritize "compliance-by-design" as a market differentiator. With many new state AI regulations emerging, we can gain a significant advantage by building features like audit logs, bias testing, and human-review checkpoints directly into our core product, rather than rushing to retrofit them later.
Pattern recognition and agentic AI are converging on payment integrity faster than the regulatory floor beneath them is settling. Organizations that treat explainability and human oversight as core product features, not compliance overhead, are best positioned to capture the underlying $300 billion opportunity without inheriting its legal exposure.
References
Accenture. (2026, February 6). Agentic AI is transforming health insurance claims. Accenture Insurance Blog. https://insuranceblog.accenture.com/agentic-ai-transforming-claims-health-insurance
Centene Corporation. (2026). Combating fraud, waste and abuse (FWA). https://www.centene.com/why-were-different/healthcare-fraud-waste-abuse-oversight.html
Cohere Health. (2026, February 27). Agentic AI for health plans: Key Gartner 2026 insights. https://www.coherehealth.com/blog/agentic-ai-health-plans-gartner-2026-insights
Cotiviti, Inc. (2026a). Healthcare claim payment accuracy solutions. https://www.cotiviti.com/solutions/payment-accuracy
Cotiviti, Inc. (2026b). Payment accuracy solutions for health plans. https://resources.cotiviti.com/payment-accuracy-solutions
HealthVerity. (2025, December 29). AI trends shaping healthcare in 2026: Agentic, physical & sovereign AI. https://blog.healthverity.com/ai-trends-shaping-healthcare-in-2026-agentic-physical-sovereign-ai
Holland & Knight. (2026, May). States continue efforts to regulate AI in healthcare: A review of legislation passed in 2026. https://www.hklaw.com/en/insights/publications/2026/05/states-continue-efforts-to-regulate-ai-in-healthcare
Kaiser Family Foundation. (2026, May 6). Regulation of AI in prior authorization and claims review: A look at federal and state consumer protections. https://www.kff.org/patient-consumer-protections/regulation-of-ai-in-prior-authorization-and-claims-review-a-look-at-federal-and-state-consumer-protections/
National Health Care Anti-Fraud Association. (n.d.). The challenge of health care fraud. https://www.nhcaa.org/tools-insights/about-health-care-fraud/the-challenge-of-health-care-fraud/
PCMI Corporation. (2026, April 27). The regulatory clock on AI claims is already running. https://www.pcmicorp.com/2026/04/the-regulatory-clock-on-ai-claims-is-already-running/
Sheppard Mullin. (2026, April 21). State legislatures consider oversight of artificial intelligence in health insurance decisions. https://www.sheppard.com/insights/blogs/state-legislatures-consider-oversight-of-artificial-intelligence-in-health-insurance-decisions
UiPath, Inc. (2026, February 23). UiPath launches agentic AI solutions to break administrative & financial bottlenecks for clinicians and healthcare admins. https://ir.uipath.com/news/detail/428/uipath-launches-agentic-ai-solutions-to-break-administrative-financial-bottlenecks-for-clinicians-and-healthcare-admins
Vee Healthtek. (2024). Fraud, waste, and abuse prevention and protection. https://www.veehealthtek.com/resources/white-papers/healthcare-white-papers/fraud-waste-and-abuse-prevention-and-protection.htm


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