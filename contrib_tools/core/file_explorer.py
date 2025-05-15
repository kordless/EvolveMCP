
import sys
import os
import json
import logging
import glob
from typing import Dict, Any, List, Optional, Union

__version__ = "0.1.7"
__updated__ = "2025-05-15"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure logs directory exists

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, "file_explorer.log"))
    ]
)
logger = logging.getLogger("file_explorer")

# Import MCP server
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("file-explorer-server")

@mcp.tool()
async def file_explorer(path: str = None, show_hidden: bool = False, pattern: Optional[str] = None, 
                       read_file: bool = False, encoding: str = "utf-8", 
                       recursive: bool = False, max_depth: int = 2) -> Dict[str, Any]:
    """
    Lists directory contents or reads file contents at the specified path, with the parent directory as default.

    A more powerful version of evolve_filysystem().
    
    Args:
        path: Path to the directory or file to explore (defaults to parent directory using '..')
        show_hidden: Whether to include hidden files (starting with .)
        pattern: Optional glob pattern to filter files (e.g. "*.txt")
        read_file: If True and path is a file, returns the file contents
        encoding: Text encoding to use when reading files (default: utf-8)
        recursive: Whether to list directories recursively
        max_depth: Maximum recursion depth when recursive is True
    
    Returns:
        Dictionary with directory contents or file information
    """
    logger.info(f"Exploring path: {path} (read_file={read_file}, show_hidden={show_hidden}, pattern={pattern}, recursive={recursive})")
    
    try:
        # Import fnmatch at the beginning for pattern matching
        import fnmatch
        # Get current working directory
        cwd = os.getcwd()
        logger.info(f"Current working directory: {cwd}")
        
        # Default to parent directory if no path is provided
        if path is None:
            path = parent_dir
            logger.info(f"No path provided, using parent directory: {path}")
        
        # Expand user directory if needed
        if path.startswith('~'):
            path = os.path.expanduser(path)
            logger.info(f"Expanded user directory path to: {path}")
        
        # Check if path contains wildcard characters
        has_wildcard = path and ('*' in path or '?' in path or '[' in path)
        
        # If path has wildcards, we need to handle it specially
        if has_wildcard:
            logger.info(f"Path contains wildcard: {path}")
            
            # Try to find the base directory (non-wildcard part)
            base_path = os.path.dirname(path)
            wildcard_part = os.path.basename(path)
            
            if not base_path:
                # If there's no directory part, use current directory
                base_path = "."
                
            logger.info(f"Split wildcard path into base_path: {base_path}, wildcard_part: {wildcard_part}")
            
            # Try multiple base path resolution strategies for the directory part
            potential_base_paths = [
                base_path,                                # Absolute path or relative to CWD
                os.path.join(cwd, base_path),             # Relative to current working directory
                os.path.join(parent_dir, base_path),      # Relative to parent directory
                os.path.join(current_dir, base_path)      # Relative to tool directory
            ]
            
            # Find first valid base path
            resolved_base_path = None
            for bp in potential_base_paths:
                if os.path.exists(bp) and os.path.isdir(bp):
                    resolved_base_path = bp
                    logger.info(f"Resolved base path to: {resolved_base_path}")
                    break
                    
            if not resolved_base_path:
                logger.error(f"Could not resolve wildcard base path: {base_path}")
                return {
                    "error": f"Base directory for wildcard path does not exist: {base_path}",
                    "paths_tried": potential_base_paths
                }
                
            # Use the wildcard part as the pattern and the resolved base path as our path
            pattern = wildcard_part
            path = resolved_base_path
            logger.info(f"Using wildcard as pattern: pattern={pattern}, path={path}")
            
        else:
            # For non-wildcard paths, try multiple path resolution strategies
            potential_paths = [
                path,                                   # Absolute path or relative to CWD
                os.path.join(cwd, path),                # Relative to current working directory
                os.path.join(parent_dir, path),         # Relative to parent directory
                os.path.join(current_dir, path)         # Relative to tool directory
            ]
            
            # Try each path strategy until one works
            resolved_path = None
            for p in potential_paths:
                if os.path.exists(p):
                    resolved_path = p
                    logger.info(f"Resolved path to: {resolved_path}")
                    break
            
            # If none of the paths exist, return an error
            if resolved_path is None:
                paths_tried = "\n".join(potential_paths)
                logger.error(f"Path does not exist. Tried:\n{paths_tried}")
                return {
                    "error": f"Path does not exist: {path}",
                    "paths_tried": potential_paths
                }
            
            # Update path to the resolved path
            path = resolved_path
        
        # Handle file reading if requested
        if os.path.isfile(path):
            logger.info(f"Path is a file: {path}")
            file_info = {
                "name": os.path.basename(path),
                "path": path,
                "size": os.path.getsize(path),
                "last_modified": os.path.getmtime(path),
                "is_directory": False,
                "extension": os.path.splitext(path)[1].lower() if os.path.splitext(path)[1] else None
            }
            
            # Read file contents if requested
            if read_file:
                logger.info(f"Reading file contents with encoding: {encoding}")
                try:
                    # Try to detect if it's a text or binary file (quick heuristic)
                    is_likely_binary = False
                    with open(path, 'rb') as f:
                        chunk = f.read(1024)
                        if b'\x00' in chunk:  # Null bytes suggest binary
                            is_likely_binary = True
                    
                    # If it seems like a binary file, flag it
                    if is_likely_binary:
                        logger.info("Binary file detected by heuristic, cannot display contents")
                        file_info["content"] = None
                        file_info["encoding"] = None
                        file_info["binary"] = True
                        file_info["error"] = "Binary file detected. Cannot display contents."
                    else:
                        # Try to read as text with the specified encoding
                        with open(path, 'r', encoding=encoding) as f:
                            file_content = f.read()
                        file_info["content"] = file_content
                        file_info["encoding"] = encoding
                        logger.info(f"Successfully read file with encoding: {encoding}")
                except UnicodeDecodeError:
                    # If text reading fails, indicate it's a binary file
                    logger.info(f"Binary file detected (UnicodeDecodeError), cannot display contents")
                    file_info["content"] = None
                    file_info["encoding"] = None
                    file_info["binary"] = True
                    file_info["error"] = "Binary file detected. Cannot display contents."
            
            return {
                "type": "file",
                "file_info": file_info
            }
        
        # Handle directory listing
        elif os.path.isdir(path):
            logger.info(f"Path is a directory: {path}")
            
            def list_directory(dir_path, current_depth=0):
                """Helper function to list directory contents, potentially recursively"""
                # Get directory contents
                try:
                    contents = os.listdir(dir_path)
                except PermissionError:
                    logger.error(f"Permission denied for directory: {dir_path}")
                    return {
                        "name": os.path.basename(dir_path),
                        "path": dir_path,
                        "is_directory": True,
                        "error": "Permission denied"
                    }
                
                logger.info(f"Directory {dir_path} contains {len(contents)} items")
                
                # Filter hidden files if needed
                if not show_hidden:
                    contents = [item for item in contents if not item.startswith('.')]
                    logger.info(f"After filtering hidden files: {len(contents)} items")
                
                # Important: We no longer filter by pattern here before recursion
                # This enables us to find pattern matches in subdirectories
                
                # Get details for each item
                all_items = []
                matching_items = []
                
                for item in contents:
                    item_path = os.path.join(dir_path, item)
                    try:
                        is_dir = os.path.isdir(item_path)
                        item_info = {
                            "name": item,
                            "path": item_path,
                            "is_directory": is_dir,
                            "size": None if is_dir else os.path.getsize(item_path),
                            "last_modified": os.path.getmtime(item_path),
                            "extension": os.path.splitext(item)[1].lower() if not is_dir and os.path.splitext(item)[1] else None
                        }
                        
                        # Check if this item matches the pattern (if pattern provided)
                        item_matches = False
                        if not pattern or (not is_dir and fnmatch.fnmatch(item, pattern)):
                            item_matches = True
                        
                        # Always recurse into subdirectories regardless of pattern match
                        if recursive and is_dir and current_depth < max_depth:
                            sub_items = list_directory(item_path, current_depth + 1)
                            
                            # Store recursive results if there are any
                            if isinstance(sub_items, list) and sub_items:
                                item_info["contents"] = sub_items
                                # If subdirectory has matching items, consider this dir a match too
                                if not item_matches:
                                    item_matches = True
                            elif isinstance(sub_items, dict) and sub_items.get("error"):
                                # Handle error case
                                item_info["error"] = sub_items.get("error")
                        
                        # Append to the appropriate list based on pattern matching
                        all_items.append(item_info)
                        if item_matches:
                            matching_items.append(item_info)
                    except Exception as e:
                        logger.error(f"Error getting info for {item_path}: {str(e)}")
                        # Add the item with error information
                        items.append({
                            "name": item,
                            "path": item_path,
                            "error": str(e)
                        })
                
                # Sort items: directories first, then files
                matching_items.sort(key=lambda x: (not x.get("is_directory", False), x.get("name", "").lower()))
                return matching_items if pattern else all_items
            
            # List the directory contents
            items = list_directory(path)
            
            # For better user understanding, log how many items we found after recursive search
            if pattern:
                logger.info(f"After recursive search with pattern '{pattern}': {len(items)} matching items")
            
            return {
                "type": "directory",
                "directory": path,
                "item_count": len(items),
                "items": items
            }
        else:
            logger.error(f"Path is neither a file nor a directory: {path}")
            return {"error": f"Path is neither a file nor a directory: {path}"}
            
    except Exception as e:
        logger.error(f"Error exploring path: {str(e)}\")")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": f"Error exploring path: {str(e)}"}

if __name__ == "__main__":
    logger.info("Starting File Explorer MCP server")
    mcp.run(transport='stdio')
