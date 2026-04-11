# unicc_ai_safety_lab_sp26

Courtroom-style AI Safety Lab for the UNICC Spring 2026 capstone.

## Overview

This project evaluates AI systems for safety, risk, and trustworthiness using a multi-expert review workflow:

- Judge 1, Judge 2, and Judge 3 assess the same target from different expert lenses
- The Ultimate Judge arbitrates across those three outputs and produces the final decision
- Each run saves structured JSON artifacts and a PDF report under `runs/<timestamp>/`

The app currently supports three input paths:

- JSON case file upload
- Public GitHub repository URL ingestion
- App / endpoint runtime probing
- Internal chat-based case generation

## What The Evaluator Can Do

From the Streamlit app, a first-time user can:

1. Open the `Instructions` tab for onboarding
2. Evaluate a JSON case file
3. Evaluate a public GitHub repository by pasting its URL
4. Evaluate a live app or endpoint URL with safe runtime probes
5. Generate a demo case inside the app
6. Run the expert panel and download a PDF report

## Setup

### Requirements

- Python `3.11+`
- `uv`

Install `uv` if needed:

```bash
brew install uv
```

Preferred install path:

```bash
uv sync --extra dev
```

Compatibility fallback for tools that expect `requirements.txt`:

```bash
pip install -r requirements.txt
```

Create a local `.env` file or export the variables directly in your shell:

```bash
cp .env.example .env
```

Set these required API keys:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

You can set them in `.env`:

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Or export them in the shell before you run the app:

```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
export GEMINI_API_KEY=your_key_here
```

Important:

- Never commit `.env`
- Never paste real keys into GitHub, screenshots, slides, or shared docs
- Each teammate should create their own local `.env`
- The evaluator may supply their own keys through environment variables instead of a local `.env` file

Recommended quick start on a clean machine:

```bash
uv sync --extra dev
cp .env.example .env
# add OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY
uv run streamlit run src/ui/app.py
```

## Run The App

```bash
uv run streamlit run src/ui/app.py
```

Then open the local Streamlit URL shown in the terminal.

## Recommended Evaluator Flow

The app opens with four tabs:

1. `Instructions`
2. `Upload JSON`
3. `GitHub URL`
4. `App / Endpoint URL`
5. `Internal Chat Generator`

For repository-based evaluation, the simplest path is:

1. Open `GitHub URL`
2. Paste a public GitHub repository URL
3. Click `Load Repository Preview`
4. Review the intake summary and evidence preview
5. Click `Run Safety Evaluation`

For JSON-based evaluation:

1. Open `Upload JSON`
2. Upload a `case_file.json`
3. Click `Run Safety Evaluation`

For generated demo evaluation:

1. Open `Internal Chat Generator`
2. Select a scenario
3. Click `Run Safety Evaluation`

For runtime app or endpoint evaluation:

1. Open `App / Endpoint URL`
2. Enter a runtime URL
3. Select `Auto-detect`, `JSON API`, or `Simple Web App`
4. Provide the prompt field name if you are probing a JSON API
5. Click `Load Runtime Preview`
6. Review the intake summary and runtime logs
7. Click `Run Safety Evaluation`

## GitHub Repository Ingestion

When a public GitHub repository URL is provided, the app:

1. fetches the repository locally
2. inspects prioritized files such as `README.md`, `requirements.txt`, `.env.example`, and app entrypoints
3. extracts structured evidence such as:
   - framework/app type
   - model/backend usage
   - upload or file-processing surfaces
   - auth/security signals
   - dependency/setup signals
   - reporting/output behavior
4. converts those findings into a `SystemCase`
5. sends that `SystemCase` through the same expert evaluation pipeline

This repository ingestion is deterministic and evidence-driven. It does not depend on an LLM to decide which files to inspect.

## App / Endpoint Runtime Probing

The app also supports runtime evaluation of live targets through the `App / Endpoint URL` tab.

Current runtime support is intentionally scoped to:

- JSON API endpoints
- simple public HTML forms

The runtime probe flow:

1. loads the target URL
2. auto-detects or uses the selected runtime mode
3. sends a small set of safe, text-only probes
4. captures request/response observations
5. converts those observations into a `SystemCase`
6. sends that case through the same expert evaluation pipeline

### Current runtime limitations

The current runtime mode does **not** attempt to support:

- login or authenticated flows
- JavaScript-heavy apps
- browser automation
- file uploads
- multi-step workflows

If a runtime target falls outside those constraints, the app should surface that limitation in preview or error handling rather than crashing.

## Verdict Mapping

This project uses the following verdict labels in the UI and JSON outputs:

- `SAFE` = functionally equivalent to `APPROVE`
- `NEEDS_REVIEW` = functionally equivalent to `REVIEW`
- `UNSAFE` = functionally equivalent to `REJECT`

We keep `SAFE / NEEDS_REVIEW / UNSAFE` as the internal courtroom-style decision labels, but they map directly to the evaluation rubric’s approval categories.

## Run Artifacts

Each evaluation run creates a timestamped folder in `runs/`.

Typical artifacts include:

- `system_case.json`
- `run_metadata.json`
- `judge1.json`
- `judge2.json`
- `judge3.json`
- `final_judge.json`
- `report.pdf`

For enriched inputs such as GitHub repository analysis, the run may also include intake artifacts such as:

- `intake_summary.json`
- `intake_logs.json`
- `repo_extraction.json`
- `runtime_probe_config.json`
- `runtime_probe_result.json`
- `legacy_case_file.json` for compatibility flows

## Testing

Run the full test suite with:

```bash
uv run pytest
```

## Key Paths

- Streamlit app: `src/ui/app.py`
- Pipeline: `src/pipeline.py`
- Core pipeline implementation: `src/ai_safety_lab/pipeline.py`
- System schema: `src/ai_safety_lab/schemas/system_case.py`
- GitHub ingestion: `src/ai_safety_lab/ingestion/`
- Judges: `src/ai_safety_lab/judges/`
- Ultimate judge: `src/ai_safety_lab/final_judge/ultimate_judge.py`
- PDF reporting: `src/ai_safety_lab/reporting/make_report_pdf.py`
- Example cases: `examples/cases/`

## Notes

- `config/config.example.yaml` contains model/backend defaults for the MVP
- `.env.example` is committed; `.env` stays local only
- `runs/` is generated output and is mostly ignored by Git
- Public GitHub repositories are supported in the current ingestion flow
- Runtime evaluation is currently limited to JSON APIs and simple public HTML forms
