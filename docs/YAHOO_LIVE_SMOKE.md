# Yahoo Live Smoke Validation

## Purpose

The Yahoo Live Smoke workflow performs a controlled, manually triggered request through the canonical `YahooProvider` adapter. It checks that the best-effort public Yahoo chart endpoint still returns a payload that the adapter can normalize into at least one valid daily canonical observation.

This is operational evidence of a bounded live call. It is not a guarantee of production availability, official API support, schema stability, or uninterrupted long-term service.

## Execution

- Workflow: `.github/workflows/yahoo-smoke.yml`
- Trigger: manual `workflow_dispatch`
- Python entry point: `tools/yahoo_smoke.py`
- Representative symbol: `SPY`
- Dataset: `market_prices`
- Interval: daily
- Request window: most recent 14 days
- Secret requirement: none

The workflow is intentionally manual to avoid unnecessary polling of an undocumented public endpoint.

## Success Criteria

A run succeeds only when:

1. The adapter returns at least one canonical observation.
2. No fatal provider failure is present.
3. Returned observations remain within the bounded request window.
4. Canonical values and timestamps pass the adapter's existing `Decimal` and UTC normalization.

`MISSING_VALUE` and `OUT_OF_RANGE` may be reported as tolerated row-level warnings only when at least one valid observation is also present.

## Safe Failure Behavior

The smoke test fails for conditions including:

- HTTP 429 rate limiting
- Other HTTP failures
- Network or timeout errors
- Yahoo error responses
- Payload or schema changes
- Invalid observation data
- Empty results
- Any unexpected failure classification

The workflow does not retry automatically. Retry policy belongs to a future bounded retry executor rather than this connectivity check.

## Logging and Privacy

The workflow prints only bounded summary metadata:

- provider
- symbol
- observation count
- first and last observation timestamps
- currency
- interval
- classified warning or failure codes

It does not print raw payloads, complete request URLs, credentials, cookies, personal investment data, or canonical observation values.

## Operational Boundary

Yahoo is treated as a best-effort public chart endpoint. Controlled live validation is required before recording current connectivity. A fallback provider strategy, provider health model, cache, retry executor, persistence, and scheduled ingestion remain future work.
