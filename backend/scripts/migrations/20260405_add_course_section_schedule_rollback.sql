-- 20260405_add_course_section_schedule_rollback.sql
-- Rollback script for 20260405_add_course_section_schedule.sql

BEGIN;

DROP TABLE IF EXISTS course_section_schedule;

COMMIT;
