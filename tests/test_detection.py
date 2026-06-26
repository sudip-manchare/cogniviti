import pytest
from app.detection.zscore_detector import PeerZScoreDetector
from app.detection.isolation_forest_detector import IsolationForestDetector


class TestPeerZScoreDetector:
    def test_empty_claims(self):
        detector = PeerZScoreDetector(threshold=2.5)
        results = detector.detect([])
        assert results == []

    def test_single_claim_no_flag(self):
        detector = PeerZScoreDetector(threshold=2.5)
        claims = [{
            "id": 1, "provider_specialty": "Cardiology",
            "region": "Northeast", "cpt_code": "99213",
            "billed_amount": 100.0, "units": 1,
        }]
        results = detector.detect(claims)
        assert len(results) == 1
        assert not results[0].is_flagged
        assert results[0].score == 0.0

    def test_detects_anomaly(self):
        detector = PeerZScoreDetector(threshold=2.5)
        claims = [
            {"id": i, "provider_specialty": "Cardiology", "region": "Northeast", "cpt_code": "99213", "billed_amount": 100.0, "units": 1}
            for i in range(1, 20)
        ]
        claims.append({"id": 20, "provider_specialty": "Cardiology", "region": "Northeast", "cpt_code": "99213", "billed_amount": 5000.0, "units": 1})
        claims.append({"id": 21, "provider_specialty": "Cardiology", "region": "Northeast", "cpt_code": "99213", "billed_amount": 102.0, "units": 1})
        results = detector.detect(claims)
        results_by_id = {r.claim_id: r for r in results}
        assert results_by_id[20].is_flagged
        assert results_by_id[20].score > 2.5

    def test_different_groups_independent(self):
        detector = PeerZScoreDetector(threshold=2.0)
        claims = [
            {"id": 1, "provider_specialty": "Cardiology", "region": "Northeast", "cpt_code": "99213", "billed_amount": 100.0, "units": 1},
            {"id": 2, "provider_specialty": "Cardiology", "region": "Northeast", "cpt_code": "99213", "billed_amount": 110.0, "units": 1},
            {"id": 3, "provider_specialty": "Orthopedics", "region": "West", "cpt_code": "27130", "billed_amount": 2000.0, "units": 1},
            {"id": 4, "provider_specialty": "Orthopedics", "region": "West", "cpt_code": "27130", "billed_amount": 2100.0, "units": 1},
        ]
        results = detector.detect(claims)
        assert len(results) == 4

    def test_low_threshold_no_flags(self):
        detector = PeerZScoreDetector(threshold=10.0)
        claims = [
            {"id": 1, "provider_specialty": "Radiology", "region": "South", "cpt_code": "71045", "billed_amount": 50.0, "units": 1},
            {"id": 2, "provider_specialty": "Radiology", "region": "South", "cpt_code": "71045", "billed_amount": 55.0, "units": 1},
        ]
        results = detector.detect(claims)
        for r in results:
            assert not r.is_flagged

    def test_all_identical_amounts(self):
        detector = PeerZScoreDetector(threshold=2.5)
        claims = [
            {"id": i, "provider_specialty": "Cardiology", "region": "Northeast", "cpt_code": "99213", "billed_amount": 100.0, "units": 1}
            for i in range(1, 6)
        ]
        results = detector.detect(claims)
        for r in results:
            assert not r.is_flagged
            assert r.score == 0.0

    def test_method_name(self):
        detector = PeerZScoreDetector()
        assert detector.method_name == "peer_zscore"

    def test_metadata_includes_peer_group_statistics(self):
        detector = PeerZScoreDetector(threshold=2.5)
        claims = [
            {"id": i, "provider_specialty": "Cardiology", "region": "Northeast", "cpt_code": "99213", "billed_amount": 100.0, "units": 1}
            for i in range(1, 20)
        ]
        claims.append({"id": 20, "provider_specialty": "Cardiology", "region": "Northeast", "cpt_code": "99213", "billed_amount": 5000.0, "units": 1})

        results = detector.detect(claims)
        flagged = next(r for r in results if r.claim_id == 20)

        assert flagged.metadata is not None
        assert flagged.metadata["peer_group"] == "Cardiology_Northeast_99213"
        assert flagged.metadata["group_size"] == 20
        assert flagged.metadata["peer_mean_billed_amount"] == pytest.approx(345.0, rel=0.01)
        assert flagged.metadata["peer_std_billed_amount"] > 0
        assert flagged.metadata["claim_billed_amount"] == 5000.0
        assert flagged.metadata["deviation_from_peer_mean"] == pytest.approx(4655.0, rel=0.01)
        assert flagged.metadata["z_score_threshold"] == 2.5

    def test_metadata_for_insufficient_peers(self):
        detector = PeerZScoreDetector(threshold=2.5)
        claims = [{
            "id": 1, "provider_specialty": "Cardiology",
            "region": "Northeast", "cpt_code": "99213",
            "billed_amount": 100.0, "units": 1,
        }]

        results = detector.detect(claims)

        assert results[0].metadata is not None
        assert results[0].metadata["insufficient_peers"] is True
        assert results[0].metadata["group_size"] == 1
        assert results[0].metadata["z_score_threshold"] == 2.5


class TestIsolationForestDetector:
    def test_empty_claims(self):
        detector = IsolationForestDetector()
        results = detector.detect([])
        assert results == []

    def test_fewer_than_10_claims(self):
        detector = IsolationForestDetector()
        claims = [
            {"id": i, "billed_amount": 100.0, "units": 1}
            for i in range(1, 5)
        ]
        results = detector.detect(claims)
        for r in results:
            assert not r.is_flagged
            assert r.score == 0.0

    def test_detects_obvious_anomaly(self):
        detector = IsolationForestDetector(contamination=0.2)
        claims = [
            {"id": i, "billed_amount": 100.0, "units": 1}
            for i in range(1, 20)
        ]
        claims.append({"id": 20, "billed_amount": 5000.0, "units": 10})
        results = detector.detect(claims)
        flagged = [r for r in results if r.is_flagged]
        assert len(flagged) > 0

    def test_method_name(self):
        detector = IsolationForestDetector()
        assert detector.method_name == "isolation_forest"

    def test_metadata_includes_feature_values(self):
        detector = IsolationForestDetector(contamination=0.2)
        claims = [
            {"id": i, "billed_amount": 100.0, "units": 1}
            for i in range(1, 20)
        ]
        claims.append({"id": 20, "billed_amount": 5000.0, "units": 10})

        results = detector.detect(claims)
        anomalous = next(r for r in results if r.claim_id == 20)

        assert anomalous.metadata is not None
        assert anomalous.metadata["features_used"] == ["billed_amount", "units"]
        assert anomalous.metadata["feature_values"]["billed_amount"] == 5000.0
        assert anomalous.metadata["feature_values"]["units"] == 10
        assert anomalous.metadata["batch_size"] == 20
        assert anomalous.metadata["contamination"] == 0.2

    def test_metadata_for_insufficient_batch(self):
        detector = IsolationForestDetector()
        claims = [
            {"id": i, "billed_amount": 100.0, "units": 1}
            for i in range(1, 5)
        ]

        results = detector.detect(claims)

        assert results[0].metadata is not None
        assert results[0].metadata["insufficient_batch_size"] is True
        assert results[0].metadata["minimum_batch_size"] == 10
        assert results[0].metadata["actual_batch_size"] == 4