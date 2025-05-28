#!/usr/bin/env python3
"""
file_diff_writer_v2.py - Unified File Diff Editor with Revolutionary Pattern Engine

The ultimate diff management tool combining the best features from:
- file_apply_diff.py (reliable fuzzy matching)
- file_diff_writer.py (advanced multi-format support) 
- file_restore_backups.py (session-based restoration)
- file_diff_editor.py (custom regex & pattern introspection)

Features:
- Universal format support through custom regex patterns
- Intelligent conflict detection and resolution
- Pattern testing and validation framework
- Session-based change tracking and restoration
- Advanced fuzzy matching with multiple algorithms
- Self-aware tool capabilities and introspection
- Enterprise-grade backup and versioning system
- LLM-optimized design with comprehensive error handling

Copyright 2025 Kord Campbell
Licensed under the Apache License, Version 2.0
Version: 2.0.0 - The Revolutionary Edition
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

__version__ = "2.1.1"
__updated__ = "2025-05-28"

# CHANGELOG v2.1.1:
# - CRITICAL FIX: Fixed regex backreference escaping (\\1 -> \1)
# - Fixed regex backreference handling in replace_with_pattern()
# - Added safe_regex_replace() with validation
# - Improved validate_custom_pattern() with dynamic test cases  
# - Added search_in_file_regex() for proper regex search
# - Enhanced error messages and regex validation
# - Fixed literal replacement of \\1, \\2 instead of actual backreferences

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Log file path
log_file = os.path.join(logs_dir, "file_diff_writer_v2.log")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("file_diff_writer_v2")

# Import MCP server library
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("file-diff-writer-v2-server")

# ====================================
# Pattern Registry - Enhanced from file_diff_editor
# ====================================

DIFF_PATTERNS = {
    "custom_safe": {
        "pattern": r'<<<CUSTOM_SEARCH>>>\n(.*?)\n<<<CUSTOM_REPLACE>>>\n(.*?)\n<<<END_CUSTOM>>>',
        "description": "Custom safe delimiters (conflict-free)",
        "example": "<<<CUSTOM_SEARCH>>>\nold code\n<<<CUSTOM_REPLACE>>>\nnew code\n<<<END_CUSTOM>>>"
    },
    "toolkami_fenced": {
        "pattern": r'```diff\s*\n(.*?)\n<<<<<<< SEARCH\n(.*?)={7}\n(.*?)>>>>>>> REPLACE\n```',
        "description": "ToolKami-style with code fences",
        "example": "```diff\nfile.py\n<<<<<<< SEARCH\nold code\n=======\nnew code\n>>>>>>> REPLACE\n```"
    },
    "toolkami_direct": {
        "pattern": r'(.*?)\n<<<<<<< SEARCH\n(.*?)={7}\n(.*?)>>>>>>> REPLACE',
        "description": "ToolKami-style without code fences", 
        "example": "file.py\n<<<<<<< SEARCH\nold code\n=======\nnew code\n>>>>>>> REPLACE"
    },
    "simple_blocks": {
        "pattern": r'<<<<<<< SEARCH\n(.*?)={7}\n(.*?)>>>>>>> REPLACE',
        "description": "Simple SEARCH/REPLACE blocks",
        "example": "<<<<<<< SEARCH\nold code\n=======\nnew code\n>>>>>>> REPLACE"
    },
    "evolvemcp_style": {
        "pattern": r'```diff\n(.*?)<<<<<<< SEARCH\n(.*?)={7}\n(.*?)>>>>>>> REPLACE\n```',
        "description": "EvolveMCP-style diff blocks",
        "example": "```diff\n\n<<<<<<< SEARCH\nold code\n=======\nnew code\n>>>>>>> REPLACE\n```"
    },
    "git_style": {
        "pattern": r'--- a/(.*?)\n\+\+\+ b/.*?\n@@ .*? @@.*?\n(.*?)(?=\n--- a/|$)',
        "description": "Git-style diff format",
        "example": "--- a/file.py\n+++ b/file.py\n@@ -1,3 +1,3 @@\n-old code\n+new code"
    }
}

# ====================================
# File Versioning and Backup Functions
# ====================================

def ensure_version_dir(file_path: str) -> str:
    """
    Ensures that a versions directory exists for the given file.
    """
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    versions_dir = os.path.join(directory, f".{filename}_versions")
    os.makedirs(versions_dir, exist_ok=True)
    return versions_dir

def get_file_versions(file_path: str) -> List[Dict[str, Any]]:
    """
    Gets information about all versions of a file.
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
            match = re.match(r"v(\d+)_(\d+)(\..*)?\.backup", version_file)
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

def restore_file_version(file_path: str, version_number: int, create_backup: bool = True) -> Dict[str, Any]:
    """
    Restores a specific version of a file.
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
    if create_backup and os.path.exists(file_path):
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

# ====================================
# Session Management Functions (from file_restore_backups)
# ====================================

def get_backup_by_tag(change_tag: str) -> List[Dict[str, Any]]:
    """
    Finds all files that were modified with the specified change_tag.
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
                    match = re.match(rf"v(\d+)_(\d+)\.{re.escape(change_tag)}\.backup", backup_file)
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
                    match = re.match(r"v(\d+)_(\d+)\.(.+)\.backup", backup_file)
                    if match:
                        tag = match.group(3)
                        tags.add(tag)
    
    return sorted(list(tags))

# ====================================
# Regex Helper Utilities - NEW SECTION
# ====================================

def escape_regex_special_chars(text: str) -> str:
    """
    Escape special regex characters in text for literal matching.
    """
    return re.escape(text)

