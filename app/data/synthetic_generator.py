import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

SPECIALTIES = [
    "Cardiology", "Orthopedics", "Internal Medicine",
    "Radiology", "General Surgery", "Neurology",
    "Pediatrics", "Obstetrics", "Dermatology", "Oncology"
]

REGIONS = ["Northeast", "Southeast", "Midwest", "Southwest", "West"]

CPT_CODES = [
    "99213", "99214", "99215",
    "99232", "99233",
    "93000", "93005",
    "71045", "71046",
    "27130", "27447",
    "47562", "47563"
]

ICD10_CODES = [
    "I10", "E11.9", "I25.10",
    "M17.9", "M54.5", "J45.909",
    "N18.9", "E78.5", "G43.909"
]

PAYMENT_RANGES = {
    "99213": (75, 150),
    "99214": (110, 220),
    "99215": (150, 300),
    "99232": (80, 160),
    "99233": (120, 240),
    "93000": (50, 120),
    "93005": (30, 80),
    "71045": (40, 100),
    "71046": (50, 120),
    "27130": (1500, 3000),
    "27447": (1200, 2500),
    "47562": (800, 1800),
    "47563": (1000, 2200),
}


class SyntheticClaimsGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)

    def _normal_billed_amount(self, cpt_code: str) -> float:
        low, high = PAYMENT_RANGES.get(cpt_code, (100, 500))
        mu = (low + high) / 2
        sigma = (high - low) / 6
        amount = self.rng.gauss(mu, sigma)
        return round(max(low * 0.5, amount), 2)

    def _anomalous_billed_amount(self, cpt_code: str) -> float:
        low, high = PAYMENT_RANGES.get(cpt_code, (100, 500))
        multiplier = self.rng.uniform(3.0, 8.0)
        anomaly_amount = high * multiplier
        return round(anomaly_amount, 2)

    def _random_date(self) -> str:
        start = datetime(2024, 1, 1)
        end = datetime(2024, 12, 31)
        delta = end - start
        random_days = self.rng.randrange(delta.days)
        return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

    def generate_batch(
        self,
        batch_size: int = 100,
        anomaly_rate: float = 0.1
    ) -> List[Dict[str, Any]]:
        num_anomalies = max(1, int(batch_size * anomaly_rate))
        num_normal = batch_size - num_anomalies

        claims: List[Dict[str, Any]] = []
        claim_id_counter = 1

        for _ in range(num_normal):
            specialty = self.rng.choice(SPECIALTIES)
            region = self.rng.choice(REGIONS)
            cpt = self.rng.choice(CPT_CODES)
            claims.append({
                "id": claim_id_counter,
                "provider_id": f"PROV{self.rng.randint(1000, 9999)}",
                "provider_specialty": specialty,
                "region": region,
                "cpt_code": cpt,
                "icd10_code": self.rng.choice(ICD10_CODES),
                "billed_amount": self._normal_billed_amount(cpt),
                "units": self.rng.randint(1, 3),
                "date_of_service": self._random_date(),
                "patient_id": f"PAT{self.rng.randint(10000, 99999)}",
                "is_seeded_anomaly": False,
            })
            claim_id_counter += 1

        for _ in range(num_anomalies):
            specialty = self.rng.choice(SPECIALTIES)
            region = self.rng.choice(REGIONS)
            cpt = self.rng.choice(CPT_CODES)
            claims.append({
                "id": claim_id_counter,
                "provider_id": f"PROV{self.rng.randint(1000, 9999)}",
                "provider_specialty": specialty,
                "region": region,
                "cpt_code": cpt,
                "icd10_code": self.rng.choice(ICD10_CODES),
                "billed_amount": self._anomalous_billed_amount(cpt),
                "units": self.rng.randint(1, 5),
                "date_of_service": self._random_date(),
                "patient_id": f"PAT{self.rng.randint(10000, 99999)}",
                "is_seeded_anomaly": True,
            })
            claim_id_counter += 1

        self.rng.shuffle(claims)
        return claims