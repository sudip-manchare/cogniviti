from datetime import date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Claim, AnomalyFlag, PolicyExcerpt
from app.data.synthetic_generator import SyntheticClaimsGenerator
from app.data.policy_corpus import get_policy_excerpts
from app.detection.zscore_detector import PeerZScoreDetector
from app.detection.isolation_forest_detector import IsolationForestDetector
from app.genai.policy_retriever import PolicyRetriever
from app.genai.explanation_agent import ExplanationAgent


class ClaimsReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.generator = SyntheticClaimsGenerator()
        self.zscore_detector = PeerZScoreDetector(threshold=2.5)
        self.isolation_forest_detector = IsolationForestDetector()
        self.policy_retriever = PolicyRetriever(top_k=3)
        self.explanation_agent = ExplanationAgent()

    def _seed_policy_corpus(self):
        existing = self.db.query(PolicyExcerpt).count()
        if existing > 0:
            return

        excerpts = get_policy_excerpts()
        for ex in excerpts:
            policy = PolicyExcerpt(
                source_citation=ex["source_citation"],
                text=ex["text"],
            )
            self.db.add(policy)
        self.db.commit()

    def _claim_to_dict(self, claim: Claim) -> Dict[str, Any]:
        return {
            "id": claim.id,
            "provider_id": claim.provider_id,
            "provider_specialty": claim.provider_specialty,
            "region": claim.region,
            "cpt_code": claim.cpt_code,
            "icd10_code": claim.icd10_code,
            "billed_amount": claim.billed_amount,
            "units": claim.units,
            "date_of_service": claim.date_of_service.isoformat() if claim.date_of_service else None,
            "patient_id": claim.patient_id,
        }

    def generate_batch(
        self,
        batch_size: int = 100,
        anomaly_rate: float = 0.1,
        seed: int = 42,
    ) -> Dict[str, int]:
        self._seed_policy_corpus()

        claims_data = self.generator.generate_batch(
            batch_size=batch_size,
            anomaly_rate=anomaly_rate,
        )

        seeded_anomalies = sum(1 for c in claims_data if c.get("is_seeded_anomaly"))

        db_claims = []
        for claim_data in claims_data:
            claim = Claim(
                provider_id=claim_data["provider_id"],
                provider_specialty=claim_data["provider_specialty"],
                region=claim_data["region"],
                cpt_code=claim_data["cpt_code"],
                icd10_code=claim_data["icd10_code"],
                billed_amount=claim_data["billed_amount"],
                units=claim_data.get("units", 1),
                date_of_service=date.fromisoformat(claim_data["date_of_service"]) if isinstance(claim_data["date_of_service"], str) else claim_data["date_of_service"],
                patient_id=claim_data["patient_id"],
            )
            self.db.add(claim)
            self.db.flush()
            claim_data["id"] = claim.id
            db_claims.append(claim)

        self.db.commit()

        zscore_results = self.zscore_detector.detect(claims_data)

        if_results = self.isolation_forest_detector.detect(claims_data)

        all_results = {r.claim_id: r for r in zscore_results}
        for r in if_results:
            if r.claim_id not in all_results or r.is_flagged:
                all_results[r.claim_id] = r

        flagged_count = 0
        for result in all_results.values():
            flag = AnomalyFlag(
                claim_id=result.claim_id,
                method=result.method,
                score=result.score,
                is_flagged=1 if result.is_flagged else 0,
                detection_metadata=result.metadata,
            )
            self.db.add(flag)
            if result.is_flagged:
                flagged_count += 1

        self.db.commit()

        return {
            "claims_created": len(claims_data),
            "anomalies_seeded": seeded_anomalies,
            "flagged_count": flagged_count,
        }

    def _flag_to_dict(self, flag: AnomalyFlag) -> Dict[str, Any]:
        flag_dict = {
            "id": flag.id,
            "method": flag.method,
            "score": flag.score,
            "is_flagged": bool(flag.is_flagged),
            "detection_metadata": flag.detection_metadata,
            "explanation_text": flag.explanation_text,
            "cited_policy_id": flag.cited_policy_id,
        }
        if flag.cited_policy:
            flag_dict["cited_policy"] = {
                "id": flag.cited_policy.id,
                "source_citation": flag.cited_policy.source_citation,
                "text": flag.cited_policy.text,
            }
        return flag_dict

    def get_claims(self) -> List[Dict[str, Any]]:
        claims = (
            self.db.query(Claim)
            .order_by(desc(Claim.id))
            .all()
        )

        results = []
        for claim in claims:
            claim_dict = self._claim_to_dict(claim)
            claim_dict["anomaly_flags"] = [
                self._flag_to_dict(flag) for flag in claim.anomaly_flags
            ]
            results.append(claim_dict)

        return results

    def get_claim_detail(self, claim_id: int) -> Optional[Dict[str, Any]]:
        claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            return None

        claim_dict = self._claim_to_dict(claim)
        claim_dict["anomaly_flags"] = [
            self._flag_to_dict(flag) for flag in claim.anomaly_flags
        ]
        return claim_dict

    def get_flagged_claims(self) -> List[Dict[str, Any]]:
        flagged_flags = (
            self.db.query(AnomalyFlag)
            .filter(AnomalyFlag.is_flagged == 1)
            .all()
        )

        claim_ids = list(set(f.claim_id for f in flagged_flags))
        claims = self.db.query(Claim).filter(Claim.id.in_(claim_ids)).all()
        claim_map = {c.id: c for c in claims}

        results = []
        for flag in flagged_flags:
            claim = claim_map.get(flag.claim_id)
            if not claim:
                continue
            claim_dict = self._claim_to_dict(claim)
            claim_dict["anomaly_flags"] = [self._flag_to_dict(flag)]
            results.append(claim_dict)

        return results

    def get_explanation(self, claim_id: int) -> Optional[Dict[str, Any]]:
        claim = self.db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            return None

        flag = (
            self.db.query(AnomalyFlag)
            .filter(AnomalyFlag.claim_id == claim_id, AnomalyFlag.is_flagged == 1)
            .first()
        )

        if not flag:
            return {
                "claim_id": claim_id,
                "explanation_text": "This claim was not flagged as anomalous.",
                "cited_policy": None,
                "recommended_action": "Auto-Pay",
            }

        if flag.explanation_text:
            cited_policy = None
            if flag.cited_policy:
                cited_policy = {
                    "id": flag.cited_policy.id,
                    "source_citation": flag.cited_policy.source_citation,
                    "text": flag.cited_policy.text,
                }
            return {
                "claim_id": claim_id,
                "explanation_text": flag.explanation_text,
                "cited_policy": cited_policy,
                "recommended_action": "Pend for Review",
            }

        self.policy_retriever.initialize_corpus()
        claim_context = self.policy_retriever.format_claim_context(self._claim_to_dict(claim))
        retrieved = self.policy_retriever.retrieve(claim_context)

        flag_info = {
            "method": flag.method,
            "score": flag.score,
            "metadata": flag.detection_metadata,
        }

        explanation = self.explanation_agent.generate_explanation(
            self._claim_to_dict(claim),
            flag_info,
            retrieved,
        )

        cited_policy_id = None
        if retrieved:
            first_policy = retrieved[0][0]
            policy_record = (
                self.db.query(PolicyExcerpt)
                .filter(PolicyExcerpt.source_citation == first_policy["source_citation"])
                .first()
            )
            if policy_record:
                cited_policy_id = policy_record.id

        flag.explanation_text = explanation.get("rationale", "")
        flag.cited_policy_id = cited_policy_id
        self.db.commit()

        cited_policy = None
        if cited_policy_id:
            policy = self.db.query(PolicyExcerpt).filter(PolicyExcerpt.id == cited_policy_id).first()
            if policy:
                cited_policy = {
                    "id": policy.id,
                    "source_citation": policy.source_citation,
                    "text": policy.text,
                }

        return {
            "claim_id": claim_id,
            "explanation_text": explanation.get("rationale", ""),
            "cited_policy": cited_policy,
            "recommended_action": explanation.get("recommended_action", "Pend for Review"),
        }