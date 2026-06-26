
## Implementation Plan for Cogniviti FWA Detection POC

### Phase 1: Project Setup & Infrastructure
1. **Create directory structure** per the suggested repo structure
2. **Create `requirements.txt`** with all dependencies:
   - FastAPI, Uvicorn, Pydantic, SQLAlchemy
   - pandas, numpy, scikit-learn, scipy
   - google-generativeai (Gemini API)
   - python-dotenv, Jinja2
3. **Create `.env.example`** with GEMINI_API_KEY placeholder
4. **Initialize SQLite database** with SQLAlchemy models

### Phase 2: Data Models & Database (app/models.py)
5. **SQLAlchemy models** for:
   - `Claim` table (id, provider_id, provider_specialty, region, cpt_code, icd10_code, billed_amount, units, date_of_service, patient_id)
   - `PolicyExcerpt` table (id, source_citation, text, embedding)
   - `AnomalyFlag` table (id, claim_id, method, score, is_flagged, explanation_text, cited_policy_id)

### Phase 3: Pydantic Schemas (app/schemas.py)
6. **Request/Response schemas** for API endpoints
7. **Claim schema** matching the data model

### Phase 4: Detection Layer (Non-GenAI)
8. **`app/detection/base.py`** - Abstract base class `AnomalyDetector`
9. **`app/detection/zscore_detector.py`** - PeerZScoreDetector:
   - Group by (specialty, region, CPT)
   - Compute z-score on billed_amount per group
   - Flag if |z| > threshold (e.g., 2.5)
10. **`app/detection/isolation_forest_detector.py`** - IsolationForestDetector (stretch):
    - Multivariate anomaly detection on numeric features

### Phase 5: Synthetic Data Generation (app/data/synthetic_generator.py)
11. **`SyntheticClaimsGenerator`** class:
    - Fixed random seed for reproducibility
    - Generate realistic claim distributions
    - Seed known anomalies (e.g., 5-10% of batch with inflated amounts)
    - Return list of Claim objects

### Phase 6: Policy Corpus (app/data/policy_corpus.py)
12. **Hand-curated CMS policy excerpts** (10-15):
    - Real public CMS NCD/LCD citations
    - Pre-compute embeddings at startup or load from DB

### Phase 7: GenAI Layer
13. **`app/genai/policy_retriever.py`** - PolicyRetriever:
    - Embed claim context using Gemini Embeddings API
    - Cosine similarity search against policy corpus
    - Return top-k matches
14. **`app/genai/explanation_agent.py`** - ExplanationAgent:
    - Call Gemini generateContent with (claim, flag, retrieved policies)
    - Output: plain-English rationale + recommended action (pend/deny/auto-pay)
    - Must cite specific policy excerpt

### Phase 8: Orchestration Service (app/services/claims_review_service.py)
15. **`ClaimsReviewService`** class:
    - `generate_batch()` - calls generator, saves claims, runs detectors, saves flags
    - `get_claims()` - list with flag status
    - `get_claim_detail()` - single claim + flag info
    - `get_explanation()` - triggers GenAI explanation for flagged claim
    - `get_flagged_claims()` - filtered view

### Phase 9: FastAPI Routes (app/main.py)
16. **API Endpoints:**
    - POST `/claims/generate`
    - GET `/claims`
    - GET `/claims/{id}`
    - GET `/claims/{id}/explanation`
    - GET `/claims/flagged`

### Phase 10: Frontend Dashboard (app/templates/dashboard.html)
17. **Single-page dashboard** with:
    - Tailwind CDN styling
    - Claims table with color-coded badges (green/red/amber)
    - Click-to-expand rows showing: score, method, GenAI explanation, cited policy
    - "Generate New Batch" button (calls POST /claims/generate, refreshes table)
    - Vanilla JS for fetch + DOM updates

### Phase 11: Testing & Demo Verification
18. **Verify acceptance criteria:**
    - Run `uvicorn app.main:app --reload`
    - Generate batch → verify seeded anomalies flagged (100% recall)
    - Check explanations cite specific policies
    - Full demo flow < 2 minutes

---

**Key architectural decisions to confirm:**
1. **Z-score threshold** - what value? (PRD doesn't specify, suggest 2.5 or 3.0)
2. **Batch size** for synthetic generation? (suggest 100-200 claims for demo)
3. **Gemini model IDs** - need to verify current embedding/generation model names at build time
4. **Policy corpus** - I'll need to research real CMS NCD/LCD excerpts to include
