# Empyre Point Backend

This is the backend service for Empyre Point, built with Flask and Socket.IO. It provides the API endpoints, real-time collaboration features, and database management for the presentation platform.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL client
- AWS CLI (for S3 and RDS access)
- Virtual environment tool (venv)

## Setup Instructions

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
   - Create a `.env` file in the root directory
   - Add the following environment variables:
     ```
     # Flask Configuration
     SECRET_KEY=your_secret_key_here
     FLASK_ENV=development

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

4. Database Setup:
   - The application uses AWS RDS PostgreSQL
   - Database migrations are managed through custom scripts
   - To create a new migration:
     ```bash
     python create_migration.py "description_of_changes"
     ```
   - To apply migrations:
     ```bash
     python migrate.py
     ```

5. Run the development server:
```bash
python app.py
```
The server will start on `http://localhost:5000`

## Project Structure

```
Back_yrean/
├── app.py              # Main application file
├── aws_config.py       # AWS configuration
├── create_migration.py # Migration creation script
├── migrate.py         # Migration application script
├── requirements.txt   # Python dependencies
├── migrations/        # Database migration files
└── services/         # Business logic modules
```

## API Endpoints

### REST API
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

## AWS Integration

The backend uses AWS services for database and media storage. The configuration is managed through environment variables in the `.env` file:

- RDS PostgreSQL for the database
- S3 for media file storage
- IAM credentials for AWS service access

For local development, the `.env` file is already configured with the necessary AWS credentials and endpoints. No additional AWS setup is required to run the application locally.

## Security Considerations

1. Database Security:
   - Use environment variables for credentials
   - Implement proper connection pooling
   - Regular security updates

2. API Security:
   - CORS configuration
   - Rate limiting
   - Input validation
   - Authentication middleware

3. AWS Security:
   - IAM roles and policies
   - S3 bucket policies
   - RDS security groups

## Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=.
```

## Deployment

The backend is configured to deploy to AWS EC2:
1. Set up EC2 instance
2. Configure security groups
3. Set up environment variables
4. Use Gunicorn for production server

## Troubleshooting

Common issues and solutions:
1. Database connection: Verify AWS RDS credentials and security groups
2. S3 access: Check AWS credentials and bucket policies
3. WebSocket: Ensure proper CORS and proxy settings
4. Migration errors: Check migration history and database state

## Contributing

See the main project README for contribution guidelines. 