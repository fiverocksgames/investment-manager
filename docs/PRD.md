# Product Requirements Document

## Product

Investment Manager is a personal investment decision support system for conservative long-term investors. It summarizes market conditions, screens ETF candidates, and explains portfolio allocation gaps without executing transactions.

## Problem

Individual investors often combine fragmented price data, macro indicators, spreadsheets, and subjective commentary. This makes decisions inconsistent, difficult to reproduce, and vulnerable to stale data or hidden assumptions.

## Product Outcome

The product should help a user answer:

1. What is the current market regime, based on timestamped evidence?
2. Which eligible Korean or U.S. ETFs merit further review, and why?
3. How does the current portfolio differ from the target allocation?
4. What conservative rebalancing actions could close the gap?
5. What risks, assumptions, missing data, and uncertainty affect the result?

## Users

### Primary User

A self-directed long-term investor who prefers diversified ETFs and periodic decisions over frequent trading.

### Contributor

A human or AI developer who must understand and extend the project using repository documentation alone.

## MVP User Journeys

### Sign In

- User signs in with Google through Supabase Auth.
- User sees authentication errors without exposing sensitive details.
- User data remains isolated from other users.

Requirement: `REQ-AUTH-001`.

### Review Market Conditions

- User sees a risk-on, neutral, or risk-off classification.
- User sees the source and timestamp of underlying data.
- User can inspect supporting indicators and limitations.

Requirements: `REQ-MKT-001`, `REQ-MKT-002`, `REQ-SIG-001`, `REQ-SIG-002`, `REQ-SIG-003`.

### Review ETF Candidates

- User sees only eligible Korean and U.S. ETFs.
- Candidates are ranked using documented factors and weights.
- Each candidate shows evidence, risks, exclusions, confidence, and freshness.

Requirements: `REQ-REC-001`, `REQ-REC-002`, `REQ-REC-003`.

### Review Portfolio

- User imports holdings from a documented Google Sheets structure.
- Invalid data is rejected or isolated with actionable errors.
- Holdings are normalized and classified.
- Actual and target allocations are compared.

Requirements: `REQ-PORT-001`, `REQ-PORT-002`.

### Review Rebalancing Suggestions

- User receives suggested allocation adjustments, not orders.
- Suggestions show calculation basis, tolerance, rounding, and limitations.
- No brokerage action is performed.

Requirement: `REQ-PORT-003`.

## Functional Requirements

### Market and Data

- Support price, macroeconomic, and FX datasets from documented free sources.
- Store or expose observation time, retrieval time, source, and freshness.
- Mark stale, incomplete, or failed inputs explicitly.

### Analysis

- Calculate indicators deterministically in the Analysis Engine.
- Version formulas and parameters.
- Return sufficient evidence to reproduce the classification.

### Portfolio

- Define a stable sheet contract.
- Normalize symbols, currencies, quantities, prices, and classifications.
- Keep imported user data private.

### Recommendation

- Apply eligibility rules before ranking.
- Expose factor values and weights.
- Avoid personalized claims of suitability or guaranteed performance.

## Non-Functional Requirements

- Responsive PWA usable on mobile and desktop
- Accessible navigation and readable financial displays
- Graceful behavior for stale or unavailable data
- Reproducible calculations and deterministic tests
- Secure secret handling and Row Level Security
- Low-cost operation using GitHub Pages, Actions, and Supabase
- Repository-first documentation and AI handoff

## Out of Scope

- Automated or assisted order execution
- Brokerage account credentials
- Individual stocks
- Leverage, inverse, derivatives, margin, and short selling
- High-frequency or real-time trading
- Backtesting in MVP
- News and filing analysis in MVP
- Multi-user collaboration and OTP in MVP

## Product Safety

- Display educational and decision-support framing.
- Always show data timestamps and material limitations.
- Do not hide unfavorable factors.
- Do not present a score as certainty.
- Require user review before any external action.

## MVP Acceptance Summary

The MVP is acceptable when authenticated users can view timestamped market analysis, inspect explainable ETF candidates, import a valid portfolio sheet, compare target allocations, and view non-executing rebalancing suggestions with documented risks and tests.
