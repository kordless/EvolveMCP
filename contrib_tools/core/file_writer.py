
import sys
import os
import json
import logging
import re
import time
import shutil
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

__version__ = "0.1.2"
__updated__ = "2025-05-13"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure the logs directory exists

# Log file path
log_file = os.path.join(logs_dir, "file_writer.log")

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("file_writer")

# Import MCP server library
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("file-writer-server")

def ensure_version_dir(file_path: str) -> str:
    """
    Ensures that a versions directory exists for the given file.
    The versions directory is stored alongside the file with the name 
    '.{filename}_versions'.
    
    Args:
        file_path: Path to the file for which to create a versions directory
    
    Returns:
        Path to the versions directory
    """
    # Get the directory and filename from the file path
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
    # Create the versions directory name
    versions_dir = os.path.join(directory, f".{filename}_versions")
    
    # Make sure the versions directory exists
    os.makedirs(versions_dir, exist_ok=True)
    
    return versions_dir

def get_file_versions(file_path: str) -> List[Dict[str, Any]]:
    """
    Gets information about all versions of a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        List of dictionaries with version information
    """
    versions = []
    
    if not os.path.exists(file_path):
        return versions  # File doesn't exist, no versions
    
    # Get the versions directory
    versions_dir = ensure_version_dir(file_path)
    
    # If no versions directory exists yet, return just the current file
    if not os.path.exists(versions_dir):
        return versions
    
    # Get all version files from the versions directory
    try:
        version_files = [f for f in os.listdir(versions_dir) if os.path.isfile(os.path.join(versions_dir, f))]
        
        # Extract version information from filenames
        for version_file in version_files:
            # Parse version info from filename
            # Format is "v{version_number}_{timestamp}.backup" 
            match = re.match(r"v(\d+)_(\d+)\.backup", version_file)
            if match:
                version_number = int(match.group(1))
                timestamp = int(match.group(2))
                
                # Get file stats
                version_path = os.path.join(versions_dir, version_file)
                stats = os.stat(version_path)
                
                # Add version info to the list
                versions.append({
                    "version": version_number,
                    "timestamp": timestamp,
                    "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "size": stats.st_size,
                    "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                    "path": version_path
                })
    except Exception as e:
        logger.error(f"Error getting versions for {file_path}: {str(e)}")
    
    # Sort versions by version number (descending)
    versions.sort(key=lambda x: x["version"], reverse=True)
    
    # Add current file as the latest version
    if os.path.exists(file_path):
        stats = os.stat(file_path)
        versions.insert(0, {
            "version": "current",
            "timestamp": int(stats.st_mtime),
            "date": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "size": stats.st_size,
            "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
            "path": file_path
        })
    
    return versions

def get_next_version_number(file_path: str) -> int:
    """
    Gets the next version number for a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Next version number
    """
    versions = get_file_versions(file_path)
    
    # Filter out the current version
    past_versions = [v for v in versions if v["version"] != "current"]
    
    if not past_versions:
        return 1  # First version
    
    # Get the highest version number
    highest_version = max(v["version"] for v in past_versions)
    
    return highest_version + 1

