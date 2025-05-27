-- Migration: change_element_id_to_int
-- Created at: 2025-05-24T04:00:00.000000 UTC

-- First, drop all foreign key constraints that reference element_id
ALTER TABLE text_elements 
    DROP CONSTRAINT IF EXISTS text_elements_element_id_fkey;
ALTER TABLE image_elements 
    DROP CONSTRAINT IF EXISTS image_elements_element_id_fkey;
ALTER TABLE shape_elements 
    DROP CONSTRAINT IF EXISTS shape_elements_element_id_fkey;

-- Create new sequence for elements id
CREATE SEQUENCE IF NOT EXISTS elements_id_seq START WITH 1;

-- Add a new integer column to slide_elements
ALTER TABLE slide_elements ADD COLUMN new_element_id INTEGER;

-- Update the new column with sequence values
UPDATE slide_elements SET new_element_id = nextval('elements_id_seq');

-- Drop the old column and rename the new one
ALTER TABLE slide_elements DROP COLUMN element_id;
ALTER TABLE slide_elements RENAME COLUMN new_element_id TO element_id;

-- Make the new column the primary key
ALTER TABLE slide_elements ADD PRIMARY KEY (element_id);

-- Set the default value
ALTER TABLE slide_elements ALTER COLUMN element_id SET DEFAULT nextval('elements_id_seq');

-- Update text_elements table
ALTER TABLE text_elements ADD COLUMN new_element_id INTEGER;
UPDATE text_elements te 
SET new_element_id = se.element_id 
FROM slide_elements se 
WHERE te.element_id::text = se.element_id::text;

-- Drop the old column and rename the new one in text_elements
ALTER TABLE text_elements DROP COLUMN element_id;
ALTER TABLE text_elements RENAME COLUMN new_element_id TO element_id;

-- Add back the foreign key constraint for text_elements
ALTER TABLE text_elements 
    ADD CONSTRAINT text_elements_element_id_fkey 
    FOREIGN KEY (element_id) 
    REFERENCES slide_elements(element_id)
    ON DELETE CASCADE;

-- Update image_elements table
ALTER TABLE image_elements ADD COLUMN new_element_id INTEGER;
UPDATE image_elements ie 
SET new_element_id = se.element_id 
FROM slide_elements se 
WHERE ie.element_id::text = se.element_id::text;

-- Drop the old column and rename the new one in image_elements
ALTER TABLE image_elements DROP COLUMN element_id;
ALTER TABLE image_elements RENAME COLUMN new_element_id TO element_id;

-- Add back the foreign key constraint for image_elements
ALTER TABLE image_elements 
    ADD CONSTRAINT image_elements_element_id_fkey 
    FOREIGN KEY (element_id) 
    REFERENCES slide_elements(element_id)
    ON DELETE CASCADE;

-- Update shape_elements table
ALTER TABLE shape_elements ADD COLUMN new_element_id INTEGER;
UPDATE shape_elements se 
SET new_element_id = sle.element_id 
FROM slide_elements sle 
WHERE se.element_id::text = sle.element_id::text;

-- Drop the old column and rename the new one in shape_elements
ALTER TABLE shape_elements DROP COLUMN element_id;
ALTER TABLE shape_elements RENAME COLUMN new_element_id TO element_id;

-- Add back the foreign key constraint for shape_elements
ALTER TABLE shape_elements 
    ADD CONSTRAINT shape_elements_element_id_fkey 
    FOREIGN KEY (element_id) 
    REFERENCES slide_elements(element_id)
    ON DELETE CASCADE; 