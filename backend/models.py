# backend/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Article(Base):
    """Article model for storing article information"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, index=True, nullable=False)
    title = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    summary_type = Column(String(50), default="comprehensive")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    summaries = relationship("Summary", back_populates="article")

    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...')>"

class Summary(Base):
    """Summary model for storing generated summaries"""
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    summary_text = Column(Text, nullable=False)
    key_points = Column(JSON, default=list)  # Store as JSON array
    summary_type = Column(String(50), default="comprehensive")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    article = relationship("Article", back_populates="summaries")

    def __repr__(self):
        return f"<Summary(id={self.id}, article_id={self.article_id}, type='{self.summary_type}')>"
