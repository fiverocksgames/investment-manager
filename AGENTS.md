# AGENTS.md

## Purpose

This file defines mandatory operating rules for AI and human contributors. The repository, not conversation history, is the source of truth. `PROJECT_POLICY.md` is the controlling development-policy document.

## Core Rules

1. Read `PROJECT_CHARTER.md`, `PROJECT_POLICY.md`, `README.md`, `ROADMAP.md`, `WORKLOG.md`, `AI_HANDOFF.md`, `docs/FEATURE_MATRIX.md`, and relevant specifications before changing behavior.
2. Work from an Issue and stable Requirement IDs for substantial changes.
3. Follow: Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close.
4. Never commit directly to `main`.
5. Never delete or silently rename a Requirement ID. Deprecate it with rationale and replacement links.
6. Update documentation in the same PR as behavior changes.
7. Update `WORKLOG.md`, `AI_HANDOFF.md`, and `CHANGELOG.md` in every substantial PR.
8. Record material technical or product choices in `docs/DECISIONS.md` before or with implementation.
9. Do not invent market data, test results, provider guarantees, or completed work.
10. Do not merge without explicit user approval.

## Architecture Boundaries

- Indicators such as RSI, MACD, moving averages, momentum, volatility, and market regime are calculated only in the Analysis Engine.
- The UI renders server-produced or job-produced results and must not duplicate financial calculation logic.
- Portfolio normalization and rebalancing calculations belong to the Portfolio Engine.
- Recommendation scoring consumes normalized Analysis Engine and Portfolio Engine outputs.
- Provider-specific formats must be isolated behind data adapters.
- Authentication and authorization checks must be enforced at the data boundary, not only in the UI.
- Preserve the processing direction: Provider → Normalizer → Cache → Analysis Engine → Portfolio Engine → Recommendation Engine → UI.

## Investment Safety

- The product is a decision support system, not an automated trader.
- Never add order execution, brokerage credential storage, or automatic portfolio changes in MVP.
- Recommendations must show evidence, timestamps, uncertainty, assumptions, and risks.
- Never imply guaranteed returns or omit material limitations.
- Leverage, inverse products, individual stocks, derivatives, and short selling are outside MVP.

## Security Rules

- Never commit API keys, service-role keys, access tokens, private credentials, or user portfolio data.
- Use GitHub Actions secrets and environment variables.
- Use least-privilege Supabase policies and Row Level Security.
- Redact sensitive values from logs and fixtures.
- Treat spreadsheets and imported holdings as untrusted input.

## Data Rules

- Every dataset must document provider, symbol or series identifier, frequency, timezone, retrieval time, transformation, license or usage limits, and known gaps.
- Reject or mark stale data rather than silently using it.
- Preserve raw observations where practical and produce normalized derived tables separately.
- Avoid look-ahead bias and document point-in-time assumptions.

## Testing Rules

- Financial formulas require deterministic unit tests with known fixtures.
- Provider adapters require contract tests using recorded or mocked responses.
- Critical user flows require integration or end-to-end coverage.
- Documentation-only PRs require link, structure, and traceability validation.
- Do not claim tests passed unless they were actually run.

## PR Requirements

Every substantial PR begins as Draft and its body must include:

- Summary
- Requirement IDs
- Validation
- Test
- Documentation
- Known Limitations
- Next Steps

A PR is incomplete when documentation, tests, worklog, handoff, or traceability updates are missing. Mark it ready only after required CI succeeds.

## Handoff Rules

Before ending work, record:

- Current Issue, branch, and PR
- Completed and incomplete work
- Relevant commits and files
- Validation performed
- Risks, blockers, and assumptions
- Exact next recommended task

## Conflict Resolution

When instructions conflict, apply this order:

1. Security and legal constraints
2. `PROJECT_CHARTER.md`, `PROJECT_POLICY.md`, and investment policy
3. Accepted decision records
4. Architecture and feature specifications
5. Current Issue and PR scope
6. Contributor preference
