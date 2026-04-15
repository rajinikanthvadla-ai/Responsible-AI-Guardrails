"""Central policy definitions for the guardrails lab."""

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class PolicyConfig:
    blocked_keywords: Dict[str, List[str]]
    pii_patterns: Dict[str, str]
    bias_terms: List[str]
    sensitive_storage_intent_terms: List[str]
    max_risk_score: int


def default_policy_config() -> PolicyConfig:
    """Return simple, classroom-friendly default policy settings."""
    return PolicyConfig(
        blocked_keywords={
            "violence": ["kill", "hurt someone", "bomb", "attack plan"],
            "self_harm": ["self harm", "suicide method", "end my life"],
            "hate": ["hate speech", "racial slur", "inferior race"],
            "illegal": ["hack bank", "fake passport", "evade police"],
            "piracy": [
                "windows crack keys",
                "crack key",
                "license bypass",
                "bypass software license activation",
                "pirated software",
                "activation bypass",
            ],
        },
        pii_patterns={
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            "phone": r"\b(?:\+?\d{1,3})?[-.\s]?(?:\d{3})[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "national_id_like": r"\b\d{3}[- ]?\d{2}[- ]?\d{4}\b",
        },
        bias_terms=[
            "only young people",
            "only men",
            "only women",
            "specific race only",
            "reject older candidates",
        ],
        sensitive_storage_intent_terms=[
            "store it",
            "store this",
            "save it",
            "save this",
            "keep it for future",
            "remember this",
            "add to records",
            "persist this",
        ],
        max_risk_score=49,
    )
