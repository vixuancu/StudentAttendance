# SQL Migrations (Manual)

## Files
- `20260405_add_course_section_schedule.sql`: create `course_section_schedule` + indexes + backfill
- `20260405_add_course_section_schedule_rollback.sql`: rollback script (drop table)

## Apply
Run SQL with your PostgreSQL client, for example:

```bash
psql -h <host> -U <user> -d <database> -f 20260405_add_course_section_schedule.sql
```

## Verify
After apply, check:

```sql
SELECT COUNT(*) FROM course_section_schedule;
SELECT * FROM course_section_schedule ORDER BY id DESC LIMIT 10;
```

## Notes
- Script is idempotent for table/index create and backfill guard.
- Backfill inserts one schedule row per existing `course_section`.
- Rollback drops the schedule table.
