-- Migration: ccreate_elements_tables
-- Created at: 2025-05-22T20:32:53.389741 UTC

CREATE TABLE slide_elements (
    element_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slide_id UUID NOT NULL REFERENCES slides(slide_id) ON DELETE CASCADE,
    element_type VARCHAR(50) NOT NULL, 
    x_position DECIMAL(10, 2) NOT NULL, 
    y_position DECIMAL(10, 2) NOT NULL, 
    width DECIMAL(10, 2),
    height DECIMAL(10, 2),
    rotation DECIMAL(5, 2) DEFAULT 0,
    z_index INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE text_elements (
    element_id UUID PRIMARY KEY REFERENCES slide_elements(element_id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    font_family VARCHAR(100) DEFAULT 'Arial',
    font_size INT DEFAULT 18,
    font_color VARCHAR(7) DEFAULT '#000000',
    bold BOOLEAN DEFAULT FALSE,
    italic BOOLEAN DEFAULT FALSE,
    underline BOOLEAN DEFAULT FALSE,
    text_align VARCHAR(20) DEFAULT 'left'
);


CREATE TABLE image_elements (
    element_id UUID PRIMARY KEY REFERENCES slide_elements(element_id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    alt_text VARCHAR(255)
);

