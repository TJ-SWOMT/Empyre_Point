-- Migration: change_presentation_id_to_int
-- Created at: 2025-05-24T01:54:27.303059 UTC

-- First, drop all foreign key constraints that reference presentations.presentation_id
ALTER TABLE slides 
  DROP CONSTRAINT IF EXISTS slides_presentation_id_fkey;

-- Create new sequence for presentations id
CREATE SEQUENCE IF NOT EXISTS presentations_id_seq START WITH 1;

-- Change presentation_id column type from UUID to INTEGER
ALTER TABLE presentations
  ALTER COLUMN presentation_id TYPE INTEGER USING (presentation_id::text::integer);

-- Set sequence to start after highest existing ID
SELECT setval('presentations_id_seq', COALESCE((SELECT MAX(presentation_id) FROM presentations), 1));

-- Set default to use sequence
ALTER TABLE presentations 
  ALTER COLUMN presentation_id SET DEFAULT nextval('presentations_id_seq');

-- Change presentation_id column type in slides table from UUID to INTEGER
ALTER TABLE slides
  ALTER COLUMN presentation_id TYPE INTEGER USING (presentation_id::text::integer);

-- Add back the foreign key constraint
ALTER TABLE slides 
  ADD CONSTRAINT slides_presentation_id_fkey 
  FOREIGN KEY (presentation_id) 
  REFERENCES presentations(presentation_id)
  ON DELETE CASCADE;
