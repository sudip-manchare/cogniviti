import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict, Any
from app.detection.base import AnomalyDetector, DetectionResult


class PeerZScoreDetector(AnomalyDetector):
    def __init__(self, threshold: float = 2.5):
        self.threshold = threshold

    @property
    def method_name(self) -> str:
        return "peer_zscore"

    def _build_metadata(
        self,
        group_key: str,
        group_size: int,
        billed_amount: float,
        z_score: float,
        peer_mean: float = None,
        peer_std: float = None,
        insufficient_peers: bool = False,
    ) -> Dict[str, Any]:
        metadata = {
            "peer_group": group_key,
            "group_size": group_size,
            "claim_billed_amount": billed_amount,
            "z_score_threshold": self.threshold,
        }
        if insufficient_peers:
            metadata["insufficient_peers"] = True
        else:
            metadata["peer_mean_billed_amount"] = float(peer_mean)
            metadata["peer_std_billed_amount"] = float(peer_std)
            metadata["deviation_from_peer_mean"] = float(billed_amount - peer_mean)
            metadata["z_score"] = z_score
        return metadata

    def detect(self, claims: List[Dict[str, Any]]) -> List[DetectionResult]:
        if not claims:
            return []

        df = pd.DataFrame(claims)

        group_cols = ["provider_specialty", "region", "cpt_code"]
        df["group_key"] = df[group_cols].astype(str).agg("_".join, axis=1)

        results = []

        for group_key, group_df in df.groupby("group_key"):
            if len(group_df) < 2:
                for _, row in group_df.iterrows():
                    results.append(DetectionResult(
                        claim_id=row["id"],
                        method=self.method_name,
                        score=0.0,
                        is_flagged=False,
                        metadata=self._build_metadata(
                            group_key=group_key,
                            group_size=len(group_df),
                            billed_amount=float(row["billed_amount"]),
                            z_score=0.0,
                            insufficient_peers=True,
                        ),
                    ))
                continue

            amounts = group_df["billed_amount"].values
            peer_mean = float(amounts.mean())
            peer_std = float(amounts.std(ddof=1))
            z_scores = np.abs(stats.zscore(amounts, ddof=1))

            for idx, (_, row) in enumerate(group_df.iterrows()):
                z_score = float(z_scores[idx]) if not np.isnan(z_scores[idx]) else 0.0
                is_flagged = z_score > self.threshold

                results.append(DetectionResult(
                    claim_id=row["id"],
                    method=self.method_name,
                    score=z_score,
                    is_flagged=is_flagged,
                    metadata=self._build_metadata(
                        group_key=group_key,
                        group_size=len(group_df),
                        billed_amount=float(row["billed_amount"]),
                        z_score=z_score,
                        peer_mean=peer_mean,
                        peer_std=peer_std,
                    ),
                ))

        return results
