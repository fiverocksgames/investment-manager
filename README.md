# Investment Manager

Investment Manager is a personal investment decision-support system for conservative, long-term investors. It is designed to explain market conditions, identify ETF candidates, analyze portfolio allocation, and provide reviewable rebalancing guidance.

> This project does not perform automated trading and does not provide guaranteed returns or individualized fiduciary advice.

## Status

Phase 0 — Foundation. Project governance and product specifications are being reviewed in Draft PR #1. No runnable application exists yet.

## MVP Scope

- Korean and US ETF-focused market monitoring.
- Economic and exchange-rate data ingestion using approved free sources.
- Deterministic indicators and market-regime analysis.
- Google Sheets portfolio import.
- Allocation, concentration, drift, and snapshot analysis.
- Explainable rebalance guidance subject to an approved investment policy.
- Supabase authentication and user-data isolation.
- React, TypeScript, Vite, PWA, TailwindCSS, Python, GitHub Actions, GitHub Pages, and Supabase PostgreSQL.

## Excluded from MVP

Automated order execution, individual-stock recommendations, leverage, inverse products, derivatives, margin, short selling, production backtesting, news analysis, multi-user collaboration, and OTP are outside the initial scope unless separately approved and documented.

## Investment Philosophy

The project prioritizes capital preservation, diversification, ETF-based exposure, long holding periods, explainability, data freshness, and gradual rebalancing. See [`docs/INVESTMENT_POLICY.md`](docs/INVESTMENT_POLICY.md).

## Documentation Map

### Governance

- [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) — goals, scope, success criteria, Definition of Done, risks, and roadmap.
- [`AGENTS.md`](AGENTS.md) — mandatory rules for AI and human contributors.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution and PR process.
- [`ROADMAP.md`](ROADMAP.md) — phased delivery plan.
- [`WORKLOG.md`](WORKLOG.md) — current work, incomplete items, next steps, and cautions.
- [`AI_HANDOFF.md`](AI_HANDOFF.md) — exact continuation context for the next contributor.
- [`CHANGELOG.md`](CHANGELOG.md) — notable project changes.

### Product and engineering

- [`docs/PRD.md`](docs/PRD.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/FEATURE_MATRIX.md`](docs/FEATURE_MATRIX.md)
- [`docs/ANALYSIS_SPEC.md`](docs/ANALYSIS_SPEC.md)
- [`docs/PORTFOLIO_SPEC.md`](docs/PORTFOLIO_SPEC.md)
- [`docs/DATABASE.md`](docs/DATABASE.md)
- [`docs/API_SPEC.md`](docs/API_SPEC.md)
- [`docs/SECURITY.md`](docs/SECURITY.md)
- [`docs/OPERATIONS.md`](docs/OPERATIONS.md)
- [`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md)
- [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md)
- [`docs/DECISIONS.md`](docs/DECISIONS.md)

## Requirement Traceability

Every product requirement receives a stable ID such as `REQ-MKT-001`, `REQ-SIG-001`, `REQ-PORT-001`, or `REQ-AUTH-001`. The path from requirement through design, database, API, UI, tests, and PR evidence is tracked in `docs/FEATURE_MATRIX.md`.

## Development Process

Work follows:

`Issue → Design → Documentation → Implementation → Test → Pull Request`

A feature is not complete when its documentation, worklog, handoff, tests, or traceability evidence is missing.

## Running and Testing

There is no runnable application or automated test suite yet. Do not invent setup commands. Phase 1 will add the frontend, development environment, CI, and verified run instructions.

## Contributing

Read `PROJECT_CHARTER.md`, `AGENTS.md`, `CONTRIBUTING.md`, `WORKLOG.md`, and `AI_HANDOFF.md` before making changes. Never commit credentials, personal portfolio data, or undocumented investment logic.

## License

No license has been selected yet. Until a license is added, normal copyright restrictions apply even though the repository is public.
