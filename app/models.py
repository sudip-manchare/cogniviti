from datetime import date
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Index, JSON
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(String(50), nullable=False, index=True)
    provider_specialty = Column(String(100), nullable=False, index=True)
    region = Column(String(50), nullable=False, index=True)
    cpt_code = Column(String(20), nullable=False, index=True)
    icd10_code = Column(String(20), nullable=False)
    billed_amount = Column(Float, nullable=False)
    units = Column(Integer, nullable=False, default=1)
    date_of_service = Column(Date, nullable=False, index=True)
    patient_id = Column(String(50), nullable=False, index=True)

    anomaly_flags = relationship("AnomalyFlag", back_populates="claim", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_claims_specialty_region_cpt", "provider_specialty", "region", "cpt_code"),
    )


class PolicyExcerpt(Base):
    __tablename__ = "policy_excerpts"

    id = Column(Integer, primary_key=True, index=True)
    source_citation = Column(String(200), nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True)

    anomaly_flags = relationship("AnomalyFlag", back_populates="cited_policy")


class AnomalyFlag(Base):
    __tablename__ = "anomaly_flags"

    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, index=True)
    method = Column(String(50), nullable=False)
    score = Column(Float, nullable=False)
    is_flagged = Column(Integer, nullable=False, default=0)
    detection_metadata = Column(JSON, nullable=True)
    explanation_text = Column(Text, nullable=True)
    cited_policy_id = Column(Integer, ForeignKey("policy_excerpts.id", ondelete="SET NULL"), nullable=True)

    claim = relationship("Claim", back_populates="anomaly_flags")
    cited_policy = relationship("PolicyExcerpt", back_populates="anomaly_flags")