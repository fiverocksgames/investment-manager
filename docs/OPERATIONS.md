# Operations Specification

## Purpose

Define how Investment Manager is built, deployed, scheduled, monitored, recovered, and handed over between maintainers.

## Environments

Use separate local, preview, and production configurations. Production data and credentials must not be used in local development. Environment-specific values must be documented without exposing secrets.

## Deployment

The React PWA is built by GitHub Actions and deployed to GitHub Pages. Deployments must be reproducible from a tagged or identified commit. Build failures block deployment. Rollback uses a previously verified artifact or commit.

## Scheduled Jobs

Python jobs may collect market prices, economic indicators, and exchange rates and may run analysis after successful ingestion. Jobs must be idempotent, use explicit data cutoffs, enforce timeouts and retry limits, and avoid overlapping runs for the same dataset.

## Observability

Record job identifier, commit, model version, start and end times, status, row counts, source status, data cutoff, warnings, and error category. Logs must not contain credentials or sensitive portfolio values unless explicitly required and protected.

## Data Freshness

Each dataset requires an expected cadence and stale threshold. The UI and API must display degraded or stale states instead of silently presenting old results as current.

## Failure Handling

Provider outages must not corrupt prior good data. Partial failures are recorded by source and dataset. Repeated failures should disable unsafe retries and surface an operational alert. Analysis must not run when required inputs fail validation.

## Backup and Recovery

Database backup, restore, and recovery-point expectations must be defined before production. Portfolio snapshots and policy versions require durable recovery. Recovery exercises must be documented.

## Change Management

Every production-affecting change requires an Issue, Requirement IDs, documentation, validation evidence, and a PR. Database migrations and workflow-permission changes require focused review.

## Runbooks

Future runbooks must cover failed deployment, failed ingestion, stale data, authentication outage, database recovery, credential rotation, and provider schema change.

## Service Objectives

Initial service objectives are informational until usage is established. The project prioritizes correctness, data freshness transparency, and recoverability over high availability or low latency.
