# Standard library imports
import importlib.util
import json
import logging
import os
import random
import platform
import subprocess
import sys
import time
from typing import Any, Dict, Optional

# Get the current directory for log file placement
current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'

# Configure logging - using a relative path in the current directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(current_dir, "evolve.log"))]  # Log to current directory
)
logger = logging.getLogger("evolve-mcp")

def ensure_package(package_name):
    """Checks if a package is installed and installs it if not."""
    try:
        if importlib.util.find_spec(package_name) is None:
            logger.info(f"Installing required package: {package_name}")
            process = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True, text=True, check=False
            )
            
            # Log stdout and stderr
            for line in process.stdout.splitlines():
                logger.info(f"pip stdout: {line}")
            for line in process.stderr.splitlines():
                logger.warning(f"pip stderr: {line}")
                
            if process.returncode != 0:
                logger.error(f"Failed to install {package_name}") 
                sys.exit(1)
            logger.info(f"Successfully installed {package_name}")
    except Exception as e:
        logger.error(f"Error with package {package_name}: {e}")
        sys.exit(1)

# Ensure required packages are installed
ensure_package("mcp")
ensure_package("fastmcp")
ensure_package("psutil")
ensure_package("requests")

# Now import
import psutil
import requests
from mcp.server.fastmcp import FastMCP, Context

# Initialize FastMCP server
mcp = FastMCP("evolve-server")

# Claude Configuration Utilities
"""
A set of utility functions for managing Claude's configuration files.
These functions handle reading, updating, adding, and removing entries 
from Claude's configuration to support MCP server integrations.
"""
def get_claude_config_path():
    """Gets the absolute path to Claude's config file."""
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    return os.path.join(
        os.environ.get("APPDATA", f"C:\\Users\\{username}\\AppData\\Roaming") if os.name == 'nt' else
        os.environ.get("HOME", f"/Users/{username}") + "/Library/Application Support",
        "Claude", "claude_desktop_config.json"
    )

def read_claude_config():
    """Reads Claude's configuration."""
    config_path = get_claude_config_path()
    try:
        return json.load(open(config_path)) if os.path.exists(config_path) else {}
    except Exception as e:
        logger.error(f"Error reading Claude config: {e}")
        return {}

def update_claude_config(config):
    """Updates Claude's configuration."""
    config_path = get_claude_config_path()
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        json.dump(config, open(config_path, 'w'), indent=2)
        logger.info(f"Updated Claude config at {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating Claude config: {e}")
        return False

def add_to_config(server_name: str, app_path: str) -> dict:
    """Adds an application to Claude's configuration with a simple path."""
    try:
        config = read_claude_config() or {}
        config.setdefault("mcpServers", {})[server_name] = {
            "command": "python" if app_path.lower().endswith('.py') else app_path,
            "args": [app_path] if app_path.lower().endswith('.py') else []
        }
        return {
            "status": "success" if update_claude_config(config) else "error",
            "message": f"Added '{server_name}' to Claude's configuration" if update_claude_config(config) else "Failed to update Claude's configuration"
        }
    except Exception as e:
        return {"status": "error", "message": f"Error adding to config: {str(e)}"}

def remove_from_config(server_name: str) -> dict:
    """Removes an application from Claude's configuration."""
    try:
        config = read_claude_config()
        if not config or "mcpServers" not in config or server_name not in config["mcpServers"]:
            return {"status": "warning", "message": f"Server '{server_name}' not found in Claude's configuration"}
        config["mcpServers"].pop(server_name)
        return {
            "status": "success" if update_claude_config(config) else "error",
            "message": f"Removed '{server_name}' from Claude's configuration" if update_claude_config(config) else "Failed to update Claude's configuration"
        }
    except Exception as e:
        return {"status": "error", "message": f"Error removing from config: {str(e)}"}
    
