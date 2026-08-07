# AI Handoff

## Current State

Phase 2 includes the canonical data model/provider contract, FRED live-validated adapter, Yahoo daily market-data adapter with successful live smoke evidence, provider-independent bounded retry, and the merged ECOS `StatisticSearch` economic-series adapter.

PR #37 merged as `0f3106bb8772317679df52e76717c6e9ddfebe94`. ECOS Live Smoke run `31174803601` failed safely with `MISSING_SECRET`. After `ECOS_API_KEY` was configured, run `31180017610` exhausted three bounded attempts with canonical `TRANSPORT_ERROR`. ECOS live retrieval success is therefore not yet claimed.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/ecos-transport-diagnostics`
- Issue: #38 — `fix: improve ECOS transport diagnostics`
- PR: to be opened as Draft

## Active Implementation

- Canonical ECOS failure code remains `TRANSPORT_ERROR` and retry behavior is unchanged.
- Transport failures now receive one sanitized type-only category: `timeout`, `dns`, `tls`, `connection`, or fallback `transport`.
- Raw exception text, API keys, secret-bearing URLs, payloads, and observation values are never included in diagnostics.
- `tools/ecos_smoke.py` emits sanitized `transport_details` when available.
- Deterministic tests cover timeout, DNS-style `URLError`, TLS-style `URLError`, and connection reset.
- `docs/ECOS_ADAPTER.md` and `WORKLOG.md` record actual live evidence and security boundaries.

## Validation Status

- CI for Issue #38 is pending until the Draft PR is opened.
- Do not claim ECOS live connectivity until an actual smoke run returns trusted observations.
- After this PR merges, manually rerun ECOS Live Smoke on `main`; use the sanitized category to guide the next fix if it still fails.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit secrets, raw live payloads, secret-bearing URLs, or personal investment data.
3. Financial values remain `Decimal`; datetimes remain timezone-aware and normalized to UTC.
4. Do not hide provider failures, partial results, stale states, or validation gaps.
5. Substantial PRs begin as Draft.
6. Never merge without explicit user approval.

## Exact Next Recommended Task

Open Draft PR for Issue #38, run Python and Documentation CI, fix failures if any, update living-document CI evidence, and mark Ready for Review only after the final head passes. Stop for explicit user merge approval. After merge, rerun ECOS Live Smoke manually and inspect the sanitized transport category or successful observation evidence.
