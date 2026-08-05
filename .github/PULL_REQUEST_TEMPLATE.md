## Summary

Describe what changed and why.

## Requirement IDs

List every affected requirement ID. Do not delete or silently rename existing IDs.

- `REQ-...`

## Validation

List the commands, inspections, or evidence used to validate the change. Do not claim checks that were not run.

## Test

Describe automated and manual tests, including edge cases and financial-calculation fixtures where applicable.

## Documentation

List documents updated. A feature PR without required documentation updates is incomplete.

- [ ] Product/design documents updated
- [ ] `docs/FEATURE_MATRIX.md` updated
- [ ] `WORKLOG.md` updated
- [ ] `AI_HANDOFF.md` updated
- [ ] `CHANGELOG.md` updated when user-visible behavior changes

## Investment and Data Safety

- [ ] No automated-trading capability was introduced
- [ ] No secrets or personal portfolio data were committed
- [ ] Data source, timestamp, freshness, assumptions, and uncertainty are disclosed where relevant
- [ ] Calculations remain outside the UI layer
- [ ] Recommendation output includes rationale and risks where relevant

## Known Limitations

State unresolved limitations, unavailable validation, and deferred work.

## Next Steps

List the next traceable actions or issues.
