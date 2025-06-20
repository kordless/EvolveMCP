import sys
import os
import logging
import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
from mcp.server.fastmcp import FastMCP, Context
from urllib.parse import urlparse

__version__ = "1.0.0"
__updated__ = "2025-06-20"

# Setup logging
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir, "wraith_crawler.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file)]
)
logger = logging.getLogger("wraith_crawler")

# Initialize MCP server
mcp = FastMCP("wraith-crawler-server")

# Server URLs - using the new markdown API endpoint
LOCAL_SERVER_URL = "http://localhost:5678"
REMOTE_SERVER_URL = "https://wraith.nuts.services"

# Auth token file path
WRAITH_ENV_FILE = os.path.join(parent_dir, ".wraithenv")

def get_auth_token() -> Optional[str]:
    """Get auth token from .wraithenv file."""
    try:
        if os.path.exists(WRAITH_ENV_FILE):
            with open(WRAITH_ENV_FILE, 'r') as f:
                content = f.read().strip()
                if content.startswith('WRAITH_AUTH_TOKEN='):
                    return content.split('=', 1)[1].strip()
        return None
    except Exception as e:
        logger.error(f"Error reading auth token: {e}")
        return None

@mcp.tool()
async def set_wraith_auth_token(
    token: str,
    ctx: Context = None
) -> Dict[str, Any]:
    '''
    Set the Wraith API authentication token and save it to .wraithenv file.
    
    Args:
        token: The authentication token for Wraith API
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary with success status and message
    '''
    if not token:
        return {"success": False, "error": "No token provided"}
    
    try:
        # Save token to .wraithenv file
        with open(WRAITH_ENV_FILE, 'w') as f:
            f.write(f"WRAITH_AUTH_TOKEN={token}\n")
        
        logger.info("Wraith auth token saved successfully")
        return {
            "success": True, 
            "message": "Authentication token saved to .wraithenv file",
            "file_path": WRAITH_ENV_FILE
        }
    except Exception as e:
        error_msg = f"Error saving auth token: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def extract_domain(url: str) -> str:

    """Extract domain from URL."""
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except:
        return "unknown"

@mcp.tool()
async def wraith_crawler(
    url: str,
    take_screenshot: bool = True,
    javascript_enabled: bool = False,
    ocr_extraction: bool = False,
    markdown_extraction: str = "enhanced",
    server_url: str = None,
    title: str = None,
    timeout: int = 30,
    use_local_server: bool = False,
    ctx: Context = None
) -> Dict[str, Any]:
    '''
    Gnosis Wraith API crawler - returns raw markdown from Wraith API.
    
    Args:
        url: The URL to crawl
        take_screenshot: Whether to take a screenshot of the page
        javascript_enabled: Whether to enable JavaScript during crawling
        ocr_extraction: Whether to extract text using OCR (for images)
        markdown_extraction: Type of markdown extraction ("basic", "enhanced")
        server_url: URL of the Gnosis Wraith server (default: based on use_local_server)
        title: Custom title for the report (default: auto-generated from URL)
        timeout: Request timeout in seconds (default: 30)
        use_local_server: Whether to use local server (http://localhost:5678) instead of remote (default: False)
        ctx: Context object for logging and progress
        
    Returns:
        Raw dictionary response from Wraith API
    '''
    if not url:
        return {"success": False, "error": "No URL provided"}
    
    # Determine server URL
    if server_url:
        base_url = server_url
    else:
        base_url = LOCAL_SERVER_URL if use_local_server else REMOTE_SERVER_URL
    
    # Use the new markdown API endpoint
    endpoint = f"{base_url}/api/markdown"
    
    # Auto-generate title if not provided
    if not title:
        domain = extract_domain(url)
        title = f"Crawl: {domain}"

    try:
        # Prepare payload for the new markdown API
        payload = {
            "url": url,
            "javascript_enabled": javascript_enabled,
            "screenshot_mode": "full" if take_screenshot else None,
            # Note: OCR extraction is handled differently in the new API
            # markdown_extraction is now handled by the API automatically
        }
        
        # Add filter options if enhanced markdown is requested
        if markdown_extraction == "enhanced":
            payload["filter"] = "pruning"
            payload["filter_options"] = {
                "threshold": 0.48,
                "min_words": 2
            }
        
        logger.info(f"Crawling URL: {url} using endpoint: {endpoint}")
        logger.info(f"Payload: {payload}")
        
        # Prepare headers with auth token if available
        headers = {}
        auth_token = get_auth_token()
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            logger.info("Using authentication token")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                endpoint, 
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:

                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Successfully crawled {url}")
                    return result
                else:
                    error_text = await response.text()
                    error_msg = f"API request failed with status {response.status}: {error_text}"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}
    
    except asyncio.TimeoutError:
        error_msg = f"Request timeout after {timeout} seconds"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Error during crawl: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


