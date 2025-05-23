-- Migration: add_indexing
-- Created at: 2025-05-23T15:05:06.052911 UTC

CREATE INDEX idx_slides_presentation_id ON slides (presentation_id);
CREATE INDEX idx_slide_elements_slide_id ON slide_elements (slide_id);
CREATE INDEX idx_slide_elements_element_type ON slide_elements (element_type);