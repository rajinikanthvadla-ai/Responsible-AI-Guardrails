# Responsible AI Guardrails Lab

Minimal Python lab for running an open-source LLM with safety guardrails.

## What this lab does

- Applies input and output safety checks
- Masks personal data (PII)
- Detects risky/bias-sensitive prompts
- Blocks unsafe requests
- Writes structured safety logs

Model used: `google/flan-t5-small`

## Project structure

```text
app/
  main.py
  model.py
  guardrails.py
  policies.py
  logger.py
data/
  demo_prompts.json
tests/
  test_guardrails.py
requirements.txt
README.md
```

## Run steps (Windows PowerShell)

1. Create virtual environment

```powershell
python -m venv .venv
```

2. Activate virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

3. Install dependencies

```powershell
pip install -r requirements.txt
```

4. Run tests

```powershell
pytest -q
```

5. Start app

```powershell
python -m app.main
```

6. Exit app

Type `exit` or `quit`.

## Output format

For each prompt, the app prints:

- `Input Decision`
- `Output Decision`
- `Final Decision`

Each decision includes:

- `status`
- `action`
- `risk_score`
- `reasons`
- `bias_alert`
- `sanitized_text`

## Logs

Safety events are saved to:

`logs/safety_events.jsonl`
