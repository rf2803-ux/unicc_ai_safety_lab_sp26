# Roadmap

This roadmap distinguishes current capabilities from planned improvements. The project should be described as a framework-aligned assessment workflow, not as a certification or legal compliance product.

## Current Capabilities

- Four input modes:
  - JSON case upload
  - public GitHub repository ingestion
  - limited app / endpoint runtime probing
  - internal chat case generation
- Normalization into a shared `SystemCase`
- Three expert reviewers plus final arbitration
- Structured JSON artifacts per run
- PDF report generation
- Framework alignment to selected NIST AI RMF, ISO/IEC 42001, and EU AI Act themes
- Control assessment layer for remediation-oriented review

## Near-Term Roadmap

- Improve runtime target classification and unsupported-target messages.
- Expand safe runtime probe packs.
- Add derived confidence scoring based on evidence quality and reviewer agreement.
- Add evidence-to-control trace tables.
- Improve partial-failure handling so completed evidence is preserved when one provider fails.
- Add stronger documentation for contributors and maintainers.

## Medium-Term Roadmap

- Add hosted chat app assessment mode.
- Add browser-based runtime runner for controlled local assessments.
- Support multi-turn runtime probe sessions.
- Improve report exports and machine-readable summaries.
- Add more provider configuration examples.
- Add optional dependency and security scanning workflows.

## Longer-Term Roadmap

- Remediation tracking across runs.
- More explicit evidence provenance.
- Stronger EU AI Act documentation-support workflows.
- Pluggable probe packs by target type.
- Extensible provider and judge configuration.

## Non-Goals For The Current Release

- Formal legal certification.
- Full penetration testing.
- High-volume load or stress testing.
- Authenticated browser automation without explicit user consent and isolation.

