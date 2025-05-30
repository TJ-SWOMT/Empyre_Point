# Empyre Point Frontend

This is the frontend application for Empyre Point, built with Vue 3 and Vite. It provides a modern, responsive interface for creating and collaborating on presentations.

## Prerequisites

- Node.js (v16 or higher)
- npm (v7 or higher)
- Modern web browser

## Setup Instructions

1. Install dependencies:
```bash
npm install
```

2. Environment Configuration:
   - Create a `.env` file in the root directory
   - Add the following environment variables:
     ```
     # Development (local backend)
     VITE_API_URL=http://localhost:5000/api
     
     # Production (AWS backend)
     # VITE_API_URL=http://44.201.125.158:5001/api
     ```
   - Uncomment the appropriate URL based on your setup

3. Development Server:
```bash
npm run dev
```
The development server will start at `http://localhost:5173`

4. Building for Production:
```bash
npm run build
```
This will create a `dist` directory with the production build.

## Project Structure

```
Front_yrean/
├── src/              # Source files
│   ├── assets/      # Static assets
│   ├── components/  # Vue components
│   ├── views/       # Page components
│   └── App.vue      # Root component
├── public/          # Public static files
└── index.html       # Entry HTML file
```

## Features

- Real-time collaboration using WebSocket
- Modern, responsive UI
- Drag-and-drop interface
- Real-time slide updates
- Media upload and management
- Presentation sharing

## Development Guidelines

1. Component Structure:
   - Use Vue 3 Composition API with `<script setup>`
   - Follow single-file component pattern
   - Implement proper prop validation
   - Use TypeScript for type safety

2. State Management:
   - Use Pinia for global state
   - Implement proper state persistence
   - Handle real-time updates efficiently

3. Styling:
   - Use scoped CSS
   - Follow BEM naming convention
   - Implement responsive design
   - Use CSS variables for theming

## Testing

```bash
# Run unit tests
npm run test:unit

# Run end-to-end tests
npm run test:e2e
```

## Deployment

The frontend is configured to deploy to AWS S3:
1. Build the production version
2. Upload the `dist` directory contents to S3
3. Configure CloudFront for CDN distribution

## Troubleshooting

Common issues and solutions:
1. CORS errors: Ensure backend CORS settings match frontend URL
2. WebSocket connection: Verify backend WebSocket endpoint
3. API connection: Check environment variables
4. Build errors: Clear node_modules and reinstall

## Contributing

See the main project README for contribution guidelines.
