# Backend for PowerPoint-like Web App

This is the backend service for a PowerPoint-like web application, built with Flask and Socket.IO.

## Setup Instructions

1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Environment Configuration:
- Copy `.env.example` to `.env`
- Fill in the required environment variables in `.env`:
  - Flask secret key
  - Database connection string (DATABASE_URL)
  - AWS credentials
  - S3 bucket name

4. Database Setup and Migrations:
```bash
# Create a new migration
python create_migration.py "description_of_changes"

# Apply migrations
python migrate.py
```

5. Run the development server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## Project Structure

- `app.py`: Main application file with Flask and Socket.IO setup
- `aws_config.py`: AWS configuration for S3 and RDS access
- `requirements.txt`: Python dependencies
- `.env`: Environment variables (create from .env.example)
- `migrations/`: Directory containing SQL migration files
- `create_migration.py`: Script to create new migration files
- `migrate.py`: Script to apply database migrations

## Database Migrations

The project uses a custom migration system to manage database schema changes:

1. Creating Migrations:
   - Use `create_migration.py` to generate a new migration file
   - Migration files are stored in the `migrations/` directory
   - Each migration is timestamped and includes a description
   - Example: `python create_migration.py add_user_table`

2. Applying Migrations:
   - Run `python migrate.py` to apply all pending migrations
   - Migrations are tracked in a `migrations` table
   - Failed migrations can be retried
   - Migrations are applied in chronological order

## Features

- WebSocket communication for real-time updates
- AWS S3 integration for image storage
- AWS RDS integration for slide data
- RESTful API endpoints for slide management
- Custom database migration system
- PostgreSQL database with SQLAlchemy ORM
- CORS support for cross-origin requests
- Production-ready with Gunicorn server 