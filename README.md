# unicc_ai_safety_lab_sp26

Courtroom-style AI Safety Lab for the UNICC Spring 2026 capstone.

## Overview

This project evaluates AI conversations before deployment using a courtroom-style council:

- Judge 1, Judge 2, and Judge 3 review the same case with the same baseline rubric
- The Ultimate Judge reads only the three judge outputs and produces the final verdict
- Each run saves JSON artifacts and a PDF report under `runs/<timestamp>/`

## MVP scope

- Upload or generate a `case_file.json`
- Run three holistic judges with the same rubric
- Run an Ultimate Judge on only the three judge outputs
- Save run artifacts under `runs/<timestamp>/`
- Generate a PDF report for each run

## Setup

```bash
brew install uv
uv sync
cp .env.example .env
```

Set these local secrets in `.env`:

- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`

Example:

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
```

Important:

- Never commit `.env`
- Never paste real keys into GitHub, screenshots, slides, or shared docs
- Each teammate should create their own local `.env`

## Run the Streamlit app

```bash
uv run streamlit run src/ui/app.py
```

## Run tests

```bash
uv run pytest
```

## Share With Teammates

If you want classmates or teammates to use the project without changing your main repository:

1. Push the code to GitHub
2. Share the repository link with read-only access, or keep the repo public without adding write collaborators
3. Ask each teammate to:
   - clone the repo
   - run `cp .env.example .env`
   - add their own API keys locally
   - run the app on their machine

Recommended rule:

- Do not share `.env`
- Do not share API keys
- Do not give direct write access to `main` unless you want them to edit the repo

## Key paths

- Streamlit app: `src/ui/app.py`
- Pipeline: `src/pipeline.py`
- Provider clients: `src/clients/`
- Judges: `src/judges/`
- Ultimate judge: `src/final_judge/ultimate_judge.py`
- PDF reporting: `src/reporting/make_report_pdf.py`
- Example cases: `examples/cases/`

## Notes

- `config/config.example.yaml` contains model/backend defaults for the MVP
- `.env.example` is committed; `.env` stays local only
- `runs/` is generated output and is mostly ignored by Git
