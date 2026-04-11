# Control Assessment Library

The UNICC Review Framework includes a lightweight control assessment layer to make results more actionable.

This layer does **not** certify a target system or determine legal compliance. Instead, it groups category-level findings into practical control areas that support structured review, remediation planning, and framework-aligned discussion.

## Control Areas

### Governance and Accountability
- Focus: ownership, review accountability, and documented oversight expectations
- Primary categories:
  - `auditability`
  - `transparency_reliability`

### Logging and Traceability
- Focus: ability to reconstruct inputs, outputs, decisions, and operational events
- Primary categories:
  - `auditability`

### Transparency and User Disclosure
- Focus: user-facing clarity about limits, confidence, behavior, and overclaiming
- Primary categories:
  - `transparency_reliability`
  - `deception_impersonation_overclaiming`

### Human Oversight and Escalation
- Focus: manual review, escalation, and safeguards for high-impact or ambiguous outputs
- Primary categories:
  - `harmful_content_unsafe_instructions`
  - `bias_discrimination_hate`
  - `transparency_reliability`

### Data Governance and Privacy Safeguards
- Focus: privacy protection, sensitive data handling, and dataset risk
- Primary categories:
  - `privacy_data_leakage`
  - `bias_discrimination_hate`

### Security and Misuse Resilience
- Focus: cyber misuse resistance, prompt injection resilience, and operational hardening
- Primary categories:
  - `cyber_misuse`
  - `prompt_injection_jailbreak_resistance`

## Status Semantics

The current UI and PDF use three control states:

- `Needs attention`
  - current evidence suggests a material control weakness or missing safeguard
- `Review needed`
  - some supporting evidence exists, but the control still needs manual validation
- `Better supported`
  - current evidence is comparatively stronger, though this is still not a compliance determination

## Evidence Basis

Each control summary is derived from:

- category scores across expert reviewers
- category rationales
- surfaced evidence snippets

This makes the control layer traceable back to the same evidence the reviewers used, rather than inventing a separate assurance signal.
