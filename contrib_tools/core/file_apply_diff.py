
"""
file_apply_diff.py - Edit files using a diff-fenced format and apply the changes

Copyright 2025 Kord Campbell
Based on concepts from ToolKami: https://github.com/aperoc/toolkami
Original implementation by Edwin (https://github.com/ocyedwin)

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Note: While most of the EvolveMCP project is under the Gnosis AI-Sovereign License,
this specific file is being released under the Apache License 2.0.
"""

import sys
import os
import re
import logging
import pathlib
import time
import shutil
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime

__version__ = "0.1.4"
__updated__ = "2025-05-19"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure the logs directory exists

# Log file path
log_file = os.path.join(logs_dir, "file_apply_diff.log")

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("file_apply_diff")

# Import MCP server library
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("file-apply-diff-server")

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

def create_file_backup(file_path: str, change_tag: str = None) -> Dict[str, Any]:
    """
    Creates a backup of the file in a versioned directory.
    
    Args:
        file_path: Path to the file to back up
        change_tag: Optional tag to identify related changes across multiple files
    
    Returns:
        Dictionary with backup information
    """
    # Get the versions directory
    versions_dir = ensure_version_dir(file_path)
    
    # Get the next version number
    version_number = get_next_version_number(file_path)
    
    # Create a timestamp
    timestamp = int(time.time())
    
    # Create the backup filename (with optional change_tag)
    if change_tag:
        # Sanitize tag to be filename-safe
        safe_tag = re.sub(r'[^\w\-_]', '_', change_tag)
        backup_filename = f"v{version_number}_{timestamp}_{safe_tag}.backup"
    else:
        backup_filename = f"v{version_number}_{timestamp}.backup"
    
    backup_path = os.path.join(versions_dir, backup_filename)
    
    # Copy the file to the backup location
    shutil.copy2(file_path, backup_path)
    logger.info(f"Created backup at {backup_path}")
    
    # Get file stats
    stats = os.stat(backup_path)
    
    return {
        "version": version_number,
        "timestamp": timestamp,
        "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "size": stats.st_size,
        "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
        "path": backup_path,
        "change_tag": change_tag
    }

def extract_diff_blocks(diff_text: str) -> List[Tuple[str, str]]:
    """
    Extract diff blocks from the provided diff text.
    
    Args:
        diff_text: Text containing diff blocks
        
    Returns:
        List of tuples with (search_text, replace_text)
    """
    # First try with code fences
    pattern = r'```diff\n(.*?)<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE\n```'
    blocks = re.findall(pattern, diff_text, re.DOTALL)
    
    if not blocks:
        # Try without code fences
        pattern = r'<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE'
        blocks = re.findall(pattern, diff_text, re.DOTALL)
        
        if blocks:
            # Convert the 2-element tuples to 3-element tuples with empty first element
            blocks = [("", match[0], match[1]) for match in blocks]
    
    # Process the blocks to extract search and replace text
    result = []
    for block in blocks:
        if len(block) == 3:
            _, search_text, replace_text = block
            # Strip any leading/trailing whitespace
            search_text = search_text.strip()
            replace_text = replace_text.strip()
            result.append((search_text, replace_text))
    
    return result

def apply_diff_blocks(original_text: str, diff_blocks: List[Tuple[str, str]], replace_all: bool = True) -> Tuple[str, int, Dict[str, Any]]:
    """
    Apply diff blocks to the original text.
    
    Args:
        original_text: Original file content
        diff_blocks: List of (search_text, replace_text) tuples
        replace_all: If True, replace all occurrences; if False, only replace first occurrence
                     and error if multiple matches exist
        
    Returns:
        A tuple containing:
        - Modified text after applying all diff blocks
        - Number of changes made
        - Dictionary with warnings/errors
    """
    result = original_text
    changes_made = 0
    issues = {"warnings": [], "errors": []}
    
    for i, (search_text, replace_text) in enumerate(diff_blocks):
        if not search_text.strip():
            # If search text is empty, append the replace text
            result += '\n' + replace_text
            changes_made += 1
            continue
            
        # Count occurrences of the search text
        count = result.count(search_text)
        
        if count == 0:
            # No matches
            issues["warnings"].append(f"Block {i+1}: Search text not found in file")
            continue
            
        if count > 1 and not replace_all:
            # Multiple matches found but replace_all is False
            issues["errors"].append(f"Block {i+1}: Multiple matches ({count}) found for search text, but replace_all=False")
            continue
        
        if replace_all:
            # Replace all occurrences
            new_text = result.replace(search_text, replace_text)
            result = new_text
            changes_made += count
        else:
            # Replace only the first occurrence
            new_text = result.replace(search_text, replace_text, 1)
            result = new_text
            changes_made += 1
    
    return result, changes_made, issues

