# Investment Policy

## Purpose

This policy constrains product behavior so that Investment Manager remains a conservative, explainable decision support system.

## Objectives

- Support disciplined long-term accumulation
- Prefer diversification, liquidity, transparency, and low complexity
- Make market and portfolio evidence understandable
- Reduce impulsive decisions through documented rules and review
- Preserve user control over all investment actions

## Eligible MVP Assets

- Broad Korean equity ETFs
- Broad U.S. equity ETFs
- Investment-grade bond ETFs
- Gold ETFs or similarly transparent gold exposure where legally and technically supported
- Unleveraged Bitcoin exposure may be analyzed only after its eligibility, data source, custody assumptions, and risk treatment are explicitly designed and approved

Eligibility does not imply recommendation. Products must pass documented liquidity, history, data quality, and structure checks.

## Excluded MVP Assets and Activities

- Individual equities
- Leveraged and inverse products
- Options, futures, swaps, and other derivatives
- Margin, short selling, and securities lending strategies
- Automated trading or order routing
- Guaranteed-return or capital-protection claims
- High-frequency, intraday, or market-timing execution systems

## Decision Hierarchy

1. Investment safety and user constraints
2. Diversification and target allocation
3. Data quality and freshness
4. Market regime and risk conditions
5. Candidate ranking factors
6. Transaction practicality and rounding

A high candidate score must not override exclusions, stale data, insufficient liquidity, or portfolio concentration limits.

## Recommendation Requirements

Every recommendation or candidate detail must show:

- Instrument name, symbol, market, and asset class
- Eligibility result and exclusion reasons
- Source and data timestamp
- Factor values and weights
- Calculation or scoring version
- Key positive evidence
- Material risks and counter-evidence
- Confidence or data-quality status
- Relevant portfolio concentration or allocation impact
- Statement that no trade is executed

## Portfolio Principles

- Rebalancing is target-allocation based, not prediction-only.
- Tolerance bands should avoid unnecessary small transactions.
- Contributions and withdrawals should be considered before recommending sales.
- Currency exposure must be visible rather than silently netted.
- Fees, taxes, spreads, and minimum transaction sizes must be marked as user-specific limitations until modeled.
- Suggestions must be expressed as scenarios or target gaps, not mandatory instructions.

## Market Regime Use

Market regime is contextual evidence, not a standalone buy or sell command.

- Risk-on may increase confidence in growth exposure within target bounds.
- Neutral should favor adherence to strategic allocation.
- Risk-off may favor caution, liquidity review, and rebalance pacing.

Regime classification must never authorize leverage, inverse exposure, or automatic liquidation.

## Scoring Governance

- Factors and weights are versioned and documented.
- Missing factors cannot be silently treated as favorable.
- Scores are comparable only within the same methodology version and eligible universe.
- Changes to factor definitions or weights require a decision record, tests, and feature matrix update.
- The system must expose the distinction between raw metrics, normalized factors, composite score, and recommendation narrative.

## Risk Disclosure

The product must communicate that:

- Market prices can fall and losses are possible.
- Historical data does not guarantee future results.
- Free data can be delayed, incomplete, revised, or unavailable.
- Currency, interest-rate, inflation, tracking-error, liquidity, and concentration risks may apply.
- The user is responsible for suitability, tax, legal, and transaction decisions.

## Prohibited Product Language

Do not use language implying:

- Guaranteed profit
- Certainty of price direction
- Risk-free investment
- Personalized fiduciary or regulated advice unless the project later establishes the required legal basis
- Urgency designed to cause impulsive trading

## Change Control

Changes to eligible assets, exclusions, risk thresholds, scoring policy, or recommendation language require:

1. Requirement IDs
2. `docs/DECISIONS.md` entry
3. Specification and feature matrix updates
4. Tests and documented validation
5. Review for security, legal, and user-harm implications
