# Open-Source Release Checklist

Use this checklist before publishing the project publicly.

## Repository Hygiene

- [ ] Confirm `.env` is not committed.
- [ ] Confirm `config/config.local.yaml` is not committed.
- [ ] Remove or sanitize generated `runs/` artifacts.
- [ ] Review screenshots and PDFs for secrets or private data.
- [ ] Confirm example cases are synthetic or approved for release.
- [ ] Update copyright holder in `LICENSE` if needed.

## Documentation

- [ ] Review `README.md` for accuracy.
- [ ] Publish `CONTRIBUTING.md`.
- [ ] Publish `SECURITY.md` with the official reporting contact.
- [ ] Publish roadmap and known limitations.
- [ ] Document provider setup and API key handling.
- [ ] Document runtime endpoint limitations.

## Security And Quality

- [ ] Run `uv run pytest`.
- [ ] Run dependency vulnerability scan.
- [ ] Run static security scan.
- [ ] Run secret scan.
- [ ] Review endpoint probing behavior for safe defaults.
- [ ] Review third-party dependency licenses, including transitives.

## Community Readiness

- [ ] Add issue templates.
- [ ] Add pull request template.
- [ ] Add maintainer response expectations.
- [ ] Define contribution review process.
- [ ] Define supported versions and release process.

