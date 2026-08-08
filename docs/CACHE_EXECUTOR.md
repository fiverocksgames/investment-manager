# Cache Executor

## Purpose

`CacheExecutor` is a provider-independent process-local cache for canonical `FetchResult` values. It reduces repeated provider calls inside an explicit dataset TTL without changing the canonical observations returned by the provider.

## Cache Key

An entry is isolated by the full request boundary:

- provider name;
- dataset;
- ordered source identifiers;
- UTC-normalized request start;
- UTC-normalized request end.

A result for one provider, symbol set, dataset, or time range must never satisfy a different request.

## TTL

The executor uses `DatasetPolicy.cache_ttl`. Cache insertion time and expiry time are execution metadata only. They are not provider provenance and are not written into `Observation` or `ProviderMetadata`.

A cache hit is permitted only while `now < expires_at`. At the exact expiry boundary the entry is discarded and the provider is called again.

## Provenance and Freshness

A cache hit returns the stored canonical `FetchResult` unchanged. The executor must not rewrite:

- `observation_id`;
- `observed_at`;
- `value`;
- quality;
- freshness;
- provider name;
- source identifier;
- `retrieved_at`;
- revision;
- source attributes.

**Cache age is not source freshness.** A recent cache hit can still contain an aging or stale observation, and downstream policy must evaluate the canonical observation timestamps rather than treating cache reuse as new retrieval evidence.

## What Is Cached

Only fully successful `FetchResult` values (`observations` present and no failures) are cached.

The following are not cached:

- partial results;
- provider failures;
- transport failures;
- authentication failures;
- empty-invalid results (already rejected by `FetchResult`).

This prevents an intermittent or partial provider outcome from being reused as if it were a trusted complete result.

## Expiry and Failure

Expired entries are removed before the provider call. If the provider then fails, the failure is returned directly. This milestone does **not** enable stale-on-error fallback because doing so could hide provider failure and misrepresent the current operational state.

A future stale fallback, if ever added, requires an explicit policy, separate result status, and visible stale provenance.

## Scope and Limitations

This milestone implements an in-memory/process-local executor only. It does not include:

- Redis or distributed caching;
- persistent cache storage;
- cache warming;
- background refresh;
- stale-while-revalidate;
- stale-on-error fallback;
- provider fallback;
- cross-process invalidation;
- scheduler integration.

The API is intentionally bounded so a future cache backend can change without changing the canonical provider or observation contracts.
