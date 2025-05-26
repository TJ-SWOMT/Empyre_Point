-- Migration: change_slide_id_to_int
-- Created at: 2025-05-24T03:00:00.000000 UTC

-- First, drop all foreign key constraints that reference slides.slide_id
ALTER TABLE slide_elements 
  DROP CONSTRAINT IF EXISTS slide_elements_slide_id_fkey;

-- Create new sequence for slides id
CREATE SEQUENCE IF NOT EXISTS slides_id_seq START WITH 1;

-- Add a new integer column
ALTER TABLE slides ADD COLUMN new_slide_id INTEGER;

-- Update the new column with sequence values
UPDATE slides SET new_slide_id = nextval('slides_id_seq');

-- Drop the old column and rename the new one
ALTER TABLE slides DROP COLUMN slide_id;
ALTER TABLE slides RENAME COLUMN new_slide_id TO slide_id;

-- Make the new column the primary key
ALTER TABLE slides ADD PRIMARY KEY (slide_id);

-- Set the default value
ALTER TABLE slides ALTER COLUMN slide_id SET DEFAULT nextval('slides_id_seq');

-- Update slide_elements table to use the new integer IDs
ALTER TABLE slide_elements ADD COLUMN new_slide_id INTEGER;
UPDATE slide_elements se 
SET new_slide_id = s.slide_id 
FROM slides s 
WHERE se.slide_id::text = s.slide_id::text;

-- Drop the old column and rename the new one in slide_elements
ALTER TABLE slide_elements DROP COLUMN slide_id;
ALTER TABLE slide_elements RENAME COLUMN new_slide_id TO slide_id;

-- Add back the foreign key constraint
ALTER TABLE slide_elements 
  ADD CONSTRAINT slide_elements_slide_id_fkey 
  FOREIGN KEY (slide_id) 
  REFERENCES slides(slide_id)
  ON DELETE CASCADE; 