# Empyre Point

Empyre Point is a modern, collaborative PowerPoint-like web application that enables real-time presentation creation and editing. Built with Vue.js and Flask, it offers a seamless experience for creating, editing, and sharing presentations in the browser.

## 🚀 Project Overview

Empyre Point combines the power of modern web technologies to deliver a robust presentation platform:

- **Real-time Collaboration**: Multiple users can edit presentations simultaneously
- **Modern UI/UX**: Built with Vue 3 and Vite for a smooth, responsive interface
- **Robust Backend**: Flask-powered API with WebSocket support for real-time updates
- **Cloud Storage**: AWS S3 integration for media storage
- **Database**: PostgreSQL database with AWS RDS for reliable data persistence

## 📁 Project Structure

```
Empyre_Point/
├── Front_yrean/     # Vue 3 frontend application
├── Back_yrean/      # Flask backend service
└── package.json     # Root package configuration
```

## 🛠️ Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- PostgreSQL
- AWS Account (for S3 and RDS)

### Environment Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd Empyre_Point
```

2. Set up environment variables:
- Copy `.env.example` to `.env` in both frontend and backend directories
- Configure AWS credentials and database connection strings
- Set up necessary API keys and secrets

### Development Setup

The project consists of two main components that need to be set up separately:

1. **Frontend Setup** (`Front_yrean/`):
   - See [Frontend README](Front_yrean/README.md) for detailed setup instructions
   - Built with Vue 3 + Vite
   - Uses modern Vue 3 composition API

2. **Backend Setup** (`Back_yrean/`):
   - See [Backend README](Back_yrean/README.md) for detailed setup instructions
   - Flask-based REST API
   - WebSocket support for real-time features
   - Custom database migration system

## 🔧 Development

### Running the Development Environment

1. Start the backend server:
```bash
cd Back_yrean
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

2. Start the frontend development server:
```bash
cd Front_yrean
npm install
npm run dev
```

## 📚 Documentation

For detailed documentation about each component:

- [Frontend Documentation](Front_yrean/README.md)
- [Backend Documentation](Back_yrean/README.md)

## 🔐 Environment Variables

The project requires several environment variables to be configured. See the respective README files in each directory for detailed setup instructions.

Key environment variables include:
- Database connection strings
- AWS credentials
- API keys
- Secret keys

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Vue.js team for the amazing framework
- Flask team for the backend framework
- AWS for cloud services 