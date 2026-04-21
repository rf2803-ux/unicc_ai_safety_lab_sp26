# Security Policy

UNICC AI Safety Lab evaluates AI systems and may process repository contents, endpoint responses, model outputs, and generated reports. Please handle all test data and provider credentials carefully.

## Supported Versions

The public release candidate is currently version `0.1.x`.

## Reporting A Vulnerability

Before public release, this section should be updated with the official UNICC security reporting contact.

Until then, please report suspected vulnerabilities privately to the project maintainers rather than opening a public issue.

When reporting, include:

- affected version or commit
- description of the issue
- reproduction steps
- potential impact
- whether any secrets or private data may have been exposed

## Sensitive Data Handling

Do not commit:

- `.env`
- API keys
- provider credentials
- local browser session data
- `config/config.local.yaml`
- generated private run artifacts
- screenshots containing secrets or personal data

Generated evaluation outputs can contain snippets from repositories, endpoint responses, or model outputs. Review and sanitize generated artifacts before sharing them publicly.

## Recommended Pre-Release Checks

Before an open-source release, maintainers should run:

- automated test suite: `uv run pytest`
- dependency vulnerability scan, such as `pip-audit`
- static security scan, such as `bandit`
- secret scan, such as `gitleaks`
- license scan for direct and transitive dependencies
- manual review of example cases and generated artifacts

## Runtime Endpoint Assessment Safety

Runtime endpoint probing is intended for safe, limited behavioral assessment. It is not a penetration testing tool.

Current runtime limitations should be respected:

- no authenticated flows unless explicitly implemented and documented
- no credential scraping
- no destructive actions
- no file upload testing unless explicitly scoped
- no high-volume stress testing

