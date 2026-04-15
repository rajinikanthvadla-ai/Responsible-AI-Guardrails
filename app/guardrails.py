"""Guardrail engine: content filtering, PII masking, bias alerts, and explainability."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

from app.policies import PolicyConfig


@dataclass
class GuardrailDecision:
    status: str
    action: str
    risk_score: int
    reasons: List[str]
    bias_alert: bool
    sanitized_text: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "status": self.status,
            "action": self.action,
            "risk_score": self.risk_score,
            "reasons": self.reasons,
            "bias_alert": self.bias_alert,
            "sanitized_text": self.sanitized_text,
        }


class GuardrailEngine:
    """Apply simple policy checks before and after model generation."""

    def __init__(self, policy: PolicyConfig) -> None:
        self.policy = policy

    def _detect_blocked_content(self, text: str) -> List[str]:
        text_low = text.lower()
        reasons: List[str] = []
        for category, terms in self.policy.blocked_keywords.items():
            if any(term in text_low for term in terms):
                reasons.append(f"blocked_{category}")
        return reasons

    def _detect_bias_alert(self, text: str) -> bool:
        text_low = text.lower()
        return any(term in text_low for term in self.policy.bias_terms)

    def _mask_pii(self, text: str) -> Tuple[str, List[str]]:
        findings: List[str] = []
        sanitized = text
        for pii_type, pattern in self.policy.pii_patterns.items():
            updated = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", sanitized)
            if updated != sanitized:
                findings.append(f"pii_{pii_type}")
            sanitized = updated
        return sanitized, findings

    def _is_sensitive_storage_request(self, text: str) -> bool:
        text_low = text.lower()
        return any(
            term in text_low for term in self.policy.sensitive_storage_intent_terms
        )

    def evaluate(self, text: str) -> GuardrailDecision:
        reasons = self._detect_blocked_content(text)
        bias_alert = self._detect_bias_alert(text)
        sanitized, pii_findings = self._mask_pii(text)
        reasons.extend(pii_findings)
        if pii_findings and self._is_sensitive_storage_request(text):
            reasons.append("blocked_sensitive_storage_request")

        risk_score = 0
        risk_score += 40 * len([r for r in reasons if r.startswith("blocked_")])
        risk_score += 15 * len([r for r in reasons if r.startswith("pii_")])
        if bias_alert:
            risk_score += 20
            reasons.append("bias_alert")
        risk_score = min(risk_score, 100)

        is_blocked = any(r.startswith("blocked_") for r in reasons)
        if is_blocked or risk_score > self.policy.max_risk_score:
            status = "blocked"
            action = "block"
        elif pii_findings:
            status = "allowed"
            action = "allow_with_masking"
        else:
            status = "allowed"
            action = "allow"

        return GuardrailDecision(
            status=status,
            action=action,
            risk_score=risk_score,
            reasons=reasons or ["no_policy_trigger"],
            bias_alert=bias_alert,
            sanitized_text=sanitized,
        )

    def combine_decisions(
        self, input_decision: GuardrailDecision, output_decision: GuardrailDecision
    ) -> GuardrailDecision:
        """Combine input/output decisions for a single final enforcement decision."""
        combined_reasons = list(
            dict.fromkeys(input_decision.reasons + output_decision.reasons)
        )
        combined_risk = max(input_decision.risk_score, output_decision.risk_score)
        combined_bias_alert = input_decision.bias_alert or output_decision.bias_alert
        is_blocked = (
            input_decision.status == "blocked"
            or output_decision.status == "blocked"
            or combined_risk > self.policy.max_risk_score
        )

        if is_blocked:
            status = "blocked"
            action = "block"
        elif (
            input_decision.action == "allow_with_masking"
            or output_decision.action == "allow_with_masking"
        ):
            status = "allowed"
            action = "allow_with_masking"
        else:
            status = "allowed"
            action = "allow"

        return GuardrailDecision(
            status=status,
            action=action,
            risk_score=combined_risk,
            reasons=combined_reasons or ["no_policy_trigger"],
            bias_alert=combined_bias_alert,
            sanitized_text=output_decision.sanitized_text,
        )

    @staticmethod
    def safe_refusal() -> str:
        return (
            "I cannot help with that request. "
            "Please ask a safe, legal, and respectful question."
        )
