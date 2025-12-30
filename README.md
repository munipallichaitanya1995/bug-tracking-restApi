# IssueHub Backend API

A lightweight, production-ready bug tracking system backend built with FastAPI, PostgreSQL, and JWT authentication.

## 🚀 Tech Stack

### Core Technologies
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: ORM for database operations
- **SQLite**: Local development database (easily switchable to PostgreSQL)
- **Pydantic**: Data validation and serialization
- **JWT**: Secure token-based authentication
- **bcrypt**: Password hashing for security

### Key Dependencies
- `fastapi`: Web framework with automatic API documentation
- `sqlalchemy`: Database ORM with async support
- `python-jose[cryptography]`: JWT token handling
- `python-multipart`: Form data handling
- `bcrypt`: Secure password hashing

## 🏗️ Architecture

### Project Structure
```
backend/
├── main.py              # FastAPI application entry point
├── database.py          # Database connection and session management
├── models.py            # SQLAlchemy ORM models (UUID-based)
├── schemas.py           # Pydantic schemas for request/response validation
├── auth.py              # JWT authentication utilities
├── routers/             # API route handlers
│   ├── auth.py         # Authentication endpoints
│   ├── users.py        # User management
│   ├── projects.py     # Project CRUD operations
│   ├── issues.py       # Issue management
│   └── comments.py     # Comment system
├── seed.py              # Database seeding script
└── alembic/            # Database migrations
```

### Design Decisions & Trade-offs

#### UUID Primary Keys
**Choice**: UUID strings instead of auto-incrementing integers
- ✅ **Pros**: Globally unique, secure (no ID enumeration), scalable
- ❌ **Cons**: Slightly larger storage, not sequential

#### SQLite for Development
**Choice**: SQLite with easy PostgreSQL migration path
- ✅ **Pros**: Zero configuration, file-based, fast setup
- ❌ **Cons**: Limited concurrent connections, different SQL syntax

#### JWT Authentication
**Choice**: Stateless token-based auth over sessions
- ✅ **Pros**: Scalable, API-friendly, stateless
- ❌ **Cons**: Token refresh complexity, storage requirements

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🛠️ Setup Instructions

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=sqlite:///./issuehub.db

# Security
SECRET_KEY=your-super-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (for development)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Database Setup

```bash
# Create database tables
python main.py

# Seed with demo data (optional)
python seed.py
```

## 🚀 Running the Application

### Development Server

```bash
# Start FastAPI server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **Local**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc

### Production Deployment

```bash
# Using gunicorn (recommended for production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🧪 Testing

### Unit Tests (Not Implemented Yet)

```bash
# Run tests (when implemented)
pytest

# With coverage
pytest --cov=backend --cov-report=html
```

### Manual Testing

Use the interactive API documentation at `/docs` or test with curl:

```bash
# Health check
curl http://localhost:8000/

# API documentation
open http://localhost:8000/docs
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Users
- `GET /api/me` - Get current user profile
- `PUT /api/me` - Update current user profile

### Projects
- `GET /api/projects` - List user's projects
- `POST /api/projects` - Create new project
- `POST /api/projects/{id}/members` - Add project member
- `GET /api/projects/{id}/members` - List project members

### Issues
- `GET /api/projects/{id}/issues` - List project issues
- `POST /api/projects/{id}/issues` - Create new issue
- `GET /api/issues/{id}` - Get issue details
- `PATCH /api/issues/{id}` - Update issue
- `DELETE /api/issues/{id}` - Delete issue

### Comments
- `GET /api/issues/{id}/comments` - Get issue comments
- `POST /api/issues/{id}/comments` - Add comment to issue

## 🔒 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure, time-limited access tokens
- **CORS Protection**: Configurable origin restrictions
- **Input Validation**: Pydantic model validation
- **SQL Injection Prevention**: Parameterized queries

## 🐛 Known Limitations & Future Improvements

### Current Limitations

1. **Database**: SQLite limits concurrent connections
2. **Authentication**: No refresh token mechanism
3. **File Uploads**: No attachment support for issues
4. **Real-time**: No WebSocket support for live updates
5. **Testing**: No comprehensive test suite
6. **Caching**: No Redis/memcached integration
7. **Monitoring**: No application metrics/logging

### What I'd Do With More Time

#### High Priority
- **PostgreSQL Migration**: Production-ready database
- **Comprehensive Testing**: Unit, integration, and E2E tests
- **File Attachments**: Image/document uploads for issues
- **Email Notifications**: SMTP integration for updates
- **Advanced Filtering**: Saved filters, bulk operations

#### Medium Priority
- **Refresh Tokens**: Secure token refresh mechanism
- **Rate Limiting**: API rate limiting and abuse prevention
- **Audit Logging**: Track all user actions
- **API Versioning**: Support multiple API versions
- **Background Jobs**: Async task processing (Celery)

#### Nice to Have
- **WebSocket Support**: Real-time issue updates
- **Advanced Search**: Full-text search with Elasticsearch
- **API Analytics**: Usage tracking and insights
- **Multi-tenancy**: Organization/workspace support
- **Mobile API**: Optimized endpoints for mobile apps

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions or issues, please open a GitHub issue or contact the development team.
