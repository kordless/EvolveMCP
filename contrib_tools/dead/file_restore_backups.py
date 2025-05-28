"""
file_restore_backups.py - Restores files from backups created by file_apply_diff

This tool helps recover files that were changed using file_apply_diff by restoring
them based on change tags. It supports simple, focused restoration of related changes.
"""

import os
import re
import sys
import shutil
import logging
import pathlib
from datetime import datetime
from typing import Dict, Any, List

# Import MCP server library
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("file-restore-backups-server")

# Setup logging
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir, "file_restore_backups.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file)]
)
logger = logging.getLogger("file_restore_backups")

def get_backup_by_tag(change_tag: str) -> List[Dict[str, Any]]:
    """
    Finds all files that were modified with the specified change_tag.
    
    Args:
        change_tag: Tag used to identify related changes
    
    Returns:
        List of dictionaries with file and backup information
    """
    results = []
    
    # Get the EvolveMCP directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Walk through directories to find backup files with the tag
    for root, dirs, files in os.walk(parent_dir):
        # Skip system directories
        if '.git' in root or '__pycache__' in root:
            continue
            
        # Look for backup version directories
        for d in dirs:
            if d.startswith('.') and d.endswith('_versions'):
                versions_dir = os.path.join(root, d)
                
                # Extract the original filename
                original_filename = d[1:-9]  # Remove leading '.' and trailing '_versions'
                original_path = os.path.join(root, original_filename)
                
                # Skip if original file doesn't exist
                if not os.path.exists(original_path):
                    continue
                
                # Find backups with the specified tag
                for backup_file in os.listdir(versions_dir):
                    # Match filename pattern with change_tag
                    match = re.match(rf"v(\d+)_(\d+)_{re.escape(change_tag)}\.backup", backup_file)
                    if match:
                        version = int(match.group(1))
                        timestamp = int(match.group(2))
                        
                        # Get file stats
                        backup_path = os.path.join(versions_dir, backup_file)
                        stats = os.stat(backup_path)
                        
                        # Add to results
                        results.append({
                            "original_path": original_path,
                            "backup_path": backup_path,
                            "version": version,
                            "timestamp": timestamp,
                            "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                            "size": stats.st_size,
                            "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB"
                        })
    
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x["timestamp"], reverse=True)
    return results

def list_change_tags() -> List[str]:
    """
    Lists all available change tags across all backup files.
    
    Returns:
        List of unique change tags
    """
    tags = set()
    
    # Get the EvolveMCP directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    
    # Walk through directories to find backup files with tags
    for root, dirs, files in os.walk(parent_dir):
        # Skip system directories
        if '.git' in root or '__pycache__' in root:
            continue
            
        # Look for backup version directories
        for d in dirs:
            if d.startswith('.') and d.endswith('_versions'):
                versions_dir = os.path.join(root, d)
                
                # Find backups with tags
                for backup_file in os.listdir(versions_dir):
                    # Match filename pattern with change_tag
                    match = re.match(r"v(\d+)_(\d+)_(.+)\.backup", backup_file)
                    if match:
                        tag = match.group(3)
                        tags.add(tag)
    
    return sorted(list(tags))

@mcp.tool()
async def list_change_sessions() -> Dict[str, Any]:
    """
    Lists all available change sessions (by tag) with summary information.
    
    Returns:
        Dictionary with change session information
    """
    tags = list_change_tags()
    sessions = {}
    
    for tag in tags:
        files = get_backup_by_tag(tag)
        
        if files:
            # Get average timestamp
            timestamps = [f["timestamp"] for f in files]
            avg_timestamp = sum(timestamps) // len(timestamps)
            
            # Format file paths for readability
            file_paths = sorted([os.path.basename(f["original_path"]) for f in files])
            
            sessions[tag] = {
                "file_count": len(files),
                "files": file_paths,
                "date": datetime.fromtimestamp(avg_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": avg_timestamp
            }
    
    # Sort sessions by timestamp (newest first)
    sorted_sessions = dict(sorted(
        sessions.items(),
        key=lambda item: item[1]["timestamp"],
        reverse=True
    ))
    
    return {
        "success": True,
        "session_count": len(sorted_sessions),
        "sessions": sorted_sessions
    }

@mcp.tool()
async def restore_change_session(
    change_tag: str
) -> Dict[str, Any]:
    """
    Restores all files that were modified in a specific change session.
    This operation itself is recorded as a new change.
    
    Args:
        change_tag: Tag identifying the change session to restore
        
    Returns:
        Dictionary with restore results
    """
    # First, get all files with this change tag
    files = get_backup_by_tag(change_tag)
    
    if not files:
        available_tags = list_change_tags()
        return {
            "success": False,
            "message": f"No files found with change tag '{change_tag}'",
            "available_tags": available_tags
        }
    
    # Create a unique tag for this restoration operation
    restore_tag = f"restore_{change_tag}_{int(datetime.now().timestamp())}"
    
    # Prepare results
    results = []
    
    # Restore each file
    for file_info in files:
        try:
            original_path = file_info["original_path"]
            backup_path = file_info["backup_path"]
            
            # Create backup directory if it doesn't exist
            backup_dir = os.path.join(os.path.dirname(original_path), f".{os.path.basename(original_path)}_versions")
            os.makedirs(backup_dir, exist_ok=True)
            
            # Determine next version number
            existing_versions = []
            for f in os.listdir(backup_dir):
                match = re.match(r"v(\d+)_", f)
                if match:
                    existing_versions.append(int(match.group(1)))
            
            next_version = max(existing_versions) + 1 if existing_versions else 1
            
            # Create backup filename with restore tag
            timestamp = int(datetime.now().timestamp())
            backup_filename = f"v{next_version}_{timestamp}_{restore_tag}.backup"
            new_backup_path = os.path.join(backup_dir, backup_filename)
            
            # Backup current file
            shutil.copy2(original_path, new_backup_path)
            
            # Copy backup to original
            shutil.copy2(backup_path, original_path)
            
            results.append({
                "success": True,
                "file_path": original_path,
                "message": f"Restored file from backup version {file_info['version']}",
                "backup_used": file_info,
                "new_backup_path": new_backup_path
            })
            
        except Exception as e:
            logger.error(f"Error restoring {file_info['original_path']}: {str(e)}")
            results.append({
                "success": False,
                "file_path": file_info["original_path"],
                "error": str(e),
                "backup_info": file_info
            })
    
    # Compile statistics
    success_count = sum(1 for r in results if r.get("success", False))
    
    return {
        "success": success_count > 0,
        "message": f"Restored {success_count} out of {len(files)} files from session '{change_tag}'",
        "restore_tag": restore_tag,
        "original_tag": change_tag,
        "file_count": len(files),
        "success_count": success_count,
        "failure_count": len(files) - success_count,
        "file_results": results
    }

# Log application startup
logger.info("Starting file_restore_backups MCP tool")
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
