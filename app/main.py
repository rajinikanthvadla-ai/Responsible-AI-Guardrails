"""Interactive Responsible AI guardrails lab app."""

from __future__ import annotations

import json

from app.guardrails import GuardrailEngine
from app.logger import SafetyLogger
from app.model import OpenSourceTextModel
from app.policies import default_policy_config


def run() -> None:
    print("=== Responsible AI Guardrails Lab ===")
    print("Type 'exit' to stop.\n")

    policy = default_policy_config()
    engine = GuardrailEngine(policy)
    logger = SafetyLogger()
    model = OpenSourceTextModel()

    while True:
        user_prompt = input("User> ").strip()
        if user_prompt.lower() in {"exit", "quit"}:
            print("Session ended.")
            break
        if not user_prompt:
            continue

        input_decision = engine.evaluate(user_prompt)
        if input_decision.status == "blocked":
            response = engine.safe_refusal()
            output_decision = input_decision
        else:
            raw_response = model.generate(input_decision.sanitized_text)
            output_decision = engine.evaluate(raw_response)
        final_decision = engine.combine_decisions(input_decision, output_decision)
        response = (
            engine.safe_refusal()
            if final_decision.status == "blocked"
            else output_decision.sanitized_text
        )

        logger.log_event(
            prompt=user_prompt,
            model_name=model.model_name,
            decision={
                "input": input_decision.to_dict(),
                "output": output_decision.to_dict(),
                "final": final_decision.to_dict(),
                "final_response": response,
            },
        )

        print("\nAssistant>", response)
        print("Input Decision>", json.dumps(input_decision.to_dict(), indent=2))
        print("Output Decision>", json.dumps(output_decision.to_dict(), indent=2))
        print("Final Decision>", json.dumps(final_decision.to_dict(), indent=2))
        print()


if __name__ == "__main__":
    run()
