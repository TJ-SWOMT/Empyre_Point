# Empyre Point - Collaborative Presentation Platform

## Project Context

This project was developed as a coding test to create a stripped-down version of PowerPoint with markdown support. The goal was to demonstrate full-stack development skills while implementing a practical, real-world application.

### Original Prompt

Create a web app that is a stripped-down version of PowerPoint with the contents of the slides written using markdown.

**Minimum Requirements:**
- Move forward/backwards in the presentation
- Parse and display markdown code

**Additional Features Implemented:**
- ✅ Editing and saving slides through an editor
- ✅ Storing slides in a backend service (AWS RDS)
- ✅ Highlighting/formatting code snippets
- ✅ Supporting different slide layouts
- ✅ Displaying a presentation progress bar
- ✅ Implementing hotkeys support
- ✅ Mobile-friendly design
- ✅ Unit and integration tests

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
└── Back_yrean/      # Flask backend service (AWS hosted)
```

## Quick Start

To get started with development:

1. Clone the repository
2. Set up the frontend (see Front_yrean/README.md)
3. Start the frontend development server

**Note:** The backend is already deployed and running on AWS. You don't need to set up or run the backend locally. The frontend is configured to connect to the global backend automatically.

## Development Environment

The project uses:
- Vue 3 with Vite for the frontend
- Flask with Socket.IO for the backend (AWS hosted)
- PostgreSQL on AWS RDS for the database
- AWS S3 for media storage
- WebSocket for real-time collaboration

## Architecture & Design Decisions

### Frontend
- Vue 3 with Composition API for modern, maintainable code
- Custom markdown parser for slide content
- Minimal UI libraries to demonstrate raw implementation
- Responsive design for all device sizes
- Hotkey support for presentation navigation

### Backend
- Flask REST API for slide management
- AWS RDS for persistent storage
- AWS S3 for media file storage
- WebSocket for real-time collaboration
- JWT for authentication

### Future Considerations
- Real-time collaboration features
- Slide templates and themes
- Export to PDF/PPTX
- User roles and permissions
- Presentation analytics

## Contributing

When contributing to this project:
1. Create a new branch for your feature
2. Follow the existing code style
3. Update documentation as needed
4. Test thoroughly before submitting PRs 