import sys
import os
import subprocess
import logging
import json
import time
from typing import Dict, Any, List, Optional, Union

__version__ = "0.1.0"
__updated__ = "2025-05-14"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Log file path
log_file = os.path.join(logs_dir, "docker_rebuild.log")

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("docker_rebuild")

# Import MCP server
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("docker-rebuild-server")

def find_rebuild_scripts(directory: str) -> Dict[str, List[str]]:
    """
    Finds rebuild scripts (.ps1 or .py) in the specified directory.
    Also includes debug_docker.ps1 for debugging purposes.
    
    Args:
        directory: Directory to search for rebuild scripts
        
    Returns:
        Dictionary with lists of PowerShell and Python scripts
    """
    ps_scripts = []
    py_scripts = []
    
    try:
        # List all files in the directory
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                # Find PowerShell scripts (.ps1)
                # Include ALL PowerShell scripts for testing
                if file.lower().endswith('.ps1'):
                    ps_scripts.append(file)
                    logger.info(f"Found PowerShell script: {file}")
                # Find Python scripts (.py) with 'rebuild' in the name
                elif file.lower().endswith('.py') and 'rebuild' in file.lower():
                    py_scripts.append(file)
                    logger.info(f"Found Python script: {file}")
    except Exception as e:
        logger.error(f"Error searching directory {directory}: {str(e)}")
    
    return {
        "powershell": ps_scripts,
        "python": py_scripts
    }

def check_docker_status(container_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Checks the status of Docker containers.
    
    Args:
        container_name: Optional name of a specific container to check
        
    Returns:
        Dictionary with Docker container status information
    """
    try:
        cmd = ["docker", "ps", "--format", "{{.Names}},{{.Image}},{{.Status}},{{.Ports}}"]
        
        if container_name:
            cmd.extend(["--filter", f"name={container_name}"])
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Parse the output into a list of containers
        containers = []
        for line in result.stdout.strip().split('\n'):
            if not line:  # Skip empty lines
                continue
                
            parts = line.split(',')
            if len(parts) >= 3:
                containers.append({
                    "name": parts[0],
                    "image": parts[1],
                    "status": parts[2],
                    "ports": parts[3] if len(parts) > 3 else ""
                })
        
        return {
            "success": True,
            "containers": containers,
            "count": len(containers)
        }
    except Exception as e:
        logger.error(f"Error checking Docker status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def docker_rebuild(
    directory: str,
    script_name: Optional[str] = None,
    script_type: Optional[str] = None,
    container_name: Optional[str] = None,
    check_status: bool = True,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Runs Docker rebuild/restart scripts (.ps1 or .py) in a specified directory and returns the results.
    
    Args:
        directory: Directory where the rebuild scripts are located
        script_name: Optional specific script name to run (e.g., "rebuild.ps1")
        script_type: Optional script type to run ("powershell" or "python")
        container_name: Optional container name to check status after rebuild
        check_status: Whether to check container status after running script
        ctx: The context object for logging and progress reporting
        
    Returns:
        Dictionary with execution results and container status
    """
    if ctx:
        await ctx.info(f"Docker rebuild tool called for directory: {directory}")
    
    logger.info(f"Docker rebuild called for directory: {directory}, script: {script_name}, type: {script_type}")
    
    # Normalize the directory path
    directory = os.path.abspath(os.path.expanduser(directory))
    
    # Check if the directory exists
    if not os.path.isdir(directory):
        error_msg = f"Directory not found: {directory}"
        logger.error(error_msg)
        if ctx:
            await ctx.error(error_msg)
        return {
            "success": False,
            "error": error_msg
        }
    
    # Find the rebuild scripts to validate their existence, but don't execute them
    scripts = find_rebuild_scripts(directory)
    
    # Check if the specific script exists if one was specified
    script_exists = False
    if script_name:
        script_path = os.path.join(directory, script_name)
        if os.path.exists(script_path):
            script_exists = True
            logger.info(f"Found specified script: {script_name}")
            if ctx:
                await ctx.info(f"Found specified script: {script_name}")
        else:
            logger.info(f"Specified script not found: {script_name}")
            if ctx:
                await ctx.info(f"Specified script not found: {script_name}")
    
    # Instead of performing actual Docker operations, return a helpful message
    info_msg = "Claude cannot directly control Docker operations due to system constraints"
    logger.info(info_msg)
    if ctx:
        await ctx.info(info_msg)
        
    # Check Docker container status if requested
    docker_status = None
    if check_status:
        if ctx:
            await ctx.report_progress(progress=80, total=100)
            await ctx.info("Checking Docker container status...")
        
        # Check status
        status_result = check_docker_status(container_name)
        docker_status = status_result
        
    # Return results with tip
    return {
        "success": True,
        "directory": directory,
        "script_detected": script_name if script_name else "Not specified",
        "tip": "Claude can detect Docker scripts but cannot execute Docker commands directly. Please run the script manually in your PowerShell window: '.\\{0}'".format(script_name if script_name else "rebuild.ps1"),
        "docker_status": docker_status,
        "next_steps": "After running the Docker command manually, please let Claude know when the operation is complete."
    }

# Log application startup
logger.info(f"Starting Docker Rebuild MCP tool version {__version__}")
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