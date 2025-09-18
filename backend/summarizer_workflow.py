# backend/summarizer_workflow.py
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_aws import ChatBedrock
from langchain_core.messages import HumanMessage, SystemMessage
import requests
from bs4 import BeautifulSoup
from newspaper import Article
import os
import logging

logger = logging.getLogger(__name__)

class WorkflowState:
    """State management for the summarizer workflow"""
    def __init__(self):
        self.url: str = ""
        self.title: str = ""
        self.content: str = ""
        self.summary: str = ""
        self.key_points: List[str] = []
        self.summary_type: str = "comprehensive"
        self.error: str = ""

class SummarizerWorkflow:
    """LangGraph workflow for article summarization"""
    
    def __init__(self):
        # Set AWS credentials as environment variables
        if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            import boto3
            # Configure boto3 session with credentials
            session = boto3.Session(
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name=os.getenv("AWS_REGION", "us-east-1")
            )
            
        self.bedrock_llm = ChatBedrock(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
        )
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(dict)
        
        # Add nodes
        workflow.add_node("extract_content", self._extract_content)
        workflow.add_node("generate_summary", self._generate_summary)
        workflow.add_node("extract_key_points", self._extract_key_points)
        
        # Define edges
        workflow.add_edge("extract_content", "generate_summary")
        workflow.add_edge("generate_summary", "extract_key_points")
        workflow.add_edge("extract_key_points", END)
        
        # Set entry point
        workflow.set_entry_point("extract_content")
        
        return workflow.compile()
    
    async def run(self, url: str, summary_type: str = "comprehensive") -> Dict[str, Any]:
        """Run the summarization workflow"""
        try:
            initial_state = {
                "url": url,
                "summary_type": summary_type,
                "title": "",
                "content": "",
                "summary": "",
                "key_points": [],
                "error": ""
            }
            
            # Execute workflow
            result = await self.workflow.ainvoke(initial_state)
            
            if result.get("error"):
                raise Exception(result["error"])
            
            return {
                "title": result["title"],
                "content": result["content"],
                "summary": result["summary"],
                "key_points": result["key_points"]
            }
            
        except Exception as e:
            logger.error(f"Workflow execution error: {e}")
            raise
    
    async def _extract_content(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract content from the article URL"""
        try:
            url = state["url"]
            logger.info(f"Extracting content from: {url}")
            
            # Use newspaper3k for better content extraction
            article = Article(url)
            article.download()
            article.parse()
            
            if not article.text:
                # Fallback to requests + BeautifulSoup
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, timeout=10, headers=headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                # Try different content selectors
                content = ""
                for selector in ['article', 'main', '.content', '.post-content', '.entry-content', '.article-body']:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(strip=True, separator=' ')
                        break
                
                if not content:
                    # Get all paragraph text as fallback
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
                
                if not content:
                    content = soup.get_text(strip=True, separator=' ')
                
                # Clean up content
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                content = ' '.join(lines)
                
                title = soup.find('title')
                title = title.text.strip() if title else "Untitled Article"
                
                # Try to get better title from meta tags
                og_title = soup.find('meta', property='og:title')
                if og_title and og_title.get('content'):
                    title = og_title['content']
            else:
                content = article.text
                title = article.title or "Untitled Article"
            
            # Ensure content is not too long for Bedrock
            if len(content) > 100000:  # Limit to ~100k characters
                content = content[:100000] + "..."
            
            # Basic content validation
            if len(content.strip()) < 100:
                raise Exception("Article content too short or extraction failed")
            
            state["title"] = title
            state["content"] = content
            
            logger.info(f"Successfully extracted content. Title: {title}, Content length: {len(content)}")
            return state
            
        except Exception as e:
            error_msg = f"Content extraction failed: {str(e)}"
            logger.error(error_msg)
            state["error"] = error_msg
            return state
    
    async def _generate_summary(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary using AWS Bedrock"""
        try:
            if state.get("error"):
                return state
            
            content = state["content"]
            summary_type = state["summary_type"]
            
            # Define summary prompts based on type
            summary_prompts = {
                "brief": "Provide a brief 2-3 sentence summary of the main points.",
                "comprehensive": "Provide a comprehensive summary that covers all major points and key insights.",
                "detailed": "Provide a detailed summary with in-depth analysis and context."
            }
            
            prompt = summary_prompts.get(summary_type, summary_prompts["comprehensive"])
            
            messages = [
                SystemMessage(content=f"""You are an expert content summarizer. {prompt}
                
Guidelines:
- Focus on the most important information
- Maintain the original tone and context
- Be clear and concise
- Ensure factual accuracy"""),
                HumanMessage(content=f"Please summarize the following article:\n\nTitle: {state['title']}\n\nContent: {content}")
            ]
            
            response = await self.bedrock_llm.ainvoke(messages)
            summary = response.content
            
            state["summary"] = summary
            logger.info(f"Generated summary: {len(summary)} characters")
            
            return state
            
        except Exception as e:
            error_msg = f"Summary generation failed: {str(e)}"
            logger.error(error_msg)
            state["error"] = error_msg
            return state
    
    async def _extract_key_points(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key points from the content"""
        try:
            if state.get("error"):
                return state
            
            content = state["content"]
            
            messages = [
                SystemMessage(content="""You are an expert at extracting key points from articles. 
                Extract 3-7 key points from the content. Each point should be:
                - A complete, standalone insight
                - Clear and concise (1-2 sentences max)
                - Covering different aspects of the article
                
                Return only the key points as a JSON array of strings."""),
                HumanMessage(content=f"Extract key points from this article:\n\nTitle: {state['title']}\n\nContent: {content}")
            ]
            
            response = await self.bedrock_llm.ainvoke(messages)
            
            # Parse the response to extract key points
            try:
                import json
                key_points = json.loads(response.content)
                if not isinstance(key_points, list):
                    raise ValueError("Response is not a list")
            except:
                # Fallback: split by lines and clean up
                lines = response.content.strip().split('\n')
                key_points = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('[') and not line.startswith(']'):
                        # Clean up common prefixes
                        line = line.lstrip('- •*').strip()
                        if line.startswith('"') and line.endswith('"'):
                            line = line[1:-1]
                        if line:
                            key_points.append(line)
                
                # Limit to 7 points
                key_points = key_points[:7]
            
            state["key_points"] = key_points
            logger.info(f"Extracted {len(key_points)} key points")
            
            return state
            
        except Exception as e:
            error_msg = f"Key points extraction failed: {str(e)}"
            logger.error(error_msg)
            # Don't fail the whole workflow for key points
            state["key_points"] = []
            return state
