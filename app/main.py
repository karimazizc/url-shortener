"""FastAPI URL Shortener Application."""

import os
from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database import get_db, init_db
from app.models import URL
from app.utils import generate_short_code, is_valid_url, normalize_url

# Load environment variables
load_dotenv()

# Configuration
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Initialize FastAPI app
app = FastAPI(
    title="URL Shortener",
    description="A simple URL shortener built with FastAPI",
    debug=DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request, short_url: str = None, error: str = None):
    """
    Render the home page with URL shortening form.
    
    Args:
        request: FastAPI request object
        short_url: Generated short URL to display (optional)
        error: Error message to display (optional)
    """
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "short_url": short_url,
            "error": error,
            "base_url": BASE_URL
        }
    )


@app.post("/shorten", response_class=HTMLResponse)
async def shorten_url(
    request: Request,
    long_url: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Create a shortened URL.
    
    Args:
        request: FastAPI request object
        long_url: The original URL to shorten
        db: Database session
    """
    # Validate URL format
    normalized_url = normalize_url(long_url.strip())
    
    if not is_valid_url(normalized_url):
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Invalid URL format. Please enter a valid URL.",
                "long_url": long_url,
                "base_url": BASE_URL
            }
        )
    
    # Check if URL already exists
    existing = db.query(URL).filter(URL.long_url == normalized_url).first()
    if existing:
        short_url = f"{BASE_URL}/{existing.short_code}"
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "short_url": short_url,
                "short_code": existing.short_code,
                "base_url": BASE_URL
            }
        )
    
    # Generate unique short code
    max_attempts = 10
    for _ in range(max_attempts):
        short_code = generate_short_code()
        # Check if code already exists
        if not db.query(URL).filter(URL.short_code == short_code).first():
            break
    else:
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Failed to generate unique short code. Please try again.",
                "base_url": BASE_URL
            }
        )
    
    # Create new URL record
    new_url = URL(long_url=normalized_url, short_code=short_code)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    
    short_url = f"{BASE_URL}/{short_code}"
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "short_url": short_url,
            "short_code": short_code,
            "base_url": BASE_URL
        }
    )


@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request, db: Session = Depends(get_db)):
    """
    Display click analytics for all URLs.
    
    Args:
        request: FastAPI request object
        db: Database session
    """
    urls = db.query(URL).order_by(URL.click_count.desc()).limit(50).all()
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "urls": urls,
            "base_url": BASE_URL
        }
    )


@app.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Redirect to the original URL.
    
    Args:
        short_code: The short code to look up
        request: FastAPI request object
        db: Database session
    """
    # Look up short code
    url_record = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url_record:
        # Return 404 page
        return templates.TemplateResponse(
            "404.html",
            {
                "request": request,
                "short_code": short_code,
                "base_url": BASE_URL
            },
            status_code=404
        )
    
    # Increment click count
    url_record.click_count += 1
    db.commit()
    
    # Redirect to original URL
    return RedirectResponse(url=url_record.long_url, status_code=302)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=DEBUG)
