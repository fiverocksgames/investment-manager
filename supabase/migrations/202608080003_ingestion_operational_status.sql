begin;

create table if not exists public.ingestion_runs (
    run_id uuid primary key,
    provider text not null,
    dataset text not null,
    started_at timestamptz not null,
    ended_at timestamptz not null,
    status text not null check (status in ('succeeded', 'partial', 'failed')),
    attempt integer not null check (attempt >= 1),
    provider_attempts integer not null check (provider_attempts >= 0),
    records_received integer not null check (records_received >= 0),
    records_accepted integer not null check (records_accepted >= 0 and records_accepted <= records_received),
    cache_hit boolean not null default false,
    snapshot_id uuid references public.source_snapshots(snapshot_id) on delete restrict,
    created_at timestamptz not null default now(),
    constraint ingestion_runs_time_order check (ended_at >= started_at)
);

create table if not exists public.ingestion_failures (
    run_id uuid not null references public.ingestion_runs(run_id) on delete restrict,
    position integer not null check (position >= 0),
    code text not null,
    message text not null,
    retryable boolean not null,
    occurred_at timestamptz not null,
    provider_reference text,
    primary key (run_id, position)
);

create index if not exists ingestion_runs_provider_dataset_started_idx
    on public.ingestion_runs(provider, dataset, started_at desc);
create index if not exists ingestion_failures_code_occurred_idx
    on public.ingestion_failures(code, occurred_at desc);

comment on table public.ingestion_runs is
    'Server-managed terminal ingestion operational evidence; no secrets or raw payloads.';
comment on table public.ingestion_failures is
    'Ordered sanitized failure evidence for a terminal ingestion run.';

alter table public.ingestion_runs enable row level security;
alter table public.ingestion_failures enable row level security;

-- Intentionally no browser/client RLS policies. Scheduled ingestion writes through
-- a protected server-side PostgreSQL connection only.

commit;
