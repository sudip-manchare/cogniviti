import pytest
from app.data.synthetic_generator import SyntheticClaimsGenerator, SPECIALTIES, REGIONS, CPT_CODES


class TestSyntheticClaimsGenerator:
    def test_generate_batch_defaults(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=100, anomaly_rate=0.1)

        assert len(claims) == 100

    def test_generate_batch_size(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=200, anomaly_rate=0.1)
        assert len(claims) == 200

    def test_seeded_anomaly_count(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=100, anomaly_rate=0.1)
        seeded = [c for c in claims if c.get("is_seeded_anomaly")]
        assert len(seeded) == 10

    def test_anomalous_amounts_are_higher(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=100, anomaly_rate=0.1)
        for c in claims:
            if c.get("is_seeded_anomaly"):
                assert c["billed_amount"] > 200

    def test_reproducibility_same_seed(self):
        gen1 = SyntheticClaimsGenerator(seed=42)
        gen2 = SyntheticClaimsGenerator(seed=42)
        claims1 = gen1.generate_batch(batch_size=50, anomaly_rate=0.1)
        claims2 = gen2.generate_batch(batch_size=50, anomaly_rate=0.1)

        for c1, c2 in zip(claims1, claims2):
            assert c1["billed_amount"] == c2["billed_amount"]
            assert c1["provider_specialty"] == c2["provider_specialty"]
            assert c1["region"] == c2["region"]
            assert c1["is_seeded_anomaly"] == c2["is_seeded_anomaly"]

    def test_different_seed_different_output(self):
        gen1 = SyntheticClaimsGenerator(seed=42)
        gen2 = SyntheticClaimsGenerator(seed=99)
        claims1 = gen1.generate_batch(batch_size=50, anomaly_rate=0.1)
        claims2 = gen2.generate_batch(batch_size=50, anomaly_rate=0.1)

        differences = sum(
            1 for c1, c2 in zip(claims1, claims2)
            if c1["billed_amount"] != c2["billed_amount"]
        )
        assert differences > 0

    def test_claim_structure(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=10, anomaly_rate=0.1)
        for c in claims:
            assert "id" in c
            assert "provider_id" in c
            assert "provider_specialty" in c
            assert "region" in c
            assert "cpt_code" in c
            assert "icd10_code" in c
            assert "billed_amount" in c
            assert "units" in c
            assert "date_of_service" in c
            assert "patient_id" in c
            assert "is_seeded_anomaly" in c
            assert isinstance(c["billed_amount"], float)
            assert isinstance(c["units"], int)
            assert c["billed_amount"] > 0

    def test_valid_specialty_region_cpt(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=50, anomaly_rate=0.1)
        for c in claims:
            assert c["provider_specialty"] in SPECIALTIES
            assert c["region"] in REGIONS
            assert c["cpt_code"] in CPT_CODES

    def test_min_anomaly_rate(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=5, anomaly_rate=0.01)
        seeded = [c for c in claims if c.get("is_seeded_anomaly")]
        assert len(seeded) >= 1

    def test_generated_ids_are_unique(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=100, anomaly_rate=0.1)
        ids = [c["id"] for c in claims]
        assert len(ids) == len(set(ids))

    def test_lower_anomaly_rate(self):
        generator = SyntheticClaimsGenerator(seed=42)
        claims = generator.generate_batch(batch_size=100, anomaly_rate=0.05)
        seeded = [c for c in claims if c.get("is_seeded_anomaly")]
        assert len(seeded) == 5