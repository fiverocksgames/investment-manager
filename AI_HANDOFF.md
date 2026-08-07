# AI Handoff

## Current State

Phase 1 application infrastructure is complete with residual PWA and data-isolation validation work. Phase 2 includes the canonical Python data model, provider contract, FRED adapter with verified live connectivity, Yahoo daily market-data adapter, Yahoo live-smoke workflow, provider-independent bounded retry, and Yahoo HTTP header hardening.

Yahoo Live Smoke run `31169043266` succeeded on merged `main` commit `18dd594a93ca45f966b79a3b612808751c99c112` after header hardening. It returned 10 trusted SPY daily observations on the first attempt. This proves that bounded live retrieval succeeded for that run; it does not guarantee future Yahoo availability.

ECOS economic-series adapter work is now active.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/ecos-adapter`
- Issue: #36 — `feat: implement ECOS economic-series adapter`
- Draft PR: #37 — `feat: implement ECOS economic-series adapter`

## Implemented on the Active Branch

- `investment_manager/data/ecos.py` with `EcosProvider` and `EcosSeriesBinding`.
- ECOS `StatisticSearch` JSON access using runtime `ECOS_API_KEY`.
- Explicit statistic/item/cycle bindings and canonical identity mapping.
- Initial cycle support for annual, quarterly, monthly, and daily data.
- `Decimal` financial values and timezone-aware UTC period-start timestamps.
- Deterministic observation UUIDs and ECOS source metadata preservation.
- Explicit authentication, HTTP, transport, payload, missing-value, invalid-row, range, and binding failure classification.
- `tests/test_ecos_provider.py` with deterministic fixture coverage and no live dependency.
- `tools/ecos_smoke.py` plus manual `.github/workflows/ecos-smoke.yml` using the common bounded retry executor and GitHub Actions secret `ECOS_API_KEY`.
- `docs/ECOS_ADAPTER.md` documents normalization, failure behavior, secret handling, and boundaries.
- Python CI path filtering includes the ECOS smoke workflow.

## Validation Status

- Draft PR #37 is open.
- Python and Documentation CI are running on the initial implementation head.
- ECOS live connectivity has not been claimed. The manual workflow cannot provide accepted live evidence until it exists on `main` and is executed with `ECOS_API_KEY` configured.
- Yahoo live retrieval is verified by run `31169043266`: SPY, 10 observations, first-attempt success.

## ECOS Rules

- ECOS is treated as the Bank of Korea official economic-statistics provider and requires an API key.
- API keys are runtime secrets only and must not appear in code, logs, fixtures, PR bodies, or documentation.
- Canonical identity comes from explicit `EcosSeriesBinding` entries, never provider labels.
- Canonical values use `Decimal`; timestamps are UTC-aware.
- Period-start timestamps are normalization conventions, not publication timestamps.
- Source units and ECOS identifiers remain metadata so mismatches can be audited.
- Adapter code classifies failures; retry orchestration remains in the common executor.

## Known Limitations

- ECOS `StatisticSearch` only; no metadata-list APIs or other ECOS services yet.
- Initial cycle support is `A`, `Q`, `M`, `D` only.
- Pagination beyond one configured response page is not yet orchestrated.
- ECOS live smoke has not yet run successfully.
- Identifier-scoped retry, `Retry-After` handling, cache, immutable snapshot integration, persistence, scheduled ingestion, and dataset versioning remain future work.
- PWA install/offline validation, user-owned tables, RLS, and cross-user isolation remain pending.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit secrets, tokens, raw live payloads, or personal portfolio data.
3. Preserve Requirement IDs and update traceability documents.
4. Do not claim live-provider validation without actual run evidence.
5. Substantial pull requests begin as Draft.
6. Never merge without explicit user approval.

## Exact Next Recommended Task

Complete ECOS living-document and traceability updates, inspect Python and Documentation CI for PR #37, fix any failures, then re-run fresh CI on the final head. Mark Ready for Review only after all evidence agrees. Do not merge without explicit user approval. After merge, configure `ECOS_API_KEY` if necessary and manually execute ECOS Live Smoke before recording live connectivity.
