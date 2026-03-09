# unicc_ai_safety_lab_sp26

Courtroom-style AI Safety Lab for the UNICC Spring 2026 capstone.

## MVP scope

- Upload or generate a `case_file.json`
- Run three holistic judges with the same rubric
- Run an Ultimate Judge on only the three judge outputs
- Save run artifacts under `runs/<timestamp>/`
- Generate a PDF report for each run

## Setup

```bash
uv sync
cp .env.example .env
```

Set these local secrets in `.env`:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

## Run the Streamlit app

```bash
uv run streamlit run src/ui/app.py
```

## Run tests

```bash
uv run pytest
```

## Key paths

- Streamlit app: `src/ui/app.py`
- Pipeline: `src/pipeline.py`
- Provider clients: `src/clients/`
- Judges: `src/judges/`
- Ultimate judge: `src/final_judge/ultimate_judge.py`
- PDF reporting: `src/reporting/make_report_pdf.py`
- Example cases: `examples/cases/`
