-- Migration: alter_users_table_id
-- Created at: 2025-05-23T12:09:00.000000 UTC

-- First, create a new column for the sequential ID
ALTER TABLE users ADD COLUMN new_user_id SERIAL;

-- Update the new column with sequential numbers
UPDATE users SET new_user_id = nextval('users_new_user_id_seq');

-- Drop the old primary key constraint
ALTER TABLE users DROP CONSTRAINT users_pkey;

-- Drop the old UUID column
ALTER TABLE users DROP COLUMN user_id;

-- Rename the new column to user_id
ALTER TABLE users RENAME COLUMN new_user_id TO user_id;

-- Make the new column the primary key
ALTER TABLE users ADD PRIMARY KEY (user_id);

-- Update any foreign key references if they exist
-- Note: Add any necessary foreign key updates here if other tables reference user_id 