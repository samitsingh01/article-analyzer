# backend/schemas.py
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime

class ArticleCreate(BaseModel):
    """Schema for creating a new article"""
    url: HttpUrl = Field(..., description="URL of the article to summarize")
    summary_type: Optional[str] = Field("comprehensive", description="Type of summary: brief, comprehensive, or detailed")

    class Config:
        schema_extra = {
            "example": {
                "url": "https://example.com/article",
                "summary_type": "comprehensive"
            }
        }

class SummaryResponse(BaseModel):
    """Schema for summary response"""
    id: int
    summary_text: str = Field(..., description="Generated summary text")
    key_points: List[str] = Field(default_factory=list, description="Key points from the article")
    summary_type: str = Field(..., description="Type of summary")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "summary_text": "This article discusses...",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "summary_type": "comprehensive",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class ArticleResponse(BaseModel):
    """Schema for article response"""
    id: int
    url: str = Field(..., description="Original article URL")
    title: str = Field(..., description="Article title")
    summary_type: str = Field(..., description="Type of summary")
    summary: Optional[SummaryResponse] = Field(None, description="Generated summary")
    created_at: datetime = Field(..., description="Creation timestamp")

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "url": "https://example.com/article",
                "title": "Example Article Title",
                "summary_type": "comprehensive",
                "created_at": "2024-01-01T00:00:00Z"
            }
        }

class SearchQuery(BaseModel):
    """Schema for search queries"""
    query: str = Field(..., min_length=1, description="Search query")
    limit: Optional[int] = Field(5, ge=1, le=20, description="Number of results to return")

    class Config:
        schema_extra = {
            "example": {
                "query": "artificial intelligence trends",
                "limit": 5
            }
        }

class SearchResult(BaseModel):
    """Schema for search results"""
    article_id: int
    title: str
    url: str
    summary_excerpt: str
    similarity_score: float
    metadata: dict

    class Config:
        schema_extra = {
            "example": {
                "article_id": 1,
                "title": "AI Trends 2024",
                "url": "https://example.com/ai-trends",
                "summary_excerpt": "Recent developments in AI show...",
                "similarity_score": 0.85,
                "metadata": {"summary_type": "comprehensive"}
            }
        }
