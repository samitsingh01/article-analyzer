# backend/rag_service.py
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import os
import logging
import uuid

logger = logging.getLogger(__name__)

class RAGService:
    """RAG service for article search and retrieval using ChromaDB"""
    
    def __init__(self):
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = int(os.getenv("CHROMA_PORT", 8000))
        self.client = None
        self.collection = None
        self.embedding_model = None
        
    async def initialize(self):
        """Initialize ChromaDB client and embedding model"""
        try:
            # Initialize ChromaDB client with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.client = chromadb.HttpClient(
                        host=self.chroma_host,
                        port=self.chroma_port,
                        settings=Settings(allow_reset=True)
                    )
                    
                    # Test connection by getting heartbeat
                    self.client.heartbeat()
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        logger.warning(f"ChromaDB connection attempt {attempt + 1} failed: {e}, retrying...")
                        import asyncio
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise e
            
            # Create or get collection
            self.collection = self.client.get_or_create_collection(
                name="articles",
                metadata={"description": "Article summaries and content for RAG"}
            )
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info("RAG service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            # Don't raise the error - allow the service to start without RAG
            self.client = None
            self.collection = None
            self.embedding_model = None
    
    async def add_article(
        self,
        article_id: int,
        content: str,
        summary: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Add article to the RAG system"""
        try:
            # Create document text combining content and summary
            document_text = f"Title: {metadata.get('title', 'Untitled')}\n\nSummary: {summary}\n\nContent: {content[:5000]}"  # Limit content size
            
            # Generate embedding
            embedding = self.embedding_model.encode(document_text).tolist()
            
            # Add to ChromaDB
            doc_id = f"article_{article_id}"
            
            self.collection.add(
                documents=[document_text],
                embeddings=[embedding],
                metadatas=[{
                    "article_id": article_id,
                    "title": metadata.get("title", ""),
                    "url": metadata.get("url", ""),
                    "summary_type": metadata.get("summary_type", ""),
                    "summary": summary[:1000]  # Store truncated summary in metadata
                }],
                ids=[doc_id]
            )
            
            logger.info(f"Added article {article_id} to RAG system")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add article {article_id} to RAG system: {e}")
            return False
    
    async def search(
        self,
        query: str,
        limit: int = 5,
        similarity_threshold: float = 0.3
    ) -> List[Dict[str, Any]]:
        """Search for similar articles"""
        try:
            if not self.collection:
                raise Exception("RAG service not initialized")
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Process results
            search_results = []
            
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    distance = results['distances'][0][i]
                    similarity_score = 1 - distance  # Convert distance to similarity
                    
                    if similarity_score >= similarity_threshold:
                        metadata = results['metadatas'][0][i]
                        
                        search_results.append({
                            "article_id": metadata.get("article_id"),
                            "title": metadata.get("title", "Untitled"),
                            "url": metadata.get("url", ""),
                            "summary_excerpt": metadata.get("summary", "")[:200] + "...",
                            "similarity_score": round(similarity_score, 3),
                            "metadata": {
                                "summary_type": metadata.get("summary_type", ""),
                            }
                        })
            
            logger.info(f"Found {len(search_results)} results for query: {query}")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    async def get_article_by_id(self, article_id: int) -> Optional[Dict[str, Any]]:
        """Get specific article from RAG system"""
        try:
            doc_id = f"article_{article_id}"
            
            results = self.collection.get(
                ids=[doc_id],
                include=['documents', 'metadatas']
            )
            
            if results['documents']:
                metadata = results['metadatas'][0]
                return {
                    "article_id": metadata.get("article_id"),
                    "title": metadata.get("title"),
                    "url": metadata.get("url"),
                    "document": results['documents'][0],
                    "metadata": metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get article {article_id}: {e}")
            return None
    
    async def delete_article(self, article_id: int) -> bool:
        """Delete article from RAG system"""
        try:
            doc_id = f"article_{article_id}"
            self.collection.delete(ids=[doc_id])
            
            logger.info(f"Deleted article {article_id} from RAG system")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete article {article_id}: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            count = self.collection.count()
            
            return {
                "total_articles": count,
                "collection_name": "articles"
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"total_articles": 0, "collection_name": "articles"}
