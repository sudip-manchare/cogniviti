import pytest
from unittest.mock import MagicMock, patch

from app.genai.explanation_agent import ExplanationAgent


class TestFormatDetectionContext:
    def test_peer_zscore_metadata_includes_peer_statistics(self):
        agent = ExplanationAgent()
        flag_info = {
            "method": "peer_zscore",
            "score": 3.21,
            "metadata": {
                "peer_group": "Cardiology_Northeast_99213",
                "group_size": 20,
                "peer_mean_billed_amount": 100.0,
                "peer_std_billed_amount": 2.5,
                "claim_billed_amount": 5000.0,
                "deviation_from_peer_mean": 4900.0,
                "z_score_threshold": 2.5,
            },
        }

        text = agent.format_detection_context(flag_info)

        assert "peer_zscore" in text
        assert "Cardiology_Northeast_99213" in text
        assert "20" in text
        assert "100.00" in text
        assert "2.50" in text
        assert "5000.00" in text
        assert "4900.00" in text
        assert "3.21" in text
        assert "2.50" in text

    def test_isolation_forest_metadata_includes_features(self):
        agent = ExplanationAgent()
        flag_info = {
            "method": "isolation_forest",
            "score": 0.92,
            "metadata": {
                "features_used": ["billed_amount", "units"],
                "feature_values": {"billed_amount": 5000.0, "units": 10},
                "batch_size": 20,
                "contamination": 0.2,
            },
        }

        text = agent.format_detection_context(flag_info)

        assert "isolation_forest" in text
        assert "billed_amount" in text
        assert "units" in text
        assert "5000.00" in text
        assert "10" in text
        assert "20" in text
        assert "0.92" in text

    def test_missing_metadata_falls_back_to_method_and_score(self):
        agent = ExplanationAgent()
        flag_info = {"method": "peer_zscore", "score": 2.8}

        text = agent.format_detection_context(flag_info)

        assert "peer_zscore" in text
        assert "2.80" in text

    def test_build_prompt_includes_detection_context(self):
        agent = ExplanationAgent()
        claim = {
            "id": 1,
            "provider_id": "P001",
            "provider_specialty": "Cardiology",
            "region": "Northeast",
            "cpt_code": "99213",
            "icd10_code": "I10",
            "billed_amount": 5000.0,
            "units": 1,
        }
        flag_info = {
            "method": "peer_zscore",
            "score": 3.21,
            "metadata": {
                "peer_group": "Cardiology_Northeast_99213",
                "group_size": 20,
                "peer_mean_billed_amount": 100.0,
                "peer_std_billed_amount": 2.5,
                "claim_billed_amount": 5000.0,
                "deviation_from_peer_mean": 4900.0,
                "z_score_threshold": 2.5,
            },
        }
        policies = [
            (
                {
                    "source_citation": "CMS NCD 100-2",
                    "text": "Services must be reasonable and necessary.",
                },
                0.85,
            )
        ]

        prompt = agent.build_prompt(claim, flag_info, policies)

        assert "DETECTION CONTEXT:" in prompt
        assert "peer_mean_billed_amount" not in prompt
        assert "100.00" in prompt
        assert "CMS NCD 100-2" in prompt

    @patch.object(ExplanationAgent, "_get_client")
    def test_generate_explanation_passes_enriched_context_to_model(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.models.generate_content.return_value = MagicMock(
            text='{"rationale": "test", "cited_policy": "CMS", "recommended_action": "Pend for Review"}'
        )

        agent = ExplanationAgent()
        flag_info = {
            "method": "peer_zscore",
            "score": 3.21,
            "metadata": {
                "peer_group": "Cardiology_Northeast_99213",
                "group_size": 20,
                "peer_mean_billed_amount": 100.0,
                "peer_std_billed_amount": 2.5,
                "claim_billed_amount": 5000.0,
                "deviation_from_peer_mean": 4900.0,
                "z_score_threshold": 2.5,
            },
        }

        agent.generate_explanation(
            claim={"id": 1, "provider_id": "P1", "provider_specialty": "Cardiology",
                   "region": "Northeast", "cpt_code": "99213", "icd10_code": "I10",
                   "billed_amount": 5000.0, "units": 1},
            flag_info=flag_info,
            retrieved_policies=[],
        )

        prompt = mock_client.models.generate_content.call_args.kwargs["contents"]
        assert "DETECTION CONTEXT:" in prompt
        assert "100.00" in prompt
