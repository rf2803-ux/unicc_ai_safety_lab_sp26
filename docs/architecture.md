# Architecture

The MVP uses a schema-first pipeline:

1. Validate a case file
2. Run three judges with the same rubric and different lenses
3. Run the ultimate judge on only the judge outputs
4. Persist artifacts under `runs/<timestamp>/`
5. Generate a PDF and show the result in Streamlit
