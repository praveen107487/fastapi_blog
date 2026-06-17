# FastAPI Asynchronous Blog Engine

A modern, high-performance asynchronous blog platform built with **FastAPI**, **SQLAlchemy 2.0**, and **Pydantic v2**.

The project provides secure authentication, blog publishing workflows, image processing with AWS S3 integration, automated database migrations, server-side rendered templates, REST APIs, and a fully asynchronous testing infrastructure.

---

## 🌐 Live Deployment

**Application URL:** https://fastapi-blog-6n25.onrender.com/

| Service          | URL                                          |
| ---------------- | -------------------------------------------- |
| Live Application | https://fastapi-blog-6n25.onrender.com/      |
| Swagger UI       | https://fastapi-blog-6n25.onrender.com/docs  |
| ReDoc            | https://fastapi-blog-6n25.onrender.com/redoc |

> **Note:** The application is hosted on Render's free tier. Initial requests may take a few seconds if the service is waking from an idle state.

---

## 🚀 Features

### Asynchronous Database Layer

* Native async/await support using SQLAlchemy 2.0 Async Engine
* PostgreSQL integration via Psycopg 3
* Efficient transaction management and connection pooling

### Secure Authentication System

* OAuth2 Bearer Token authentication
* JWT access tokens
* Password hashing and verification
* User profile management
* Email-based password reset workflow

### Cloud Image Storage

* Avatar image processing using Pillow
* Automatic center-cropping and JPEG optimization
* AWS S3 uploads via Boto3
* Background thread execution for blocking operations

### Dual Frontend Architecture

* RESTful API endpoints
* Server-side rendered HTML using Jinja2 templates
* Static asset management (CSS, JavaScript, Icons)

### Database Migration Management

* Alembic-powered schema migrations
* Automatic migration generation
* Cross-platform async database support

### Comprehensive Testing

* Async integration and unit testing
* Pytest + AnyIO support
* HTTPX API testing
* AWS infrastructure mocking using Moto
* Transaction-safe database testing

---

# 🛠️ Tech Stack

| Category         | Technology                 |
| ---------------- | -------------------------- |
| Framework        | FastAPI                    |
| ORM              | SQLAlchemy 2.0 (Async)     |
| Database Driver  | Psycopg 3                  |
| Validation       | Pydantic v2                |
| Configuration    | Pydantic Settings          |
| Migrations       | Alembic                    |
| Image Processing | Pillow (PIL)               |
| Cloud Storage    | AWS S3 (Boto3)             |
| Package Manager  | UV                         |
| Testing          | Pytest, AnyIO, HTTPX, Moto |

---

# 📁 Project Structure

```text
fastapi_blog/
├── alembic/
│   ├── versions/
│   └── env.py
│
├── media/
│
├── routers/
│   ├── __init__.py
│   ├── post.py
│   └── users.py
│
├── static/
│   ├── css/
│   ├── icons/
│   └── js/
│
├── templates/
│   ├── email/
│   ├── account.html
│   ├── home.html
│   └── layout.html
│
├── tests/
│   ├── conftest.py
│   ├── test_image.jpg
│   ├── test_posts.py
│   └── test_users.py
│
├── auth.py
├── config.py
├── database.py
├── email_utils.py
├── image_utils.py
├── main.py
├── models.py
├── schemas.py
├── pyproject.toml
└── uv.lock
```

---

# ⚙️ Local Development Setup

## 1. Create and Activate Virtual Environment

```powershell
uv venv
.venv\Scripts\activate
```

---

## 2. Configure Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=postgresql+psycopg://postgres:your_local_password@localhost:5432/fastapi_blog

SECRET_KEY=your_super_secure_random_jwt_secret_key_string
ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
RESET_TOKEN_EXPIRE_MINUTES=60

FRONTEND_URL=http://127.0.0.1:8000

MAIL_SERVER=sandbox.smtp.mailtrap.io
MAIL_PORT=2525
MAIL_USERNAME=your_mailtrap_username
MAIL_PASSWORD=your_mailtrap_password
MAIL_FROM=noreply@gmail.com
MAIL_USE_TLS=True

S3_BUCKET_NAME=your-production-s3-bucket-name
S3_REGION=us-east-1
S3_ACCESS_KEY_ID=your_aws_access_key_id
S3_SECRET_ACCESS_KEY=your_aws_secret_access_key
S3_ENDPOINT_URL=https://s3.amazonaws.com
```

> **Note:** Ensure your `.env` file is included in `.gitignore`.

---

## 3. Install Dependencies

```powershell
uv sync
```

---

# 🗄️ Database Setup

## Create Databases

Using PostgreSQL:

```sql
CREATE DATABASE fastapi_blog;
CREATE DATABASE test_blog;
```

The `test_blog` database is used exclusively for automated tests.

---

## Apply Existing Migrations

```powershell
uv run alembic upgrade head
```

---

## Generate New Migrations

Whenever `models.py` changes:

```powershell
uv run alembic revision --autogenerate -m "describe schema changes"
uv run alembic upgrade head
```

---

# 🖥️ Running the Application

Start the development server with automatic reloading:

```powershell
uv run uvicorn main:app --reload
```

Application URLs:

| Service         | Local URL                   | Production URL                               |
| --------------- | --------------------------- | -------------------------------------------- |
| Web Application | http://127.0.0.1:8000       | https://fastapi-blog-6n25.onrender.com/      |
| Swagger UI      | http://127.0.0.1:8000/docs  | https://fastapi-blog-6n25.onrender.com/docs  |
| ReDoc           | http://127.0.0.1:8000/redoc | https://fastapi-blog-6n25.onrender.com/redoc |

---

# 🧪 Running Tests

The test suite uses:

* Moto for AWS S3 mocking
* HTTPX AsyncClient for API testing
* Transaction rollbacks for database isolation

Run the entire suite:

```powershell
uv run pytest
```

Run specific test modules:

```powershell
uv run pytest tests/test_posts.py -v

uv run pytest tests/test_users.py -v
```

Generate a coverage report:

```powershell
uv run pytest --cov=. --cov-report=term-missing
```

---

# ☁️ AWS S3 Storage Workflow

Uploaded user avatars are:

1. Validated
2. Center-cropped
3. Optimized as JPEG
4. Uploaded to AWS S3
5. Stored with generated object keys

Local storage can be used as a fallback when S3 is unavailable.

---

# 🔐 Authentication Flow

1. User Registration
2. Password Hashing
3. JWT Token Generation
4. OAuth2 Bearer Authentication
5. Protected Route Access
6. Password Reset via Email

---

# 📧 Email Services

Email functionality includes:

* Password reset emails
* Account notifications
* HTML email templates using Jinja2

SMTP configuration is handled through environment variables.

---

# 📜 License

This project is licensed under the MIT License.

Feel free to use, modify, and distribute it according to the license terms.
