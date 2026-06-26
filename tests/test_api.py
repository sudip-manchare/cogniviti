import pytest
import os
import tempfile
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


class TestAPI:
    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_generate_batch_default(self):
        response = client.post("/claims/generate")
        assert response.status_code == 200
        data = response.json()
        assert data["claims_created"] == 100
        assert data["anomalies_seeded"] == 10

    def test_generate_batch_custom(self):
        response = client.post("/claims/generate?batch_size=50&anomaly_rate=0.2&seed=99")
        assert response.status_code == 200
        data = response.json()
        assert data["claims_created"] == 50
        assert data["anomalies_seeded"] == 10

    def test_list_claims_empty(self):
        response = client.get("/claims")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_claims_after_generate(self):
        client.post("/claims/generate?batch_size=20")
        response = client.get("/claims")
        assert response.status_code == 200
        claims = response.json()
        assert len(claims) == 20
        for c in claims:
            assert "id" in c
            assert "anomaly_flags" in c
            assert "billed_amount" in c

    def test_get_claim_by_id(self):
        client.post("/claims/generate?batch_size=20")
        claims = client.get("/claims").json()
        claim_id = claims[0]["id"]
        response = client.get(f"/claims/{claim_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == claim_id
        assert "anomaly_flags" in data

    def test_get_claim_not_found(self):
        response = client.get("/claims/99999")
        assert response.status_code == 404

    def test_get_explanation_unflagged(self):
        client.post("/claims/generate?batch_size=20")
        claims = client.get("/claims").json()
        clean_claims = [
            c for c in claims
            if not any(f.get("is_flagged") for f in c.get("anomaly_flags", []))
        ]
        if clean_claims:
            claim_id = clean_claims[0]["id"]
            response = client.get(f"/claims/{claim_id}/explanation")
            assert response.status_code == 200
            data = response.json()
            assert data["recommended_action"] == "Auto-Pay"

    def test_flagged_claims_endpoint(self):
        client.post("/claims/generate?batch_size=50")
        response = client.get("/claims/flagged")
        assert response.status_code == 200
        flagged = response.json()

        for c in flagged:
            assert any(f.get("is_flagged") for f in c.get("anomaly_flags", []))

    def test_generate_twice(self):
        r1 = client.post("/claims/generate?batch_size=30").json()
        r2 = client.post("/claims/generate?batch_size=30").json()
        assert r1["claims_created"] == 30
        assert r2["claims_created"] == 30

        claims = client.get("/claims").json()
        assert len(claims) == 60

    def test_dashboard_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_flagged_claims_store_detection_metadata(self):
        client.post("/claims/generate?batch_size=50&seed=42")
        flagged = client.get("/claims/flagged").json()

        assert len(flagged) > 0
        for claim in flagged:
            for flag in claim["anomaly_flags"]:
                assert flag.get("detection_metadata") is not None
                metadata = flag["detection_metadata"]
                if flag["method"] == "peer_zscore":
                    assert "peer_group" in metadata
                    assert "z_score_threshold" in metadata
                elif flag["method"] == "isolation_forest":
                    assert "features_used" in metadata
                    assert "batch_size" in metadata