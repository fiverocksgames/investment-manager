# AI Handoff

## Current State

Phase 2 has live-validated FRED, Yahoo, and ECOS providers, provider-independent bounded retry, and explicit ECOS transport diagnostics. ECOS Live Smoke run `31182329368` succeeded with 99 trusted observations on attempt 1; Yahoo Live Smoke run `31169043266` succeeded with 10 trusted SPY observations on attempt 1. These are bounded run-specific evidence, not availability guarantees.

The active milestone is canonical FX normalization.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/fx-normalization`
- Issue: #42 — `feat: add canonical FX normalization`
- Draft PR: #43 — `feat: add canonical FX normalization`

## Active Implementation

- `investment_manager/data/fx.py` adds `FxPair`, `FxNormalizationBinding`, `FxNormalizationError`, and `FxNormalizer`.
- Canonical FX direction is quote currency per one base currency, with explicit units such as `KRW_per_USD`.
- Direct source direction preserves the source `Decimal` exactly.
- Exactly reversed source direction uses a fixed 34-digit `Decimal` reciprocal with `ROUND_HALF_EVEN`.
- Zero/negative rates, non-FX observations, subject mismatches, invalid currency codes, and unrelated source currency pairs are rejected explicitly.
- Provider, source identifier, source retrieval time, revision, quality/freshness, and provider metadata are preserved.
- Normalized identifiers are deterministic from pair, provider/source identity, observation time, and revision.
- `tests/test_fx_normalization.py` includes a network-free Yahoo `KRW=X` fixture configured explicitly as USD/KRW plus direct/inverse/error/provenance coverage.
- `docs/FX_NORMALIZATION.md`, `docs/DATA_MODEL.md`, `docs/DATA_SOURCES.md`, and `docs/TEST_PLAN.md` define the contract and test boundaries.

## Validation Status

- Initial implementation head `044e350e9c028eb25944463328a69905c3b1ec73`: Documentation run #103 passed; Python run #51 test job passed.
- Living-document and traceability updates changed the head; fresh final-head Python and Documentation CI are required before Ready for Review.
- No new external provider call is introduced by FX normalization.

## Critical FX Rule

Do not infer rate direction from ticker syntax. Yahoo Finance displays `KRW=X` as USD/KRW, and this source convention is configured explicitly as base `USD`, quote `KRW`. Future provider FX bindings require separately verified direction semantics.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Never commit secrets, raw live payloads, secret-bearing URLs, or personal investment data.
3. Financial values remain `Decimal`; datetimes remain timezone-aware and UTC-normalized.
4. Never hide failed, partial, stale, or ambiguous data.
5. Substantial PRs begin as Draft.
6. Never merge without explicit user approval.

## Exact Next Recommended Task

Finish living-document evidence updates, run fresh Python and Documentation CI on the final PR #43 head, fix any failures, update PR validation, and mark Ready for Review only after both applicable checks pass. Stop for explicit user merge approval. After merge, proceed to normalization/immutable source-snapshot integration.
