# backend/main.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Smart Article Summarizer",
    description="AI-powered article summarization with RAG capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import with error handling
try:
    from database import get_db, init_db
    from models import Article, Summary
    from schemas import ArticleCreate, ArticleResponse, SummaryResponse
    database_available = True
except ImportError as e:
    logger.error(f"Database import error: {e}")
    database_available = False

try:
    from summarizer_workflow import SummarizerWorkflow
    workflow_available = True
except ImportError as e:
    logger.error(f"Workflow import error: {e}")
    workflow_available = False

try:
    from rag_service import RAGService
    rag_available = True
except ImportError as e:
    logger.error(f"RAG service import error: {e}")
    rag_available = False

# Initialize services with error handling
summarizer_workflow = None
rag_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    global summarizer_workflow, rag_service
    
    try:
        if database_available:
            init_db()
            logger.info("Database initialized successfully")
        
        if workflow_available:
            summarizer_workflow = SummarizerWorkflow()
            logger.info("Summarizer workflow initialized")
        
        if rag_available:
            rag_service = RAGService()
            await rag_service.initialize()
            logger.info("RAG service initialized")
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        # Don't raise error to allow health check to work

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "message": "Smart Article Summarizer API is running",
        "services": {
            "database": database_available,
            "workflow": workflow_available,
            "rag": rag_available
        }
    }
    return status

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Article Summarizer API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if database_available:
    @app.post("/articles/", response_model=ArticleResponse)
    async def create_article(
        article_data: ArticleCreate,
        db: Session = Depends(get_db)
    ):
        """Create a new article and generate summary using LangGraph workflow"""
        try:
            if not workflow_available:
                raise HTTPException(status_code=503, detail="Summarizer workflow not available")
            
            logger.info(f"Processing article from URL: {article_data.url}")
            
            # Run LangGraph workflow to process article
            result = await summarizer_workflow.run(
                url=article_data.url,
                summary_type=article_data.summary_type or "comprehensive"
            )
            
            # Create article record
            article = Article(
                url=article_data.url,
                title=result["title"],
                content=result["content"],
                summary_type=article_data.summary_type or "comprehensive"
            )
            
            db.add(article)
            db.commit()
            db.refresh(article)
            
            # Create summary record
            summary = Summary(
                article_id=article.id,
                summary_text=result["summary"],
                key_points=result.get("key_points", []),
                summary_type=article_data.summary_type or "comprehensive"
            )
            
            db.add(summary)
            db.commit()
            db.refresh(summary)
            
            # Add to RAG system for future retrieval
            if rag_available and rag_service:
                await rag_service.add_article(
                    article_id=article.id,
                    content=result["content"],
                    summary=result["summary"],
                    metadata={
                        "title": result["title"],
                        "url": article_data.url,
                        "summary_type": article_data.summary_type or "comprehensive"
                    }
                )
            
            return ArticleResponse(
                id=article.id,
                url=article.url,
                title=article.title,
                summary_type=article.summary_type,
                summary=SummaryResponse(
                    id=summary.id,
                    summary_text=summary.summary_text,
                    key_points=summary.key_points,
                    summary_type=summary.summary_type,
                    created_at=summary.created_at
                ),
                created_at=article.created_at
            )
            
        except Exception as e:
            logger.error(f"Error processing article: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/articles/", response_model=List[ArticleResponse])
    async def get_articles(
        skip: int = 0,
        limit: int = 10,
        db: Session = Depends(get_db)
    ):
        """Get list of processed articles"""
        try:
            articles = db.query(Article).offset(skip).limit(limit).all()
            
            result = []
            for article in articles:
                summary = db.query(Summary).filter(
                    Summary.article_id == article.id
                ).first()
                
                article_response = ArticleResponse(
                    id=article.id,
                    url=article.url,
                    title=article.title,
                    summary_type=article.summary_type,
                    created_at=article.created_at
                )
                
                if summary:
                    article_response.summary = SummaryResponse(
                        id=summary.id,
                        summary_text=summary.summary_text,
                        key_points=summary.key_points,
                        summary_type=summary.summary_type,
                        created_at=summary.created_at
                    )
                
                result.append(article_response)
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching articles: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/articles/{article_id}", response_model=ArticleResponse)
    async def get_article(article_id: int, db: Session = Depends(get_db)):
        """Get specific article by ID"""
        try:
            article = db.query(Article).filter(Article.id == article_id).first()
            if not article:
                raise HTTPException(status_code=404, detail="Article not found")
            
            summary = db.query(Summary).filter(
                Summary.article_id == article_id
            ).first()
            
            article_response = ArticleResponse(
                id=article.id,
                url=article.url,
                title=article.title,
                summary_type=article.summary_type,
                created_at=article.created_at
            )
            
            if summary:
                article_response.summary = SummaryResponse(
                    id=summary.id,
                    summary_text=summary.summary_text,
                    key_points=summary.key_points,
                    summary_type=summary.summary_type,
                    created_at=summary.created_at
                )
            
            return article_response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error fetching article {article_id}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

if rag_available:
    @app.post("/search/")
    async def search_articles(query: Dict[str, Any]):
        """Search articles using RAG"""
        try:
            if not rag_service:
                raise HTTPException(status_code=503, detail="RAG service not available")
            
            search_query = query.get("query", "")
            limit = query.get("limit", 5)
            
            if not search_query:
                raise HTTPException(status_code=400, detail="Query is required")
            
            results = await rag_service.search(search_query, limit=limit)
            
            return {
                "query": search_query,
                "results": results
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Fallback endpoints when services are not available
if not database_available:
    @app.get("/articles/")
    async def get_articles_fallback():
        return {"error": "Database not available", "articles": []}

if not rag_available:
    @app.post("/search/")
    async def search_fallback():
        return {"error": "RAG service not available", "results": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8080))
    )