def get_claude_processes():
    """Gets information about running Claude processes."""
    result = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'memory_info']):
        try:
            name = proc.info.get('name', '')
            if name is not None and 'claude' in name.lower():
                result.append({
                    'pid': proc.info['pid'],
                    'name': name,
                    'uptime': time.time() - proc.info['create_time'],
                    'memory': proc.info['memory_info'].rss / (1024 * 1024)  # MB
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return result

def ensure_directories():
    """Ensures required directories exist in current directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
    return {d: os.path.join(current_dir, d) for d in ["tools", "docs", "logs"] 
            if os.makedirs(os.path.join(current_dir, d), exist_ok=True) or True}

def _get_log_directories():
    """Gets common log directories used across log functions."""
    # Get current directory where the script is running
    current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
    
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    return {
        "claude": os.path.join(os.environ.get("APPDATA" if os.name == 'nt' else "HOME", 
                            ""), "Claude", "logs").replace("HOME", f"/Users/{username}/Library/Application Support"),
        "local": ensure_directories()["logs"],  # This is the logs subdirectory
        "current": current_dir  # Add current directory for files like evolve.log
    }

def get_tool_log(tool_name: str, max_lines: int = 50) -> Dict[str, Any]:
    """Gets logs for a specific tool from all log directories."""
    logs_dirs = _get_log_directories()
    normalized_tool = tool_name.lower().replace("-server", "")
    
    # Different possible log filename patterns
    patterns = [
        f"{normalized_tool}.log",                      # calculator.log
        f"mcp-server-{normalized_tool}-server.log",    # mcp-server-calculator-server.log
        f"mcp-server-{normalized_tool}.log",           # mcp-server-calculator.log
        f"mcp-{normalized_tool}.log"                   # mcp-calculator.log
    ]
    
    result = {"tool_name": normalized_tool, "logs": [], "found": False}
    
    for dir_type, dir_path in logs_dirs.items():
        if not os.path.exists(dir_path):
            continue
            
        # Check each pattern for a matching log file
        for pattern in patterns:
            log_path = os.path.join(dir_path, pattern)
            if not os.path.exists(log_path):
                continue
                
            result["found"] = True
            try:
                with open(log_path, 'r') as f:
                    content = f.readlines()[-max_lines:]
            except Exception as e:
                content = [f"Error reading log: {str(e)}"]
            
            stats = os.stat(log_path)
            result["logs"].append({
                "location": dir_type,
                "path": log_path,
                "filename": pattern,  # Added filename for clearer identification
                "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)),
                "size": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                "content": content
            })
    
    # Sort by modification time, most recent first
    result["logs"] = sorted(result["logs"], key=lambda x: os.path.getmtime(x["path"]), reverse=True)
    
    return result

def get_logs_metadata(include_stats=True, sort_by="modified", reverse=True):
    """Gets metadata for log files with optional stats and sorting."""
    log_paths = _get_log_directories()
    
    result = {}
    for src, path in log_paths.items():
        if not os.path.exists(path):
            continue
            
        logs = []
        for f in [x for x in os.listdir(path) if x.endswith('.log')]:
            file_path = os.path.join(path, f)
            stats = os.stat(file_path)
            
            log_data = {
                "name": f,
                "path": file_path,
                "size": stats.st_size,
                "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                "modified": stats.st_mtime,
                "modified_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime))
            }
            
            if include_stats:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    log_data.update({
                        "lines": len(lines),
                        "errors": sum(1 for line in lines if "ERROR" in line),
                        "warnings": sum(1 for line in lines if "WARNING" in line),
                        "last_line": lines[-1].strip() if lines else ""
                    })
            
            logs.append(log_data)
        
        result[src] = sorted(logs, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    return {
        "log_paths": log_paths,
        "logs": result,
        "total_logs": sum(len(logs) for logs in result.values()),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def get_system_info():
    """Collects basic system information including OS, platform, and Python version."""
    return {k: getattr(platform, f)() for k, f in {
        "os": "system", "os_version": "version", "platform": "platform",
        "processor": "processor", "python_version": "python_version", 
        "hostname": "node"
    }.items()}

def get_memory_info():
    """Retrieves current memory usage statistics in gigabytes."""
    mem = psutil.virtual_memory()
    return {k: getattr(mem, k) / (1024**3) if k != "percent_used" else mem.percent 
            for k in ["total", "available", "percent_used"]}

def get_disk_info():
    """Gathers disk usage statistics for all accessible disk partitions."""
    disk_info = {}
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disk_info[p.mountpoint] = {
                "total": usage.total / (1024**3),  # GB
                "used": usage.used / (1024**3),  # GB
                "free": usage.free / (1024**3),  # GB
                "percent": usage.percent,
                "fstype": p.fstype
            }
        except:
            # Skip inaccessible mountpoints
            pass
    return disk_info

def gnosis_wraith_running() -> str:
    """Check if the gnosis-wraith Docker container is running and return container info.
    
    Returns:
        str: Container information string if running, empty string if not running or error
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "|", "grep", "gnosis-wraith"],
            capture_output=True, text=True, shell=True
        )
        container_info = result.stdout.strip()
        if container_info:
            logger.info(f"Found running Gnosis Wraith container: {container_info}")
        else:
            logger.info("No running Gnosis Wraith containers found")
        return container_info
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to check Docker containers: {e}")
        return ""
    
