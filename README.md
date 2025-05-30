# Empyre Point - Collaborative Presentation Platform

## Project Story

Empyre Point is a modern, collaborative presentation platform that reimagines the traditional PowerPoint experience for the web. Born from the need for real-time collaboration and seamless sharing, this project combines the power of Vue.js and Flask to create an intuitive, cloud-based presentation tool.

### The Journey

The development of Empyre Point began with a vision to create a presentation platform that would:
- Provide seamless cloud storage for presentations
- Offer a modern, intuitive user interface
- Support instant sharing and presentation capabilities
- Maintain data persistence across sessions

The project evolved through several key phases:
1. **Initial Architecture**: Setting up the Vue.js frontend with Vite and Flask backend
2. **Database Integration**: Implementing AWS RDS for reliable data storage
3. **Real-time Features**: Adding WebSocket support for live collaboration
4. **Cloud Storage**: Integrating AWS S3 for media storage
5. **Deployment**: Setting up production infrastructure on AWS

## Project Structure

The project is organized into two main components:

```
Empyre_Point/
├── Front_yrean/     # Vue.js frontend application
└── Back_yrean/      # Flask backend service
```

## Quick Start

To get started with development:

1. Clone the repository
2. Set up the backend (see Back_yrean/README.md)
3. Set up the frontend (see Front_yrean/README.md)
4. Configure environment variables (if needed)
5. Start both services

## Development Environment

The project uses:
- Vue 3 with Vite for the frontend
- Flask with Socket.IO for the backend
- PostgreSQL on AWS RDS for the database
- AWS S3 for media storage
- WebSocket for real-time collaboration

## Contributing

When contributing to this project:
1. Create a new branch for your feature
2. Follow the existing code style
3. Update documentation as needed
4. Test thoroughly before submitting PRs 