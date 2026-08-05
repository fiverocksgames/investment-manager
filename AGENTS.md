# AGENTS.md

## Purpose

This file defines mandatory operating rules for AI and human contributors. The repository, not conversation history, is the source of truth.

## Core Rules

1. Read `PROJECT_CHARTER.md`, `README.md`, `ROADMAP.md`, `WORKLOG.md`, `AI_HANDOFF.md`, `docs/FEATURE_MATRIX.md`, and relevant specifications before changing behavior.
2. Work from an Issue and stable Requirement IDs.
3. Follow: Issue → Design → Documentation → Implementation → Test → PR.
4. Never delete or silently rename a Requirement ID. Deprecate it with rationale and replacement links.
5. Update documentation in the same PR as behavior changes.
6. Update `WORKLOG.md` and `AI_HANDOFF.md` in every PR.
7. Record material technical or product choices in `docs/DECISIONS.md` before or with implementation.
8. Do not invent market data, test results, provider guarantees, or completed work.

## Architecture Boundaries

- Indicators such as RSI, MACD, moving averages, momentum, volatility, and market regime are calculated only in the Analysis Engine.
- The UI renders server-produced or job-produced results and must not duplicate financial calculation logic.
- Portfolio normalization and rebalancing calculations belong to the Portfolio Engine.
- Recommendation scoring consumes normalized Analysis Engine and Portfolio Engine outputs.
- Provider-specific formats must be isolated behind data adapters.
- Authentication and authorization checks must be enforced at the data boundary, not only in the UI.

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

Every PR body must include:

- Summary
- Requirement IDs
- Validation
- Test
- Documentation
- Known Limitations
- Next Steps

A PR is incomplete when documentation, tests, worklog, or handoff updates are missing.

## Handoff Rules

Before ending work, record:

- Current branch and PR
- Completed and incomplete work
- Relevant commits and files
- Validation performed
- Risks, blockers, and assumptions
- Exact next recommended task

## Conflict Resolution

When instructions conflict, apply this order:

1. Security and legal constraints
2. `PROJECT_CHARTER.md` and investment policy
3. Accepted decision records
4. Architecture and feature specifications
5. Current Issue and PR scope
6. Contributor preference
