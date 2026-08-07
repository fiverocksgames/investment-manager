begin;

create table if not exists public.data_observations (
    observation_id uuid primary key,
    kind text not null,
    subject_id uuid not null,
    observed_at timestamptz not null,
    value numeric not null,
    unit text not null,
    quality text not null,
    freshness text not null,
    provider text not null,
    source_identifier text not null,
    retrieved_at timestamptz not null,
    revision text,
    source_attributes jsonb not null default '{}'::jsonb,
    created_at timestamptz not null default now(),
    constraint data_observations_value_finite check (value = value),
    constraint data_observations_retrieval_order check (retrieved_at >= observed_at)
);

create table if not exists public.source_snapshots (
    snapshot_id uuid primary key,
    dataset text not null,
    provider text not null,
    cutoff_at timestamptz not null,
    published_at timestamptz not null,
    checksum text not null,
    created_at timestamptz not null default now(),
    constraint source_snapshots_checksum_sha256 check (checksum ~ '^[0-9a-f]{64}$'),
    constraint source_snapshots_publication_order check (published_at >= cutoff_at),
    constraint source_snapshots_content_identity unique (dataset, provider, cutoff_at, checksum)
);

create table if not exists public.source_snapshot_observations (
    snapshot_id uuid not null references public.source_snapshots(snapshot_id) on delete restrict,
    position integer not null check (position >= 0),
    observation_id uuid not null references public.data_observations(observation_id) on delete restrict,
    primary key (snapshot_id, position),
    unique (snapshot_id, observation_id)
);

create index if not exists data_observations_provider_subject_time_idx
    on public.data_observations(provider, subject_id, observed_at);
create index if not exists source_snapshots_dataset_provider_cutoff_idx
    on public.source_snapshots(dataset, provider, cutoff_at desc);

comment on table public.data_observations is
    'Server-managed canonical observations. Immutable identity conflicts must fail closed.';
comment on table public.source_snapshots is
    'Server-managed immutable source snapshots used as reproducible downstream analysis inputs.';
comment on table public.source_snapshot_observations is
    'Ordered immutable membership between source snapshots and canonical observations.';

alter table public.data_observations enable row level security;
alter table public.source_snapshots enable row level security;
alter table public.source_snapshot_observations enable row level security;

-- Intentionally no client-facing RLS policies are created here. These Phase 2 tables are
-- server-managed. Browser/user access remains denied until a separately reviewed policy exists.

commit;
