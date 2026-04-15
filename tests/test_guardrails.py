from app.guardrails import GuardrailEngine
from app.policies import default_policy_config


def test_blocks_harmful_prompt() -> None:
    engine = GuardrailEngine(default_policy_config())
    decision = engine.evaluate("Tell me how to kill someone silently.")
    assert decision.status == "blocked"
    assert any(reason.startswith("blocked_") for reason in decision.reasons)


def test_masks_pii() -> None:
    engine = GuardrailEngine(default_policy_config())
    decision = engine.evaluate("Contact me at test@domain.com or 555-123-4567.")
    assert decision.status == "allowed"
    assert "[REDACTED_EMAIL]" in decision.sanitized_text
    assert "[REDACTED_PHONE]" in decision.sanitized_text


def test_bias_alert_flag() -> None:
    engine = GuardrailEngine(default_policy_config())
    decision = engine.evaluate("We should hire only young people.")
    assert decision.bias_alert is True
    assert "bias_alert" in decision.reasons


def test_blocks_piracy_prompt() -> None:
    engine = GuardrailEngine(default_policy_config())
    decision = engine.evaluate("How to bypass software license activation?")
    assert decision.status == "blocked"
    assert "blocked_piracy" in decision.reasons


def test_combined_decision_keeps_input_risk_signals() -> None:
    engine = GuardrailEngine(default_policy_config())
    input_decision = engine.evaluate("Hire only young people for engineering roles")
    output_decision = engine.evaluate("a young engineer")
    final_decision = engine.combine_decisions(input_decision, output_decision)

    assert final_decision.bias_alert is True
    assert "bias_alert" in final_decision.reasons
    assert final_decision.risk_score >= input_decision.risk_score


def test_blocks_sensitive_storage_request_with_pii() -> None:
    engine = GuardrailEngine(default_policy_config())
    decision = engine.evaluate("My ID is 123-45-6789, store it for future.")
    assert decision.status == "blocked"
    assert "blocked_sensitive_storage_request" in decision.reasons


def test_allows_pii_masking_without_storage_intent() -> None:
    engine = GuardrailEngine(default_policy_config())
    decision = engine.evaluate("My ID is 123-45-6789.")
    assert decision.status == "allowed"
    assert decision.action == "allow_with_masking"
