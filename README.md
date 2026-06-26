# Intern Submission — Cogniviti

**Topic:** Clinical Decision Making and Pattern Recognition in Health Care: Chain Reasoning, Agentic Generative AI, Classification, Prediction, Inference, Clustering, & Time-Series Anomaly Detection for Treatment, Payment, & Operations (TPO)

Hybrid ML + GenAI pipeline for healthcare claims fraud, waste, and abuse detection — a hackathon POC demonstrating classification, anomaly detection, and agentic GenAI reasoning on synthetic claims data.

## Deliverables

| Deliverable | Link |
|-------------|------|
| **POC Demo Code** | This repository |
| **Video Recording** | [![Watch Demo](https://img.youtube.com/vi/8l6WAxyj4Kc/0.jpg)](https://youtu.be/8l6WAxyj4Kc) |
| **Slide Presentation** | [`Cogniviti_AI-Driven_Payment_Integrity.pptx`](./Cogniviti_AI-Driven_Payment_Integrity.pptx) |
| **Written Report** | [`Cotiviti_FWA_Report.docx`](./Cotiviti_FWA_Report.docx) |

## Quick Start

```bash
cp .env.example .env    # add your GEMINI_API_KEY
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000 — click "Generate New Batch" to seed claims and see flagged results.

## Architecture

Three explicit layers:

1. **Detection (non-GenAI)** — `PeerZScoreDetector` & `IsolationForestDetector` compute anomaly scores from claim data alone (zero network).
2. **GenAI** — `PolicyRetriever` embeds claim context via Gemini Embeddings, cosine-similarity matches against 15 real CMS NCD/LCD excerpts; `ExplanationAgent` calls Gemini to produce cited rationale + recommended action.
3. **Interface** — Tailwind CSS dashboard with expandable flagged-claim details.

## Project Structure

```
app/
├── main.py                           # FastAPI app, routes, lifespan
├── models.py                         # SQLAlchemy ORM models
├── schemas.py                        # Pydantic request/response schemas
├── database.py                       # SQLite engine + session
├── detection/
│   ├── base.py                       # AnomalyDetector ABC
│   ├── zscore_detector.py            # Peer-group z-score detection
│   └── isolation_forest_detector.py  # Multivariate Isolation Forest
├── genai/
│   ├── policy_retriever.py           # Gemini embeddings + cosine-similarity retrieval
│   └── explanation_agent.py          # Gemini generateContent → rationale + action
├── data/
│   ├── synthetic_generator.py        # Reproducible claim batches with seeded anomalies
│   └── policy_corpus.py              # 15 hand-curated, cited CMS policy excerpts
├── services/
│   └── claims_review_service.py      # Orchestrator: generate, detect, explain
└── templates/
    └── dashboard.html                # Single-page Tailwind + vanilla JS UI

tests/
├── test_synthetic_generator.py       # 10 tests — batch size, seeding, reproducibility
├── test_detection.py                 # 11 tests — z-score, Isolation Forest edge cases
├── test_api.py                       # 11 tests — all 5 endpoints, edge cases
└── test_integration.py               # 5 tests — full pipeline end-to-end
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/claims/generate` | Create a synthetic batch (params: `batch_size`, `anomaly_rate`, `seed`) |
| GET | `/claims` | List all claims with flag status |
| GET | `/claims/flagged` | Filter to flagged claims only |
| GET | `/claims/{id}` | Single claim detail with flags |
| GET | `/claims/{id}/explanation` | Generate/return GenAI rationale for a flagged claim |
| GET | `/health` | Health check |

## Testing

```bash
python3 -m pytest tests/ -v
```

38 tests covering all functional requirements (F1–F8) plus integration.

## Key Design Decisions

- Detection layer is fully independent — computable and testable with zero network access.
- Fixed random seed (42) makes demo runs reproducible.
- Policy corpus contains real CMS NCD/LCD excerpts with proper citations.
- `GEMINI_API_KEY` read from environment, never hardcoded.

## Tech Stack

Python 3.11+ · FastAPI · Uvicorn · SQLAlchemy + SQLite · pandas · numpy · scikit-learn · Google Gemini API · Jinja2 · Tailwind CSS
