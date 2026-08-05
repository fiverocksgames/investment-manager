# Security

## Objectives

Protect account identity, portfolio information, application configuration, and service credentials. Enforce user isolation and preserve auditable records for sensitive changes.

## Authentication and access

Supabase Auth with Google Login is the initial sign-in method. Authorization must be enforced by database policy or trusted server-side logic, not only by the user interface. User-owned tables require Row Level Security with default-deny rules and tests proving cross-user isolation.

The frontend restores the current Supabase session and subscribes to authentication-state changes. Missing public configuration must produce a visible configuration state rather than a crash. OAuth end-to-end success is not established until a real Supabase project and Google provider are configured and tested.

## Credential handling

Credentials and tokens must not be committed to the repository. Development, CI, and production values must use approved environment or platform secret storage. Application logs and error responses must avoid exposing sensitive values.

The frontend may receive only the Supabase project URL and browser-safe publishable or anon key through `VITE_` variables. Supabase service-role keys, database passwords, and Google OAuth client secrets must never be exposed to Vite or committed. Setup and validation steps are documented in `docs/SUPABASE_SETUP.md`.

## Client and API controls

Only browser-safe configuration may be included in the frontend. Inputs require validation, redirects require allow-listing, and error responses must avoid internal details. Public and privileged operations must have clearly separated permissions.

Authentication establishes identity but does not by itself authorize access to portfolio or analysis data. Every user-owned table requires Row Level Security before frontend access is enabled.

## Financial data

Portfolio data is sensitive. Collect only necessary fields, encrypt network traffic, restrict access by owner, and define export and deletion behavior before production use.

## External services

Google integrations should request the minimum scope needed. Market and economic provider responses are untrusted inputs and require schema checks, timeouts, retry limits, and size limits. GitHub Actions workflows must use minimal repository permissions.

## Dependencies

Use lockfiles, automated dependency review, vulnerability scanning, and reviewed updates. Production workflows should pin third-party actions to stable immutable versions where practical.

## AI boundary

Generated commentary cannot change calculations, policy constraints, authorization rules, migrations, or executable behavior without human review and tests. External text must never be treated as trusted instructions.

## Incident handling

An incident process must cover containment, access revocation, credential replacement, impact assessment, evidence preservation, recovery, communication, and documented corrective actions.

## Production gate

Production requires passing user-isolation tests, credential scanning, authentication tests, dependency review, safe logging checks, backup readiness, and documentation of unresolved risks.