def validate_backreferences(replacement_text: str, group_count: int) -> Dict[str, Any]:
    """
    Validate that backreferences in replacement text don't exceed available groups.
    """
    # Find all backreferences like \1, \2, etc.
    backrefs = re.findall(r'\\(\d+)', replacement_text)
    
    invalid_refs = []
    for ref in backrefs:
        ref_num = int(ref)
        if ref_num > group_count:
            invalid_refs.append(ref_num)
    
    return {
        "valid": len(invalid_refs) == 0,
        "backreferences_found": [int(ref) for ref in backrefs],
        "invalid_references": invalid_refs,
        "max_group_available": group_count
    }

def safe_regex_replace(pattern: str, replacement: str, text: str) -> Tuple[str, int, Dict[str, Any]]:
    """
    Safely perform regex replacement with proper backreference handling and validation.
    """
    try:
        # Compile the pattern
        compiled_pattern = re.compile(pattern, re.DOTALL)
        
        # Convert double backslashes in backreferences to single backslashes
        # This fixes the issue where \\1 gets passed instead of \1
        processed_replacement = re.sub(r'\\\\(\d+)', r'\\\1', replacement)
        
        # Validate backreferences in replacement text (use original for validation)
        group_count = compiled_pattern.groups
        validation = validate_backreferences(replacement, group_count)
        
        if not validation["valid"]:
            return text, 0, {
                "error": f"Invalid backreferences: {validation['invalid_references']}. Pattern only has {group_count} groups.",
                "validation": validation
            }
        
        # Perform the replacement with processed replacement text
        result, count = re.subn(compiled_pattern, processed_replacement, text)
        
        return result, count, {
            "success": True,
            "groups_available": group_count,
            "backreferences_used": validation["backreferences_found"],
            "validation": validation,
            "original_replacement": replacement,
            "processed_replacement": processed_replacement
        }
        
    except re.error as e:
        return text, 0, {
            "error": f"Regex error: {str(e)}",
            "pattern": pattern,
            "replacement": replacement
        }

# ====================================
# Text Processing and Matching Functions
# ====================================

