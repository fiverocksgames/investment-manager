begin;

create index if not exists ingestion_runs_snapshot_id_idx
    on public.ingestion_runs(snapshot_id);

commit;
