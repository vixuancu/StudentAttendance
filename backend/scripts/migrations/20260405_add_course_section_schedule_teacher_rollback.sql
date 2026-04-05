-- 20260405_add_course_section_schedule_teacher_rollback.sql
-- Rollback script for 20260405_add_course_section_schedule_teacher.sql

BEGIN;

ALTER TABLE course_section_schedule
    DROP CONSTRAINT IF EXISTS fk_css_user;

ALTER TABLE course_section_schedule
    DROP COLUMN IF EXISTS user_id;

DROP INDEX IF EXISTS idx_css_user_day;

COMMIT;
