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

## HTTP Request Headers

The default Yahoo transport sends a small explicit header set documented in `docs/YAHOO_TRANSPORT.md`:

- stable project-specific `User-Agent`
- `Accept: application/json`
- `Accept-Language: en-US,en;q=0.9`

No Yahoo login, API key, cookie, crumb token, browser session, proxy, or IP rotation is used. These headers do not guarantee avoidance of rate limiting.

## Retry Policy

Yahoo smoke uses the common `BoundedRetryExecutor` rather than a provider-specific retry loop.

- Maximum attempts: 3
- Exponential base delay: 5 seconds
- Maximum delay: 20 seconds
- Jitter: up to 2 seconds
- Retry only when there are no trusted observations and every failure is marked retryable
- Do not retry partial results or deterministic non-retryable failures

This policy can recover from transient HTTP 429, transport, or selected server failures when the adapter classifies them as retryable. Exhaustion remains an explicit failed smoke run and does not prove live connectivity.

## Recorded Live Evidence

- Run `31141445027`: reached Yahoo and failed safely with `HTTP_429` before bounded retry was merged.
- Run `31150601290`: bounded retry executed three attempts and exhausted safely with `HTTP_429`; `attempts=3`, `retry_exhausted=true`.

Neither run proves successful Yahoo live retrieval.

## Success Criteria

A run succeeds only when:

1. The adapter returns at least one canonical observation.
2. No fatal provider failure is present.
3. Returned observations remain within the bounded request window.
4. Canonical values and timestamps pass the adapter's existing `Decimal` and UTC normalization.

`MISSING_VALUE` and `OUT_OF_RANGE` may be reported as tolerated row-level warnings only when at least one valid observation is also present.

## Safe Failure Behavior

The smoke test fails for conditions including:

- HTTP 429 after bounded retry exhaustion
- Other retryable failures after exhaustion
- Non-retryable HTTP failures
- Yahoo error responses
- Payload or schema changes
- Invalid observation data
- No-observation results
- Any unexpected failure classification

## Logging and Privacy

The workflow prints only bounded summary metadata:

- provider
- symbol
- attempt count
- retry exhaustion state on failure
- observation count
- first and last observation timestamps
- currency
- interval
- classified warning or failure codes

It does not print raw payloads, complete request URLs, credentials, cookies, personal investment data, or canonical observation values.

## Operational Boundary

Yahoo is treated as a best-effort public chart endpoint. Controlled live validation is required before recording current connectivity. A fallback provider strategy, provider health model, cache, persistence, and scheduled ingestion remain future work.
