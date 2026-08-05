# Project Development Policy

## 1. Purpose

This policy defines the durable development and operating rules for Investment Manager. The repository is the single source of truth; conversation history, temporary notes, and external forks are not authoritative.

## 2. Canonical Repository

The canonical repository is:

`fiverocksgames/investment-manager`

All Issues, branches, commits, pull requests, CI evidence, reviews, merges, and project records are created and maintained in this repository. Any future repository transfer, mirror, or migration requires an explicit decision record and must not disrupt the development workflow.

## 3. Priority of Concerns

When priorities compete, use this order:

1. Security, legal, and data-usage constraints
2. Investment safety and capital-preservation principles
3. Approved product requirements and decision records
4. Architecture and data integrity
5. Documentation and traceability
6. Implementation convenience
7. UI polish

## 4. Mandatory Development Workflow

Substantial work follows this sequence:

`Issue → Design → Documentation → Branch → Implementation → Test → Draft PR → CI → Review → User Approval → Merge → Issue Close`

Rules:

- Create an Issue before substantial work begins.
- Define scope, exclusions, Requirement IDs, acceptance criteria, and validation evidence in the Issue.
- Update design and documentation before or with implementation.
- Never commit directly to `main`.
- Create a short-lived branch from the current `main`.
- Open a Draft PR before review is requested.
- Do not mark a PR ready until required CI passes.
- Do not merge without explicit user approval.
- Close the linked Issue only after merge and final evidence are recorded.

Small typo, broken-link, or formatting-only corrections may omit a separate Issue when they do not change behavior, requirements, architecture, data, security, or operations.

## 5. Branch Policy

Use focused, short-lived branches:

- `agent/<description>` for AI-led work
- `feature/<description>` for product behavior
- `fix/<description>` for defects
- `docs/<description>` for documentation-only changes
- `ci/<description>` for automation changes

A branch must have one coherent purpose. Unrelated changes require separate branches and PRs.

## 6. Documentation-First Policy

The project follows:

`Investment Policy → Design → Documentation → Data and Code → UI`

Relevant documentation must be updated before implementation is considered complete. Financial calculations must not live in the UI. Provider-specific formats must remain behind adapters.

Minimum living-document updates for substantial PRs:

- `WORKLOG.md`
- `AI_HANDOFF.md`
- `CHANGELOG.md`
- `docs/FEATURE_MATRIX.md` when requirements or evidence change

Update other specifications when affected, including architecture, database, API, security, operations, analysis, portfolio, data-source, testing, and decision documents.

## 7. Document Classes

### Constitution Documents

These define durable project principles and should change rarely:

- `PROJECT_CHARTER.md`
- `PROJECT_POLICY.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `docs/INVESTMENT_POLICY.md`

Material changes require a dedicated Issue and PR with clear rationale.

### Living Operational Documents

These must reflect current reality:

- `WORKLOG.md`
- `AI_HANDOFF.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `docs/FEATURE_MATRIX.md`

## 8. Requirement Traceability

Every substantive behavior must use stable Requirement IDs. IDs are append-only and must not be silently deleted or renamed.

The required traceability chain is:

`Requirement → Issue → Design → Documentation → Implementation → Test → PR`

Preferred domain prefixes include:

- `GOV-*`
- `REQ-DATA-*`
- `REQ-PROVIDER-*`
- `REQ-ANALYSIS-*`
- `REQ-PORTFOLIO-*`
- `REQ-RECOMMEND-*`
- `REQ-UI-*`
- `REQ-AUTH-*`
- `REQ-INFRA-*`
- `REQ-SEC-*`
- `REQ-OPS-*`

Existing Requirement IDs remain valid and are not renamed solely for consistency.

## 9. Pull Request Policy

Every substantial PR begins as Draft and includes:

- Summary
- Requirement IDs
- Validation
- Test
- Documentation
- Known Limitations
- Next Steps

A PR is incomplete when applicable documentation, testing, traceability, worklog, or handoff evidence is missing. CI success is necessary but does not replace manual validation where required.

## 10. AI Handoff Policy

The project must remain operable without conversation history. Before work ends, record:

- Current Issue, branch, and PR
- Completed and incomplete work
- Relevant files and commits
- Validation performed
- Risks, blockers, assumptions, and security cautions
- Exact next recommended task

No important decision may exist only in chat. Record it in the appropriate repository document.

## 11. Architecture Boundaries

The required processing direction is:

`Provider → Normalizer → Cache → Analysis Engine → Portfolio Engine → Recommendation Engine → UI`

- The UI does not calculate investment indicators, portfolio allocations, or recommendation scores.
- Providers do not leak provider-specific schemas beyond adapter boundaries.
- Analysis results must include input period, source, timestamp, and freshness context.
- Recommendations must be explainable and non-executing.

## 12. Security and Privacy

Never commit:

- Supabase service-role keys
- Google client secrets
- API secrets or access tokens
- Database passwords or JWT secrets
- Personal portfolio data

Only browser-safe public configuration may enter frontend builds. Authentication proves identity, not authorization. User-owned data requires default-deny Row Level Security and cross-user isolation tests before production use.

## 13. Data and Investment Integrity

- Never invent market data, provider behavior, test results, or completed validation.
- Document source, identifier, frequency, timezone, retrieval time, transformation, freshness, usage limits, and known gaps.
- Fail safely on missing or stale data.
- Avoid look-ahead bias and document point-in-time assumptions.
- The product remains a decision-support system and must not execute trades or imply guaranteed returns.

## 14. Phase and Milestone Governance

Each phase must have explicit objectives, deliverables, exit criteria, and validation evidence. Phase closure requires updates to:

- `WORKLOG.md`
- `AI_HANDOFF.md`
- `CHANGELOG.md`
- `ROADMAP.md`
- `docs/FEATURE_MATRIX.md`

Phase 2 uses milestones such as Data Model, Provider Interface, provider adapters, Normalizer, Cache, and Integration. GitHub Projects may be introduced when parallel work makes a board materially useful; it is not required before then.

## 15. Tooling Policy

GitHub-connected tools are the default mechanism for repository work. Tool limitations must not weaken the Issue, documentation, review, CI, or approval process. If an exception is unavoidable, record the reason and impact in `docs/DECISIONS.md` or `WORKLOG.md`.

## 16. Policy Changes

Changes to this policy require:

1. A dedicated Issue
2. Explicit rationale and impact analysis
3. Documentation updates
4. A Draft PR and successful CI
5. Explicit user approval before merge