def create_file_backup(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Creates a backup of the file if it exists.
    
    Args:
        file_path: Path to the file to back up
    
    Returns:
        Dictionary with backup information or None if no backup was created
    """
    if not os.path.exists(file_path):
        return None  # File doesn't exist, no backup needed
    
    # Get the versions directory
    versions_dir = ensure_version_dir(file_path)
    
    # Get the next version number
    version_number = get_next_version_number(file_path)
    
    # Create a timestamp
    timestamp = int(time.time())
    
    # Create the backup filename
    backup_filename = f"v{version_number}_{timestamp}.backup"
    backup_path = os.path.join(versions_dir, backup_filename)
    
    try:
        # Copy the file to the backup location
        shutil.copy2(file_path, backup_path)
        
        # Get file stats
        stats = os.stat(backup_path)
        
        return {
            "version": version_number,
            "timestamp": timestamp,
            "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "size": stats.st_size,
            "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
            "path": backup_path
        }
    except Exception as e:
        logger.error(f"Error creating backup for {file_path}: {str(e)}")
        return None

@mcp.tool()
async def file_writer(
    action: str,
    file_path: str,
    content: Union[str, Dict, List, Any] = None,
    version: str = None,
    create_backup: bool = True,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Creates, writes, and reads files with automatic versioning support.
    
    Args:
        action: Action to perform ('write', 'read', 'list_versions', 'restore')
        file_path: Path to the file to operate on
        content: Content to write to the file (only for 'write' action)
        version: Version to read or restore (only for 'read' and 'restore' actions)
        create_backup: Whether to create a backup when writing (only for 'write' action)
        encoding: Text encoding to use when reading/writing files (default: utf-8)
    
    Returns:
        Dictionary with operation results
    """
    logger.info(f"file_writer called with action={action}, file_path={file_path}")

    # Normalize the file path
    file_path = os.path.abspath(os.path.expanduser(file_path))
    
    # Handle the requested action
    if action == "write":
        # Writing a file with optional backup
        try:
            # Check if the file already exists
            file_exists = os.path.exists(file_path)
            
            # Create a backup if requested and the file exists
            backup_info = None
            if file_exists and create_backup:
                backup_info = create_file_backup(file_path)
                logger.info(f"Created backup for {file_path}: {backup_info}")
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Process content based on its type
            write_content = content
            if not isinstance(content, str):
                # If content is not a string (likely a dictionary or list), convert to JSON string
                logger.info(f"Converting content type {type(content)} to JSON string for file {file_path}")
                try:
                    if content is not None:
                        write_content = json.dumps(content, indent=2)
                    else:
                        write_content = ""
                except Exception as e:
                    logger.error(f"Error converting content to JSON: {str(e)}")
                    return {
                        "action": "write",
                        "success": False,
                        "file_path": file_path,
                        "error": f"Failed to convert content to string: {str(e)}"
                    }
            
            # Write the content to the file
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(write_content)
            
            # Get the file stats
            stats = os.stat(file_path)
            
            return {
                "action": "write",
                "success": True,
                "file_path": file_path,
                "size": stats.st_size,
                "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                "created": not file_exists,
                "updated": file_exists,
                "backup_created": backup_info is not None,
                "backup_info": backup_info
            }
        except Exception as e:
            logger.error(f"Error writing to {file_path}: {str(e)}")
            return {
                "action": "write",
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }
    
    elif action == "read":
        # Reading a file or a specific version
        try:
            # If version is specified, read that version
            if version and version != "current":
                versions = get_file_versions(file_path)
                
                # Find the requested version
                version_info = next((v for v in versions if str(v["version"]) == version), None)
                
                if not version_info:
                    return {
                        "action": "read",
                        "success": False,
                        "file_path": file_path,
                        "error": f"Version {version} not found"
                    }
                
                # Read the version file
                with open(version_info["path"], 'r', encoding=encoding) as f:
                    content = f.read()
                
                return {
                    "action": "read",
                    "success": True,
                    "file_path": file_path,
                    "version": version,
                    "content": content,
                    "size": version_info["size"],
                    "size_human": version_info["size_human"],
                    "date": version_info["date"]
                }
            
            # Otherwise, read the current file
            if not os.path.exists(file_path):
                return {
                    "action": "read",
                    "success": False,
                    "file_path": file_path,
                    "error": "File not found"
                }
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            stats = os.stat(file_path)
            
            return {
                "action": "read",
                "success": True,
                "file_path": file_path,
                "version": "current",
                "content": content,
                "size": stats.st_size,
                "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                "date": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            return {
                "action": "read",
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }
    
    elif action == "list_versions":
        # Listing all versions of a file
        try:
            versions = get_file_versions(file_path)
            
            return {
                "action": "list_versions",
                "success": True,
                "file_path": file_path,
                "versions": versions,
                "versions_count": len(versions)
            }
        except Exception as e:
            logger.error(f"Error listing versions for {file_path}: {str(e)}")
            return {
                "action": "list_versions",
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }
    
    elif action == "restore":
        # Restoring a specific version
        try:
            versions = get_file_versions(file_path)
            
            # Find the requested version
            version_info = next((v for v in versions if str(v["version"]) == version), None)
            
            if not version_info:
                return {
                    "action": "restore",
                    "success": False,
                    "file_path": file_path,
                    "error": f"Version {version} not found"
                }
            
            # Create a backup of the current file if it exists and the version isn't already current
            backup_info = None
            if version != "current" and os.path.exists(file_path):
                backup_info = create_file_backup(file_path)
                logger.info(f"Created backup before restoring {file_path}: {backup_info}")
            
            # Restore the specified version
            if version != "current":
                # Ensure the directory exists
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # Copy the version file to the target location
                shutil.copy2(version_info["path"], file_path)
            
            # Get the file stats
            stats = os.stat(file_path)
            
            return {
                "action": "restore",
                "success": True,
                "file_path": file_path,
                "version": version,
                "size": stats.st_size,
                "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                "backup_created": backup_info is not None,
                "backup_info": backup_info
            }
        except Exception as e:
            logger.error(f"Error restoring version {version} for {file_path}: {str(e)}")
            return {
                "action": "restore",
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }
    
    else:
        return {
            "action": action,
            "success": False,
            "file_path": file_path,
            "error": f"Unknown action: {action}. Valid actions are 'write', 'read', 'list_versions', 'restore'."
        }

# Log application startup
logger.info(f"Starting file_writer MCP tool version {__version__}")
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
