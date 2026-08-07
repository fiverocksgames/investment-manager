# AI Handoff

## Current State

Phase 2 includes the canonical data model/provider contract, FRED live-validated adapter, Yahoo daily market-data adapter with successful live smoke evidence, provider-independent bounded retry, and the merged ECOS `StatisticSearch` economic-series adapter with verified live retrieval.

ECOS adapter PR #37 merged as `0f3106bb8772317679df52e76717c6e9ddfebe94`. ECOS transport-diagnostic PR #39 merged as `23bd2ef88ce7ab3f3da2f288ad066089c163f2e8`. ECOS Live Smoke run `31182329368` then succeeded on that merged `main` commit with 99 trusted observations on attempt 1. This is bounded live-success evidence, not an availability guarantee.

FRED, Yahoo, and ECOS each now have verified successful live retrieval evidence.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/ecos-live-evidence`
- Issue: #40 — `docs: record ECOS live-success evidence`
- PR: evidence-only PR to be opened as Draft

## Verified ECOS Live Evidence

- Workflow run: `31182329368`
- Commit: `23bd2ef88ce7ab3f3da2f288ad066089c163f2e8`
- provider: `ecos`
- source_identifier: `bok_base_rate_daily`
- attempt_count: `1`
- observation_count: `99`
- first_observed_at: `2026-02-09T00:00:00+00:00`
- last_observed_at: `2026-05-18T00:00:00+00:00`
- unit: `percent_per_annum`
- cycle: `D`
- tolerated warning: `OUT_OF_RANGE`

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit secrets, raw live payloads, secret-bearing URLs, or personal investment data.
3. Financial values remain `Decimal`; datetimes remain timezone-aware and normalized to UTC.
4. Do not hide provider failures, partial results, stale states, or validation gaps.
5. Substantial PRs begin as Draft.
6. Never merge without explicit user approval. The user has already explicitly approved merging this evidence-only follow-up after CI passes.

## Exact Next Recommended Task

Open the Draft PR for Issue #40, run Python and Documentation CI, update the PR with final evidence, and merge this evidence-only PR under the already-granted approval if the final head remains mergeable and all required CI passes. Then close/verify Issue #40 and continue to the next roadmap item.
