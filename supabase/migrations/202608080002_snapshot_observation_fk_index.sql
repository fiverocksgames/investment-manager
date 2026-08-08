begin;

create index if not exists source_snapshot_observations_observation_id_idx
    on public.source_snapshot_observations(observation_id);

commit;
