import os
import json
import re
from typing import Dict, Any, List, Tuple
from google import genai

from app.data.policy_corpus import get_policy_excerpts


class ExplanationAgent:
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            api_key = os.environ.get("GEMINI_API_KEY", "")
            self._client = genai.Client(api_key=api_key) if api_key else genai.Client()
        return self._client

    def format_detection_context(self, flag_info: Dict[str, Any]) -> str:
        method = flag_info.get("method", "N/A")
        score = flag_info.get("score", 0)
        metadata = flag_info.get("metadata") or {}

        lines = [
            f"Detection method: {method}",
            f"Anomaly score: {score:.2f}",
        ]

        if method == "peer_zscore":
            lines.extend(self._format_peer_zscore_context(metadata))
        elif method == "isolation_forest":
            lines.extend(self._format_isolation_forest_context(metadata))
        elif metadata:
            for key, value in metadata.items():
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    def _format_peer_zscore_context(self, metadata: Dict[str, Any]) -> List[str]:
        lines = [
            f"Peer group: {metadata.get('peer_group', 'N/A')}",
            f"Peer group size: {metadata.get('group_size', 'N/A')} claims",
            f"This claim billed amount: ${metadata.get('claim_billed_amount', 0):.2f}",
            f"Z-score threshold: {metadata.get('z_score_threshold', 'N/A')}",
        ]

        if metadata.get("insufficient_peers"):
            lines.append("Note: insufficient peer claims in group for statistical comparison")
            return lines

        lines.extend([
            f"Peer mean billed amount: ${metadata.get('peer_mean_billed_amount', 0):.2f}",
            f"Peer standard deviation: ${metadata.get('peer_std_billed_amount', 0):.2f}",
            f"Deviation from peer mean: ${metadata.get('deviation_from_peer_mean', 0):.2f}",
            f"Computed z-score: {metadata.get('z_score', 0):.2f}",
        ])
        return lines

    def _format_isolation_forest_context(self, metadata: Dict[str, Any]) -> List[str]:
        if metadata.get("insufficient_batch_size"):
            return [
                f"Features available: {', '.join(metadata.get('features_used', []))}",
                f"Batch size: {metadata.get('actual_batch_size', 'N/A')} "
                f"(minimum required: {metadata.get('minimum_batch_size', 'N/A')})",
                "Note: batch too small for isolation forest analysis",
            ]

        feature_values = metadata.get("feature_values", {})
        feature_lines = [
            f"  {name}: {value:.2f}" if isinstance(value, float) else f"  {name}: {value}"
            for name, value in feature_values.items()
        ]

        return [
            f"Features analyzed: {', '.join(metadata.get('features_used', []))}",
            "Claim feature values:",
            *feature_lines,
            f"Batch size: {metadata.get('batch_size', 'N/A')} claims",
            f"Contamination rate: {metadata.get('contamination', 0):.2f}",
            f"Normalized anomaly score: {metadata.get('normalized_anomaly_score', 0):.2f} "
            "(higher = more anomalous)",
        ]

    def build_prompt(
        self,
        claim: Dict[str, Any],
        flag_info: Dict[str, Any],
        retrieved_policies: List[Tuple[Dict[str, str], float]],
    ) -> str:
        claim_summary = (
            f"Claim #{claim.get('id', 'N/A')}: Provider {claim.get('provider_id', 'N/A')} "
            f"({claim.get('provider_specialty', 'N/A')}), Region: {claim.get('region', 'N/A')}, "
            f"CPT: {claim.get('cpt_code', 'N/A')}, ICD-10: {claim.get('icd10_code', 'N/A')}, "
            f"Billed: ${claim.get('billed_amount', 0):.2f}, Units: {claim.get('units', 1)}"
        )

        detection_context = self.format_detection_context(flag_info)

        policies_text = ""
        for i, (policy, policy_score) in enumerate(retrieved_policies, 1):
            policies_text += (
                f"\n{i}. {policy['source_citation']}\n"
                f"   Relevance: {policy_score:.3f}\n"
                f"   Text: {policy['text']}\n"
            )

        return (
            "You are a healthcare claims review analyst. A claim has been flagged for "
            "potential fraud, waste, or abuse. Based on the claim details, detection "
            "statistics, and relevant policy excerpts below, provide:\n\n"
            "1. A plain-English rationale explaining why this claim is suspicious\n"
            "2. The specific policy citation(s) that support the concern\n"
            "3. A recommended action: one of 'Pend for Review', 'Deny Claim', or 'Auto-Pay'\n\n"
            f"CLAIM DETAILS:\n{claim_summary}\n\n"
            f"DETECTION CONTEXT:\n{detection_context}\n\n"
            f"RELEVANT POLICY EXCERPTS:\n{policies_text}\n\n"
            "Use the peer-group statistics or feature values above to quantify how far "
            "this claim deviates from expected norms in your rationale.\n\n"
            "Respond with a JSON object with exactly these keys:\n"
            "{\n"
            '  "rationale": "plain english explanation",\n'
            '  "cited_policy": "the specific citation(s) from above",\n'
            '  "recommended_action": "Pend for Review | Deny Claim | Auto-Pay"\n'
            "}\n"
            "Do not include any text outside the JSON object."
        )

    def generate_explanation(
        self,
        claim: Dict[str, Any],
        flag_info: Dict[str, Any],
        retrieved_policies: List[Tuple[Dict[str, str], float]],
    ) -> Dict[str, str]:
        client = self._get_client()
        prompt = self.build_prompt(claim, flag_info, retrieved_policies)

        try:
            response = client.models.generate_content(
                model="models/gemma-4-31b-it",
                contents=prompt,
            )
            result = self._parse_response(response.text)
        except Exception:
            result = self._fallback_explanation(claim, flag_info, retrieved_policies)

        return result

    def _fallback_explanation(
        self,
        claim: Dict[str, Any],
        flag_info: Dict[str, Any],
        retrieved_policies: List[Tuple[Dict[str, str], float]],
    ) -> Dict[str, str]:
        metadata = flag_info.get("metadata") or {}
        deviation_detail = ""

        if flag_info.get("method") == "peer_zscore" and metadata.get("peer_mean_billed_amount") is not None:
            deviation_detail = (
                f" The billed amount of ${claim.get('billed_amount', 0):.2f} is "
                f"${metadata.get('deviation_from_peer_mean', 0):.2f} above the peer-group "
                f"mean of ${metadata.get('peer_mean_billed_amount', 0):.2f} "
                f"(z-score: {flag_info.get('score', 0):.2f}, threshold: "
                f"{metadata.get('z_score_threshold', 'N/A')})."
            )
        elif flag_info.get("method") == "isolation_forest":
            feature_values = metadata.get("feature_values", {})
            feature_summary = ", ".join(
                f"{name}={value:.2f}" if isinstance(value, float) else f"{name}={value}"
                for name, value in feature_values.items()
            )
            deviation_detail = (
                f" Feature values ({feature_summary}) scored "
                f"{flag_info.get('score', 0):.2f} on the normalized anomaly scale."
            )

        return {
            "rationale": (
                f"Claim #{claim.get('id', 'N/A')} was flagged by "
                f"{flag_info.get('method', 'anomaly detection')} with a score of "
                f"{flag_info.get('score', 0):.2f}.{deviation_detail}"
            ),
            "cited_policy": (
                retrieved_policies[0][0]["source_citation"]
                if retrieved_policies else "CMS NCD 100-2, Chapter 15 – Reasonable and Necessary"
            ),
            "recommended_action": "Pend for Review",
        }

    def _parse_response(self, text: str) -> Dict[str, str]:
        json_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
        return {
            "rationale": text.strip(),
            "cited_policy": "",
            "recommended_action": "Pend for Review",
        }
