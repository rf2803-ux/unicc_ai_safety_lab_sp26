# Contributing

Thank you for your interest in contributing to UNICC AI Safety Lab. This project is an AI safety assessment workflow with four major layers:

- evidence intake
- normalization into `SystemCase`
- multi-reviewer evaluation
- final arbitration and reporting

Please keep that separation clear when proposing changes.

## Local Setup

Use Python `3.11+`.

Preferred setup:

```bash
uv sync --extra dev
cp .env.example .env
```

Add local provider keys to `.env` only when running live model calls:

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Never commit `.env`, real API keys, generated private runs, screenshots containing secrets, or local provider override files.

## Run The App

```bash
uv run streamlit run src/ui/app.py
```

## Run Tests

```bash
uv run pytest
```

If `uv` is unavailable:

```bash
pip install -r requirements.txt
pytest
```

## Development Guidelines

- Keep input collection separate from evaluation logic.
- Normalize new input modes into `SystemCase`.
- Preserve traceability by saving structured artifacts for new workflows.
- Avoid claiming legal certification or formal compliance.
- Prefer clear failure states over low-confidence or misleading outputs.
- Add tests for schema changes, ingestion behavior, and reporting helpers.

## Adding A New Input Mode

New input modes should follow this pattern:

1. collect evidence from the source
2. produce structured intake artifacts
3. map evidence into `SystemCase`
4. reuse the existing judge and final arbitration pipeline
5. update documentation and tests

## Adding A New Provider Or Judge

Provider changes should include:

- a client wrapper under `src/ai_safety_lab/clients/`
- clear error handling
- timeout and retry configuration
- schema validation tests or mocked client tests
- documentation updates in `README.md` or provider docs

## Pull Request Expectations

Before opening a pull request:

- run `uv run pytest`
- avoid committing generated `runs/` output
- document user-facing behavior changes
- include screenshots for UI/reporting changes when useful
- note any new dependencies and licensing implications

