# Project Charter

## Project Goal

Investment Manager is a personal investment decision support system (DSS). It helps users understand market conditions, identify conservative ETF candidates, and review portfolio rebalancing decisions. It does not place trades or provide guaranteed-return advice.

## Investment Philosophy

- Conservative, long-term accumulation
- Diversification before concentration
- Evidence-based decisions using reproducible data
- ETF-first implementation for Korean and U.S. markets
- Explicit uncertainty, risk, and data limitations

## MVP Scope

- Market regime summary using price and macroeconomic data
- Korean and U.S. ETF candidate screening
- Portfolio import from Google Sheets
- Target allocation comparison and rebalancing suggestions
- Explainable scores, assumptions, risks, and data timestamps
- Supabase authentication with Google login
- React, TypeScript, Vite, PWA, TailwindCSS frontend
- Python data and analysis jobs operated through GitHub Actions
- GitHub Pages hosting and Supabase PostgreSQL persistence

## Excluded from MVP

- Automated trading or brokerage order execution
- Individual stock recommendations
- Leverage and inverse products
- Derivatives, margin, and short selling
- Real-time high-frequency data
- AI-generated decisions without deterministic evidence
- Backtesting, news analysis, filings analysis, multi-user collaboration, and OTP

## Success Criteria

1. A user can sign in and view the latest data timestamp and market regime.
2. ETF candidates include explainable scores, supporting metrics, and risks.
3. A Google Sheets portfolio can be normalized and compared with a target allocation.
4. Rebalancing suggestions never execute trades and disclose assumptions.
5. Every released feature is traceable from requirement through test and PR.
6. Scheduled data jobs fail safely and expose stale or missing data.

## Quality Standards

- Deterministic calculations are implemented outside the UI.
- Financial calculations have unit tests and documented formulas.
- External data includes source, retrieval time, frequency, and limitations.
- Secrets and credentials are never committed.
- Accessibility, responsive behavior, and offline-safe PWA behavior are reviewed.
- Documentation changes are required for behavioral changes.

## Definition of Done

A requirement is done only when:

- It has a stable Requirement ID.
- Design and architecture impacts are documented.
- Data, database, API, and UI impacts are addressed or marked not applicable.
- Automated tests and manual validation are recorded.
- Security and privacy effects are reviewed.
- `FEATURE_MATRIX.md`, `WORKLOG.md`, and `AI_HANDOFF.md` are updated.
- A PR contains Summary, Requirement IDs, Validation, Test, Documentation, Known Limitations, and Next Steps.
- Known limitations and follow-up work are explicit.

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Free data outages or schema changes | Stale or missing analysis | Provider adapters, caching, freshness checks, fallback status |
| Survivorship or look-ahead bias | Misleading results | Point-in-time rules, documented methodology, test fixtures |
| Investment advice interpretation | User harm or regulatory exposure | DSS framing, risk disclosure, no trade execution, explainability |
| Secret leakage | Account or data compromise | Environment secrets, scanning, least privilege, rotation |
| Scope expansion | Delayed MVP | Feature matrix, phase gates, explicit excluded scope |
| AI handoff drift | Inconsistent implementation | AGENTS.md, decisions, worklog, handoff, traceability |

## Roadmap

- Phase 0 — Foundation: governance, documentation, CI, templates
- Phase 1 — Infrastructure: frontend, PWA, Pages, Supabase, configuration
- Phase 2 — Data Platform: market, macro, FX, normalization, caching
- Phase 3 — Analysis Engine: RSI, MACD, moving averages, regime, momentum, volatility
- Phase 4 — Portfolio Engine: holdings, targets, snapshots, performance, rebalancing
- Phase 5 — Recommendation Engine: ETF screening, scoring, explanations, risks
- Phase 6 — Notification and Automation: scheduled reports and Telegram
- Phase 7 — Advanced: backtesting, news, filings, multi-user, OTP

## Governance Requirements

- `GOV-BOOT-001`: Establish project governance and required documentation.
- `GOV-TRACE-001`: Maintain end-to-end requirement traceability.
- `GOV-AI-001`: Preserve implementation context for future AI and human contributors.
- `GOV-DOC-001`: Treat documentation review as equal to code review.

## Change Control

Changes to scope, investment philosophy, data policy, or Definition of Done require an entry in `docs/DECISIONS.md` and corresponding updates to the roadmap and feature matrix.
