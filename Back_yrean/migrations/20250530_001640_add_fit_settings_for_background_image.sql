-- Migration: add_fit_settings_for_background_image
-- Created at: 2025-05-30T00:16:40.830176 UTC

ALTER TABLE slides
ADD COLUMN background_image_fit VARCHAR(255);

ALTER TABLE slides
ADD COLUMN background_image_opacity FLOAT;