@mcp.tool()
async def wraith_batch_crawler(
    urls: List[str],
    javascript_enabled: bool = False,
    take_screenshot: bool = False,
    async_mode: bool = True,
    collate: bool = False,
    collate_title: str = None,
    server_url: str = None,
    timeout: int = 60,
    use_local_server: bool = False,
    ctx: Context = None
) -> Dict[str, Any]:
    '''
    Batch crawl multiple URLs using the new Wraith API batch endpoint.
    
    Args:
        urls: List of URLs to crawl
        javascript_enabled: Whether to enable JavaScript during crawling
        take_screenshot: Whether to take screenshots
        async_mode: Whether to process asynchronously (True) or wait for completion (False)
        collate: Whether to merge all results into a single document
        collate_title: Title for the collated document
        server_url: URL of the Gnosis Wraith server
        timeout: Request timeout in seconds (default: 60)
        use_local_server: Whether to use local server instead of remote
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary with batch processing results
    '''
    if not urls:
        return {"success": False, "error": "No URLs provided"}
    
    if len(urls) > 50:
        return {"success": False, "error": "Maximum 50 URLs allowed per batch"}
    
    # Determine server URL
    if server_url:
        base_url = server_url
    else:
        base_url = LOCAL_SERVER_URL if use_local_server else REMOTE_SERVER_URL
    
    # Use the new markdown API endpoint
    endpoint = f"{base_url}/api/markdown"
    
    try:
        # Prepare payload for batch processing
        payload = {
            "urls": urls,
            "javascript_enabled": javascript_enabled,
            "screenshot_mode": "full" if take_screenshot else None,
            "async": async_mode,
            "collate": collate
        }
        
        # Add collation options if requested
        if collate:
            payload["collate_options"] = {
                "title": collate_title or f"Batch Crawl Results ({len(urls)} URLs)",
                "add_toc": True,
                "add_source_headers": True
            }
        
        logger.info(f"Batch crawling {len(urls)} URLs using endpoint: {endpoint}")
        logger.info(f"Async mode: {async_mode}, Collate: {collate}")
        
        # Prepare headers with auth token if available
        headers = {}
        auth_token = get_auth_token()
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            logger.info("Using authentication token for batch crawl")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                endpoint, 
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:

                
                if response.status in [200, 202]:  # 202 for async mode
                    result = await response.json()
                    logger.info(f"Successfully initiated batch crawl for {len(urls)} URLs")
                    return result
                else:
                    error_text = await response.text()
                    error_msg = f"Batch API request failed with status {response.status}: {error_text}"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}
    
    except asyncio.TimeoutError:
        error_msg = f"Batch request timeout after {timeout} seconds"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Error during batch crawl: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


@mcp.tool()
async def wraith_raw_html(
    url: str,
    javascript_enabled: bool = True,
    javascript_payload: str = None,
    server_url: str = None,
    timeout: int = 30,
    use_local_server: bool = False,
    ctx: Context = None
) -> Dict[str, Any]:
    '''
    Get raw HTML from a URL without markdown conversion or storage.
    
    Args:
        url: The URL to fetch
        javascript_enabled: Whether to enable JavaScript rendering
        javascript_payload: Optional JavaScript code to execute
        server_url: URL of the Gnosis Wraith server
        timeout: Request timeout in seconds
        use_local_server: Whether to use local server instead of remote
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary with raw HTML content
    '''
    if not url:
        return {"success": False, "error": "No URL provided"}
    
    # Determine server URL
    if server_url:
        base_url = server_url
    else:
        base_url = LOCAL_SERVER_URL if use_local_server else REMOTE_SERVER_URL
    
    # Use the raw HTML API endpoint
    endpoint = f"{base_url}/api/raw"
    
    try:
        payload = {
            "url": url,
            "javascript_enabled": javascript_enabled
        }
        
        if javascript_payload:
            payload["javascript_payload"] = javascript_payload
        
        logger.info(f"Fetching raw HTML from: {url}")
        
        # Prepare headers with auth token if available
        headers = {}
        auth_token = get_auth_token()
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
            logger.info("Using authentication token for raw HTML fetch")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                endpoint, 
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=timeout)
            ) as response:

                
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"Successfully fetched raw HTML from {url}")
                    return result
                else:
                    error_text = await response.text()
                    error_msg = f"Raw HTML API request failed with status {response.status}: {error_text}"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}
    
    except asyncio.TimeoutError:
        error_msg = f"Request timeout after {timeout} seconds"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Error fetching raw HTML: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


# Start the MCP server
if __name__ == "__main__":
    try:
        logger.info(f"Starting Enhanced Wraith Crawler v{__version__}")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical(f"Failed to start: {str(e)}", exc_info=True)
        sys.exit(1)

