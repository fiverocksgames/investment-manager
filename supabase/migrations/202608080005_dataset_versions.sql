begin;

create table if not exists public.dataset_versions (
    version_id uuid primary key,
    dataset text not null,
    as_of timestamptz not null,
    created_at timestamptz not null,
    checksum text not null,
    constraint dataset_versions_time_order check (created_at >= as_of),
    constraint dataset_versions_checksum_shape check (checksum ~ '^[0-9a-f]{64}$')
);

create table if not exists public.dataset_version_snapshots (
    version_id uuid not null references public.dataset_versions(version_id) on delete restrict,
    position integer not null check (position >= 0),
    snapshot_id uuid not null references public.source_snapshots(snapshot_id) on delete restrict,
    primary key (version_id, position),
    unique (version_id, snapshot_id)
);

create index if not exists dataset_versions_dataset_as_of_idx
    on public.dataset_versions(dataset, as_of desc);
create index if not exists dataset_version_snapshots_snapshot_idx
    on public.dataset_version_snapshots(snapshot_id);

comment on table public.dataset_versions is
    'Server-managed immutable logical dataset versions built from source snapshots.';
comment on table public.dataset_version_snapshots is
    'Deterministic ordered source-snapshot membership for an immutable dataset version.';

alter table public.dataset_versions enable row level security;
alter table public.dataset_version_snapshots enable row level security;

-- Intentionally no browser/client RLS policies. Dataset versions are written through
-- protected server-side PostgreSQL connections only.

commit;
