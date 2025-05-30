# Empyre Point Backend

This is the backend service for Empyre Point, built with Flask and Socket.IO. The service is hosted on AWS and provides the API endpoints, real-time collaboration features, and database management for the presentation platform.

## Current Status

The backend is currently deployed and running on AWS at:
```
http://44.201.125.158:5001/api
```

All frontend applications are configured to use this global backend. No local setup is required to use the application.

## Architecture Overview

### AWS Infrastructure
- **API Server**: AWS EC2 instance running Flask
- **Database**: AWS RDS PostgreSQL
- **Storage**: AWS S3 for media files
- **Security**: AWS IAM for access management

### Key Components
- Flask REST API for slide management
- WebSocket server for real-time updates
- PostgreSQL database for data persistence
- S3 integration for media storage
- JWT-based authentication

## API Documentation

### REST Endpoints
- `GET /api/slides` - List all slides
- `POST /api/slides` - Create new slide
- `GET /api/slides/<id>` - Get slide details
- `PUT /api/slides/<id>` - Update slide
- `DELETE /api/slides/<id>` - Delete slide

### WebSocket Events
- `slide:update` - Real-time slide updates
- `collaboration:join` - Join presentation session
- `collaboration:leave` - Leave presentation session
- `media:upload` - Handle media uploads

## Database Schema

The database uses PostgreSQL with the following main tables:
- `slides` - Presentation slides
- `users` - User information
- `collaborations` - Collaboration sessions
- `media` - Uploaded media files

## Development Information

This section is for developers who need to work on the backend code.

### Prerequisites
- Python 3.8 or higher
- PostgreSQL client
- AWS CLI
- Virtual environment tool (venv)

### Local Development Setup
1. Create and activate a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Environment Configuration:
   The `.env` file contains the AWS configuration:
   ```
   # Database Configuration (AWS RDS)
   DB_USERNAME=EmpyrePointAdmin
   DB_PASSWORD=your_password_here
   DB_ENDPOINT=empyre-point.ckbeyci4yeyy.us-east-1.rds.amazonaws.com
   DB_PORT=5432
   DB_NAME=Empyre_Point_DB
   DATABASE_URL=postgresql://${DB_USERNAME}:${DB_PASSWORD}@${DB_ENDPOINT}:${DB_PORT}/${DB_NAME}

   # AWS Configuration
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=us-east-1
   S3_BUCKET_NAME=empyre-point-images
   ```

4. Database Migrations:
   - Migrations are managed through custom scripts
   - To create a new migration:
     ```bash
     python create_migration.py "description_of_changes"
     ```
   - To apply migrations:
     ```bash
     python migrate.py
     ```

### Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=.
```

## Security Considerations

1. Database Security:
   - AWS RDS with encrypted connections
   - Environment variables for credentials
   - Proper connection pooling
   - Regular security updates

2. API Security:
   - CORS configuration for frontend access
   - Rate limiting
   - Input validation
   - JWT authentication

3. AWS Security:
   - IAM roles and policies
   - S3 bucket policies
   - RDS security groups
   - VPC configuration

## Deployment

The backend is deployed on AWS EC2:
1. Uses Gunicorn as production server
2. Configured with proper security groups
3. Integrated with AWS RDS and S3
4. Monitored with AWS CloudWatch

## Troubleshooting

Common issues and solutions:
1. Database connection: Verify AWS RDS credentials and security groups
2. S3 access: Check AWS credentials and bucket policies
3. WebSocket: Ensure proper CORS and proxy settings
4. Migration errors: Check migration history and database state

## Contributing

See the main project README for contribution guidelines. 