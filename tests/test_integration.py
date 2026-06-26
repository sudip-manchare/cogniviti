import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base
from app.database import init_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cogniviti.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


class TestIntegration:
    def test_full_pipeline(self):
        generate_resp = client.post("/claims/generate?batch_size=50&anomaly_rate=0.1&seed=42")
        assert generate_resp.status_code == 200
        batch_info = generate_resp.json()
        assert batch_info["claims_created"] == 50
        assert batch_info["anomalies_seeded"] == 5

        claims_resp = client.get("/claims/flagged")
        assert claims_resp.status_code == 200
        flagged_claims = claims_resp.json()
        flagged_count = len(flagged_claims)

        claims_resp_all = client.get("/claims")
        assert claims_resp_all.status_code == 200
        all_claims = claims_resp_all.json()
        assert len(all_claims) == 50

        if flagged_count > 0:
            first_flagged_id = flagged_claims[0]["id"]
            detail_resp = client.get(f"/claims/{first_flagged_id}")
            assert detail_resp.status_code == 200
            assert "anomaly_flags" in detail_resp.json()

        claims_without_explanation = [
            c for c in all_claims
            if any(
                f.get("is_flagged") and not f.get("explanation_text")
                for f in c.get("anomaly_flags", [])
            )
        ]

        if claims_without_explanation:
            claim_id = claims_without_explanation[0]["id"]
            explanation_resp = client.get(f"/claims/{claim_id}/explanation")
            assert explanation_resp.status_code == 200
            expl_data = explanation_resp.json()
            assert "explanation_text" in expl_data
            assert expl_data["explanation_text"] is not None

    def test_pipeline_reproducibility(self):
        r1 = client.post("/claims/generate?batch_size=100&anomaly_rate=0.1&seed=42").json()
        r2 = client.post("/claims/generate?batch_size=100&anomaly_rate=0.1&seed=42").json()

        assert r1["claims_created"] == r2["claims_created"]
        assert r1["anomalies_seeded"] == r2["anomalies_seeded"]

    def test_flagged_claims_have_correct_structure(self):
        client.post("/claims/generate?batch_size=100&anomaly_rate=0.1")

        flagged = client.get("/claims/flagged").json()
        for claim in flagged:
            assert "id" in claim
            assert "provider_specialty" in claim
            assert "billed_amount" in claim
            assert "anomaly_flags" in claim
            for flag in claim["anomaly_flags"]:
                assert "method" in flag
                assert "score" in flag
                assert flag["is_flagged"] is True

    def test_dashboard_loads_empty_state(self):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_dashboard_loads_with_data(self):
        client.post("/claims/generate?batch_size=20")
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]