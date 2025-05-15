import sys
import os
import logging
import json
import datetime
import httpx
import asyncio
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP, Context

__version__ = "0.1.4"
__updated__ = "2025-05-12"

# Setup logging
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)
log_file = os.path.join(logs_dir, "crawl4ai.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file)]
)
logger = logging.getLogger("crawl4ai")

# Utility for safe serialization
def safe_serialize(obj):
    try:
        return json.dumps(obj, default=str)
    except (TypeError, OverflowError, ValueError):
        return f"<Non-serializable: {type(obj).__name__}>"

# Initialize MCP server
mcp = FastMCP("crawl4ai-server")
DEFAULT_API_URL = "http://localhost:11235/crawl"

@mcp.tool()
async def crawl4ai(
    url: str, 
    query: str = None,
    enable_pruning: bool = False,
    pruning_threshold: float = 0.5,
    timeout: int = 60,
    exclude_social_media: bool = True,
    ctx: Context = None
) -> Dict[str, Any]:
    '''
    Crawls a URL and returns markdown content with preserved links.
    
    Args:
        url: The URL to crawl
        query: Optional query for content filtering
        enable_pruning: Whether to use pruning filter
        pruning_threshold: Threshold for pruning (0.0 to 1.0)
        timeout: Timeout in seconds
        exclude_social_media: Whether to exclude social media domains
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary with markdown content and preserved links
    '''
    request_id = ctx.request_id if ctx else f"req-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Log and validate inputs
    if ctx:
        await ctx.info(f"Crawling: {url}")
        await ctx.report_progress(progress=0, total=100)
    else:
        logger.info(f"[{request_id}] Crawling: {url}")
    
    if not url:
        return {"error": "No URL provided", "request_id": request_id}
    
    try:
        # Configure crawler with markdown always enabled
        crawler_config = {
            "type": "CrawlerRunConfig",
            "params": {
                "scraping_strategy": {"type": "WebScrapingStrategy", "params": {}},
                "stream": True,
                "markdown_generator": {
                    "type": "DefaultMarkdownGenerator",
                    "params": {
                        "options": {
                            "ignore_links": False,
                            "escape_html": True
                        }
                    }
                }
            }
        }
        
        # Add content filters if requested
        content_filters = []
        if query:
            content_filters.append({
                "type": "BM25ContentFilter",
                "params": {
                    "user_query": query,
                    "bm25_threshold": 1.2
                }
            })
        
        if enable_pruning:
            content_filters.append({
                "type": "PruningContentFilter",
                "params": {
                    "threshold": pruning_threshold,
                    "min_word_threshold": 50
                }
            })
        
        if content_filters:
            crawler_config["params"]["markdown_generator"]["params"]["content_filter"] = (
                content_filters[0] if len(content_filters) == 1 else content_filters
            )
        
        # Prepare request payload
        payload = {"urls": [url], "crawler_config": crawler_config}
        
        # Report progress
        if ctx:
            await ctx.debug("Starting request")
            await ctx.report_progress(progress=20, total=100)
        
        # Make API request
        async with httpx.AsyncClient() as client:
            response = await client.post(
                DEFAULT_API_URL,
                json=payload,
                timeout=timeout + 5  # Buffer
            )
            
            if ctx:
                await ctx.report_progress(progress=80, total=100)
            
            # Check response
            if response.status_code != 200:
                error_msg = f"API request failed: {response.status_code}"
                if ctx:
                    await ctx.error(error_msg)
                return {
                    "error": error_msg,
                    "status_code": response.status_code,
                    "request_id": request_id
                }
            
            # Parse response
            result_data = response.json()
            
            # Create simplified result (markdown only, no HTML)
            result = {
                "request_id": request_id,
                "url": url,
                "success": True,
                "title": None,
                "markdown": None,
                "links": []
            }
            
            # Check for empty results
            if not result_data or "results" not in result_data or not result_data["results"]:
                if ctx:
                    await ctx.warning("Empty results")
                result["success"] = False
                result["error"] = "No results returned"
                return result
            
            # Extract first result
            crawl_result = result_data["results"][0]
            
            # Check for crawl failure
            if not crawl_result.get("success", False):
                error_message = crawl_result.get("error_message", "Unknown error")
                if ctx:
                    await ctx.warning(f"Crawl failed: {error_message}")
                result["success"] = False
                result["error"] = error_message
                return result
            
            # Extract data
            result["title"] = crawl_result.get("title", "")
            
            # Extract markdown
            if "markdown" in crawl_result and crawl_result["markdown"]:
                markdown_data = crawl_result["markdown"]
                if isinstance(markdown_data, dict) and "raw_markdown" in markdown_data:
                    result["markdown"] = markdown_data.get("fit_markdown") or markdown_data.get("raw_markdown", "")
                else:
                    result["markdown"] = str(markdown_data)
            
            # Extract links
            if "links" in crawl_result and crawl_result["links"]:
                links = crawl_result["links"]
                if isinstance(links, list):
                    result["links"] = [link["href"] for link in links if isinstance(link, dict) and "href" in link]
            
            # Final progress
            if ctx:
                await ctx.report_progress(progress=100, total=100)
                await ctx.info(f"Complete: {len(result['markdown'] or '')} chars, {len(result['links'])} links")
            
            return result
    
    except asyncio.TimeoutError:
        error_msg = f"Timeout after {timeout} seconds"
        if ctx:
            await ctx.error(error_msg)
        return {"error": error_msg, "request_id": request_id, "success": False}
    
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        else:
            logger.error(f"[{request_id}] {error_msg}", exc_info=True)
        return {"error": error_msg, "request_id": request_id, "success": False}

# Start the MCP server
if __name__ == "__main__":
    try:
        logger.info(f"Starting Crawl4AI v{__version__}")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical(f"Failed to start: {str(e)}", exc_info=True)
        sys.exit(1)