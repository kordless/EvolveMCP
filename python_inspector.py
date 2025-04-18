
import sys
import os
import platform
import subprocess
import json
import logging
import importlib.util
from pathlib import Path
from typing import Dict, Any

# Configure logging to file instead of stdout to avoid interfering with MCP JSON communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("python_inspector.log")]
)
logger = logging.getLogger("python_inspector")

# Install required packages
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

ensure_package("mcp-server")
ensure_package("psutil")  # For system info

# Import MCP after ensuring it's installed
from mcp.server.fastmcp import FastMCP
import psutil

# Create MCP server
mcp = FastMCP("python_inspector")

def get_pip_packages():
    """Get installed pip packages and versions"""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True
        )
        packages = json.loads(result.stdout)
        return packages
    except Exception as e:
        logger.error(f"Error getting pip packages: {e}")
        return []

def get_process_info():
    """Get information about the current process"""
    try:
        current_process = psutil.Process()
        
        return {
            "pid": current_process.pid,
            "parent_pid": current_process.ppid(),
            "created_time": current_process.create_time(),
            "username": current_process.username(),
            "command_line": current_process.cmdline(),
            "cwd": current_process.cwd(),
            "parent_name": psutil.Process(current_process.ppid()).name() if current_process.ppid() else None,
            "memory_info": dict(current_process.memory_info()._asdict()),
            "num_threads": current_process.num_threads(),
            "status": current_process.status()
        }
    except Exception as e:
        logger.error(f"Error getting process info: {e}")
        return {"error": str(e)}

def get_sys_path_info():
    """Get detailed information about sys.path entries"""
    path_info = []
    for i, path in enumerate(sys.path):
        path_obj = Path(path)
        info = {
            "index": i,
            "path": path,
            "exists": path_obj.exists(),
            "is_dir": path_obj.is_dir() if path_obj.exists() else None,
            "is_file": path_obj.is_file() if path_obj.exists() else None,
            "is_absolute": path_obj.is_absolute(),
        }
        path_info.append(info)
    return path_info

@mcp.tool()
async def inspect_python() -> Dict[str, Any]:
    '''
    Inspects the Python environment and returns detailed information about the execution context.
    
    Returns:
        A dictionary with comprehensive information about the Python environment
    '''
    # Get environment variables
    env_vars = {k: v for k, v in os.environ.items()}
    
    # Get detailed sys.path information
    python_path_info = get_sys_path_info()
    
    # Get installed packages
    packages = get_pip_packages()
    
    # Get process information
    process_info = get_process_info()
    
    # Collect all information
    result = {
        # Python information
        "python_version": {
            "version": sys.version,
            "version_info": {
                "major": sys.version_info.major,
                "minor": sys.version_info.minor,
                "micro": sys.version_info.micro,
                "releaselevel": sys.version_info.releaselevel,
                "serial": sys.version_info.serial
            },
            "executable": sys.executable,
            "prefix": sys.prefix,
            "implementation": sys.implementation.name,
        },
        
        # Platform information
        "platform_info": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "architecture": platform.architecture(),
            "python_build": platform.python_build(),
            "python_compiler": platform.python_compiler(),
            "python_branch": platform.python_branch(),
            "python_implementation": platform.python_implementation(),
        },
        
        # System path information
        "sys_path_count": len(sys.path),
        "sys_path_detailed": python_path_info,
        
        # Process information
        "process_info": process_info,
        
        # Module information
        "modules_count": len(sys.modules),
        "module_search_path": sys.path,
        
        # Package information
        "installed_packages_count": len(packages),
        "installed_packages": packages,
        
        # Environment variables (selected ones related to Python and system)
        "environment_variables": {
            key: env_vars.get(key) for key in [
                "PATH", "PYTHONPATH", "PYTHONHOME", "PYTHONSTARTUP", 
                "PYTHONOPTIMIZE", "PYTHONDEBUG", "PYTHONVERBOSE",
                "PYTHONCASEOK", "PYTHONDONTWRITEBYTECODE", 
                "VIRTUAL_ENV", "CONDA_PREFIX", "USER", "HOME", "LANG",
                "SHELL", "TERM", "HOSTNAME", "PWD", "LOGNAME"
            ] if key in env_vars
        },
        
        # Current working directory
        "current_working_directory": os.getcwd(),
    }
    
    return result

logger.info("Starting python_inspector MCP tool")

if __name__ == "__main__":
    mcp.run(transport='stdio')
