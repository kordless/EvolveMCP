
import sys
import importlib.util
import os
import subprocess
import logging
from typing import Dict, Any
import json
import datetime
import math

__version__ = "0.1.2"
__updated__ = "2025-05-13"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure the logs directory exists

# Log file path
log_file = os.path.join(logs_dir, "math_and_stats.log")

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("math-and-stats")

# Function to safely serialize objects for logging
def safe_serialize(obj):
    # Safely serialize objects for logging, including handling non-serializable types.
    try:
        return json.dumps(obj, default=str)
    except (TypeError, OverflowError, ValueError) as e:
        return f"<Non-serializable value: {type(obj).__name__}>"

# Create MCP server with a unique name
logger.info("Initializing MCP server with name 'math-and-stats-server'")

# imports mcp-server
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("math-and-stats-server")

@mcp.tool()
async def calculator(expression: str) -> Dict[str, Any]:
    '''
    Calculates mathematical expressions with math module functions.
    
    Args:
        expression: Math expression (e.g., "2 + 3 * 4", "sqrt(16) + pi")
    
    Returns:
        Dictionary with result or error information
    '''
    logger.info(f"Processing expression: {expression}")
    
    # Safe math functions dictionary
    allowed_names = {
        'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e,
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'log': math.log, 'log10': math.log10, 'exp': math.exp,
        'pow': math.pow, 'ceil': math.ceil, 'floor': math.floor,
        'factorial': math.factorial, 'abs': abs,
        'round': round, 'max': max, 'min': min
    }

    try:
        expression = expression.replace('^', '**')  # Support ^ for powers
        logger.info(f"Evaluating expression after replacement: {expression}")
        result = eval(expression, {"__builtins__": None}, allowed_names)
        logger.info(f"Calculation result: {result}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Calculation failed: {str(e)}")
        return {"success": False, "error": "Calculation failed", "reason": str(e)}

# Define your tool with the @mcp.tool() decorator and Context parameter
@mcp.tool()
async def analyzer(text: str = None, ctx: Context = None) -> Dict[str, Any]:
    '''
    Analyzes text and returns basic statistics.
    
    Args:
        text: The text to analyze
        ctx: The context object for logging and progress reporting
        
    Returns:
        A dictionary with text analysis statistics
    '''
    # Use the request_id from the context
    request_id = ctx.request_id if ctx else f"req-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{id(text)}"
    
    # Log input details using context
    if ctx:
        await ctx.info(f"Analyzer tool called with request ID: {request_id}")
    else:
        logger.info(f"[{request_id}] Analyzer tool called (no context provided)")
    
    # Validate input
    if not text:
        if ctx:
            await ctx.warning(f"No text provided for analysis")
        else:
            logger.warning(f"[{request_id}] No text provided for analysis")
        
        return {
            "error": "No text provided",
            "request_id": request_id
        }
    
    # Log input sample
    text_sample = text[:100] + "..." if len(text) > 100 else text
    if ctx:
        await ctx.info(f"Input text sample: {text_sample}")
        await ctx.debug(f"Input text length: {len(text)} chars")
    else:
        logger.info(f"[{request_id}] Input text sample: {text_sample}")
        logger.debug(f"[{request_id}] Input text length: {len(text)} chars")
    
    try:
        # Log the start of processing
        if ctx:
            await ctx.debug("Starting text analysis")
            # Report initial progress
            await ctx.report_progress(progress=0, total=100)
        else:
            logger.debug(f"[{request_id}] Starting text analysis")
        
        # Basic text analysis - Part 1
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        # Report progress
        if ctx:
            await ctx.report_progress(progress=30, total=100)
        
        # Basic text analysis - Part 2
        sentences = text.count('.') + text.count('!') + text.count('?')
        sentences = max(1, sentences)  # Ensure at least 1 sentence
        
        # Calculate average word and sentence length
        avg_word_length = char_count / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentences if sentences > 0 else 0
        
        # Report progress
        if ctx:
            await ctx.report_progress(progress=60, total=100)
            await ctx.debug(f"Calculated basic metrics: {word_count} words, {char_count} chars, {sentences} sentences")
        
        # Process text to uppercase (simulating more complex processing)
        uppercase_text = text.upper()
        
        # Final progress report
        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Analysis complete: {word_count} words, {char_count} characters")
        else:
            logger.info(f"[{request_id}] Analysis complete: {word_count} words, {char_count} characters")
        
        # Create result dictionary
        result = {
            "request_id": request_id,
            "word_count": word_count,
            "character_count": char_count,
            "sentence_count": sentences,
            "avg_word_length": round(avg_word_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "uppercase": uppercase_text
        }
        
        # Log the result
        if ctx:
            await ctx.debug(f"Returning result: {safe_serialize(result)}")
        else:
            logger.debug(f"[{request_id}] Returning result: {safe_serialize(result)}")
        
        return result
    
    except Exception as e:
        # Log any exceptions that occur during processing
        if ctx:
            await ctx.error(f"Error during text analysis: {str(e)}")
        else:
            logger.error(f"[{request_id}] Error during text analysis: {str(e)}", exc_info=True)
        
        return {
            "error": "Analysis failed",
            "reason": str(e),
            "request_id": request_id
        }

# Log application startup
logger.info(f"Starting math and stats MCP tool version 1.0.0")
logger.info(f"Logging to: {log_file}")
logger.info(f"Python version: {sys.version}")

# Start the MCP server
if __name__ == "__main__":
    try:
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical(f"Failed to start MCP server: {str(e)}", exc_info=True)
        sys.exit(1)
