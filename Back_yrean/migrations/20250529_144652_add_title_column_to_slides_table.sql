-- Migration: add_title_column_to_slides_table
-- Created at: 2025-05-29T14:46:52.388599 UTC

ALTER TABLE slides
ADD COLUMN title VARCHAR(255);

