import sys
import importlib.util
import subprocess
import logging
from typing import Dict, Any, Optional, Union

# Configure logging to file instead of stdout to avoid interfering with MCP JSON communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("wraith_crawler.log")]
)
logger = logging.getLogger("wraith_crawler")

# This function checks if a package is installed and installs it if needed
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            logger.info("Installing " + package_name)
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            # Log pip output to file instead of printing to stdout
            for line in stdout.splitlines():
                logger.info(line)
            if stderr:
                for line in stderr.splitlines():
                    logger.warning(line)
                    
            if process.returncode == 0:
                logger.info("Successfully installed " + package_name)
            else:
                logger.error("Failed to install " + package_name)
                sys.exit(1)
    except Exception as e:
        logger.error("Error with package " + package_name + ": " + str(e))
        sys.exit(1)

# Install required packages
ensure_package("mcp-server")
ensure_package("requests")

# Import MCP after ensuring it's installed
from mcp.server.fastmcp import FastMCP
import requests
import json

# Create MCP server with a unique name
mcp = FastMCP("wraith_crawler")

@mcp.tool()
async def crawl_url(
    url: str,
    javascript_enabled: bool = False,
    llm_provider: Optional[str] = None,
    llm_token: Optional[str] = None,
    output_format: str = "markdown"
) -> Dict[str, Any]:
    '''
    Crawl a URL with Gnosis Wraith and get the extracted text and optionally LLM summary.
    
    Args:
        url: The URL to crawl
        javascript_enabled: Whether to enable JavaScript for the crawl
        llm_provider: LLM provider to use for summarization (e.g., 'anthropic', 'openai')
        llm_token: API token for the LLM provider
        output_format: Format of the output ('markdown', 'text', 'html')
        
    Returns:
        dict: API response with crawl results
    '''
    if not url:
        return {
            "error": "No URL provided",
            "success": False
        }
    
    api_url = "http://localhost:5678/api/crawl"
    
    payload = {
        "url": url,
        "javascript_enabled": javascript_enabled,
        "output_format": output_format
    }
    
    # Add LLM configuration if provided
    if llm_provider and llm_token:
        payload["llm_provider"] = llm_provider
        payload["llm_token"] = llm_token
    
    try:
        logger.info(f"Sending crawl request for URL: {url}")
        response = requests.post(
            api_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            timeout=60  # Add a timeout to prevent indefinite waiting
        )
        
        if response.status_code != 200:
            logger.error(f"API returned non-200 status code: {response.status_code}")
            return {
                "error": f"API returned status code {response.status_code}",
                "response_text": response.text,
                "success": False
            }
        
        try:
            result = response.json()
            logger.info(f"Successfully crawled URL: {url}")
            
            # Add a success flag for easier handling
            result["success"] = True
            
            # Add a basic summary of results
            if "results" in result and isinstance(result["results"], list):
                result["summary"] = {
                    "urls_processed": len(result["results"]),
                    "total_content_length": sum(len(r.get("extracted_text", "")) for r in result["results"])
                }
            
            return result
        except json.JSONDecodeError:
            logger.error("Could not parse JSON response")
            return {
                "error": "Could not parse JSON response",
                "response_text": response.text[:1000],  # Include part of the response for debugging
                "success": False
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception during crawl: {str(e)}")
        return {
            "error": f"Request error: {str(e)}",
            "success": False
        }
    except Exception as e:
        logger.error(f"Unexpected error during crawl: {str(e)}")
        return {
            "error": f"Unexpected error: {str(e)}",
            "success": False
        }

# Log to file, NOT to stdout
logger.info("Starting wraith_crawler MCP tool")

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
