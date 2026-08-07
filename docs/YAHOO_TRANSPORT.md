# Yahoo Transport Hardening

## Purpose

Document the minimal explicit HTTP headers used by the Yahoo chart adapter. The goal is to send a conventional, standards-compatible request without adding authentication, cookies, scraping behavior, proxying, or browser automation.

## Default Headers

The default transport sends:

- `User-Agent`: `InvestmentManager/0.1 (+https://github.com/fiverocksgames/investment-manager)`
- `Accept`: `application/json`
- `Accept-Language`: `en-US,en;q=0.9`

The adapter does not require a Yahoo account, API key, cookie, crumb token, or browser session.

## Failure and Retry Behavior

The header change does not alter provider failure classification. HTTP 429 remains explicit and retryable. The provider-independent bounded retry executor may retry a no-observation result when all failures are retryable, within its configured attempt budget.

## Boundaries

- No rotating user agents.
- No cookies or authenticated Yahoo session.
- No proxy, IP rotation, CAPTCHA bypass, or HTML scraping.
- No claim that these headers prevent rate limiting.
- No claim that Yahoo is an official or production-grade stable API.

Yahoo remains a best-effort public chart endpoint. A successful live workflow run is still required before current live retrieval success is recorded.
