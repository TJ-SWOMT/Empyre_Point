#!/usr/bin/env python3

import os
import sys
from datetime import datetime

def create_migration(description):
    # Get UTC timestamp
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    
    # Create filename
    filename = f"{timestamp}_{description}.sql"
    
    # Ensure migrations directory exists
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    os.makedirs(migrations_dir, exist_ok=True)
    
    # Create the migration file
    filepath = os.path.join(migrations_dir, filename)
    with open(filepath, 'w') as f:
        f.write("-- Migration: " + description + "\n")
        f.write("-- Created at: " + datetime.utcnow().isoformat() + " UTC\n\n")
    
    print(f"Created new migration file: {filename}")
    return filepath

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_migration.py 'description_of_migration'")
        sys.exit(1)
    
    description = sys.argv[1].replace(' ', '_').lower()
    create_migration(description) 