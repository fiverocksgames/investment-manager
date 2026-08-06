# Decision Log

Material technical, product, data, and investment-policy choices are recorded here. Decisions are append-only; superseded decisions remain for history.

## Template

### DEC-XXX — Title

- Status: Proposed | Accepted | Superseded | Rejected
- Date: YYYY-MM-DD
- Requirement IDs:
- Context:
- Decision:
- Alternatives:
- Consequences:
- Follow-up:

## DEC-001 — Use React, TypeScript, and Vite

- Status: Accepted
- Date: 2026-08-05
- Requirement IDs: GOV-BOOT-001
- Context: The project needs a maintainable static web frontend with strong typing and broad contributor familiarity.
- Decision: Use React with TypeScript and Vite.
- Alternatives: Next.js, Vue, Svelte, server-rendered frameworks.
- Consequences: Fast static builds and simple GitHub Pages hosting; backend capabilities must be provided separately.
- Follow-up: Define frontend structure during Phase 1.

## DEC-002 — Host the frontend on GitHub Pages

- Status: Accepted
- Date: 2026-08-05
- Requirement IDs: GOV-BOOT-001
- Context: MVP requires low-cost public static hosting integrated with repository workflows.
- Decision: Use GitHub Pages for the frontend.
- Alternatives: Vercel, Netlify, Cloudflare Pages, custom hosting.
- Consequences: Static hosting is simple and free; routing and secret handling must respect a public client environment.
- Follow-up: Document deployment workflow and base-path behavior.

## DEC-003 — Use Supabase for database and authentication

- Status: Accepted
- Date: 2026-08-05
- Requirement IDs: REQ-AUTH-001, GOV-BOOT-001
- Context: MVP needs PostgreSQL persistence and managed Google authentication with minimal infrastructure.
- Decision: Use Supabase PostgreSQL and Supabase Auth.
- Alternatives: Firebase, custom backend, Auth0 plus managed PostgreSQL.
- Consequences: Row Level Security becomes mandatory; service-role secrets must remain server-side or in GitHub Actions.
- Follow-up: Define schemas and policies before implementation.

## DEC-004 — Use Google Sheets as the initial portfolio source

- Status: Accepted
- Date: 2026-08-05
- Requirement IDs: REQ-PORT-001
- Context: Users need a familiar, editable source for holdings without brokerage integration.
- Decision: Import portfolio data from a documented Google Sheets format.
- Alternatives: Manual form entry, CSV only, brokerage APIs.
- Consequences: Input validation, permission handling, and schema guidance are required; automatic trade synchronization is excluded.
- Follow-up: Define the sheet contract and import error model.

## DEC-005 — Use free data providers through adapters

- Status: Accepted
- Date: 2026-08-05
- Requirement IDs: REQ-MKT-001
- Context: The project is intended to operate with no paid market-data dependency during MVP.
- Decision: Use Yahoo Finance, FRED, and ECOS through provider-specific adapters and normalized schemas.
- Alternatives: Paid institutional feeds, direct exchange data, single-provider coupling.
- Consequences: Availability and terms may change; freshness checks, caching, retries, and explicit limitations are required.
- Follow-up: Validate each provider's current terms and identifiers before implementation.

## DEC-006 — Keep financial calculations out of the UI

- Status: Accepted
- Date: 2026-08-05
- Requirement IDs: REQ-SIG-001, REQ-PORT-001
- Context: Duplicated formulas create inconsistent results and are difficult to audit.
- Decision: Analysis and portfolio engines own calculations; the UI only presents versioned results and explanations.
- Alternatives: Client-side calculations, duplicated shared formulas.
- Consequences: Outputs require stable contracts and timestamps; frontend remains simpler and safer.
- Follow-up: Define engine interfaces in API and architecture specifications.

## DEC-007 — Treat documentation review as equal to code review

- Status: Accepted
- Date: 2026-08-05
- Requirement IDs: GOV-DOC-001
- Context: Long-term continuity depends on repository knowledge rather than conversation memory.
- Decision: A functional PR without corresponding documentation is not complete.
- Alternatives: Retrospective documentation, code-only Definition of Done.
- Consequences: PRs may take longer but remain auditable and transferable.
- Follow-up: Enforce the policy through PR templates and documentation validation.

## DEC-008 — Use the MIT License

- Status: Accepted
- Date: 2026-08-05
- Requirement IDs: GOV-BOOT-001
- Context: The project is intended to be easy to inspect, reuse, modify, and extend while retaining a clear warranty disclaimer.
- Decision: License the repository under the MIT License.
- Alternatives: Apache License 2.0, GPL family licenses, no explicit license.
- Consequences: Broad reuse is permitted with preservation of the copyright and license notice.
- Follow-up: Revisit only through a documented legal and governance decision.

## DEC-009 — Use a provider-independent canonical observation model

- Status: Accepted
- Date: 2026-08-06
- Requirement IDs: REQ-DATA-001, REQ-PROVIDER-001
- Context: Yahoo Finance, FRED, ECOS, and FX sources use incompatible identifiers, timestamps, units, revisions, and error models.
- Decision: Isolate provider formats behind adapters and normalize all accepted records into canonical assets, series, observations, ingestion runs, failures, and source snapshots defined in `docs/DATA_MODEL.md`.
- Alternatives: Persist provider payloads directly, create provider-specific downstream models, or normalize in the UI.
- Consequences: Initial adapter work is larger, but analysis and UI remain provider-independent and auditable.
- Follow-up: Implement typed Python domain models and adapter contracts before provider-specific code.

## DEC-010 — Publish immutable source snapshots

- Status: Accepted
- Date: 2026-08-06
- Requirement IDs: REQ-DATA-002, REQ-OPS-002
- Context: Downstream analysis must know exactly which coherent data inputs, cutoff, revisions, and quality states were used.
- Decision: Successful ingestion publishes an immutable source snapshot. Failed runs never publish a successful snapshot, and prior good data keeps its original timestamps.
- Alternatives: Read mutable latest rows directly or treat ingestion completion time as the only cutoff.
- Consequences: Additional metadata and transactional publication are required, but reproducibility and failure safety improve.
- Follow-up: Add database constraints and integration tests for snapshot publication.

## DEC-011 — Use policy-driven freshness, cache, and retries

- Status: Accepted
- Date: 2026-08-06
- Requirement IDs: REQ-DATA-002, REQ-PROVIDER-002, REQ-OPS-002
- Context: Market, FX, and macro datasets have different calendars, publication delays, revision behavior, and rate limits.
- Decision: Define versioned dataset policies containing cadence, stale thresholds, partial-data rules, cache behavior, and bounded retry behavior.
- Alternatives: Apply one global TTL and retry count or let each adapter make undocumented choices.
- Consequences: Policies require maintenance, but stale and degraded states become consistent and testable.
- Follow-up: Approve initial policies with each provider implementation PR.
