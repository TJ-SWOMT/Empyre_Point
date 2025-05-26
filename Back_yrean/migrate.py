#!/usr/bin/env python3

import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

def run_migrations():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False  # Explicitly disable autocommit
    cur = conn.cursor()
    
    try:
        # Use the absolute path for the migrations directory
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        sql_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
        
        # Check if migrations table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'migrations'
            );
        """)
        migrations_table_exists = cur.fetchone()[0]
        
        if not migrations_table_exists:
            logger.info("Migrations table does not exist. Looking for initial migration...")
            # Find the migration that creates the migrations table
            initial_migration = next((f for f in sql_files if 'create_migrations_table' in f), None)
            if initial_migration:
                logger.info(f"Found initial migration: {initial_migration}")
                with open(os.path.join(migrations_dir, initial_migration), 'r') as file:
                    sql = file.read()
                    cur.execute(sql)
                conn.commit()
                logger.info("Successfully created migrations table")
            else:
                raise Exception("Could not find migration to create migrations table")
        
        # Get list of all migrations in the table (both successful and failed)
        cur.execute("SELECT migration_name FROM migrations")
        existing_migrations = {row[0] for row in cur.fetchall()}
        
        # Now run only completely new migrations
        for sql_file in sql_files:
            # Skip if migration exists in the table at all
            if sql_file in existing_migrations:
                logger.info(f"Skipping existing migration: {sql_file}")
                continue

            try:
                logger.info(f"Applying new migration: {sql_file}")
                with open(os.path.join(migrations_dir, sql_file), 'r') as file:
                    sql = file.read()
                    
                # Start a new transaction for each migration
                cur.execute("BEGIN")
                
                # Execute the migration
                cur.execute(sql)
                
                # Record the successful migration
                cur.execute("""
                    INSERT INTO migrations (migration_name, status, applied_at) 
                    VALUES (%s, 'success', CURRENT_TIMESTAMP)
                """, (sql_file,))
                
                # Commit the transaction
                conn.commit()
                logger.info(f"Successfully applied migration: {sql_file}")

            except psycopg2.Error as migration_error:
                # Rollback the transaction
                conn.rollback()
                error_message = str(migration_error)
                
                # For type conversion errors, provide more helpful error message
                if "cannot be cast automatically" in error_message:
                    error_message = f"Type conversion error: {error_message}. Please check the USING clause in the migration."
                
                # Record the failed migration
                cur.execute("""
                    INSERT INTO migrations (migration_name, status, error_message, applied_at) 
                    VALUES (%s, 'failed', %s, CURRENT_TIMESTAMP)
                """, (sql_file, error_message))
                conn.commit()
                logger.error(f"Failed to apply migration: {sql_file} with error: {error_message}")

    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_migrations() 