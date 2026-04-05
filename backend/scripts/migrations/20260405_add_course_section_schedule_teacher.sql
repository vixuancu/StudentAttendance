-- 20260405_add_course_section_schedule_teacher.sql
-- Purpose:
-- 1) Add user_id to course_section_schedule so each weekly session can have its own lecturer
-- 2) Backfill existing rows from course_section.user_id
-- 3) Add index for lecturer conflict lookups

BEGIN;

ALTER TABLE course_section_schedule
    ADD COLUMN IF NOT EXISTS user_id INTEGER NULL;

UPDATE course_section_schedule css
SET user_id = cs.user_id
FROM course_section cs
WHERE css.course_section_id = cs.id
  AND css.user_id IS NULL;

ALTER TABLE course_section_schedule
    ADD CONSTRAINT fk_css_user FOREIGN KEY (user_id)
    REFERENCES users(id);

ALTER TABLE course_section_schedule
    ALTER COLUMN user_id SET NOT NULL;

CREATE INDEX IF NOT EXISTS idx_css_user_day
    ON course_section_schedule(user_id, day_of_week);

COMMIT;
