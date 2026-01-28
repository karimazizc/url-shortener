"""SQLAlchemy models for URL shortener."""

from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class URL(Base):
    """Model for storing URL mappings."""
    
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    long_url = Column(String(2048), nullable=False)
    short_code = Column(String(10), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    click_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<URL(short_code='{self.short_code}', clicks={self.click_count})>"