def normalize_whitespace(text: str, preserve_structure: bool = True) -> str:
    """
    Normalize whitespace for flexible matching.
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
    
    # Strategy 4: Single-line fuzzy matching
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
        token_similarity = calculate_similarity(search_text, content, "token_sort")
        
        if token_similarity >= similarity_threshold:
            start_pos = content.lower().find(search_text.strip().lower())
            if start_pos < 0:
                # Try with first few words
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

# ====================================
# Pattern Extraction Functions
# ====================================

def extract_diff_blocks_enhanced(diff_text: str, custom_pattern: str = None) -> Tuple[List[Tuple[str, str, Dict[str, Any]]], str]:
    """
    Extract diff blocks using either built-in patterns or custom pattern.
    Enhanced version combining file_diff_editor and file_diff_writer approaches.
    """
    blocks = []
    
    # Try custom pattern first if provided
    if custom_pattern:
        try:
            matches = re.findall(custom_pattern, diff_text, re.DOTALL)
            if matches:
                for match in matches:
                    if len(match) >= 2:
                        search_text, replace_text = match[0], match[1]
                        blocks.append((search_text, replace_text, {"method": "custom_pattern"}))
                return blocks, custom_pattern
        except re.error as e:
            # Invalid regex pattern
            return [], f"INVALID_PATTERN: {str(e)}"
    
    # Try built-in patterns in priority order
    for pattern_name, pattern_info in DIFF_PATTERNS.items():
        pattern = pattern_info["pattern"]
        try:
            matches = re.findall(pattern, diff_text, re.DOTALL)
            if matches:
                for match in matches:
                    if len(match) >= 2:
                        # Handle different match group structures
                        if len(match) == 3 and pattern_name in ["toolkami_fenced", "toolkami_direct", "evolvemcp_style"]:
                            # (filename, search_text, replace_text)
                            search_text, replace_text = match[1], match[2]
                            blocks.append((search_text, replace_text, {"filename_hint": match[0].strip(), "method": pattern_name}))
                        elif pattern_name == "git_style":
                            # Convert git-style diff to search/replace format
                            filename, diff_content = match
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
                            blocks.append((search_text, replace_text, {"filename_hint": filename.strip(), "method": pattern_name}))
                        else:
                            # (search_text, replace_text)
                            search_text, replace_text = match[0], match[1]
                            blocks.append((search_text, replace_text, {"method": pattern_name}))
                return blocks, pattern_name
        except re.error:
            continue
    
    return blocks, "NO_PATTERN_MATCHED"

# ====================================
# File Operations
# ====================================

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

# ====================================
# MCP Tool Functions - Core Operations
# ====================================

@mcp.tool()
async def file_diff_write(
    file_path: str,
    diff_text: str = None,
    custom_pattern: str = None,
    search_text: str = None,
    replace_text: str = None,
    use_direct_mode: bool = False,
    similarity_threshold: float = 0.8,
    allow_partial_matches: bool = True,
    replace_all: bool = True,
    create_backup: bool = True,
    change_tag: str = None,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Enhanced diff application with custom regex support and advanced fuzzy matching.
    """
    logger.info(f"file_diff_write called with file_path={file_path}")
    
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
        
        # Handle direct mode (bypass diff parsing)
        if use_direct_mode:
            if search_text is None or replace_text is None:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "Direct mode requires both search_text and replace_text parameters"
                }
            
            # Create backup if requested
            backup_info = None
            if create_backup:
                try:
                    backup_info = create_file_backup(file_path, change_tag)
                    logger.info(f"Created backup: version {backup_info['version']} at {backup_info['path']}")
                except Exception as e:
                    logger.warning(f"Failed to create backup: {str(e)}")
            
            # Read and apply direct replacement
            original_content = read_file_content(file_path, encoding)
            
            # Find matches
            matches = find_fuzzy_matches(search_text, original_content, similarity_threshold)
            
            if not matches:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "No matches found for search text in direct mode",
                    "backup_created": backup_info is not None,
                    "backup_info": backup_info
                }
            
            # Apply replacement
            best_match = matches[0]
            match_text = best_match["text"]
            
            if replace_all:
                count = original_content.count(match_text)
                modified_content = original_content.replace(match_text, replace_text)
            else:
                modified_content = original_content.replace(match_text, replace_text, 1)
                count = 1 if modified_content != original_content else 0
            
            if modified_content != original_content:
                write_file_content(file_path, modified_content, encoding)
                stats = os.stat(file_path)
                
                return {
                    "success": True,
                    "file_path": file_path,
                    "message": f"Successfully applied direct mode change to {file_path}",
                    "changes_applied": count,
                    "method": "direct_mode",
                    "match_info": best_match,
                    "size": stats.st_size,
                    "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                    "backup_created": backup_info is not None,
                    "backup_info": backup_info
                }
            else:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": "Direct mode replacement failed - no changes made",
                    "backup_created": backup_info is not None,
                    "backup_info": backup_info
                }
        
        # Standard diff mode - require diff_text
        if diff_text is None:
            return {
                "success": False,
                "file_path": file_path,
                "error": "Either diff_text must be provided, or use_direct_mode=True with search_text and replace_text"
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
        diff_blocks, pattern_used = extract_diff_blocks_enhanced(diff_text, custom_pattern)
        
        if not diff_blocks:
            return {
                "success": False,
                "file_path": file_path,
                "error": "No valid diff blocks found in the provided diff text",
                "pattern_attempted": pattern_used,
                "tip": "Make sure your diff is formatted correctly or provide a custom_pattern",
                "backup_created": backup_info is not None,
                "backup_info": backup_info,
                "supported_formats": list(DIFF_PATTERNS.keys())
            }
        
        # Apply the diff blocks
        result_content = original_content
        changes_made = 0
        block_results = []
        
        for i, (search_text_block, replace_text_block, metadata) in enumerate(diff_blocks):
            block_num = i + 1
            
            if not search_text_block.strip():
                # Empty search text - append operation
                result_content += '\n' + replace_text_block
                changes_made += 1
                block_results.append({
                    "block_number": block_num,
                    "success": True,
                    "operation": "append",
                    "metadata": metadata
                })
                continue
            
            # Find matches for this block
            matches = find_fuzzy_matches(search_text_block, result_content, similarity_threshold)
            
            if not matches:
                block_results.append({
                    "block_number": block_num,
                    "success": False,
                    "error": "no_matches_found",
                    "search_preview": search_text_block[:100] + ("..." if len(search_text_block) > 100 else ""),
                    "metadata": metadata
                })
                continue
            
            # Apply replacement using best match
            best_match = matches[0]
            match_text = best_match["text"]
            
            if replace_all:
                count = result_content.count(match_text)
                result_content = result_content.replace(match_text, replace_text_block)
                changes_made += count
            else:
                result_content = result_content.replace(match_text, replace_text_block, 1)
                changes_made += 1 if result_content != original_content else 0
            
            block_results.append({
                "block_number": block_num,
                "success": True,
                "operation": "replace_all" if replace_all else "replace_first",
                "match_info": best_match,
                "replaced_count": count if replace_all else 1,
                "metadata": metadata
            })
        
        # Check if any changes were made
        if changes_made == 0:
            return {
                "success": False,
                "file_path": file_path,
                "error": "No changes were applied to the file",
                "pattern_used": pattern_used,
                "blocks_processed": len(diff_blocks),
                "block_results": block_results,
                "backup_created": backup_info is not None,
                "backup_info": backup_info
            }
        
        # Write the modified content back to the file
        write_file_content(file_path, result_content, encoding)
        
        # Get the file stats
        stats = os.stat(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "message": f"Successfully applied {changes_made} changes to {file_path}",
            "changes_applied": changes_made,
            "pattern_used": pattern_used,
            "blocks_processed": len(diff_blocks),
            "block_results": block_results,
            "size": stats.st_size,
            "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
            "backup_created": backup_info is not None,
            "backup_info": backup_info
        }
        
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
    custom_pattern: str = None,
    similarity_threshold: float = 0.8,
    allow_partial_matches: bool = True,
    replace_all: bool = False
) -> Dict[str, Any]:
    """
    Enhanced diff-fenced editing for text with detailed diagnostics.
    """
    logger.info(f"text_diff_edit called with similarity_threshold={similarity_threshold}")
    
    start_time = time.time()
    
    try:
        # Extract diff blocks
        diff_blocks, pattern_used = extract_diff_blocks_enhanced(diff_text, custom_pattern)
        
        if not diff_blocks:
            return {
                "success": False,
                "error": "No valid diff blocks found in the provided text",
                "pattern_attempted": pattern_used,
                "tip": "Make sure your diff uses a supported format or provide a custom_pattern",
                "original_text": original_text,
                "modified_text": original_text,
                "blocks_processed": 0,
                "changes_applied": 0,
                "supported_formats": list(DIFF_PATTERNS.keys())
            }
        
        # Apply the diff blocks
        result_text = original_text
        changes_made = 0
        block_results = []
        
        for i, (search_text_block, replace_text_block, metadata) in enumerate(diff_blocks):
            block_num = i + 1
            
            if not search_text_block.strip():
                # Empty search text - append operation
                result_text += '\n' + replace_text_block
                changes_made += 1
                block_results.append({
                    "block_number": block_num,
                    "success": True,
                    "operation": "append",
                    "metadata": metadata
                })
                continue
            
            # Find matches for this block
            matches = find_fuzzy_matches(search_text_block, result_text, similarity_threshold)
            
            if not matches:
                block_results.append({
                    "block_number": block_num,
                    "success": False,
                    "error": "no_matches_found",
                    "search_preview": search_text_block[:50] + ("..." if len(search_text_block) > 50 else ""),
                    "replace_preview": replace_text_block[:50] + ("..." if len(replace_text_block) > 50 else ""),
                    "metadata": metadata
                })
                continue
            
            # Apply replacement using best match
            best_match = matches[0]
            match_text = best_match["text"]
            
            if replace_all:
                count = result_text.count(match_text)
                result_text = result_text.replace(match_text, replace_text_block)
                changes_made += count
            else:
                result_text = result_text.replace(match_text, replace_text_block, 1)
                changes_made += 1 if result_text != original_text else 0
            
            block_results.append({
                "block_number": block_num,
                "success": True,
                "operation": "replace_all" if replace_all else "replace_first",
                "match_info": best_match,
                "replaced_count": count if replace_all else 1,
                "search_preview": search_text_block[:50] + ("..." if len(search_text_block) > 50 else ""),
                "replace_preview": replace_text_block[:50] + ("..." if len(replace_text_block) > 50 else ""),
                "metadata": metadata
            })
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Determine overall success
        overall_success = changes_made > 0
        
        result = {
            "success": overall_success,
            "original_text": original_text,
            "modified_text": result_text,
            "pattern_used": pattern_used,
            "blocks_processed": len(diff_blocks),
            "changes_applied": changes_made,
            "processing_time_ms": round(processing_time * 1000, 2),
            "block_results": block_results,
            "summary": {
                "total_blocks": len(diff_blocks),
                "successful_blocks": sum(1 for block in block_results if block.get("success", False)),
                "failed_blocks": sum(1 for block in block_results if not block.get("success", False)),
                "text_changed": result_text != original_text,
                "similarity_threshold_used": similarity_threshold
            }
        }
        
        if not overall_success:
            result.update({
                "error": f"No changes could be applied. {len(diff_blocks) - changes_made} of {len(diff_blocks)} blocks failed.",
                "tip": "Check the block_results for detailed debugging information about why each block failed."
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error in text_diff_edit: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "tip": "Check the input format and try again with simpler diff blocks.",
            "original_text": original_text,
            "modified_text": original_text,
            "blocks_processed": 0,
            "changes_applied": 0
        }

@mcp.tool()
async def simple_text_diff(original_text: str, diff_text: str, custom_pattern: str = None) -> str:
    """
    Simple diff-fenced editing that returns just the modified text.
    """
    logger.info("simple_text_diff called")
    
    result = await text_diff_edit(original_text, diff_text, custom_pattern)
    
    if result["success"]:
        return result["modified_text"]
    else:
        # Return original text if editing failed
        logger.warning(f"Diff editing failed: {result.get('error', 'Unknown error')}")
        return original_text

# ====================================
# Pattern Management Tools
# ====================================

@mcp.tool()
async def get_diff_formats() -> Dict[str, Any]:
    """
    Get all supported diff formats and custom pattern capabilities.
    """
    return {
        "supported_patterns": [
            {
                "name": name,
                "pattern": info["pattern"],
                "description": info["description"],
                "example": info["example"]
            }
            for name, info in DIFF_PATTERNS.items()
        ],
        "custom_pattern_support": True,
        "custom_pattern_info": {
            "description": "Send custom regex pattern with 'custom_pattern' parameter",
            "requirements": [
                "Pattern must have exactly 2 capture groups: (search_text) and (replace_text)",
                "Pattern must be valid Python regex",
                "Use re.DOTALL flag compatibility (multiline matching)"
            ],
            "example": {
                "pattern": r'\[\[FIND\]\]\n(.*?)\n\[\[REPLACE\]\]\n(.*?)\n\[\[END\]\]',
                "usage": "[[FIND]]\nold code\n[[REPLACE]]\nnew code\n[[END]]"
            }
        },
        "total_patterns": len(DIFF_PATTERNS)
    }

@mcp.tool()
async def test_diff_pattern(
    test_text: str,
    custom_pattern: str = None
) -> Dict[str, Any]:
    """
    Test a diff pattern against sample text to see what it matches.
    """
    blocks, pattern_used = extract_diff_blocks_enhanced(test_text, custom_pattern)
    
    return {
        "success": len(blocks) > 0,
        "pattern_used": pattern_used,
        "blocks_found": len(blocks),
        "blocks": [
            {
                "search_text": block[0][:100] + ("..." if len(block[0]) > 100 else ""),
                "replace_text": block[1][:100] + ("..." if len(block[1]) > 100 else ""),
                "metadata": block[2]
            }
            for block in blocks
        ],
        "test_text_length": len(test_text)
    }

@mcp.tool()
async def analyze_content_for_patterns(content: str) -> Dict[str, Any]:
    """
    Analyze content to suggest safe diff patterns that won't conflict.
    """
    # Check for problematic sequences
    conflicts = {}
    conflicts["seven_equals"] = content.count("=======")
    conflicts["many_equals"] = len(re.findall(r'={10,}', content))
    conflicts["search_markers"] = content.count("<<<<<<< SEARCH")
    conflicts["replace_markers"] = content.count(">>>>>>> REPLACE")
    conflicts["custom_safe"] = content.count("<<<CUSTOM_SEARCH>>>")
    
    # Recommend safe patterns
    recommendations = []
    if conflicts["seven_equals"] == 0 and conflicts["search_markers"] == 0:
        recommendations.append("simple_blocks")
    if conflicts["custom_safe"] == 0:
        recommendations.append("custom_safe")
    
    # Suggest custom delimiters if needed
    safe_delimiters = []
    test_delimiters = [
        ("[CHANGE]", "[TO]", "[DONE]"),
        ("{{OLD}}", "{{NEW}}", "{{END}}"),
        ("---START---", "---REPLACE---", "---FINISH---"),
        ("[[[FIND]]]", "[[[REPLACE]]]", "[[[END]]]")
    ]
    
    for start, middle, end in test_delimiters:
        if start not in content and middle not in content and end not in content:
            safe_delimiters.append({
                "delimiters": [start, middle, end],
                "pattern": f"r'{re.escape(start)}\\n(.*?)\\n{re.escape(middle)}\\n(.*?)\\n{re.escape(end)}'"
            })
            if len(safe_delimiters) >= 3:  # Limit suggestions
                break
    
    return {
        "content_length": len(content),
        "conflicts_found": conflicts,
        "safe_builtin_patterns": recommendations,
        "suggested_custom_delimiters": safe_delimiters,
        "analysis": {
            "has_conflicts": any(count > 0 for count in conflicts.values()),
            "needs_custom_pattern": len(recommendations) == 0,
            "recommended_approach": "custom_pattern" if len(recommendations) == 0 else "builtin_patterns"
        }
    }

@mcp.tool()
async def suggest_safe_pattern(content: str) -> Dict[str, Any]:
    """
    Auto-generate conflict-free custom delimiters based on content analysis.
    """
    analysis = await analyze_content_for_patterns(content)
    
    if not analysis["analysis"]["has_conflicts"]:
        return {
            "success": True,
            "message": "No conflicts detected - standard patterns are safe to use",
            "recommended_pattern": "simple_blocks",
            "safe_builtin_patterns": analysis["safe_builtin_patterns"]
        }
    
    if analysis["suggested_custom_delimiters"]:
        best_delimiter = analysis["suggested_custom_delimiters"][0]
        return {
            "success": True,
            "message": "Generated safe custom pattern",
            "recommended_pattern": "custom",
            "custom_pattern": best_delimiter["pattern"],
            "custom_delimiters": best_delimiter["delimiters"],
            "usage_example": f"{best_delimiter['delimiters'][0]}\nold code\n{best_delimiter['delimiters'][1]}\nnew code\n{best_delimiter['delimiters'][2]}"
        }
    
    return {
        "success": False,
        "message": "Unable to generate safe pattern - content has extensive conflicts",
        "recommendation": "Consider using a different approach or manually clean the content"
    }

@mcp.tool()
async def validate_custom_pattern(pattern: str) -> Dict[str, Any]:
    """
    Comprehensive pattern validation with dynamic test cases.
    """
    try:
        # Compile the pattern to check for syntax errors
        compiled_pattern = re.compile(pattern, re.DOTALL)
        
        # Check for exactly 2 capture groups
        group_count = compiled_pattern.groups
        
        if group_count != 2:
            return {
                "valid": False,
                "error": f"Pattern must have exactly 2 capture groups, found {group_count}",
                "suggestion": "Use (search_text) and (replace_text) capture groups"
            }
        
        # Generate dynamic test cases based on common patterns
        test_cases = [
            # Basic delimiter patterns
            "[SEARCH]\nold code\n[REPLACE]\nnew code\n[END]",
            "{{OLD}}\nsome text\n{{NEW}}\nreplacement text\n{{END}}",
            "<<<FIND>>>\noriginal\n<<<REPLACE>>>\nmodified\n<<<DONE>>>",
            # More complex cases
            "START_CHANGE\ndef old_function():\n    return 'old'\nEND_CHANGE\nSTART_NEW\ndef new_function():\n    return 'new'\nEND_NEW",
            # Simple cases
            "OLD: some text\nNEW: different text\n",
            # Multi-line cases
            "BEFORE:\nline 1\nline 2\nAFTER:\nmodified line 1\nmodified line 2\nFINISH:"
        ]
        
        successful_tests = 0
        test_results = []
        
        for test_text in test_cases:
            test_match = compiled_pattern.search(test_text)
            if test_match and len(test_match.groups()) >= 2:
                successful_tests += 1
                test_results.append({
                    "text": test_text[:50] + "..." if len(test_text) > 50 else test_text,
                    "matched": True,
                    "groups": [test_match.group(1)[:30] + "..." if len(test_match.group(1)) > 30 else test_match.group(1),
                              test_match.group(2)[:30] + "..." if len(test_match.group(2)) > 30 else test_match.group(2)]
                })
            else:
                test_results.append({
                    "text": test_text[:50] + "..." if len(test_text) > 50 else test_text,
                    "matched": False
                })
        
        # Additional validation: check if pattern looks reasonable
        pattern_analysis = {
            "has_capture_groups": group_count == 2,
            "has_delimiters": any(delimiter in pattern for delimiter in ["\\[", "\\{", "<", ">"]),
            "has_multiline_support": "\\n" in pattern or "DOTALL" in str(compiled_pattern.flags),
            "estimated_complexity": "low" if len(pattern) < 50 else "medium" if len(pattern) < 150 else "high"
        }
        
        return {
            "valid": True,
            "pattern": pattern,
            "group_count": group_count,
            "test_cases_passed": successful_tests,
            "total_test_cases": len(test_cases),
            "success_rate": f"{(successful_tests/len(test_cases)*100):.1f}%",
            "test_results": test_results[:3],  # Show first 3 results to avoid clutter
            "pattern_analysis": pattern_analysis,
            "message": f"Pattern is valid. Passed {successful_tests}/{len(test_cases)} test cases."
        }
        
    except re.error as e:
        return {
            "valid": False,
            "error": f"Invalid regex pattern: {str(e)}",
            "suggestion": "Check your regex syntax and escape special characters"
        }

# ====================================
# Search and Replace Tools
# ====================================

@mcp.tool()
async def search_in_file_regex(
    file_path: str,
    search_pattern: str,
    pattern_type: str = "regex",
    max_results: int = 10,
    context_lines: int = 2,
    return_groups: bool = True,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Search for text in a file using regex patterns with proper backreference support.
    """
    logger.info(f"search_in_file_regex called for {file_path} with pattern='{search_pattern[:50]}...'")
    
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
        lines = content.split('\\n')
        
        if pattern_type == "regex":
            try:
                # Compile the regex pattern
                compiled_pattern = re.compile(search_pattern, re.DOTALL | re.MULTILINE)
            except re.error as e:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": f"Invalid regex pattern: {str(e)}",
                    "pattern": search_pattern
                }
            
            # Find all matches
            matches = []
            for match in compiled_pattern.finditer(content):
                # Calculate line number
                line_number = content[:match.start()].count('\\n') + 1
                
                # Get context
                line_start = max(0, line_number - context_lines - 1)
                line_end = min(len(lines), line_number + context_lines)
                context = '\\n'.join(lines[line_start:line_end])
                
                match_info = {
                    "line_number": line_number,
                    "position": {"start": match.start(), "end": match.end()},
                    "matched_text": match.group(0),
                    "context": context
                }
                
                # Include capture groups if requested
                if return_groups and match.groups():
                    match_info["groups"] = list(match.groups())
                    match_info["group_count"] = len(match.groups())
                
                matches.append(match_info)
                
                # Limit results
                if len(matches) >= max_results:
                    break
            
            return {
                "success": True,
                "file_path": file_path,
                "search_pattern": search_pattern,
                "pattern_type": "regex",
                "matches": matches,
                "summary": {
                    "match_count": len(matches),
                    "pattern_groups": compiled_pattern.groups,
                    "total_matches": len(matches)
                }
            }
        
        else:
            # Fallback to literal search for non-regex patterns
            matches = []
            start = 0
            while True:
                pos = content.find(search_pattern, start)
                if pos == -1:
                    break
                
                # Calculate line number
                line_number = content[:pos].count('\\n') + 1
                
                # Get context
                line_start = max(0, line_number - context_lines - 1)
                line_end = min(len(lines), line_number + context_lines)
                context = '\\n'.join(lines[line_start:line_end])
                
                matches.append({
                    "line_number": line_number,
                    "position": {"start": pos, "end": pos + len(search_pattern)},
                    "matched_text": search_pattern,
                    "context": context
                })
                
                start = pos + 1
                
                # Limit results
                if len(matches) >= max_results:
                    break
            
            return {
                "success": True,
                "file_path": file_path,
                "search_pattern": search_pattern,
                "pattern_type": "literal",
                "matches": matches,
                "summary": {
                    "match_count": len(matches),
                    "total_matches": len(matches)
                }
            }
        
    except Exception as e:
        logger.error(f"Error in search_in_file_regex: {e}", exc_info=True)
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
    Search for text in a file with fuzzy matching capabilities (NOT regex).
    For regex search, use search_in_file_regex() instead.
    """
    logger.info(f"search_in_file_fuzzy called for {file_path} with search_text='{search_text[:50]}...'")
    
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

@mcp.tool()
async def replace_with_pattern(
    file_path: str,
    search_pattern: str,
    replace_text: str,
    pattern_type: str = "regex",
    create_backup: bool = True,
    change_tag: str = None,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Pattern-based replacement operations using regex or custom patterns.
    """
    logger.info(f"replace_with_pattern called for {file_path} with pattern_type={pattern_type}")
    
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
        
        # Read the file content
        original_content = read_file_content(file_path, encoding)
        
        # Apply pattern-based replacement
        if pattern_type == "regex":
            # Use safe regex replacement with backreference validation
            modified_content, count, regex_info = safe_regex_replace(search_pattern, replace_text, original_content)
            
            if "error" in regex_info:
                return {
                    "success": False,
                    "file_path": file_path,
                    "error": regex_info["error"],
                    "regex_validation": regex_info.get("validation"),
                    "backup_created": backup_info is not None,
                    "backup_info": backup_info
                }
        else:
            # Use literal string replacement
            count = original_content.count(search_pattern)
            modified_content = original_content.replace(search_pattern, replace_text)
        
        # Check if any changes were made
        if count == 0:
            return {
                "success": False,
                "file_path": file_path,
                "error": "No matches found for the pattern",
                "pattern": search_pattern,
                "pattern_type": pattern_type,
                "backup_created": backup_info is not None,
                "backup_info": backup_info
            }
        
        # Write the modified content back to the file
        write_file_content(file_path, modified_content, encoding)
        
        # Get the file stats
        stats = os.stat(file_path)
        
        return {
            "success": True,
            "file_path": file_path,
            "message": f"Successfully replaced {count} occurrences using {pattern_type} pattern",
            "replacements_made": count,
            "pattern": search_pattern,
            "pattern_type": pattern_type,
            "size": stats.st_size,
            "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
            "backup_created": backup_info is not None,
            "backup_info": backup_info
        }
        
    except Exception as e:
        logger.error(f"Error in replace_with_pattern: {e}", exc_info=True)
        return {
            "success": False,
            "file_path": file_path,
            "error": f"Unexpected error: {str(e)}",
            "tip": "Check the file path and permissions"
        }

@mcp.tool()
async def bulk_pattern_replace(
    file_paths: List[str],
    search_pattern: str,
    replace_text: str,
    pattern_type: str = "regex",
    create_backup: bool = True,
    change_tag: str = None,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Multi-file pattern operations with session tracking.
    """
    logger.info(f"bulk_pattern_replace called for {len(file_paths)} files")
    
    # Generate a unique session tag if not provided
    if not change_tag:
        change_tag = f"bulk_replace_{int(time.time())}"
    
    results = []
    total_replacements = 0
    successful_files = 0
    
    for file_path in file_paths:
        try:
            result = await replace_with_pattern(
                file_path=file_path,
                search_pattern=search_pattern,
                replace_text=replace_text,
                pattern_type=pattern_type,
                create_backup=create_backup,
                change_tag=change_tag,
                encoding=encoding
            )
            
            results.append({
                "file_path": file_path,
                "success": result["success"],
                "replacements_made": result.get("replacements_made", 0),
                "error": result.get("error"),
                "backup_info": result.get("backup_info")
            })
            
            if result["success"]:
                successful_files += 1
                total_replacements += result.get("replacements_made", 0)
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            results.append({
                "file_path": file_path,
                "success": False,
                "replacements_made": 0,
                "error": f"Processing error: {str(e)}",
                "backup_info": None
            })
    
    return {
        "success": successful_files > 0,
        "session_tag": change_tag,
        "summary": {
            "total_files": len(file_paths),
            "successful_files": successful_files,
            "failed_files": len(file_paths) - successful_files,
            "total_replacements": total_replacements
        },
        "file_results": results,
        "pattern": search_pattern,
        "pattern_type": pattern_type,
        "message": f"Bulk operation completed: {successful_files}/{len(file_paths)} files processed successfully"
    }

@mcp.tool()
async def preview_diff_changes(
    file_path: str = None,
    original_text: str = None,
    diff_text: str = None,
    custom_pattern: str = None,
    similarity_threshold: float = 0.8,
    encoding: str = "utf-8"
) -> Dict[str, Any]:
    """
    Preview changes before applying them.
    """
    logger.info("preview_diff_changes called")
    
    try:
        # Get the content to preview
        if file_path:
            file_path = os.path.abspath(os.path.expanduser(file_path))
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": "File not found",
                    "file_path": file_path
                }
            content = read_file_content(file_path, encoding)
        elif original_text:
            content = original_text
        else:
            return {
                "success": False,
                "error": "Either file_path or original_text must be provided"
            }
        
        if not diff_text:
            return {
                "success": False,
                "error": "diff_text is required for preview"
            }
        
        # Extract diff blocks
        diff_blocks, pattern_used = extract_diff_blocks_enhanced(diff_text, custom_pattern)
        
        if not diff_blocks:
            return {
                "success": False,
                "error": "No valid diff blocks found",
                "pattern_attempted": pattern_used,
                "supported_formats": list(DIFF_PATTERNS.keys())
            }
        
        # Preview each block without applying changes
        preview_results = []
        
        for i, (search_text_block, replace_text_block, metadata) in enumerate(diff_blocks):
            block_num = i + 1
            
            if not search_text_block.strip():
                preview_results.append({
                    "block_number": block_num,
                    "operation": "append",
                    "preview": f"Will append: {replace_text_block[:100]}{'...' if len(replace_text_block) > 100 else ''}",
                    "metadata": metadata
                })
                continue
            
            # Find matches for preview
            matches = find_fuzzy_matches(search_text_block, content, similarity_threshold)
            
            if not matches:
                preview_results.append({
                    "block_number": block_num,
                    "operation": "no_match",
                    "preview": f"No matches found for: {search_text_block[:100]}{'...' if len(search_text_block) > 100 else ''}",
                    "metadata": metadata
                })
                continue
            
            best_match = matches[0]
            preview_results.append({
                "block_number": block_num,
                "operation": "replace",
                "match_info": {
                    "similarity": best_match["similarity"],
                    "match_type": best_match["match_type"],
                    "found_text": best_match["text"][:200] + ("..." if len(best_match["text"]) > 200 else "")
                },
                "preview": f"Will replace with: {replace_text_block[:100]}{'...' if len(replace_text_block) > 100 else ''}",
                "metadata": metadata
            })
        
        return {
            "success": True,
            "file_path": file_path,
            "pattern_used": pattern_used,
            "blocks_found": len(diff_blocks),
            "preview_results": preview_results,
            "content_length": len(content),
            "message": f"Preview generated for {len(diff_blocks)} diff blocks"
        }
        
    except Exception as e:
        logger.error(f"Error in preview_diff_changes: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

@mcp.tool()
async def optimize_pattern_performance(pattern: str, test_content: str = None) -> Dict[str, Any]:
    """
    Analyze and optimize regex patterns for better performance.
    """
    try:
        import timeit
        
        # Basic pattern analysis
        analysis = {
            "pattern_length": len(pattern),
            "has_lookahead": "(?=" in pattern or "(?!" in pattern,
            "has_lookbehind": "(?<=" in pattern or "(?<!" in pattern,
            "has_backreferences": any(f"\\{i}" in pattern for i in range(1, 10)),
            "has_character_classes": "[" in pattern and "]" in pattern,
            "has_quantifiers": any(q in pattern for q in ["*", "+", "?", "{"])
        }
        
        # Compile pattern to check for errors
        try:
            compiled_pattern = re.compile(pattern, re.DOTALL)
        except re.error as e:
            return {
                "success": False,
                "error": f"Pattern compilation failed: {str(e)}",
                "analysis": analysis
            }
        
        # Performance recommendations
        recommendations = []
        
        if analysis["has_lookahead"] or analysis["has_lookbehind"]:
            recommendations.append("Consider avoiding lookahead/lookbehind assertions for better performance")
        
        if analysis["has_backreferences"]:
            recommendations.append("Backreferences can be slow - consider using non-capturing groups (?:...)")
        
        if ".*" in pattern:
            recommendations.append("Replace .* with more specific patterns when possible")
        
        if analysis["pattern_length"] > 200:
            recommendations.append("Very long patterns can be slow - consider breaking into smaller parts")
        
        # Basic performance test if test content provided
        performance_info = None
        if test_content:
            def test_search():
                return compiled_pattern.search(test_content)
            
            def test_findall():
                return compiled_pattern.findall(test_content)
            
            try:
                search_time = timeit.timeit(test_search, number=1000)
                findall_time = timeit.timeit(test_findall, number=100)
                
                performance_info = {
                    "search_time_ms": round(search_time * 1000, 3),
                    "findall_time_ms": round(findall_time * 10, 3),  # Adjusted for different iterations
                    "test_content_length": len(test_content)
                }
            except Exception as e:
                performance_info = {"error": f"Performance test failed: {str(e)}"}
        
        return {
            "success": True,
            "pattern": pattern,
            "analysis": analysis,
            "recommendations": recommendations,
            "performance_info": performance_info,
            "optimized": len(recommendations) == 0
        }
        
    except Exception as e:
        logger.error(f"Error in optimize_pattern_performance: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }

# ====================================
# Backup & Versioning Tools
# ====================================

@mcp.tool()
async def file_diff_versions(file_path: str) -> Dict[str, Any]:
    """
    List all file versions with pattern history.
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
async def file_diff_restore(
    file_path: str,
    version_number: int,
    create_backup: bool = True
) -> Dict[str, Any]:
    """
    Restore specific file version.
    """
    logger.info(f"file_diff_restore called for {file_path}, version={version_number}")
    
    # Normalize the file path
    file_path = os.path.abspath(os.path.expanduser(file_path))
    
    try:
        # Attempt to restore
        result = restore_file_version(file_path, version_number, create_backup)
        return result
        
    except ValueError as e:
        versions = get_file_versions(file_path)
        past_versions = [v for v in versions if v["version"] != "current"]
        
        return {
            "success": False,
            "file_path": file_path,
            "error": str(e),
            "available_versions": [
                {"version": v["version"], "date": v["date"]} for v in past_versions
            ]
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
async def create_file_backup_tool(
    file_path: str,
    change_tag: str = None
) -> Dict[str, Any]:
    """
    Manual backup creation with tags.
    """
    logger.info(f"create_file_backup_tool called for {file_path}")
    
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
        
        # Create backup
        backup_info = create_file_backup(file_path, change_tag)
        
        return {
            "success": True,
            "file_path": file_path,
            "message": f"Backup created successfully",
            "backup_info": backup_info
        }
        
    except Exception as e:
        logger.error(f"Error in create_file_backup_tool: {e}", exc_info=True)
        return {
            "success": False,
            "file_path": file_path,
            "error": f"Unexpected error: {str(e)}",
            "tip": "Check the file path and permissions"
        }

# ====================================
# Session Management Tools
# ====================================

@mcp.tool()
async def list_change_sessions() -> Dict[str, Any]:
    """
    Discover all tagged change sessions.
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
async def restore_change_session(change_tag: str) -> Dict[str, Any]:
    """
    Batch restore entire change sessions.
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
            backup_filename = f"v{next_version}_{timestamp}.{restore_tag}.backup"
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

@mcp.tool()
async def get_session_details(change_tag: str) -> Dict[str, Any]:
    """
    Get detailed session information and file relationships.
    """
    files = get_backup_by_tag(change_tag)
    
    if not files:
        available_tags = list_change_tags()
        return {
            "success": False,
            "message": f"No files found with change tag '{change_tag}'",
            "available_tags": available_tags
        }
    
    # Analyze the session
    file_details = []
    total_size = 0
    earliest_timestamp = min(f["timestamp"] for f in files)
    latest_timestamp = max(f["timestamp"] for f in files)
    
    for file_info in files:
        # Get current file info if it exists
        current_info = None
        if os.path.exists(file_info["original_path"]):
            current_stats = os.stat(file_info["original_path"])
            current_info = {
                "size": current_stats.st_size,
                "size_human": f"{current_stats.st_size/1024:.1f}KB" if current_stats.st_size < 1048576 else f"{current_stats.st_size/1048576:.1f}MB",
                "modified": datetime.fromtimestamp(current_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            }
        
        file_details.append({
            "original_path": file_info["original_path"],
            "backup_info": file_info,
            "current_info": current_info,
            "exists": os.path.exists(file_info["original_path"])
        })
        
        total_size += file_info["size"]
    
    return {
        "success": True,
        "change_tag": change_tag,
        "file_count": len(files),
        "session_info": {
            "earliest_change": datetime.fromtimestamp(earliest_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "latest_change": datetime.fromtimestamp(latest_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "duration_minutes": round((latest_timestamp - earliest_timestamp) / 60, 2),
            "total_backup_size": total_size,
            "total_backup_size_human": f"{total_size/1024:.1f}KB" if total_size < 1048576 else f"{total_size/1048576:.1f}MB"
        },
        "file_details": file_details
    }

# ====================================
# Server Startup
# ====================================

# Log application startup
logger.info(f"Starting file_diff_writer_v2 MCP tool version {__version__}")
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