def read_file_content(file_path: str, encoding: str = "utf-8") -> str:
    """Read the contents of a file."""
    try:
        return pathlib.Path(file_path).read_text(encoding=encoding)
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise ValueError(f"Error reading file: {str(e)}")

def write_file_content(file_path: str, content: str, encoding: str = "utf-8") -> None:
    """Write content to a file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        pathlib.Path(file_path).write_text(content, encoding=encoding)
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        raise ValueError(f"Error writing to file: {str(e)}")

@mcp.tool()
async def file_apply_diff(
    file_path: str, 
    diff_text: str,
    replace_all: bool = True,
    create_backup: bool = True,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Edit a file using a diff-fenced format and apply the changes.
    Can be used to delete.
    
    Args:
        file_path: Path to the file to edit
        diff_text: Text containing diff blocks in the format:
                  ```diff
                  <<<<<<< SEARCH
                  [text to find]
                  =======
                  [text to replace with]
                  >>>>>>> REPLACE
                  ```
        replace_all: If True, replace all occurrences of search text; if False, only replace
                     first occurrence and error if multiple matches exist
        create_backup: Whether to create a backup before making changes
        encoding: Text encoding to use when reading/writing files (default: utf-8)
                
    Returns:
        Dictionary with operation results and modified content
    """
    logger.info(f"file_apply_diff called with file_path={file_path}, replace_all={replace_all}")
    
    # Normalize the file path
    file_path = os.path.abspath(os.path.expanduser(file_path))
    
    try:
        # Check if the file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "file_path": file_path,
                "error": "File not found"
            }
        
        # Create backup if requested
        backup_info = None
        if create_backup:
            try:
                backup_info = create_file_backup(file_path)
                logger.info(f"Created backup: version {backup_info['version']} at {backup_info['path']}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {str(e)}")
        
        # Read the original file content
        original_content = read_file_content(file_path, encoding)
        
        # Extract diff blocks
        diff_blocks = extract_diff_blocks(diff_text)
        
        if not diff_blocks:
            return {
                "success": False,
                "file_path": file_path,
                "error": "No valid diff blocks found in the provided diff text. Please try again with smaller blocks or delete blocks then replace using a common starting line",
                "backup_created": backup_info is not None,
                "backup_info": backup_info
            }
        
        # Apply the diff blocks
        modified_content, changes_made, issues = apply_diff_blocks(original_content, diff_blocks, replace_all)
        
        # If there are errors, don't apply changes
        if issues["errors"]:
            error_msg = "; ".join(issues["errors"])
            logger.error(f"Diff application errors: {error_msg}")
            return {
                "success": False,
                "file_path": file_path,
                "error": "Failed to apply diff due to multiple matches found. " 
                         "Use replace_all=True to replace all occurrences or be more specific. "
                         "Please try again with smaller blocks or delete blocks then replace using a common starting line.",
                "details": issues,
                "diff_blocks_found": len(diff_blocks),
                "backup_created": backup_info is not None,
                "backup_info": backup_info
            }
        
        # Check if any changes were made
        if changes_made == 0:
            return {
                "success": True,
                "file_path": file_path,
                "warning": "No changes were applied to the file. The search text might not be present.",
                "details": issues,
                "error": "No changes were applied. The search text was not found in the file. Please try again with smaller blocks or delete blocks then replace using a common starting line.",
                "changes_applied": 0,
                "diff_blocks_found": len(diff_blocks),
                "backup_created": backup_info is not None,
                "backup_info": backup_info
            }
        
        # Write the modified content back to the file
        write_file_content(file_path, modified_content, encoding)
        
        # Get the file stats
        stats = os.stat(file_path)
        
        result = {
            "success": True,
            "file_path": file_path,
            "message": f"Successfully applied {changes_made} changes to {file_path}",
            "changes_applied": changes_made,
            "diff_blocks_found": len(diff_blocks),
            "size": stats.st_size,
            "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
            "backup_created": backup_info is not None,
            "backup_info": backup_info
        }
        
        # Add warnings if any
        if issues["warnings"]:
            result["warnings"] = issues["warnings"]
            
        return result
        
    except Exception as e:
        logger.error(f"Error in file_apply_diff: {e}", exc_info=True)
        return {
            "success": False,
            "file_path": file_path,
            "error": f"{str(e)}. Please try again with smaller blocks or delete blocks then replace using a common starting line."
        }

# Log application startup
logger.info(f"Starting file_apply_diff MCP tool version {__version__}")
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
