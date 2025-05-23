-- Migration: create_shapes_table
-- Created at: 2025-05-23T15:01:13.456701 UTC

CREATE TYPE shape_enum AS ENUM ('rectangle', 'circle', 'triangle', 'star');

CREATE TABLE shape_elements (
    element_id UUID PRIMARY KEY REFERENCES slide_elements(element_id) ON DELETE CASCADE,
    shape_type shape_enum NOT NULL,
    fill_color VARCHAR(7) DEFAULT '#CCCCCC',
    stroke_color VARCHAR(7) DEFAULT '#000000',
    stroke_width INT DEFAULT 1,
    border_radius DECIMAL(10, 2) DEFAULT 0
);