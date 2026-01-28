# URL Shortener API

Production-ready URL shortener backend built with FastAPI, similar to TinyURL/Bitly.

![URL Shortener Logic](logic.png)

## Features

✅ **URL Shortening** - Generate short URLs using Base62 encoding  
✅ **URL Redirection** - Fast HTTP 302 redirects to original URLs  
✅ **Click Analytics** - Track clicks with async/non-blocking increments  
✅ **URL Normalization** - Consistent URL storage and deduplication  
✅ **Expiration Support** - Optional URL expiration timestamps  
✅ **CORS Enabled** - Cross-origin requests supported  
✅ **SQLite Database** - SQLAlchemy ORM with Alembic-ready models  
✅ **Docker Ready** - Multi-stage Dockerfile for production  
✅ **API Documentation** - Auto-generated Swagger/ReDoc docs  

## Project Structure

```
url-shortener/
├── app/
│   ├── __init__.py
│   ├── crud.py          # Database CRUD operations
│   ├── database.py      # Database configuration and session management
│   ├── main.py          # FastAPI application and endpoints
│   ├── models.py        # SQLAlchemy ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   └── utils.py         # Base62 encoding and URL utilities
├── .dockerignore        # Docker build exclusions
├── .env                 # Environment variables
├── .env.example         # Example environment configuration
├── .gitignore           # Git exclusions
├── Dockerfile           # Production Docker image
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env` under`app/env` and adjust if needed:

```bash
vim app/.env
```

### 3. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Docker Deployment

### Build the Image

```bash
docker build -t url-shortener .
```

### Run the Container

```bash
docker run -d \
  -p 8000:8000 \
  -e BASE_URL=http://yourdomain.com \
  --name url-shortener \
  url-shortener
```

## Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./url_shortener.db` | Database connection string |
| `BASE_URL` | `http://localhost:8000` | Base URL for shortened links |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |

## Technical Details

### Base62 Encoding

Uses Base62 (0-9, a-z, A-Z) for short codes, providing:
- 62^6 = 56+ billion possible combinations with 6-character codes
- URL-safe characters (no special encoding needed)
- Case-sensitive for maximum density

### URL Normalization

URLs are normalized before storage to prevent duplicates:
- Scheme and domain lowercased
- Trailing slashes removed
- Default ports (80, 443) removed

### Database Schema

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY,
    short_code VARCHAR(10) UNIQUE NOT NULL,
    long_url VARCHAR(2048) NOT NULL,
    clicks INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL
);

CREATE INDEX idx_short_code_created ON urls(short_code, created_at);
```

### Async Click Tracking

Click counts are incremented using FastAPI's `BackgroundTasks`, ensuring:
- Non-blocking redirects (fast response times)
- Reliable analytics tracking
- No impact on user experience

## Production Considerations

### Database Migration

For production, consider using PostgreSQL or MySQL:

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/urlshortener

# MySQL
DATABASE_URL=mysql+pymysql://user:password@localhost/urlshortener
```

Install the appropriate driver:
```bash
pip install psycopg2-binary  # PostgreSQL
# or
pip install pymysql          # MySQL
```

## License

MIT
