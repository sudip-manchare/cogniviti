from datetime import date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict


class ClaimBase(BaseModel):
    provider_id: str
    provider_specialty: str
    region: str
    cpt_code: str
    icd10_code: str
    billed_amount: float
    units: int = 1
    date_of_service: date
    patient_id: str


class ClaimCreate(ClaimBase):
    pass


class ClaimResponse(ClaimBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class AnomalyFlagBase(BaseModel):
    method: str
    score: float
    is_flagged: bool
    detection_metadata: Optional[Dict[str, Any]] = None
    explanation_text: Optional[str] = None
    cited_policy_id: Optional[int] = None


class AnomalyFlagResponse(AnomalyFlagBase):
    id: int
    claim_id: int
    model_config = ConfigDict(from_attributes=True)


class PolicyExcerptBase(BaseModel):
    source_citation: str
    text: str
    embedding: Optional[str] = None


class PolicyExcerptResponse(PolicyExcerptBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ClaimDetailResponse(ClaimResponse):
    anomaly_flags: List[AnomalyFlagResponse] = []


class BatchGenerateRequest(BaseModel):
    batch_size: int = 100
    anomaly_rate: float = 0.1
    seed: int = 42


class BatchGenerateResponse(BaseModel):
    claims_created: int
    anomalies_seeded: int
    flagged_count: int


class ExplanationResponse(BaseModel):
    claim_id: int
    explanation_text: str
    cited_policy: Optional[PolicyExcerptResponse] = None
    recommended_action: str