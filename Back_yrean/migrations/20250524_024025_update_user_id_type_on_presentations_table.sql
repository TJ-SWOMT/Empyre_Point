-- Migration: update_user_id_type_on_presentations_table
-- Created at: 2025-05-24T02:40:25.682847 UTC

-- Change user_id column type from UUID to INTEGER
ALTER TABLE presentations
  ALTER COLUMN user_id TYPE INTEGER USING (user_id::text::integer);

