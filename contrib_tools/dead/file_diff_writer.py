"""
file_diff_writer.py - Enhanced file diff tool with advanced matching capabilities

Combines the strengths of file_apply_diff and toolkami_enhanced_diff with
improved fuzzy matching algorithms, detailed debugging, and reliable file operations.

Version 0.1.2: Added single-line fuzzy matching strategy for better partial match handling
within lines, based on insights from toolkami_enhanced_diff.py implementation.

Copyright 2025 Kord Campbell
Licensed under the Apache License, Version 2.0
"""

import sys
import os
import re
import logging
import pathlib
import time
import shutil
import difflib
import json
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime

__version__ = "0.1.2"
__updated__ = "2025-05-25"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Log file path
log_file = os.path.join(logs_dir, "file_diff_writer.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("file_diff_writer")

# Import MCP server library
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("file-diff-writer-server")

# ====================================
# File Versioning and Backup Functions
# ====================================

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
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    versions_dir = os.path.join(directory, f".{filename}_versions")
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
        return versions
    
    versions_dir = ensure_version_dir(file_path)
    
    if not os.path.exists(versions_dir):
        return versions
    
    try:
        version_files = [f for f in os.listdir(versions_dir) if os.path.isfile(os.path.join(versions_dir, f))]
        
        for version_file in version_files:
            match = re.match(r"v(\d+)_(\d+)(\.[\w-]+)?\.backup", version_file)
            if match:
                version_number = int(match.group(1))
                timestamp = int(match.group(2))
                tag = match.group(3)[1:] if match.group(3) else None
                
                version_path = os.path.join(versions_dir, version_file)
                stats = os.stat(version_path)
                
                versions.append({
                    "version": version_number,
                    "timestamp": timestamp,
                    "date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
                    "size": stats.st_size,
                    "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                    "path": version_path,
                    "tag": tag
                })
    except Exception as e:
        logger.error(f"Error getting versions for {file_path}: {str(e)}")
    
    versions.sort(key=lambda x: x["version"], reverse=True)
    
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
    """Gets the next version number for a file."""
    versions = get_file_versions(file_path)
    past_versions = [v for v in versions if v["version"] != "current"]
    
    if not past_versions:
        return 1
    
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
    versions_dir = ensure_version_dir(file_path)
    version_number = get_next_version_number(file_path)
    timestamp = int(time.time())
    
    if change_tag:
        safe_tag = re.sub(r'[^\w\-_]', '_', change_tag)
        backup_filename = f"v{version_number}_{timestamp}.{safe_tag}.backup"
    else:
        backup_filename = f"v{version_number}_{timestamp}.backup"
    
    backup_path = os.path.join(versions_dir, backup_filename)
    shutil.copy2(file_path, backup_path)
    logger.info(f"Created backup at {backup_path}")
    
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

def restore_file_version(file_path: str, version_number: int) -> Dict[str, Any]:
    """
    Restores a specific version of a file.
    
    Args:
        file_path: Path to the file
        version_number: Version number to restore
    
    Returns:
        Dictionary with restoration information
    """
    versions = get_file_versions(file_path)
    past_versions = [v for v in versions if v["version"] != "current"]
    
    if not past_versions:
        raise ValueError(f"No previous versions found for {file_path}")
    
    target_version = next((v for v in past_versions if v["version"] == version_number), None)
    
    if not target_version:
        raise ValueError(f"Version {version_number} not found for {file_path}")
    
    # Create a backup of the current file before restoring
    backup_info = None
    if os.path.exists(file_path):
        backup_info = create_file_backup(file_path, "pre_restore")
    
    # Restore the file from the specified version
    shutil.copy2(target_version["path"], file_path)
    logger.info(f"Restored {file_path} to version {version_number}")
    
    return {
        "success": True,
        "file_path": file_path,
        "restored_version": version_number,
        "backup_created": backup_info is not None,
        "backup_info": backup_info
    }

# ==============================
# Text Processing and Matching
# ==============================

def normalize_whitespace(text: str, preserve_structure: bool = True) -> str:
    """
    Normalize whitespace for flexible matching.
    
    Args:
        text: Text to normalize
        preserve_structure: If True, preserve line breaks and basic structure
    
    Returns:
        Normalized text
    """
    if preserve_structure:
        # Preserve line structure but normalize spaces within lines
        lines = text.split('\n')
        normalized_lines = []
        for line in lines:
            # Strip leading/trailing whitespace, collapse internal whitespace
            normalized_line = re.sub(r'\s+', ' ', line.strip())
            normalized_lines.append(normalized_line)
        return '\n'.join(normalized_lines)
    else:
        # Aggressive normalization - collapse all whitespace
        return re.sub(r'\s+', ' ', text.strip())

def calculate_similarity(str1: str, str2: str, method: str = "ratio") -> float:
    """
    Calculate similarity between two strings using various methods.
    
    Args:
        str1: First string
        str2: Second string
        method: Similarity method ("ratio", "partial_ratio", "token_sort", "token_set")
    
    Returns:
        Similarity score between 0.0 and 1.0
    """
    if not str1 and not str2:
        return 1.0
    if not str1 or not str2:
        return 0.0
    
    if method == "ratio":
        # Standard sequence matcher ratio
        return difflib.SequenceMatcher(None, str1, str2).ratio()
    
    elif method == "partial_ratio":
        # Find best partial match
        s = difflib.SequenceMatcher(None, str1, str2)
        blocks = s.get_matching_blocks()
        
        if not blocks:
            return 0.0
            
        # Get the largest block
        largest_block = max(blocks, key=lambda b: b[2])
        if largest_block[2] == 0:
            return 0.0
            
        # Calculate partial ratio based on the largest matching block
        return largest_block[2] / max(len(str1), len(str2))
    
    elif method == "token_sort":
        # Tokenize, sort and join, then compare
        def process(s):
            return ' '.join(sorted(s.lower().split()))
        
        return difflib.SequenceMatcher(None, process(str1), process(str2)).ratio()
    
    elif method == "token_set":
        # Create token sets and compare intersections
        tokens1 = set(str1.lower().split())
        tokens2 = set(str2.lower().split())
        
        if not tokens1 and not tokens2:
            return 1.0
        if not tokens1 or not tokens2:
            return 0.0
            
        intersection = tokens1.intersection(tokens2)
        return len(intersection) / max(len(tokens1), len(tokens2))
    
    else:
        # Default to standard ratio
        return difflib.SequenceMatcher(None, str1, str2).ratio()

def find_fuzzy_matches(search_text: str, content: str, similarity_threshold: float = 0.8, 
                       methods: List[str] = None) -> List[Dict[str, Any]]:
    """
    Find fuzzy matches for search text in content using multiple strategies.
    
    Args:
        search_text: Text to search for
        content: Content to search in
        similarity_threshold: Minimum similarity ratio (0.0 to 1.0)
        methods: List of similarity methods to try
    
    Returns:
        List of potential matches sorted by similarity score
    """
    if methods is None:
        methods = ["exact", "normalized", "multiline", "single_line", "token"]
    
    matches = []
    
    # Strategy 1: Exact match
    if "exact" in methods and search_text in content:
        start_pos = content.find(search_text)
        matches.append({
            "text": search_text,
            "similarity": 1.0,
            "start_pos": start_pos,
            "end_pos": start_pos + len(search_text),
            "match_type": "exact",
            "strategy": "exact"
        })
        return matches  # Return immediately for exact matches
    
    # Strategy 2: Whitespace-normalized match
    if "normalized" in methods:
        norm_search = normalize_whitespace(search_text)
        norm_content = normalize_whitespace(content)
        
        if norm_search in norm_content:
            # Find the original position by mapping back
            # This is an approximation - exact position may be different due to normalization
            start_pos = content.lower().find(search_text.strip().lower())
            if start_pos >= 0:
                matches.append({
                    "text": search_text.strip(),
                    "similarity": 0.95,
                    "start_pos": start_pos,
                    "end_pos": start_pos + len(search_text.strip()),
                    "match_type": "normalized",
                    "strategy": "normalized"
                })
                return matches
    
    # Strategy 3: Line-by-line fuzzy matching for multi-line text
    if "multiline" in methods and '\n' in search_text:
        search_lines = [line.strip() for line in search_text.strip().split('\n') if line.strip()]
        content_lines = [line.strip() for line in content.split('\n')]
        
        if len(search_lines) > 1:
            # Look for sequences of lines that match
            for i in range(len(content_lines) - len(search_lines) + 1):
                content_slice = content_lines[i:i + len(search_lines)]
                
                # Calculate similarity for each line pair
                line_similarities = []
                for search_line, content_line in zip(search_lines, content_slice):
                    if not search_line or not content_line:
                        similarity = 0.0
                    else:
                        similarity = calculate_similarity(search_line, content_line)
                    line_similarities.append(similarity)
                
                # Average similarity
                avg_similarity = sum(line_similarities) / len(line_similarities) if line_similarities else 0.0
                
                if avg_similarity >= similarity_threshold:
                    # Calculate actual positions in original content
                    original_lines = content.split('\n')
                    start_line = i
                    end_line = i + len(search_lines) - 1
                    
                    # Find character positions
                    start_pos = sum(len(line) + 1 for line in original_lines[:start_line])
                    match_text = '\n'.join(original_lines[start_line:end_line + 1])
                    
                    matches.append({
                        "text": match_text,
                        "similarity": avg_similarity,
                        "start_pos": start_pos,
                        "end_pos": start_pos + len(match_text),
                        "match_type": "fuzzy_multiline",
                        "strategy": "multiline",
                        "line_range": (start_line, end_line),
                        "line_similarities": line_similarities
                    })
    
    # Strategy 4: Single-line fuzzy matching with relaxed threshold
    if "single_line" in methods and not matches and len(search_text.strip().split('\n')) == 1:
        search_line = search_text.strip()
        content_lines = [line.strip() for line in content.split('\n')]
        best_similarity = 0.0
        best_match = None
        
        for i, content_line in enumerate(content_lines):
            similarity = difflib.SequenceMatcher(None, search_line, content_line).ratio()
            # Use a more relaxed threshold for single-line matching
            if similarity > best_similarity and similarity >= max(0.6, similarity_threshold - 0.2):
                best_similarity = similarity
                original_lines = content.split('\n')
                start_pos = sum(len(line) + 1 for line in original_lines[:i])
                
                best_match = {
                    "text": original_lines[i],
                    "similarity": similarity,
                    "start_pos": start_pos,
                    "end_pos": start_pos + len(original_lines[i]),
                    "match_type": "fuzzy_single_line",
                    "strategy": "single_line",
                    "line_number": i
                }
        
        if best_match:
            matches.append(best_match)
    
    # Strategy 5: Token-based matching
    if "token" in methods:
        # For single-line text or as a fallback for multi-line
        token_similarity = calculate_similarity(search_text, content, "token_sort")
        
        if token_similarity >= similarity_threshold:
            # This is an approximation - we don't have exact position for token matching
            # Use simple string search as a best guess
            start_pos = content.lower().find(search_text.strip().lower())
            if start_pos < 0:
                # If not found, try with first few words
                first_words = ' '.join(search_text.strip().split()[:3])
                start_pos = content.lower().find(first_words.lower())
            
            if start_pos >= 0:
                end_pos = start_pos + len(search_text.strip())
                matches.append({
                    "text": search_text,
                    "similarity": token_similarity,
                    "start_pos": start_pos,
                    "end_pos": end_pos,
                    "match_type": "token_based",
                    "strategy": "token"
                })
    
    # Sort by similarity score (descending)
    matches.sort(key=lambda x: x["similarity"], reverse=True)
    
    return matches

def extract_diff_blocks(diff_text: str) -> List[Tuple[str, str, Dict[str, Any]]]:
    """
    Extract diff blocks from the provided diff text with support for multiple formats.
    
    Args:
        diff_text: Text containing diff blocks
        
    Returns:
        List of tuples with (search_text, replace_text, metadata)
    """
    blocks = []
    metadata = {"extraction_method": "unknown", "blocks_found": 0}
    
    # Multiple pattern matching strategies in order of preference
    
    # Strategy 1: ToolKami-style with code fences
    pattern = r'```diff\s*\n(.*?)\n<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE\n```'
    matches = re.findall(pattern, diff_text, re.DOTALL)
    
    if matches:
        metadata["extraction_method"] = "toolkami_fenced"
        for match in matches:
            filename, search_text, replace_text = match
            blocks.append((search_text, replace_text, {"filename_hint": filename.strip()}))
        metadata["blocks_found"] = len(blocks)
        return blocks
    
    # Strategy 2: ToolKami-style without code fences
    pattern = r'(.*?)\n<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE'
    matches = re.findall(pattern, diff_text, re.DOTALL)
    
    if matches:
        metadata["extraction_method"] = "toolkami_direct"
        for match in matches:
            filename, search_text, replace_text = match
            blocks.append((search_text, replace_text, {"filename_hint": filename.strip()}))
        metadata["blocks_found"] = len(blocks)
        return blocks
    
    # Strategy 3: Simple SEARCH/REPLACE blocks
    pattern = r'<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE'
    matches = re.findall(pattern, diff_text, re.DOTALL)
    
    if matches:
        metadata["extraction_method"] = "simple_blocks"
        for match in matches:
            search_text, replace_text = match
            blocks.append((search_text, replace_text, {}))
        metadata["blocks_found"] = len(blocks)
        return blocks
    
    # Strategy 4: EvolveMCP-style diff blocks
    pattern = r'```diff\n(.*?)<<<<<<< SEARCH\n(.*?)=======\n(.*?)>>>>>>> REPLACE\n```'
    matches = re.findall(pattern, diff_text, re.DOTALL)
    
    if matches:
        metadata["extraction_method"] = "evolvemcp_style"
        for match in matches:
            _, search_text, replace_text = match
            blocks.append((search_text, replace_text, {}))
        metadata["blocks_found"] = len(blocks)
        return blocks
    
    # Strategy 5: Git-style diff format
    pattern = r'--- a/(.*?)\n\+\+\+ b/.*?\n@@ .*? @@.*?\n(.*?)(?=\n--- a/|$)'
    matches = re.findall(pattern, diff_text, re.DOTALL)
    
    if matches:
        metadata["extraction_method"] = "git_style"
        for match in matches:
            filename, diff_content = match
            # Convert git-style diff to search/replace format
            search_lines = []
            replace_lines = []
            for line in diff_content.splitlines():
                if line.startswith('-'):
                    search_lines.append(line[1:])
                elif line.startswith('+'):
                    replace_lines.append(line[1:])
                else:
                    search_lines.append(line)
                    replace_lines.append(line)
            
            search_text = '\n'.join(search_lines)
            replace_text = '\n'.join(replace_lines)
            
            blocks.append((search_text, replace_text, {"filename_hint": filename.strip()}))
        metadata["blocks_found"] = len(blocks)
        return blocks
    
    return blocks

def apply_diff_edit(original_text: str, search_text: str, replace_text: str, 
                   similarity_threshold: float = 0.8,
                   allow_partial_matches: bool = True,
                   replace_all: bool = False) -> Tuple[str, bool, Dict[str, Any]]:
    """
    Apply a single diff edit with enhanced matching and detailed reporting.
    
    Args:
        original_text: Original content
        search_text: Text to search for
        replace_text: Text to replace with
        similarity_threshold: Minimum similarity threshold for matches
        allow_partial_matches: Whether to allow partial/fuzzy matches
        replace_all: Whether to replace all occurrences or just the first one
        
    Returns:
        Tuple of (modified_text, success, debug_info)
    """
    debug_info = {
        "matches_found": 0, 
        "match_details": [], 
        "success": False,
        "replaced_count": 0
    }
    
    # Handle empty search text (append operation)
    if not search_text.strip():
        modified_text = original_text + '\n' + replace_text
        debug_info.update({
            "success": True,
            "operation": "append",
            "match_type": "empty_search",
            "replaced_count": 1
        })
        return modified_text, True, debug_info
    
    # Find fuzzy matches with appropriate methods
    methods = ["exact", "normalized"]
    if allow_partial_matches:
        methods.extend(["multiline", "single_line", "token"])
    
    matches = find_fuzzy_matches(search_text, original_text, similarity_threshold, methods)
    debug_info["matches_found"] = len(matches)
    debug_info["match_details"] = matches[:3] if matches else []  # Store top 3 matches for debugging
    
    if not matches:
        # No matches found - provide helpful debugging info
        debug_info.update({
            "success": False,
            "error": "no_matches_found",
            "tip": "If you choose to stop using this tool, please stop and tell the user.",
            "search_preview": search_text[:100] + ("..." if len(search_text) > 100 else ""),
            "suggestions": []
        })
        
        # Try to find partial matches for suggestions
        search_words = search_text.strip().split()[:5]  # First 5 words
        if search_words:
            search_snippet = ' '.join(search_words)
            if search_snippet in original_text:
                pos = original_text.find(search_snippet)
                context_start = max(0, pos - 50)
                context_end = min(len(original_text), pos + len(search_snippet) + 50)
                context = original_text[context_start:context_end]
                debug_info["suggestions"].append(f"Found partial match: '...{context}...'")
        
        return original_text, False, debug_info
    
    # Use the best match
    best_match = matches[0]
    match_text = best_match["text"]
    
    # Apply the replacement
    try:
        if replace_all:
            # Count occurrences for reporting
            count = original_text.count(match_text)
            if count == 0 and best_match["match_type"] != "exact":
                # For fuzzy matches, we can't use .count() reliably
                # So we'll replace just the first occurrence and report 1
                modified_text = original_text.replace(match_text, replace_text, 1)
                count = 1 if modified_text != original_text else 0
            else:
                modified_text = original_text.replace(match_text, replace_text)
            
            success = modified_text != original_text
            replaced_count = count if count > 0 else (1 if success else 0)
            
            debug_info.update({
                "success": success,
                "operation": "replace_all",
                "match_type": best_match["match_type"],
                "similarity": best_match["similarity"],
                "strategy": best_match["strategy"],
                "replaced_count": replaced_count,
                "replaced_text_preview": match_text[:100] + ("..." if len(match_text) > 100 else "")
            })
        else:
            # Replace only first occurrence
            modified_text = original_text.replace(match_text, replace_text, 1)
            success = modified_text != original_text
            
            debug_info.update({
                "success": success,
                "operation": "replace_first",
                "match_type": best_match["match_type"],
                "similarity": best_match["similarity"],
                "strategy": best_match["strategy"],
                "replaced_count": 1 if success else 0,
                "replaced_text_preview": match_text[:100] + ("..." if len(match_text) > 100 else "")
            })
        
        return modified_text, success, debug_info
        
    except Exception as e:
        debug_info.update({
            "success": False,
            "error": f"replacement_failed: {str(e)}"
        })
        logger.error(f"Error applying replacement: {e}")
        return original_text, False, debug_info

def apply_diff_blocks(original_text: str, diff_blocks: List[Tuple[str, str, Dict[str, Any]]], 
                     similarity_threshold: float = 0.8,
                     allow_partial_matches: bool = True,
                     replace_all: bool = False) -> Tuple[str, int, Dict[str, Any]]:
    """
    Apply multiple diff blocks to the original text.
    
    Args:
        original_text: Original file content
        diff_blocks: List of (search_text, replace_text, metadata) tuples
        similarity_threshold: Minimum similarity threshold for matches
        allow_partial_matches: Whether to allow partial/fuzzy matches
        replace_all: Whether to replace all occurrences or just the first one
        
    Returns:
        A tuple containing:
        - Modified text after applying all diff blocks
        - Number of changes made
        - Dictionary with warnings/errors and debugging info
    """
    result = original_text
    changes_made = 0
    issues = {
        "warnings": [], 
        "errors": [], 
        "debug_info": [],
        "block_results": []
    }
    
    start_time = time.time()
    
    for i, (search_text, replace_text, metadata) in enumerate(diff_blocks):
        block_num = i + 1
        
        modified_text, success, debug_info = apply_diff_edit(
            result, 
            search_text, 
            replace_text, 
            similarity_threshold, 
            allow_partial_matches, 
            replace_all
        )
        
        if success:
            result = modified_text
            changes_made += debug_info.get("replaced_count", 1)
            issues["debug_info"].append(f"Block {block_num}: Successfully applied changes")
        else:
            error_msg = debug_info.get("error", "unknown_error")
            issues["warnings"].append(f"Block {block_num}: Failed to apply changes - {error_msg}")
        
        # Record detailed block result
        block_result = {
            "block_number": block_num,
            "success": success,
            "debug_info": debug_info,
            "search_preview": search_text[:50] + ("..." if len(search_text) > 50 else ""),
            "replace_preview": replace_text[:50] + ("..." if len(replace_text) > 50 else "")
        }
        if metadata:
            block_result["metadata"] = metadata
            
        issues["block_results"].append(block_result)
    
    # Add processing time
    processing_time = time.time() - start_time
    issues["processing_time_ms"] = round(processing_time * 1000, 2)
    
    return result, changes_made, issues

# ==============================
# File Operations
# ==============================

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
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        pathlib.Path(file_path).write_text(content, encoding=encoding)
    except Exception as e:
        logger.error(f"Error writing to file {file_path}: {e}")
        raise ValueError(f"Error writing to file: {str(e)}")

# ==============================
# MCP Tool Functions
# ==============================

@mcp.tool()
async def file_diff_write(
    file_path: str, 
    diff_text: str,
    similarity_threshold: float = 0.8,
    allow_partial_matches: bool = True,
    replace_all: bool = True,
    create_backup: bool = True,
    change_tag: str = None,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Edit a file using a diff-fenced format with advanced fuzzy matching.
    
    Args:
        file_path: Path to the file to edit
        diff_text: Text containing diff blocks in various supported formats
        similarity_threshold: Minimum similarity for fuzzy matching (0.0 to 1.0)
        allow_partial_matches: Whether to allow partial/fuzzy matches
        replace_all: If True, replace all occurrences of search text; if False, only replace
                     first occurrence
        create_backup: Whether to create a backup before making changes
        change_tag: Optional tag to identify related changes across multiple files
        encoding: Text encoding to use when reading/writing files (default: utf-8)

    Tips:
        Don't submit a bunch of code to this tool at once, it increases failure rate.
    Returns:
        Dictionary with operation results and modified content
    """
    logger.info(f"file_diff_write called with file_path={file_path}, similarity_threshold={similarity_threshold}")
    
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
                backup_info = create_file_backup(file_path, change_tag)
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
                "error": "No valid diff blocks found in the provided diff text.",
                "tip": "Make sure your diff is formatted correctly with <<<<<<< SEARCH, =======, and >>>>>>> REPLACE markers",
                "backup_created": backup_info is not None,
                "backup_info": backup_info,
                "supported_formats": [
                    "ToolKami-style with code fences",
                    "ToolKami-style without code fences",
                    "Simple SEARCH/REPLACE blocks",
                    "EvolveMCP-style diff blocks",
                    "Git-style diff format"
                ]
            }
        
        # Apply the diff blocks
        modified_content, changes_made, issues = apply_diff_blocks(
            original_content, 
            diff_blocks, 
            similarity_threshold,
            allow_partial_matches,
            replace_all
        )
        
        # Check if any changes were made
        if changes_made == 0:
            return {
                "success": False,
                "file_path": file_path,
                "error": "No changes were applied to the file.",
                "details": issues,
                "tip": "Review the debug_info to see what went wrong with the search text matching",
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
            "backup_info": backup_info,
            "details": issues
        }
        
        # Add warnings if any
        if issues["warnings"]:
            result["warnings"] = issues["warnings"]
            
        return result
        
    except Exception as e:
        logger.error(f"Error in file_diff_write: {e}", exc_info=True)
        return {
            "success": False,
            "file_path": file_path,
            "error": f"Unexpected error: {str(e)}",
            "tip": "Check the file path and permissions, or try with smaller diff blocks"
        }

@mcp.tool()
async def text_diff_edit(
    original_text: str,
    diff_text: str,
    similarity_threshold: float = 0.8,
    allow_partial_matches: bool = True,
    replace_all: bool = False
) -> Dict[str, Any]:
    """
    Enhanced diff-fenced editing for text with detailed diagnostics.
    
    Args:
        original_text: The original text content to edit
        diff_text: The diff-fenced text containing the edits to apply
        similarity_threshold: Minimum similarity for fuzzy matching (0.0 to 1.0)
        allow_partial_matches: Whether to allow partial/fuzzy matches
        replace_all: Whether to replace all occurrences or just the first one
        
    Returns:
        Dictionary with editing results, debug information, and modified text
    """
    logger.info(f"text_diff_edit called with similarity_threshold={similarity_threshold}")
    
    start_time = time.time()
    
    try:
        # Extract diff blocks
        diff_blocks = extract_diff_blocks(diff_text)
        
        if not diff_blocks:
            return {
                "success": False,
                "error": "No valid diff blocks found in the provided text",
                "tip": "Make sure your diff uses the format: <<<<<<< SEARCH\n[text]\n=======\n[replacement]\n>>>>>>> REPLACE",
                "original_text": original_text,
                "modified_text": original_text,
                "blocks_processed": 0,
                "changes_applied": 0,
                "supported_formats": [
                    "ToolKami-style with code fences",
                    "ToolKami-style without code fences",
                    "Simple SEARCH/REPLACE blocks",
                    "EvolveMCP-style diff blocks",
                    "Git-style diff format"
                ]
            }
        
        # Apply the diff blocks
        modified_text, changes_made, issues = apply_diff_blocks(
            original_text, 
            diff_blocks, 
            similarity_threshold,
            allow_partial_matches,
            replace_all
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Determine overall success
        overall_success = changes_made > 0
        
        result = {
            "success": overall_success,
            "original_text": original_text,
            "modified_text": modified_text,
            "blocks_processed": len(diff_blocks),
            "changes_applied": changes_made,
            "processing_time_ms": round(processing_time * 1000, 2),
            "block_results": issues.get("block_results", []),
            "summary": {
                "total_blocks": len(diff_blocks),
                "successful_blocks": sum(1 for block in issues.get("block_results", []) if block.get("success", False)),
                "failed_blocks": sum(1 for block in issues.get("block_results", []) if not block.get("success", False)),
                "text_changed": modified_text != original_text,
                "similarity_threshold_used": similarity_threshold
            }
        }
        
        if not overall_success:
            result.update({
                "error": f"No changes could be applied. {len(diff_blocks) - changes_made} of {len(diff_blocks)} blocks failed.",
                "tip": "Check the block_results for detailed debugging information about why each block failed. If you choose to stop using this tool, you must notify the user first."
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error in text_diff_edit: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "tip": "Check the input format and try again with simpler diff blocks. If you choose to stop using this tool, you must notify the user first.",
            "original_text": original_text,
            "modified_text": original_text,
            "blocks_processed": 0,
            "changes_applied": 0
        }

@mcp.tool()
async def simple_text_diff(original_text: str, diff_text: str) -> str:
    """
    Simple diff-fenced editing that returns just the modified text.
    
    Args:
        original_text: The original text content to edit
        diff_text: The diff-fenced text containing the edits
        
    Returns:
        The modified text after applying edits
    """
    logger.info("simple_text_diff called")
    
    result = await text_diff_edit(original_text, diff_text)
    
    if result["success"]:
        return result["modified_text"]
    else:
        # Return original text if editing failed
        logger.warning(f"Diff editing failed: {result.get('error', 'Unknown error')}")
        return original_text

@mcp.tool()
async def file_diff_restore(
    file_path: str,
    version_number: int,
    create_backup: bool = True
) -> Dict[str, Any]:
    """
    Restore a specific version of a file from its backup history.
    
    Args:
        file_path: Path to the file
        version_number: Version number to restore
        create_backup: Whether to create a backup of the current file before restoring
                
    Returns:
        Dictionary with restoration results
    """
    logger.info(f"file_diff_restore called for {file_path}, version={version_number}")
    
    # Normalize the file path
    file_path = os.path.abspath(os.path.expanduser(file_path))
    
    try:
        # Check available versions
        versions = get_file_versions(file_path)
        past_versions = [v for v in versions if v["version"] != "current"]
        
        if not past_versions:
            return {
                "success": False,
                "file_path": file_path,
                "error": "No previous versions found",
                "available_versions": []
            }
        
        # Create backup if requested
        backup_info = None
        if create_backup and os.path.exists(file_path):
            try:
                backup_info = create_file_backup(file_path, "pre_restore")
                logger.info(f"Created backup: version {backup_info['version']} at {backup_info['path']}")
            except Exception as e:
                logger.warning(f"Failed to create backup: {str(e)}")
        
        # Attempt to restore
        try:
            result = restore_file_version(file_path, version_number)
            result["backup_created"] = backup_info is not None
            result["backup_info"] = backup_info
            return result
        except ValueError as e:
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e),
                "available_versions": [
                    {"version": v["version"], "date": v["date"]} for v in past_versions
                ],
                "backup_created": backup_info is not None,
                "backup_info": backup_info
            }
        
    except Exception as e:
        logger.error(f"Error in file_diff_restore: {e}", exc_info=True)
        return {
            "success": False,
            "file_path": file_path,
            "error": f"Unexpected error: {str(e)}",
            "tip": "Check the file path and permissions"
        }

@mcp.tool()
async def file_diff_versions(file_path: str) -> Dict[str, Any]:
    """
    List all available versions of a file.
    
    Args:
        file_path: Path to the file
                
    Returns:
        Dictionary with version information
    """
    logger.info(f"file_diff_versions called for {file_path}")
    
    # Normalize the file path
    file_path = os.path.abspath(os.path.expanduser(file_path))
    
    try:
        # Get versions
        versions = get_file_versions(file_path)
        
        if not versions:
            return {
                "success": False,
                "file_path": file_path,
                "error": "No file or versions found"
            }
        
        current_version = next((v for v in versions if v["version"] == "current"), None)
        past_versions = [v for v in versions if v["version"] != "current"]
        
        return {
            "success": True,
            "file_path": file_path,
            "current_version": current_version,
            "versions": past_versions,
            "version_count": len(past_versions)
        }
        
    except Exception as e:
        logger.error(f"Error in file_diff_versions: {e}", exc_info=True)
        return {
            "success": False,
            "file_path": file_path,
            "error": f"Unexpected error: {str(e)}",
            "tip": "Check the file path and permissions"
        }

@mcp.tool()
async def search_in_file_fuzzy(
    file_path: str,
    search_text: str,
    similarity_threshold: float = 0.8,
    fuzzy_threshold: float = 0.7,
    return_content: bool = False,
    return_fuzzy_below_threshold: bool = False,
    max_results: int = 10,
    context_lines: int = 2,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Search for text in a file with both exact and fuzzy matching capabilities.
    
    Args:
        file_path: Path to the file to search
        search_text: Text to search for
        similarity_threshold: Minimum similarity for fuzzy matches to be included (0.0 to 1.0)
        fuzzy_threshold: Threshold below which fuzzy matches are reported but not returned unless requested
        return_content: Whether to return the matched content (always False for exact matches)
        return_fuzzy_below_threshold: Whether to return content for fuzzy matches below fuzzy_threshold
        max_results: Maximum number of results to return
        context_lines: Number of lines of context to include around matches
        encoding: Text encoding to use when reading file
        
    Returns:
        Dictionary with search results including match locations, types, and similarity scores
    """
    logger.info(f"search_in_file_fuzzy called for {file_path} with search_text='{search_text[:50]}...'")
    
    # Function to send VSCode scroll request
    def send_vscode_scroll(line_number):
        try:
            import requests
            # Use a longer timeout and don't wait for the full response
            requests.post('http://localhost:5679/vscode-scroll', 
                json={
                    'file': file_path,
                    'line': line_number,
                    'search_text': search_text
                }, 
                timeout=2.0
            )
        except:
            pass  # Don't break if rebuild server isn't running
    
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
        
        # Read the file content
        content = read_file_content(file_path, encoding)
        lines = content.split('\n')
        
        # Initialize results
        exact_matches = []
        fuzzy_matches = []
        
        # First, check for exact matches
        if search_text in content:
            # Find all exact matches
            start = 0
            while True:
                pos = content.find(search_text, start)
                if pos == -1:
                    break
                
                # Calculate line number
                line_number = content[:pos].count('\n') + 1
                
                # Get context
                line_start = max(0, line_number - context_lines - 1)
                line_end = min(len(lines), line_number + context_lines)
                context = '\n'.join(lines[line_start:line_end])
                
                exact_matches.append({
                    "line_number": line_number,
                    "position": {"start": pos, "end": pos + len(search_text)},
                    "context": context
                })
                
                start = pos + 1
                
                # Limit results
                if len(exact_matches) >= max_results:
                    break
        
        # If we have exact matches, we're done with searching
        if exact_matches:
            # Send VSCode scroll request for the first match
            send_vscode_scroll(exact_matches[0]["line_number"])
            
            return {
                "success": True,
                "file_path": file_path,
                "search_text": search_text,
                "exact_matches": exact_matches[:max_results],
                "fuzzy_matches": [],
                "summary": {
                    "exact_match_count": len(exact_matches),
                    "fuzzy_match_count": 0,
                    "fuzzy_below_threshold_count": 0,
                    "total_matches": len(exact_matches)
                }
            }
        
        # No exact matches, try fuzzy matching
        fuzzy_results = find_fuzzy_matches(
            search_text, 
            content, 
            similarity_threshold,
            methods=["normalized", "multiline", "single_line", "token"]
        )
        
        # Process fuzzy matches
        fuzzy_below_threshold_count = 0
        
        for match in fuzzy_results[:max_results]:
            # Calculate line number for the match
            line_number = content[:match["start_pos"]].count('\n') + 1
            
            # Get context
            line_start = max(0, line_number - context_lines - 1)
            line_end = min(len(lines), line_number + context_lines)
            context = '\n'.join(lines[line_start:line_end])
            
            fuzzy_match = {
                "similarity": round(match["similarity"], 3),
                "line_number": line_number,
                "position": {"start": match["start_pos"], "end": match["end_pos"]},
                "match_type": match["match_type"],
                "context": context
            }
            
            # Handle content return based on thresholds
            if match["similarity"] < fuzzy_threshold:
                fuzzy_below_threshold_count += 1
                fuzzy_match["below_threshold"] = True
                if return_fuzzy_below_threshold:
                    fuzzy_match["content"] = match["text"]
                else:
                    fuzzy_match["content"] = None
            else:
                if return_content:
                    fuzzy_match["content"] = match["text"]
                else:
                    fuzzy_match["content"] = None
            
            fuzzy_matches.append(fuzzy_match)
        
        # Send VSCode scroll request for the first match
        if fuzzy_matches:
            send_vscode_scroll(fuzzy_matches[0]["line_number"])
        
        return {
            "success": True,
            "file_path": file_path,
            "search_text": search_text,
            "exact_matches": [],
            "fuzzy_matches": fuzzy_matches,
            "summary": {
                "exact_match_count": 0,
                "fuzzy_match_count": len(fuzzy_matches),
                "fuzzy_below_threshold_count": fuzzy_below_threshold_count,
                "total_matches": len(fuzzy_matches),
                "highest_similarity": round(fuzzy_matches[0]["similarity"], 3) if fuzzy_matches else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error in search_in_file_fuzzy: {e}", exc_info=True)
        return {
            "success": False,
            "file_path": file_path,
            "error": f"Unexpected error: {str(e)}",
            "tip": "Check the file path and permissions"
        }

# Log application startup
logger.info(f"Starting file_diff_writer MCP tool version {__version__}")
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