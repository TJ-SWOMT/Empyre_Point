#!/usr/bin/env python3

import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

def run_migrations():
    conn = psycopg2.connect(DATABASE_URL)
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
            print("Migrations table does not exist. Looking for initial migration...")
            # Find the migration that creates the migrations table
            initial_migration = next((f for f in sql_files if 'create_migrations_table' in f), None)
            if initial_migration:
                print(f"Found initial migration: {initial_migration}")
                with open(os.path.join(migrations_dir, initial_migration), 'r') as file:
                    sql = file.read()
                    cur.execute(sql)
                conn.commit()
                print("Successfully created migrations table")
            else:
                raise Exception("Could not find migration to create migrations table")
        
        # Get list of already applied migrations
        cur.execute("SELECT migration_name, status FROM migrations")
        applied_migrations = {row[0]: row[1] for row in cur.fetchall()}
        
        # Now run all migrations
        for sql_file in sql_files:
            # Re-run if migration is already applied successfully
            if sql_file in applied_migrations and applied_migrations[sql_file] == 'success':
                print(f"Re-running already applied migration: {sql_file}")
                cur.execute("DELETE FROM migrations WHERE migration_name = %s", (sql_file,))
                conn.commit()
                
            # If migration failed before, try to reapply it
            if sql_file in applied_migrations and applied_migrations[sql_file] == 'failed':
                print(f"Retrying failed migration: {sql_file}")
                cur.execute("DELETE FROM migrations WHERE migration_name = %s", (sql_file,))
                conn.commit()

            try:
                print(f"Applying migration: {sql_file}")
                with open(os.path.join(migrations_dir, sql_file), 'r') as file:
                    sql = file.read()
                    cur.execute(sql)

                # Record the applied migration
                cur.execute("""
                    INSERT INTO migrations (migration_name, status, applied_at) 
                    VALUES (%s, 'success', CURRENT_TIMESTAMP)
                    ON CONFLICT (migration_name) 
                    DO UPDATE SET status = 'success', error_message = NULL, applied_at = CURRENT_TIMESTAMP
                """, (sql_file,))
                conn.commit()
                print(f"Successfully applied migration: {sql_file}")

            except Exception as migration_error:
                # Rollback the transaction
                conn.rollback()
                # Record or update the failed migration
                cur.execute("""
                    INSERT INTO migrations (migration_name, status, error_message, applied_at) 
                    VALUES (%s, 'failed', %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (migration_name) 
                    DO UPDATE SET status = 'failed', error_message = %s, applied_at = CURRENT_TIMESTAMP
                """, (sql_file, str(migration_error), str(migration_error)))
                conn.commit()
                print(f"Failed to apply migration: {sql_file} with error: {migration_error}")

    except Exception as e:
        print(f"Error running migrations: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_migrations() 