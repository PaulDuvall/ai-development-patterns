<!-- Annotated worked example. retro-analysis.py generates the metrics, root-cause table,
proposed-rule checklist, and next steps. The explicit no-repeat note and Analysis section below are
human-authored additions and are not analyzer output. -->

# Feedback Flywheel Retrospective (7-Day)

**Period**: Last 7 days
**Sessions analyzed**: 1
**First-pass acceptance rate**: 57%
**Total corrections**: 3

## Repeated Corrections (Action Required)

None detected in this period (single session). Monitor for recurrence.

## Top Root Causes

| Root Cause | Count |
|------------|-------|
| no HTTP status code convention in project rules | 1 |
| missing framework migration preference in rules | 1 |
| pagination strategy not specified in API conventions | 1 |

## Proposed Rule Updates

- [ ] Use 201 Created for POST endpoints that create resources, 204 No Content for DELETE
- [ ] Always generate Django ORM migrations via makemigrations pattern, never raw SQL DDL
- [ ] Use cursor-based pagination for all list endpoints returning >100 items

## Analysis

All three corrections share a common theme: **API design conventions are underspecified**. Rather than adding three individual rules, consider creating a dedicated `.ai/rules/api-conventions.md` file covering:

1. HTTP status codes by method (GET=200, POST=201, PUT=200, DELETE=204)
2. Migration strategy (ORM-first, no raw SQL)
3. Pagination strategy (cursor-based for large collections)

This single rules file would have prevented all three corrections in this session.

## Next Steps

1. Review proposed rules above
2. Add validated rules to `.ai/rules/api-conventions.md`
3. Address repeated corrections first (highest impact)
4. Re-run retro next period to measure improvement
