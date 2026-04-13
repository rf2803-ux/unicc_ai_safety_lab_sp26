# UNICC AI Safety Lab

Courtroom-style AI safety assessment platform for structured review of AI systems, repositories, runtime endpoints, and generated system cases.

## Overview

UNICC AI Safety Lab is a multi-expert evaluation system designed to assess AI applications for safety, trustworthiness, and deployment readiness. Instead of relying on a single model to produce one opaque verdict, the platform runs a structured expert panel:

- `Judge 1` evaluates governance, privacy, auditability, and deployment-readiness concerns
- `Judge 2` evaluates exploitability, attack surface, misuse potential, and technical failure modes
- `Judge 3` evaluates user harm, fairness, transparency, trust, and stakeholder impact
- the `Ultimate Judge` arbitrates across those three outputs to produce a final panel decision

Each run generates structured JSON artifacts and a presentation-ready PDF report under `runs/<timestamp>/`.

## Why This Architecture

The system is designed around three core ideas:

- `Structured disagreement`: differences between expert reviewers are treated as meaningful safety signals, not noise
- `Traceable evidence`: every run preserves intake artifacts, reviewer outputs, arbitration results, and reporting artifacts
- `Framework alignment`: findings are surfaced through risk categories, control assessments, and governance mappings aligned to public frameworks

This makes the platform useful not only for producing a verdict, but for supporting review, remediation planning, and governance conversations.

## Core Workflow

Every input path is normalized into a shared internal `SystemCase`. That `SystemCase` is then passed through the same evaluation pipeline:

1. intake and evidence preparation
2. normalization into `SystemCase`
3. expert review by three judges
4. arbitration by the `Ultimate Judge`
5. report generation and artifact export

This common pipeline makes outputs comparable across different input types.

## Supported Input Modes

The app currently supports four intake paths:

- `Upload JSON`
  - evaluate a structured case file directly

- `GitHub URL`
  - ingest a public repository, inspect prioritized files, and derive a system case from evidence found in code and configuration

- `App / Endpoint URL`
  - probe a live target using safe, limited text-based runtime checks and convert observations into a system case

- `Internal Chat Generator`
  - generate a demo system case inside the application for scenario-based evaluation

## GitHub Repository Ingestion

When a public GitHub repository URL is provided, the system:

1. fetches the repository locally
2. inspects prioritized files such as `README.md`, `requirements.txt`, `.env.example`, entrypoints, and relevant application files
3. extracts structured evidence such as:
   - framework or application type
   - model/backend usage
   - upload or file-processing surfaces
   - authentication and security signals
   - dependency and setup signals
   - reporting or output behavior
4. converts those findings into a `SystemCase`
5. runs the same expert evaluation pipeline used for all other input types

This ingestion path is deterministic and evidence-driven. It does not depend on an LLM to decide which files to inspect.

## Runtime Endpoint Probing

The `App / Endpoint URL` mode supports limited behavioral evaluation of live targets.

Current runtime support is intentionally scoped to:

- `JSON API` endpoints
- `simple public HTML forms`

The runtime probe flow:

1. loads the target URL
2. detects or uses the selected runtime mode
3. submits a small set of safe, text-only probes
4. records request/response observations
5. converts those observations into a `SystemCase`
6. runs the standard expert evaluation pipeline

### Current Runtime Limitations

The current runtime mode does not attempt to support:

- authenticated flows
- JavaScript-heavy web applications
- browser automation
- file uploads
- multi-step workflows
- complex agent UIs such as ChatGPT-style hosted interfaces

For unsupported targets, repository-based or JSON-based evaluation is the recommended path.

## Risk Model And Framework Alignment

The platform uses a courtroom-style review workflow supported by a structured risk rubric. Findings are organized into safety and trustworthiness categories such as:

- privacy
- harmful content
- security
- bias / fairness
- deception
- prompt injection
- transparency
- auditability

These category-level findings feed into a lightweight control assessment layer that groups risks into operational controls such as:

- governance and accountability
- logging and traceability
- transparency and user disclosure
- human oversight
- privacy safeguards
- misuse resilience

The resulting outputs are aligned to selected themes from:

- `NIST AI RMF`
- `ISO/IEC 42001`
- `EU AI Act`

This should be understood as a framework-aligned assessment workflow, not as a certification or legal compliance determination.

See also:

- [`docs/framework_crosswalk.md`](docs/framework_crosswalk.md)
- [`docs/control_library.md`](docs/control_library.md)

## Outputs And Traceability

Each run creates a timestamped folder in `runs/` containing the full artifact trail for that evaluation.

Typical outputs include:

- `system_case.json`
- `judge1.json`
- `judge2.json`
- `judge3.json`
- `final_judge.json`
- `execution_trace.json`
- `run_summary.json`
- `report.pdf`

Depending on the input mode, the run may also include intake artifacts such as:

- `intake_summary.json`
- `intake_logs.json`
- `repo_extraction.json`
- `runtime_probe_config.json`
- `runtime_probe_result.json`

This gives each evaluation a practical audit trail from intake through final report generation.

## Verdict Mapping

The application uses courtroom-style internal verdict labels:

- `SAFE`
- `NEEDS_REVIEW`
- `UNSAFE`

These are functionally equivalent to:

- `APPROVE`
- `REVIEW`
- `REJECT`

The internal labels are preserved because they align with the project’s multi-reviewer decision model while remaining easy to interpret in reporting.

## Installation

### Recommended Install Order

Use the first option that works in your environment:

1. `uv sync --extra dev`
2. `pip install -r requirements.txt`
3. Docker

### Requirements

- Python `3.11+`
- `uv` recommended

Install `uv` if needed:

```bash
brew install uv
```

Preferred install path:

```bash
uv sync --extra dev
```

Compatibility fallback:

```bash
pip install -r requirements.txt
```

Optional Docker path:

```bash
docker build -t ai-safety-lab .
docker run --env-file .env -p 8501:8501 ai-safety-lab
```

## Configuration

Create a local environment file:

```bash
cp .env.example .env
```

Set the required API keys:

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Important notes:

- never commit `.env`
- never paste real keys into shared docs, screenshots, or slides
- each teammate should maintain their own local `.env`

## Run The App

With `uv`:

```bash
uv run streamlit run src/ui/app.py
```

With `pip`:

```bash
streamlit run src/ui/app.py
```

Then open the local Streamlit URL shown in the terminal.

## Testing

Run the full test suite with:

```bash
uv run pytest
```

Fallback:

```bash
pytest
```

## Project Structure

Key paths:

- Streamlit app: `src/ui/app.py`
- Core pipeline: `src/ai_safety_lab/pipeline.py`
- Compatibility wrapper: `src/pipeline.py`
- GitHub and runtime ingestion: `src/ai_safety_lab/ingestion/`
- Judges: `src/ai_safety_lab/judges/`
- Ultimate judge: `src/ai_safety_lab/final_judge/ultimate_judge.py`
- Reporting and PDF generation: `src/ai_safety_lab/reporting/`
- Schemas: `src/ai_safety_lab/schemas/`
- Example cases: `examples/cases/`

## Notes

- `config/config.example.yaml` defines the default provider/model configuration
- optional local overrides can be placed in `config/config.local.yaml`
- `.env.example` is committed; `.env` remains local
- `runs/` contains generated outputs and is mostly ignored by Git
- public GitHub repositories are supported in the current ingestion flow
- runtime evaluation is intentionally limited to JSON APIs and simple public HTML forms
