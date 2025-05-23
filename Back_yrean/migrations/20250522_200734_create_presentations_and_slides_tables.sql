-- Migration: create_presentations_table
-- Created at: 2025-05-22T20:07:34.913249 UTC

CREATE TABLE presentations (
    presentation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE slides (
    slide_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    presentation_id UUID NOT NULL REFERENCES presentations(presentation_id) ON DELETE CASCADE,
    slide_number INT NOT NULL,
    background_color VARCHAR(7) DEFAULT '#FFFFFF',
    background_image_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (presentation_id, slide_number)
);