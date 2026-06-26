import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Any
from app.detection.base import AnomalyDetector, DetectionResult


class IsolationForestDetector(AnomalyDetector):
    MIN_BATCH_SIZE = 10

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state

    @property
    def method_name(self) -> str:
        return "isolation_forest"

    def _insufficient_batch_metadata(
        self, available_cols: List[str], batch_size: int
    ) -> Dict[str, Any]:
        return {
            "features_used": available_cols,
            "insufficient_batch_size": True,
            "minimum_batch_size": self.MIN_BATCH_SIZE,
            "actual_batch_size": batch_size,
        }

    def detect(self, claims: List[Dict[str, Any]]) -> List[DetectionResult]:
        if not claims:
            return []

        df = pd.DataFrame(claims)

        feature_cols = ["billed_amount", "units"]
        available_cols = [c for c in feature_cols if c in df.columns]

        if len(available_cols) < 2:
            results = []
            for _, row in df.iterrows():
                results.append(DetectionResult(
                    claim_id=row["id"],
                    method=self.method_name,
                    score=0.0,
                    is_flagged=False,
                    metadata=self._insufficient_batch_metadata(available_cols, len(df)),
                ))
            return results

        X = df[available_cols].values

        if len(X) < self.MIN_BATCH_SIZE:
            results = []
            for _, row in df.iterrows():
                results.append(DetectionResult(
                    claim_id=row["id"],
                    method=self.method_name,
                    score=0.0,
                    is_flagged=False,
                    metadata=self._insufficient_batch_metadata(available_cols, len(df)),
                ))
            return results

        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100
        )

        anomaly_scores = model.fit_predict(X)
        decision_scores = model.decision_function(X)

        min_score = decision_scores.min()
        max_score = decision_scores.max()
        normalized_scores = 1 - (decision_scores - min_score) / (max_score - min_score + 1e-10)

        results = []
        for idx, (_, row) in enumerate(df.iterrows()):
            is_flagged = anomaly_scores[idx] == -1
            score = float(normalized_scores[idx])
            feature_values = {col: float(row[col]) for col in available_cols}

            results.append(DetectionResult(
                claim_id=row["id"],
                method=self.method_name,
                score=score,
                is_flagged=is_flagged,
                metadata={
                    "features_used": available_cols,
                    "feature_values": feature_values,
                    "batch_size": len(df),
                    "contamination": self.contamination,
                    "normalized_anomaly_score": score,
                },
            ))

        return results
