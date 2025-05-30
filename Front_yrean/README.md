# Empyre Point Frontend

This is the frontend application for Empyre Point, built with Vue 3 and Vite. It provides a modern, responsive interface for creating and collaborating on presentations using markdown.

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
   The frontend is pre-configured to use the global AWS backend. The `.env` file contains:
   ```
   # Production (AWS backend)
   VITE_API_URL=http://44.201.125.158:5001/api
   ```
   No additional configuration is needed to connect to the backend.

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
├── src/
│   ├── assets/          # Static assets
│   ├── components/      # Vue components
│   │   ├── editor/     # Markdown editor components
│   │   ├── slides/     # Slide presentation components
│   │   └── ui/         # Reusable UI components
│   ├── views/          # Page components
│   ├── stores/         # Pinia state management
│   ├── services/       # API and WebSocket services
│   ├── utils/          # Helper functions
│   └── App.vue         # Root component
├── public/             # Public static files
└── index.html          # Entry HTML file
```

## Key Features & Implementation Details

### Markdown Editor
- Custom markdown parser using `marked` library
- Real-time preview with syntax highlighting
- Support for:
  - Code blocks with language-specific highlighting
  - Tables
  - Lists (ordered and unordered)
  - Images with drag-and-drop upload
  - Custom slide layouts

### Slide Management
- Slide CRUD operations via REST API
- Real-time slide updates using WebSocket
- Slide reordering with drag-and-drop
- Slide preview thumbnails
- Progress bar showing current position

### Presentation Mode
- Full-screen presentation view
- Keyboard navigation (arrow keys, space)
- Touch support for mobile devices
- Progress indicator
- Speaker notes support
- Custom transitions between slides

### State Management
- Pinia stores for:
  - User authentication
  - Presentation data
  - Slide editor state
  - UI preferences
- Persistent storage for user preferences
- Real-time state synchronization

### API Integration
- RESTful API calls to AWS backend
- WebSocket connection for real-time updates
- Automatic reconnection handling
- Error handling and retry logic
- Request caching for performance

### UI/UX Features
- Responsive design for all screen sizes
- Custom CSS with CSS variables for theming
- Keyboard shortcuts for common actions
- Loading states and error handling
- Toast notifications for user feedback
- Drag-and-drop file uploads
- Mobile-friendly touch interactions

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
1. CORS errors: The backend is already configured for CORS
2. WebSocket connection: Verify your network allows WebSocket connections
3. API connection: The backend URL is pre-configured, no changes needed
4. Build errors: Clear node_modules and reinstall

## Contributing

See the main project README for contribution guidelines.
