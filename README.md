# FastAPI Blog

A simple blog application built with FastAPI, featuring user authentication, post creation, and a responsive Bootstrap 5 interface.

## Features

- User registration and login
- Create and view blog posts
- Responsive design with Bootstrap 5
- Dark mode support
- User profiles
- RESTful API endpoints

## Prerequisites

- Python 3.12 or higher
- uv (Python package installer) or pip

## Installation

### Using uv (recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi_blog
```

2. Install dependencies:
```bash
uv sync
```

3. Activate the virtual environment:
```bash
uv venv
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On Unix
```

### Using pip

1. Clone the repository:
```bash
git clone <repository-url>
cd fastapi_blog
```

2. Create a virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# or
source .venv/bin/activate  # On Unix
```

3. Install dependencies:
```bash
pip install fastapi uvicorn jinja2 python-multipart passlib python-jose
```

## Running the Application

Start the development server:

```bash
uvicorn main:app --reload
```

The application will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token

### Posts
- `GET /posts` - Get all posts
- `POST /api/posts` - Create a new post (requires authentication)
- `GET /api/users/me` - Get current user info (requires authentication)

### Pages
- `GET /` - Home page
- `GET /login` - Login page
- `GET /register` - Registration page
- `GET /account` - Account page
- `GET /posts/{post_id}` - Individual post page
- `GET /users/{user_id}/posts` - User's posts

## Project Structure

```
fastapi_blog/
├── main.py              # Main application file
├── pyproject.toml      # Project dependencies
├── static/             # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   ├── icons/
│   └── images/
└── templates/          # Jinja2 templates
    ├── layout.html     # Base template
    ├── home.html       # Home page
    ├── login.html      # Login page
    └── register.html   # Registration page
```

## Development Notes

This is a demonstration project using in-memory storage. For production use, consider:

- Adding a proper database (PostgreSQL, MySQL, SQLite)
- Implementing JWT token authentication with proper expiration
- Adding password hashing with bcrypt
- Implementing proper input validation and sanitization
- Adding unit and integration tests
- Setting up proper logging and error handling

## License

This project is open source and available under the MIT License.
