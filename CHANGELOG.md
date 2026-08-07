# Changelog

All notable project changes are recorded here. The format is inspired by Keep a Changelog.

## [Unreleased]

### Added

- Provider-independent canonical FX normalization with explicit `FxPair`, `FxNormalizationBinding`, `FxNormalizationError`, and `FxNormalizer`
- Directional FX units such as `KRW_per_USD`, deterministic direct/inverse normalization, and provider-provenance preservation
- Deterministic network-free FX normalization tests including representative Yahoo `KRW=X` USD/KRW fixture coverage
- `docs/FX_NORMALIZATION.md` with canonical direction, reciprocal precision, provenance, and failure boundaries
- Sanitized ECOS transport diagnostics (`timeout`, `dns`, `tls`, `connection`, `transport`) while preserving canonical `TRANSPORT_ERROR` behavior
- Deterministic ECOS tests for timeout, DNS, TLS, and connection-reset transport classification
- Bank of Korea ECOS `StatisticSearch` economic-series adapter with explicit bindings, `Decimal` values, UTC timestamps, deterministic identifiers, and source metadata
- Deterministic ECOS fixture tests for valid, missing, malformed, range, authentication, HTTP, and cycle behavior
- Manual secret-based ECOS Live Smoke workflow using `ECOS_API_KEY` and the common bounded retry executor
- Explicit Yahoo default HTTP request headers with a stable project-specific `User-Agent`, JSON `Accept`, and English `Accept-Language`
- Provider-independent bounded retry executor with exponential backoff, jitter, attempt evidence, and deterministic tests
- Yahoo daily market-price and FX-rate adapter with explicit symbol bindings and deterministic fixture tests
- Official FRED Version 1 economic-series adapter and protected live smoke workflow
- Python 3.12 canonical data models, provider contracts, and CI

### Changed

- FX normalization now requires explicit base/quote source direction; ticker text is never used to guess rate direction.
- Reverse FX direction uses a fixed 34-digit `Decimal` reciprocal with `ROUND_HALF_EVEN`; direct direction preserves the source `Decimal` exactly.
- FX normalized observations preserve source provider, source identifier, retrieval time, revision, quality/freshness, and original provider metadata while adding canonical/source direction metadata.
- ECOS Live Smoke emits only sanitized transport-detail categories when canonical transport failures occur.
- ECOS annual, quarterly, monthly, and daily period labels normalize to timezone-aware UTC period-start timestamps while preserving the original source period.
- Retry only provider results with no trusted observations and exclusively retryable failures; partial and deterministic failures stop immediately.
- Require canonical financial values to use `Decimal` and timezone-aware UTC datetimes.

### Fixed

- Removed ambiguity from FX canonical units by defining ordered base/quote semantics rather than storing a quote currency label alone.
- Improved ECOS transport observability without logging raw exception strings that could disclose endpoint or credential context.
- Corrected retry-exhaustion evidence so it is tied to the configured maximum attempt budget.
- Corrected the Yahoo smoke test so it preserves the canonical `FetchResult` invariant while validating a no-observation outcome.
- Corrected the FRED live smoke false negative caused by normal weekend or holiday gaps and date-boundary normalization.

### Security

- FX normalization makes no external calls and does not expose provider credentials or raw payloads.
- ECOS transport diagnostics classify exception types only; raw exception text, API keys, secret-bearing URLs, raw payloads, and observation values remain excluded.
- ECOS live smoke reads `ECOS_API_KEY` only from GitHub Actions secrets.
- Retry execution does not log raw provider payloads, full request URLs, credentials, or personal investment data.
- FRED credentials remain encrypted GitHub Actions secrets only.

### Validation

- FX initial implementation head `044e350e9c028eb25944463328a69905c3b1ec73`: Documentation run #103 passed; Python run #51 test job passed. Fresh final-head CI is required after living-document updates.
- ECOS Live Smoke run `31182329368` succeeded on merged `main` commit `23bd2ef88ce7ab3f3da2f288ad066089c163f2e8` with 99 trusted observations on attempt 1; this remains bounded live-success evidence.
- ECOS transport-diagnostic final head `d9bed23781defaa1b389af93fdcf454e7f5fe058`: Python run #49 and Documentation run #99 passed before merge.
- Yahoo Live Smoke run `31169043266` succeeded with 10 trusted SPY daily observations on attempt 1.
- Protected FRED live connectivity was successfully validated against the official endpoint.
- FRED, Yahoo, and ECOS each have verified successful live retrieval evidence.

### Known Limitations

- FX normalization does not implement cross-provider fallback, averaging, triangulation, fixing-time reconciliation, bid/ask spread handling, persistence, or snapshot publication.
- The Yahoo `KRW=X` convention is explicitly configured as USD/KRW; future provider FX bindings require separately verified direction semantics.
- ECOS and Yahoo live success are bounded evidence from specific runs and do not guarantee future provider availability.
- Identifier-scoped retry, `Retry-After` handling, cache, immutable snapshot integration, persistence, migration, scheduled ingestion, and dataset versioning remain future work.
- No user-owned database tables, RLS policies, or cross-user isolation tests exist.
- Frontend CI still uses `npm install` because `package-lock.json` is not committed.
- Browser-level PWA installation and offline behavior remain unverified.
- Portfolio, analysis, recommendation, and backtest capabilities are not implemented.
