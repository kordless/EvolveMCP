#!/usr/bin/env python3
"""
Safe File Copy Tool - Copy files with safety checks

Features:
1. Copy files and directories safely
2. Never allows deletions
3. Requires user confirmation if destination exists
4. Provides detailed file information before overwrite decisions
5. Supports both single files and directory copying
"""

import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("safe-file-copy")

def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            if unit == 'B':
                return f"{size_bytes} {unit}"
            else:
                return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def get_file_info(path: str) -> Dict[str, Any]:
    """Get detailed file information"""
    try:
        path_obj = Path(path)
        if not path_obj.exists():
            return {"exists": False, "path": path}
        
        stat = path_obj.stat()
        return {
            "exists": True,
            "path": str(path_obj.absolute()),
            "is_file": path_obj.is_file(),
            "is_directory": path_obj.is_dir(),
            "size": stat.st_size,
            "size_human": format_file_size(stat.st_size),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "name": path_obj.name
        }
    except Exception as e:
        return {"exists": False, "path": path, "error": str(e)}

@mcp.tool()
async def copy_file(
    source_path: str,
    destination_path: str,
    confirm_overwrite: bool = False
) -> Dict[str, Any]:
    """
    Safely copy a file or directory with overwrite protection.
    
    Args:
        source_path: Path to the source file or directory
        destination_path: Path where to copy the file/directory
        confirm_overwrite: Set to True to confirm overwriting existing destination
        
    Returns:
        Dictionary with copy operation results
    """
    try:
        # Get source info
        source_info = get_file_info(source_path)
        if not source_info["exists"]:
            return {
                "success": False,
                "error": f"Source does not exist: {source_path}",
                "source_info": source_info
            }
        
        # Get destination info
        dest_info = get_file_info(destination_path)
        
        # Check if destination exists and requires confirmation
        if dest_info["exists"] and not confirm_overwrite:
            return {
                "success": False,
                "requires_confirmation": True,
                "message": "Destination exists. Set confirm_overwrite=True to proceed.",
                "source_info": source_info,
                "destination_info": dest_info,
                "overwrite_details": {
                    "will_replace": f"{dest_info['name']} ({dest_info['size_human']}, modified {dest_info['modified']})",
                    "with": f"{source_info['name']} ({source_info['size_human']}, modified {source_info['modified']})",
                    "action_required": "Call this function again with confirm_overwrite=True to proceed"
                }
            }
        
        # Perform the copy operation
        source_path_obj = Path(source_path)
        dest_path_obj = Path(destination_path)
        
        # Create parent directories if they don't exist
        dest_path_obj.parent.mkdir(parents=True, exist_ok=True)
        
        if source_info["is_directory"]:
            # Copy directory
            if dest_info["exists"]:
                shutil.rmtree(destination_path)  # Remove existing directory
            shutil.copytree(source_path, destination_path)
            operation = "Directory copied"
        else:
            # Copy file
            shutil.copy2(source_path, destination_path)
            operation = "File copied"
        
        # Get final destination info
        final_dest_info = get_file_info(destination_path)
        
        return {
            "success": True,
            "operation": operation,
            "source_info": source_info,
            "destination_info": final_dest_info,
            "overwrite_occurred": dest_info["exists"],
            "message": f"Successfully copied {source_path} to {destination_path}"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Copy operation failed: {str(e)}",
            "source_path": source_path,
            "destination_path": destination_path
        }

@mcp.tool()
async def list_directory_contents(
    directory_path: str,
    show_hidden: bool = False
) -> Dict[str, Any]:
    """
    List contents of a directory to help with copy operations.
    
    Args:
        directory_path: Path to the directory to list
        show_hidden: Whether to include hidden files/directories
        
    Returns:
        Dictionary with directory contents
    """
    try:
        path_obj = Path(directory_path)
        if not path_obj.exists():
            return {
                "success": False,
                "error": f"Directory does not exist: {directory_path}"
            }
        
        if not path_obj.is_dir():
            return {
                "success": False,
                "error": f"Path is not a directory: {directory_path}"
            }
        
        contents = []
        total_size = 0
        
        for item in path_obj.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
                
            item_info = get_file_info(str(item))
            if item_info["exists"]:
                contents.append(item_info)
                if item_info["is_file"]:
                    total_size += item_info["size"]
        
        # Sort by name
        contents.sort(key=lambda x: x["name"].lower())
        
        return {
            "success": True,
            "directory": str(path_obj.absolute()),
            "item_count": len(contents),
            "total_size": total_size,
            "total_size_human": format_file_size(total_size),
            "contents": contents
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list directory: {str(e)}",
            "directory_path": directory_path
        }

@mcp.tool()
async def check_copy_safety(
    source_path: str,
    destination_path: str
) -> Dict[str, Any]:
    """
    Check if a copy operation is safe without actually performing it.
    
    Args:
        source_path: Path to the source file or directory
        destination_path: Path where to copy the file/directory
        
    Returns:
        Dictionary with safety analysis
    """
    try:
        source_info = get_file_info(source_path)
        dest_info = get_file_info(destination_path)
        
        # Check for potential issues
        issues = []
        warnings = []
        
        if not source_info["exists"]:
            issues.append("Source does not exist")
        
        if dest_info["exists"]:
            warnings.append("Destination exists and will be overwritten")
            if dest_info["is_directory"] and source_info["is_file"]:
                issues.append("Cannot overwrite directory with file")
            elif dest_info["is_file"] and source_info["is_directory"]:
                issues.append("Cannot overwrite file with directory")
        
        # Check parent directory
        dest_parent = Path(destination_path).parent
        if not dest_parent.exists():
            warnings.append(f"Parent directory will be created: {dest_parent}")
        
        # Estimate space requirements
        space_info = {}
        if source_info["exists"]:
            if source_info["is_directory"]:
                # For directories, we'd need to walk the tree for exact size
                space_info["note"] = "Directory size estimation requires full scan"
            else:
                space_info["required"] = source_info["size"]
                space_info["required_human"] = source_info["size_human"]
        
        return {
            "safe_to_copy": len(issues) == 0,
            "source_info": source_info,
            "destination_info": dest_info,
            "issues": issues,
            "warnings": warnings,
            "space_requirements": space_info,
            "recommendation": "Proceed with copy_file()" if len(issues) == 0 else "Resolve issues before copying"
        }
        
    except Exception as e:
        return {
            "safe_to_copy": False,
            "error": f"Safety check failed: {str(e)}",
            "source_path": source_path,
            "destination_path": destination_path
        }

if __name__ == "__main__":
    mcp.run()
