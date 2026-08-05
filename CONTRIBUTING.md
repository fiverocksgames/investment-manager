# Contributing

## Policy

All contributors must follow [`PROJECT_POLICY.md`](PROJECT_POLICY.md). The canonical repository is `fiverocksgames/investment-manager`.

## Workflow

Substantial work follows:

Issue → Design → Documentation → Branch → Implementation → Test → Draft Pull Request → CI → Review → User Approval → Merge → Issue Close

Do not begin implementation until the requirement, scope, exclusions, acceptance criteria, and validation plan are documented.

## Issues

An Issue should include:

- Problem and user outcome
- Requirement IDs
- Scope and exclusions
- Acceptance criteria
- Data, security, architecture, and documentation impacts
- Validation plan

Use stable IDs such as:

- `REQ-DATA-*` data models and normalization
- `REQ-PROVIDER-*` provider adapters
- `REQ-ANALYSIS-*` analysis and signals
- `REQ-PORTFOLIO-*` portfolio behavior
- `REQ-RECOMMEND-*` recommendation behavior
- `REQ-UI-*` user interface
- `REQ-AUTH-*` authentication
- `REQ-INFRA-*` infrastructure
- `REQ-SEC-*` security
- `REQ-OPS-*` operations
- `GOV-*` governance

Existing identifiers such as `REQ-MKT-*`, `REQ-SIG-*`, `REQ-PORT-*`, and `REQ-REC-*` remain valid. IDs are append-only. Deprecated requirements remain documented with status and replacement references.

Small typo, broken-link, or formatting-only corrections may omit a separate Issue when they do not change behavior, requirements, architecture, data, security, or operations.

## Branches

Use short-lived branches:

- `agent/<description>` for AI-led work
- `feature/<description>` for features
- `fix/<description>` for defects
- `docs/<description>` for documentation
- `ci/<description>` for automation

Branch from the current `main`. Never commit directly to `main`. Keep one coherent purpose per branch.

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

Every substantial PR updates `WORKLOG.md`, `AI_HANDOFF.md`, and `CHANGELOG.md`. Update `docs/FEATURE_MATRIX.md` whenever requirements or evidence change.

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

Open every substantial PR as Draft. Every PR body must contain:

- Summary
- Requirement IDs
- Validation
- Test
- Documentation
- Known Limitations
- Next Steps

Mark the PR ready only after required CI succeeds. Do not merge without explicit user approval. Close the linked Issue only after the merge and final evidence are recorded.

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
