-- Create migrations table to track migration history
CREATE TABLE IF NOT EXISTS migrations (
    migration_name VARCHAR(255) PRIMARY KEY,
    status VARCHAR(50) NOT NULL CHECK (status IN ('success', 'failed')),
    error_message TEXT,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index on status for faster queries
CREATE INDEX IF NOT EXISTS idx_migrations_status ON migrations(status); 