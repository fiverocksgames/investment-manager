# Contributing

## Workflow

All work follows:

Issue → Design → Documentation → Implementation → Test → Pull Request

Do not begin implementation until the requirement, scope, and acceptance criteria are documented.

## Issues

An Issue should include:

- Problem and user outcome
- Requirement IDs
- Scope and exclusions
- Acceptance criteria
- Data, security, architecture, and documentation impacts
- Validation plan

Use stable IDs such as:

- `REQ-MKT-*` market and data
- `REQ-SIG-*` analysis and signals
- `REQ-PORT-*` portfolio
- `REQ-AUTH-*` authentication
- `REQ-BKT-*` backtesting
- `REQ-REC-*` recommendation
- `REQ-OPS-*` operations
- `GOV-*` governance

IDs are append-only. Deprecated requirements remain documented with status and replacement references.

## Branches

Use short-lived branches:

- `agent/<description>` for AI-led work
- `feature/<description>` for features
- `fix/<description>` for defects
- `docs/<description>` for documentation

Branch from the current default branch unless the Issue explicitly identifies another base.

## Documentation First

Before code, update the relevant documents:

- Product behavior: `docs/PRD.md`
- Architecture: `docs/ARCHITECTURE.md`
- Data: `docs/DATA_SOURCES.md`, `docs/DATABASE.md`
- APIs: `docs/API_SPEC.md`
- Analysis formulas: `docs/ANALYSIS_SPEC.md`
- Portfolio behavior: `docs/PORTFOLIO_SPEC.md`
- Security: `docs/SECURITY.md`
- Operations: `docs/OPERATIONS.md`
- Investment constraints: `docs/INVESTMENT_POLICY.md`
- Tests: `docs/TEST_PLAN.md`
- Decisions: `docs/DECISIONS.md`
- Traceability: `docs/FEATURE_MATRIX.md`

## Commits

Use focused commits with imperative conventional prefixes where practical:

- `docs:` documentation
- `feat:` behavior
- `fix:` defect
- `test:` tests
- `refactor:` internal change
- `ci:` automation
- `chore:` maintenance

Never combine unrelated changes only to reduce commit count.

## Validation

Run the checks relevant to the change and report exact results. Never state that a check passed unless it was executed.

At minimum, implementation PRs should eventually include:

- Formatting and linting
- Type checking
- Unit tests
- Integration or contract tests where relevant
- Production build
- Security and secret scanning
- Documentation and traceability checks

## Pull Requests

Open Draft PRs early for substantial work. Every PR body must contain:

- Summary
- Requirement IDs
- Validation
- Test
- Documentation
- Known Limitations
- Next Steps

Update `WORKLOG.md`, `AI_HANDOFF.md`, and `docs/FEATURE_MATRIX.md` in the same PR.

## Review

Documentation and code receive equal review priority. Reviewers verify:

- Scope matches the Issue
- Requirement traceability is complete
- Calculations and data assumptions are documented
- Security and privacy impacts are handled
- Tests match acceptance criteria
- Known limitations are honest
- Handoff information is sufficient for a new contributor

## Investment Safety

Contributions must not introduce automated trade execution, guaranteed-return language, hidden scoring logic, unsupported instruments, or unaudited financial calculations.
