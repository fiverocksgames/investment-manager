# AI Handoff

## Current State

Phase 1 infrastructure is complete. Phase 2 Data Platform design was merged in PR #16. Issue #17 is implementing the first executable Python foundation.

## Repository and Active Work

- Canonical repository: `fiverocksgames/investment-manager`
- Default branch: `main`
- Active branch: `agent/canonical-data-provider`
- Issue: #17 — `feat: implement canonical data model and provider abstraction`
- PR: not yet created

## Implemented on the Active Branch

- Python 3.12 package baseline in `pyproject.toml`.
- Canonical immutable domain models in `investment_manager/data/models.py`.
- Provider request, result, capability, and protocol contracts in `investment_manager/data/providers.py`.
- Standard-library unit tests in `tests/`.
- Python GitHub Actions workflow in `.github/workflows/python.yml`.

## Domain Rules Enforced

- Investment-relevant numeric observations use `Decimal`.
- Datetimes must be timezone-aware and are normalized to UTC.
- Provider metadata is preserved and immutable.
- Invalid or unavailable values cannot be represented as trusted observations.
- Terminal ingestion runs require an end time.
- Source snapshots require unique observation IDs and coherent timestamps.
- Provider results explicitly distinguish success, partial success, and failure.

## Validation

Pending Draft PR execution:

```text
python -m compileall -q investment_manager tests
python -m unittest discover -s tests -v
```

Documentation CI and Python CI must both pass before Ready for Review.

## Known Limitations

- No Yahoo Finance, FRED, ECOS, or FX adapter exists.
- No network calls, credentials, database migration, persistence, cache implementation, retry executor, or scheduled ingestion exists.
- No analysis, portfolio, or recommendation logic exists.
- Provider access methods, identifiers, terms, and rate limits require verification during each adapter Issue.
- PWA install/offline validation, user tables, RLS, and cross-user isolation remain pending.

## Development Rules

1. Follow `PROJECT_POLICY.md` and `AGENTS.md`.
2. Keep provider payloads behind adapters.
3. Preserve Requirement IDs and update `docs/FEATURE_MATRIX.md`.
4. Never use binary floating point for canonical financial values.
5. Never commit secrets, tokens, or personal portfolio data.
6. Do not claim tests passed until GitHub Actions completes.
7. Never merge without explicit user approval.

## Exact Next Recommended Task

Complete Issue #17 by updating living documents, creating a Draft PR, and passing Python and Documentation CI. After merge, implement one provider adapter in a focused Issue, beginning with a current-source verification of access method, terms, identifiers, and rate limits.
