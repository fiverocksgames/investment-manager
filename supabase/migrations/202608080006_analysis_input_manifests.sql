create table if not exists public.analysis_input_manifests (
    manifest_id uuid primary key,
    as_of timestamptz not null,
    created_at timestamptz not null,
    checksum text not null,
    constraint analysis_input_manifests_checksum_sha256
        check (checksum ~ '^[0-9a-f]{64}$'),
    constraint analysis_input_manifests_created_after_as_of
        check (created_at >= as_of),
    constraint analysis_input_manifests_content_identity
        unique (as_of, checksum)
);

create table if not exists public.analysis_input_manifest_versions (
    manifest_id uuid not null references public.analysis_input_manifests(manifest_id) on delete restrict,
    position integer not null,
    dataset text not null,
    version_id uuid not null references public.dataset_versions(version_id) on delete restrict,
    primary key (manifest_id, position),
    constraint analysis_input_manifest_versions_position_nonnegative check (position >= 0),
    constraint analysis_input_manifest_versions_dataset_nonempty check (length(btrim(dataset)) > 0),
    constraint analysis_input_manifest_versions_dataset_unique unique (manifest_id, dataset),
    constraint analysis_input_manifest_versions_version_unique unique (manifest_id, version_id)
);

create index if not exists analysis_input_manifests_as_of_idx
    on public.analysis_input_manifests (as_of desc);

create index if not exists analysis_input_manifest_versions_version_id_idx
    on public.analysis_input_manifest_versions (version_id);

alter table public.analysis_input_manifests enable row level security;
alter table public.analysis_input_manifest_versions enable row level security;

comment on table public.analysis_input_manifests is
    'Server-managed immutable identity for an exact cross-dataset analysis input set.';
comment on table public.analysis_input_manifest_versions is
    'Server-managed ordered membership from an analysis input manifest to immutable dataset versions.';
