# Investment Manager

Investment Manager is a personal investment decision-support system for conservative, long-term investors. It explains market conditions, identifies ETF candidates, analyzes portfolio allocation, and provides reviewable rebalancing guidance.

> This project does not perform automated trading and does not provide guaranteed returns or individualized fiduciary advice.

## Status

Phase 1 infrastructure is implemented in this fork and is being prepared for a one-time synchronization to `e20cboy/investment-manager`.

Implemented baseline:

- React, TypeScript, and Vite application shell
- Tailwind CSS styling
- PWA registration and manifest generation
- GitHub Pages build and deployment workflow
- Supabase browser client and authentication context
- Google sign-in and sign-out actions
- GitHub Actions repository Variables wiring for Supabase public configuration

External configuration and browser-level validation are still pending.

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

- [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md)
- [`AGENTS.md`](AGENTS.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)
- [`ROADMAP.md`](ROADMAP.md)
- [`WORKLOG.md`](WORKLOG.md)
- [`AI_HANDOFF.md`](AI_HANDOFF.md)
- [`CHANGELOG.md`](CHANGELOG.md)

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
- [`docs/INVESTMENT_POLICY.md`](docs/INVESTMENT_POLICY.md)
- [`docs/TEST_PLAN.md`](docs/TEST_PLAN.md)
- [`docs/DECISIONS.md`](docs/DECISIONS.md)
- [`docs/SUPABASE_SETUP.md`](docs/SUPABASE_SETUP.md)

## Requirement Traceability

Every product requirement receives a stable ID. The path from planning through design, data, API, UI, tests, and PR evidence is tracked in `docs/FEATURE_MATRIX.md`.

## Development Process

`Issue → Design → Documentation → Implementation → Test → Pull Request`

A feature is not complete when documentation, worklog, handoff, tests, or traceability evidence is missing.

## Running and Testing

```text
npm install
npm run dev
npm run build
```

`npm install` and `npm run build` have been verified in GitHub Actions. Browser-level PWA and OAuth validation remain pending.

## Security

Only `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` may be provided to the frontend. Never commit a Supabase service-role key, Google client secret, database password, JWT secret, or personal portfolio data.

## License

MIT License. See [`LICENSE`](LICENSE).
