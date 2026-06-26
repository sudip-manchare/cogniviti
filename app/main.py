import os
import json
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import init_db, get_db
from app.services.claims_review_service import ClaimsReviewService

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Cogniviti – Claims FWA Anomaly Detection & Explanation",
    version="0.1.0",
    description="Hybrid non-GenAI + GenAI pipeline for healthcare claims review.",
    lifespan=lifespan,
)

templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


def get_service(db: Session = Depends(get_db)) -> ClaimsReviewService:
    return ClaimsReviewService(db)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    service = ClaimsReviewService(db)
    claims = service.get_claims()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"request": request, "claims": json.dumps(claims)},
    )


@app.post("/claims/generate")
def generate_claims(
    batch_size: int = Query(100, ge=1, le=1000),
    anomaly_rate: float = Query(0.1, ge=0.01, le=0.5),
    seed: int = Query(42),
    db: Session = Depends(get_db),
):
    service = ClaimsReviewService(db)
    result = service.generate_batch(
        batch_size=batch_size,
        anomaly_rate=anomaly_rate,
        seed=seed,
    )
    return result


@app.get("/claims")
def list_claims(db: Session = Depends(get_db)):
    service = ClaimsReviewService(db)
    return service.get_claims()


@app.get("/claims/flagged")
def list_flagged_claims(db: Session = Depends(get_db)):
    service = ClaimsReviewService(db)
    return service.get_flagged_claims()


@app.get("/claims/{claim_id}")
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    service = ClaimsReviewService(db)
    claim = service.get_claim_detail(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@app.get("/claims/{claim_id}/explanation")
def get_explanation(claim_id: int, db: Session = Depends(get_db)):
    service = ClaimsReviewService(db)
    result = service.get_explanation(claim_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Claim not found")
    return result


@app.get("/health")
def health():
    return {"status": "ok"}