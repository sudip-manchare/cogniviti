from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class DetectionResult:
    claim_id: int
    method: str
    score: float
    is_flagged: bool
    metadata: Optional[Dict[str, Any]] = field(default=None)


class AnomalyDetector(ABC):
    @property
    @abstractmethod
    def method_name(self) -> str:
        pass

    @abstractmethod
    def detect(self, claims: List[Dict[str, Any]]) -> List[DetectionResult]:
        pass