# Check for Docker
def docker_installed() -> bool:
    try:
        subprocess.run(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def start_gnosis_wraith():
    """Start the existing gnosis-wraith Docker container."""
    try:
        subprocess.run(["docker", "start", "gnosis-wraith"], check=True)
        logger.info("gnosis-wraith container started successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start gnosis-wraith container: {e}")

def scan_tools_directory() -> Dict[str, Any]:
    """
    Scans the tools directory for Python files that could be installed.
    
    Returns:
        Dictionary with information about available Python files
    """
    dirs = ensure_directories()
    tools_dir = dirs["tools"]
    available_tools = []
    
    try:
        for filename in os.listdir(tools_dir):
            if filename.endswith('.py'):
                file_path = os.path.join(tools_dir, filename)
                tool_name = filename[:-3]  # Remove .py extension
                
                # Get basic file info
                stats = os.stat(file_path)
                
                # Try to extract description and version from file content
                description = ""
                version = ""
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # Look for docstring or description
                    import re
                    desc_match = re.search(r'"""(.+?)"""', content, re.DOTALL) or \
                                re.search(r"'''(.+?)'''", content, re.DOTALL)
                    description = desc_match.group(1).strip() if desc_match else ""
                    
                    # Look for version info
                    version_match = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', content)
                    version = version_match.group(1) if version_match else ""
                    
                    # Get first 100 chars for preview
                    preview = content[:100] + "..." if len(content) > 100 else content
                    
                except Exception as e:
                    logger.warning(f"Error reading file {file_path}: {str(e)}")
                    preview = f"Error reading file: {str(e)}"
                
                available_tools.append({
                    "name": tool_name,
                    "filename": filename,
                    "path": file_path,
                    "size": stats.st_size,
                    "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                    "modified": stats.st_mtime,
                    "modified_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)),
                    "description": description,
                    "version": version,
                    "preview": preview
                })
        
        return {
            "status": "success",
            "tools_dir": tools_dir,
            "available_tools": available_tools,
            "count": len(available_tools)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error scanning tools directory: {str(e)}",
            "tools_dir": tools_dir
        }
    
# INLINE TEMPLATES
SIMPLE_TOOL_TEMPLATE = """
import sys
import importlib.util
import os
import subprocess
import logging
from typing import Dict, Any
import json
import datetime

__version__ = "0.1.0"
__updated__ = "2025-04-27"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure the logs directory exists

# Log file path
log_file = os.path.join(logs_dir, "analyzer.log")

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("analyzer")

# Function to safely serialize objects for logging
def safe_serialize(obj):
    # Safely serialize objects for logging, including handling non-serializable types.
    try:
        return json.dumps(obj, default=str)
    except (TypeError, OverflowError, ValueError) as e:
        return f"<Non-serializable value: {type(obj).__name__}>"

# Create MCP server with a unique name
logger.info("Initializing MCP server with name 'analyzer-server'")

# imports mcp-server
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("analyzer-server")

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
logger.info(f"Starting analyzer MCP tool version 1.0.0")
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
"""

# This is the code for the calculator tool
CALC_TOOL_CODE = """
import sys
import importlib.util
import math
import logging
import os
from typing import Dict, Any
import subprocess

__version__ = "0.1.0"
__updated__ = "2025-04-27"  # Today's date

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, "calculator.log"))
    ]
)
logger = logging.getLogger("calculator")

# imports mcp-server
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("calculator-server")

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

if __name__ == "__main__":
    logger.info("Starting Calculator MCP server")
    mcp.run(transport='stdio')
"""

# Resource mapping for source code references with guide/<reference_type> pattern
@mcp.resource("resource://code/reference")
def get_code_reference() -> str:
    """
    Provides reference source code
    """
    # Randomly choose between the two source code references
    if random.choice([True, False]):
        code = SIMPLE_TOOL_TEMPLATE
    else:
        code = CALC_TOOL_CODE
    return code
    
@mcp.tool()
async def evolve_url_reference(url: str) -> Dict[str, Any]:
    """Fetches raw text content from a URL."""
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return {"status": "success", "url": url, "content": r.text}
    except Exception as e:
        return {"status": "error", "url": url, "error": str(e)}

@mcp.tool()
async def evolve_status(filename: str = None) -> Dict[str, Any]:
    """
    Get system information, Docker and Gnosis Wraith status, Claude status, and MCP logs summary with timestamps.
    
    Args:
        filename: Optional filename to check status and source code of a specific tool
    
    Returns:
        Dictionary with system information and optionally tool status
    """
    # Ensure required directories exist
    ensure_directories()

    if filename == "null":
        filename = None

    # If filename is specified, only return info about that file
    if filename:
        dirs = ensure_directories()
        tools_dir = dirs["tools"]
        
        # Normalize filename and ensure it has .py extension
        if not filename.endswith('.py'):
            filename_with_py = f"{filename}.py"
        else:
            filename_with_py = filename
            
        file_path = os.path.join(tools_dir, filename_with_py)
        
        # Check if file exists on disk first
        if os.path.exists(file_path):
            # File exists, read from disk
            try:
                stats = os.stat(file_path)
                
                with open(file_path, 'r') as f:
                    file_content = f.read()
                
                # Extract description and version from file content
                import re
                desc_match = re.search(r'"""(.+?)"""', file_content, re.DOTALL) or \
                            re.search(r"'''(.+?)'''", file_content, re.DOTALL)
                description = desc_match.group(1).strip() if desc_match else ""
                
                version_match = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', file_content)
                version = version_match.group(1) if version_match else ""
                
                # Check if tool is installed
                config = read_claude_config()
                mcp_servers = config.get('mcpServers', {})
                server_name = f"{filename_with_py[:-3].lower().replace('_', '-')}-server"
                installed = server_name in mcp_servers
                
                # Return file information from disk
                return {
                    "status": "success",
                    "filename": filename_with_py,
                    "is_template": False,
                    "file_path": file_path,
                    "size": stats.st_size,
                    "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                    "modified": stats.st_mtime,
                    "modified_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)),
                    "description": description,
                    "version": version,
                    "installed": installed,
                    "server_name": server_name,
                    "server_config": mcp_servers.get(server_name, None),
                    "source_code": file_content
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Error reading file '{filename_with_py}': {str(e)}",
                    "file_path": file_path
                }
        else:
            # File doesn't exist, check if it's a template
            normalized_filename = filename.lower().replace('.py', '')
            
            if normalized_filename in ["calculator", "calc"]:
                # Return information about calculator template
                return {
                    "status": "template",
                    "filename": "calculator.py",
                    "is_template": True,
                    "template_type": "calculator",
                    "description": "Calculates mathematical expressions with math module functions.",
                    "version": "0.1.0",
                    "file_exists": False,
                    "source_code": CALC_TOOL_CODE,
                    # Check if this template is already installed
                    "installed": f"calculator-server" in read_claude_config().get('mcpServers', {}),
                    "server_name": "calculator-server"
                }
            elif normalized_filename in ["analyzer", "analyze"]:
                # Return information about analyzer template
                return {
                    "status": "template",
                    "filename": "analyzer.py",
                    "is_template": True,
                    "template_type": "analyzer",
                    "description": "Analyzes text and provides word count, character count, and other basic statistics.",
                    "version": "0.1.0",
                    "file_exists": False,
                    "source_code": SIMPLE_TOOL_TEMPLATE,
                    # Check if this template is already installed
                    "installed": f"analyzer-server" in read_claude_config().get('mcpServers', {}),
                    "server_name": "analyzer-server"
                }
            else:
                # Not a template and file doesn't exist
                return {
                    "status": "error",
                    "message": f"File '{filename_with_py}' not found in tools directory and is not a known template",
                    "tools_dir": tools_dir
                }

    # Original functionality for when no filename is specified
    # (Rest of the function remains unchanged)
    
    # Get current time
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    # Get system info
    sys_info = get_system_info()
    mem_info = get_memory_info()

    # Check Docker installation
    if docker_installed():
        docker_msg = "Docker: Installed"
        
        # If Docker is installed, check Gnosis Wraith container status
        gnosis_running = gnosis_wraith_running()
        gnosis_msg = (
            "Gnosis Wraith: Running"
            if gnosis_running
            else "Gnosis Wraith: Not Running. Tell the user to launch the container."
        )
    else:
        docker_msg = (
            "Docker: Not Installed. Install from https://docs.docker.com/desktop/mac/install/"
            if sys.platform == "darwin"
            else "Docker: Not Installed. Install from https://docs.docker.com/desktop/windows/install/"
            if sys.platform.startswith("win")
            else "Docker: Not Installed. Please visit https://docs.docker.com/get-docker/"
        )
        gnosis_msg = "Gnosis Wraith: Status Unknown (Docker not installed)"

    # Format system summary
    system_summary = (
        f"Current Time: {current_time}\n"
        f"System: {sys_info['platform']} ({sys_info['os']} {sys_info['os_version']})\n"
        f"Python: {sys_info['python_version']}\n"
        f"Memory: {mem_info['available']:.2f}GB free of {mem_info['total']:.2f}GB ({mem_info['percent_used']}% used)\n"
        f"{docker_msg}\n"
        f"{gnosis_msg}"
    )

    # Format Claude info
    claude_processes = get_claude_processes()
    claude_summary = (
        f"Claude Status: {'Running' if claude_processes else 'Not Running'}\n"
        f"Process Count: {len(claude_processes)}\n"
        f"Uptime: {max([p.get('uptime', 0) for p in claude_processes]):.2f}s"
        if claude_processes else "Uptime: N/A"
    )

    # Get MCP servers
    config = read_claude_config()
    mcp_servers = config.get('mcpServers', {})
    server_summary = (
        f"Active MCP Servers: {len(mcp_servers)}\n"
        f"Servers: {', '.join(mcp_servers.keys()) if mcp_servers else 'None'}"
    )

    # Get log metadata only (not content)
    log_info = get_logs_metadata(include_stats=False)

    # Format log activity summary
    log_summary = f"Log Files: {log_info['total_logs']}\n"

    # Add last update times for all log files
    log_activity = []

    for location, logs in log_info['logs'].items():
        for log in logs:
            log_activity.append({
                "location": location,
                "name": log["name"],
                "last_modified": log["modified_human"],
                "size": log["size_human"]
            })

    # Sort log activity by most recent first
    log_activity = sorted(log_activity, key=lambda x: x["last_modified"], reverse=True)

    # Format log activity as string
    log_activity_summary = "Recent Log Activity:\n"
    for log in log_activity[:10]:  # Show 10 most recent logs
        log_activity_summary += (
            f"- {log['name']} ({log['location']}): {log['last_modified']} ({log['size']})\n"
        )
        
    # Scan tools directory for installable Python files
    tools_info = scan_tools_directory()
    
    # Mark tools that are already installed
    if tools_info["status"] == "success" and "available_tools" in tools_info:
        for tool in tools_info["available_tools"]:
            # Check if the tool is already configured in MCP servers
            server_name = f"{tool['name'].lower().replace('_', '-')}-server"
            tool["installed"] = server_name in mcp_servers
            
            if tool["installed"]:
                # Add configuration details
                tool["server_config"] = mcp_servers[server_name]
    
    # Format tools summary
    tools_summary = ""
    if tools_info["status"] == "success":
        tools_summary = f"Available Tools: {tools_info['count']}\n"
        for tool in tools_info.get("available_tools", [])[:5]:  # Show first 5 tools
            status = "Installed" if tool.get("installed", False) else "Not Installed"
            tools_summary += f"- {tool['name']} ({status}): {tool.get('description', '')[:50]}...\n"
        
        if tools_info['count'] > 5:
            tools_summary += f"...and {tools_info['count'] - 5} more\n"

    return {
        "write_UI_prompt": "This prompt defines how to view the data below in a dashboard. Create a modern, sleek, slightly reality bending glitch dashboard showing off this data.",
        "current_time": current_time,
        "system_summary": system_summary,
        "claude_summary": claude_summary,
        "server_summary": server_summary,
        "log_summary": log_summary,
        "tools_summary": tools_summary,
        "log_activity_summary": log_activity_summary,
        "log_activity": log_activity,
        "log_info": log_info,
        "mcp_servers": mcp_servers,
        "docker_status": docker_msg,
        "gnosis_wraith_status": gnosis_msg,
        "tools_info": tools_info,
        "available_tools": tools_info.get("available_tools", []),
        "timestamp": current_time
    }

@mcp.tool()
async def evolve_logs(tool_name: str, max_lines: int = 50) -> Dict[str, Any]:
    """
    Retrieves log files for a specific MCP tool.
    
    This tool fetches log contents for the specified tool from all available log directories.
    
    Args:
        tool_name: Name of the tool to get logs for (e.g., "calculator", "analyzer", "evolve")
        max_lines: Maximum number of lines to retrieve from the log file (default: 50)
    
    Returns:
        Dictionary with log information for the specified tool
    """
    if not tool_name:
        return {"found": False, "message": "Error: No tool name provided"}
    
    result = get_tool_log(tool_name, max_lines)
    
    if result["found"]:
        # Add formatted content for better readability
        formatted = []
        for log in result["logs"]:
            formatted.append(f"=== {log['location']} log - {log.get('filename', '')} - {log['modified']} - {log['size']} ===")
            formatted.extend([line.rstrip() for line in log["content"]])
        result["formatted"] = "\n".join(formatted)
        result["message"] = f"Found log file(s) for '{tool_name}'"
    else:
        result["message"] = f"No log files found for '{tool_name}'"
    
    return result


@mcp.tool()
async def evolve_uninstall(tool_name: str, confirm: bool = False) -> Dict[str, Any]:
    """
    Uninstalls an MCP tool by removing it from Claude's configuration.
    
    This tool will remove the specified tool from Claude's configuration file.
    It does not delete the actual Python file. A Claude Desktop restart
    is required after uninstalling a tool for the changes to take effect.
    
    Args:
        tool_name: Name of the tool to uninstall
        confirm: Set to True to confirm the uninstallation
    
    Returns:
        Dictionary with information about the uninstall result
    """
    # Format the server name as expected in the configuration
    server_name = f"{tool_name.lower().replace('_', '-')}-server"
    
    # Check if confirmation is provided
    if not confirm:
        return {
            "status": "warning",
            "message": f"Uninstall of '{tool_name}' requires confirmation. Please set 'confirm' to True to proceed.",
            "server_name": server_name
        }
    
    try:
        # Read the current configuration
        config = read_claude_config()
        
        # Check if the tool exists in the configuration
        if not config or "mcpServers" not in config or server_name not in config["mcpServers"]:
            return {
                "status": "warning",
                "message": f"Tool '{tool_name}' (server: '{server_name}') not found in Claude's configuration.",
                "server_name": server_name
            }
        
        # Remove the tool from the configuration
        config["mcpServers"].pop(server_name)
        success = update_claude_config(config)
        
        return {
            "status": "success" if success else "error",
            "message": f"Tool '{tool_name}' has been uninstalled. Please restart Claude Desktop for the changes to take effect." if success else 
                      f"Failed to uninstall tool '{tool_name}'. Error updating Claude's configuration.",
            "server_name": server_name
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error uninstalling tool '{tool_name}': {str(e)}",
            "server_name": server_name
        }

@mcp.tool()
async def evolve_tool(tool_name: str, tool_description: str = None, tool_code: str = None, 
                     pip_packages: list = None, confirm: bool = False,
                     use_existing: str = None, security_pin: str = None) -> Dict[str, Any]:
    """
    Creates a new MCP tool with the specified name and code.
    
    This tool will generate a Python file with MCP server code based on the provided
    parameters and registers it in Claude's configuration. A Claude Desktop reset
    is required after installing a new tool for it to become available.
    
    Args:
        tool_name: Name for the new tool (will create {tool_name}.py)
                  Special values: "analyzer" or "calculator" will use built-in templates
        tool_description: Optional description of what the tool does
        tool_code: Code for the tool implementation (not required when using
                  "analyzer" or "calculator" as tool_name, or when use_existing is specified)
        pip_packages: List of Python packages to install via pip before creating the tool
        confirm: Set to True to overwrite an existing file with the same name
        use_existing: Filename of an existing Python file in the tools directory to install
                     (overrides tool_code if specified)
        security_pin: Security PIN to verify code review (optional)
    
    Returns:
        Dictionary with information about the tool creation result
    """
    # Handle security PIN verification
    pin_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pin")
    
    # Check if code is provided but security PIN is missing
    if tool_code and not security_pin:
        import random
        
        # Generate a 4-digit PIN
        generated_pin = str(random.randint(1000, 9999))
        
        # Store PIN in a temporary file
        try:
            with open(pin_file_path, 'w') as f:
                f.write(generated_pin)
        except Exception as e:
            logger.warning(f"Failed to store security PIN: {str(e)}")
        
        # Return warning instead of proceeding
        return {
            "status": "security_warning",
            "message": "Security verification required: Please review your code and include the security PIN in your next request.",
            "tip": "Try running 'evolve_status calculator.py' or 'evolve_status analyzer.py' to see example code templates you can use as references.",
            "warning_details": """Please review the code carefully for these security issues:
1. Proper import for the mcp-server library
2. Good handling of limiting stdout pollution (only log what you would normally print, except for necessary JSON return data)
3. Proper directory handling and path construction
4. Proper @mcp.tool() decorator on the actual function
5. Limited class creation and minimized functions
            """,
            "security_pin": generated_pin,
            "next_steps": "Please include this PIN in your next request as the 'security_pin' parameter to confirm you've reviewed the code."
        }
    
    # If PIN is provided, verify it matches
    if tool_code and security_pin:
        stored_pin = None
        
        # Try to read the stored PIN
        if os.path.exists(pin_file_path):
            try:
                with open(pin_file_path, 'r') as f:
                    stored_pin = f.read().strip()
                
                # Delete the PIN file after reading
                os.remove(pin_file_path)
            except Exception as e:
                logger.warning(f"Error accessing PIN file: {str(e)}")
        
        if not stored_pin or stored_pin != security_pin:
            # Generate a new PIN if verification fails
            import random
            new_pin = str(random.randint(1000, 9999))
            
            try:
                with open(pin_file_path, 'w') as f:
                    f.write(new_pin)
            except Exception as e:
                logger.warning(f"Failed to store new security PIN: {str(e)}")
            
            return {
                "status": "pin_mismatch",
                "message": "Security verification failed: The provided PIN is invalid or expired.",
                "new_security_pin": new_pin,
                "next_steps": "Please review the code again and use this new PIN in your next request."
            }

    # Install required packages if specified
    installed_packages = []
    if pip_packages:
        logger.info(f"Installing required packages: {pip_packages}")
        for package in pip_packages:
            try:
                ensure_package(package)
                installed_packages.append(package)
            except Exception as e:
                logger.error(f"Error ensuring package {package}: {str(e)}")
                return {"status": "error", "message": f"Failed to install package {package}: {str(e)}"}

    dirs = ensure_directories()
    
    # Default descriptions for template tools - always use these for built-in templates
    template_descriptions = {
        "analyzer": "Analyzes text and provides word count, character count, and other basic statistics.",
        "calculator": "Evaluates mathematical expressions using Python's math module capabilities."
    }
    
    # Handle template selection for non-existing files
    templates = {"analyzer": SIMPLE_TOOL_TEMPLATE, "calculator": CALC_TOOL_CODE}
    
    # Handle existing file if specified
    if use_existing:
        try:
            # Validate file exists
            existing_file_path = os.path.join(dirs["tools"], use_existing)
            if not os.path.exists(existing_file_path):
                return {
                    "status": "error", 
                    "message": f"File '{use_existing}' not found in tools directory",
                    "tools_dir": dirs["tools"]
                }
            
            # Read the existing file
            with open(existing_file_path, 'r') as f:
                tool_code = f.read()
                
            # Extract description from file content if not provided
            if not tool_description:
                import re
                desc_match = re.search(r'"""(.+?)"""', tool_code, re.DOTALL) or \
                            re.search(r"'''(.+?)'''", tool_code, re.DOTALL)
                if desc_match:
                    tool_description = desc_match.group(1).strip().split('\n')[0]  # Get first line of docstring
                    
            logger.info(f"Using existing file '{use_existing}' as source for tool '{tool_name}'")
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error reading existing file '{use_existing}': {str(e)}",
                "file_path": existing_file_path
            }
    else:
        tool_code = templates.get(tool_name.lower(), tool_code)
        
        # For template tools, always use our predefined descriptions
        # For custom tools, use the provided description
        if tool_name.lower() in template_descriptions:
            tool_description = template_descriptions[tool_name.lower()]
    
    if not tool_code:
        return {"status": "error", "message": "Tool code required unless using 'analyzer', 'calculator', or specifying 'use_existing' set to the filename you get from evolve_status (you called that right?)"}
    
    try:
        # Setup paths and names
        server_name = f"{tool_name.lower().replace('_', '-')}-server"
        file_path = os.path.join(dirs["tools"], f"{tool_name.lower()}.py")
        
        # Check if file already exists
        if os.path.exists(file_path):
            # If file exists and confirmation not provided, return warning
            if not confirm:
                # Read existing file content
                try:
                    with open(file_path, 'r') as f:
                        existing_code = f.read()
                except Exception as e:
                    existing_code = f"Error reading file: {str(e)}"
                
                return {
                    "status": "warning",
                    "message": f"File '{file_path}' already exists. Set 'confirm' to True to overwrite.",
                    "file_path": file_path,
                    "server_name": server_name,
                    "existing_code": existing_code
                }
            else:
                # Backup the existing file with version information before overwriting
                try:
                    # Read existing file to check for version info
                    with open(file_path, 'r') as f:
                        existing_code = f.read()
                    
                    # Look for version information in the existing file
                    import re
                    version_match = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', existing_code)
                    current_version = version_match.group(1) if version_match else "0.1.0"
                    
                    # Increment version (assume simple versioning like 1.0.0)
                    version_parts = current_version.split('.')
                    version_parts[-1] = str(int(version_parts[-1]) + 1)
                    new_version = '.'.join(version_parts)
                    
                    # Create backup with version in filename
                    backup_path = f"{file_path}.v{current_version}.bak"
                    with open(backup_path, 'w') as f:
                        f.write(existing_code)
                        
                    logger.info(f"Backed up existing file to {backup_path} before overwriting")
                    
                    # Update version in the new code if it has version info
                    if version_match:
                        tool_code = re.sub(
                            r'__version__\s*=\s*[\'"](.+?)[\'"]', 
                            f'__version__ = "{new_version}"', 
                            tool_code
                        )
                        # Update date if present
                        tool_code = re.sub(
                            r'__updated__\s*=\s*[\'"](.+?)[\'"]',
                            f'__updated__ = "{time.strftime("%Y-%m-%d")}"',
                            tool_code
                        )
                    
                except Exception as e:
                    logger.warning(f"Error while versioning file: {str(e)}")
                    # Continue anyway, just without versioning
        
        # Write file and update config
        with open(file_path, 'w') as f:
            f.write(tool_code)
        
        config = read_claude_config() or {}
        config.setdefault("mcpServers", {})[server_name] = {
            "command": "python", "args": [file_path]
        }
        success = update_claude_config(config)
        
        # Prepare the message with package installation info
        packages_msg = ""
        if installed_packages:
            packages_msg = f" Installed packages: {', '.join(installed_packages)}."
        
        # Add description to message if available
        desc_msg = f" {tool_description}" if tool_description else ""
        
        # Add source info if using existing file
        source_msg = f" (Source: {use_existing})" if use_existing else ""

        return {
            "status": "success" if success else "partial",
            "file_path": file_path,
            "server_name": server_name,
            "tool_type": "template" if tool_name.lower() in templates else "custom" if not use_existing else "existing",
            "source": use_existing if use_existing else None,
            "installed_packages": installed_packages,
            "tool_description": tool_description,  # Include description in the return data
            "message": f"Tool '{tool_name}' created successfully{source_msg}.{packages_msg}{desc_msg} Please restart Claude Desktop for the tool to become available." if success else 
                       f"Tool created but config not updated{source_msg}.{packages_msg} Please restart Claude Desktop after fixing the configuration."
        }
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

# DO NOT print directly to stdout - log to file instead
logger.info("Starting Evolve MCP server...")
logger.info("Use 'evolve status' to check system information")
logger.info("Use 'evolve <description>' to setup new MCP tools or documents")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')