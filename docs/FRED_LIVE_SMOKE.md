# FRED Live Smoke Test

## Purpose

This workflow validates the merged FRED adapter against the official live FRED Version 1 observations endpoint without placing credentials in source code, repository Variables, logs, artifacts, pull requests, or the frontend.

## Credential

Create a repository Actions secret named `FRED_API_KEY`.

The value must be the registered 32-character lowercase alphanumeric FRED API key. Do not paste the value into an Issue, pull request, commit, workflow input, Variable, screenshot, or chat message.

## Setup

1. Open repository **Settings**.
2. Open **Secrets and variables → Actions**.
3. Select **New repository secret**.
4. Enter the name `FRED_API_KEY`.
5. Paste the registered FRED API key as the secret value.
6. Save the secret.

## Execution

The workflow is intentionally manual and is never triggered by a pull request, push, or schedule.

1. Open the repository **Actions** tab.
2. Select **FRED Live Smoke**.
3. Select **Run workflow**.
4. Run it from `main`.

## Validation Contract

The smoke test:

- uses the merged `FredProvider`;
- queries `DGS10` over a bounded recent 45-day range;
- sends the key only through the encrypted `FRED_API_KEY` environment value;
- reports provider, series, observation count, first and last observation dates, quality, and freshness;
- does not print the API key or raw request URL;
- requires at least one valid canonical observation;
- tolerates only `MISSING_VALUE` and `OUT_OF_RANGE` warnings when valid observations also exist;
- reports tolerated warning codes without raw provider payloads;
- fails for missing credentials, empty results, authentication, HTTP, transport, binding, payload, and parsing errors.

`DGS10` legitimately contains missing values for weekends and market holidays. The date-only provider endpoint can also return a boundary date outside an exact timestamp window. These conditions are warnings rather than proof of failed connectivity when valid observations are present.

A successful run proves connectivity and compatibility for this bounded request. It does not prove all FRED series, historical revisions, rate limits, persistence, scheduling, or production readiness.

## Evidence

The first live run, Actions run `31078092784`, authenticated and reached FRED but exposed a false-negative smoke policy: valid data was accompanied by expected `MISSING_VALUE` and `OUT_OF_RANGE` warnings. Issue #23 corrects that policy without weakening fatal error handling.

## Rotation and Removal

Replace the repository secret when rotating the FRED key. Delete the secret when live validation is no longer required. No code change is needed for either action.

## Security Rules

- Never use a repository Variable for the FRED key.
- Never expose the secret to frontend builds.
- Never echo the secret or a URL containing it.
- Never upload raw live responses as artifacts.
- Keep live execution manual until rate limits, scheduling, and operational ownership are separately approved.
