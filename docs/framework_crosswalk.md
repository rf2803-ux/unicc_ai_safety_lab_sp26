# Framework Crosswalk

This document describes how the UNICC Review Framework is **aligned to principles from** NIST AI RMF and **supports assessment against** selected governance, documentation, traceability, robustness, and oversight themes reflected in ISO/IEC 42001 and the EU AI Act.

This crosswalk is intended as an alignment aid for review and documentation. It should not be interpreted as a certification, legal opinion, or formal compliance determination.

## Crosswalk Summary

| UNICC rubric category | NIST AI RMF concepts | ISO/IEC 42001 themes | EU AI Act themes |
| --- | --- | --- | --- |
| Privacy | Govern, Measure, privacy-enhanced and accountable operation | Governance, risk treatment, documentation and data handling controls | Risk management, documentation, traceability and deployer information |
| Harmful content / unsafe instructions | Map, Manage, harm prevention and trustworthy use | Operational controls, human oversight, risk treatment | Human oversight, safety-oriented controls, accuracy and robustness |
| Security / cyber misuse | Measure, Manage, secure and resilient operation | Security controls, operational safeguards, risk treatment | Cybersecurity, robustness, risk mitigation |
| Bias / fairness | Map, Measure, fairness and harmful-bias management | Impact assessment, risk treatment, governance oversight | Dataset quality, discriminatory-outcome reduction, human oversight |
| Deception / overclaiming | Govern, Measure, explainability and validity | Transparency, documentation, user-facing controls | Clear information to deployers, transparency, documentation |
| Prompt injection / jailbreak resistance | Measure, Manage, secure and resilient operation | Operational controls, security safeguards, risk treatment | Cybersecurity, robustness, risk mitigation |
| Transparency / reliability | Govern, Measure, explainability and reliability | Transparency, documentation, continual improvement | Documentation, clear deployer information, accuracy |
| Auditability | Govern, Measure, accountability and traceability | Monitoring, documentation, governance and continual improvement | Logging for traceability, documentation, oversight support |

## Interpretation

- **NIST AI RMF**: the strongest alignment is around trustworthiness, risk measurement, governance, and ongoing management of deployment risk.
- **ISO/IEC 42001**: the strongest alignment is around governance, documentation, traceability, monitoring, and operational controls.
- **EU AI Act**: the strongest alignment is around risk management, documentation, logging, traceability, deployer information, human oversight, and robustness/cybersecurity.

## Current Scope

The current app supports:

- structured multi-expert risk review
- explicit arbitration of a final decision
- evidence-driven output for repository, runtime, and case-based inputs
- framework-aligned explanation of findings in the UI and exported report

The current app does **not** claim:

- formal NIST conformance certification
- ISO/IEC 42001 certification
- EU AI Act legal compliance determination

The framework should therefore be described as:

> aligned to principles from NIST AI RMF and supportive of assessment against selected ISO/IEC 42001 and EU AI Act themes
