#!/usr/bin/env python3
"""
Enhanced Diff Patterns Tool - Pattern Introspection and Custom Regex Support

Provides:
1. Pattern introspection - tool reports its own diff format capabilities
2. Custom pattern support - LLM can send dynamic regex patterns
3. Auto-detection - tool identifies which pattern was used
"""

import re
import os
import sys
import json
from typing import Dict, Any, List, Tuple, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("enhanced-diff-patterns")

# Pattern Registry - Extracted from file_diff_writer.py
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
    }
}

def extract_diff_blocks_enhanced(diff_text: str, custom_pattern: str = None) -> Tuple[List[Tuple[str, str, Dict[str, Any]]], str]:
    """
    Extract diff blocks using either built-in patterns or custom pattern
    
    Returns:
        Tuple of (blocks, pattern_used)
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
    
    # Try built-in patterns in order
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
                            blocks.append((search_text, replace_text, {"filename_hint": match[0].strip()}))
                        else:
                            # (search_text, replace_text)
                            search_text, replace_text = match[0], match[1]
                            blocks.append((search_text, replace_text, {"method": pattern_name}))
                return blocks, pattern_name
        except re.error:
            continue
    
    return blocks, "NO_PATTERN_MATCHED"

@mcp.tool()
async def get_diff_formats() -> Dict[str, Any]:
    """
    Get all supported diff formats and custom pattern capabilities.
    
    Returns:
        Dictionary with supported patterns, examples, and custom pattern info
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
                "pattern": "r'\\[\\[FIND\\]\\]\\n(.*?)\\n\\[\\[REPLACE\\]\\]\\n(.*?)\\n\\[\\[END\\]\\]'",
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
    
    Args:
        test_text: Sample diff text to test against
        custom_pattern: Optional custom regex pattern to test
        
    Returns:
        Dictionary with test results and matched blocks
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
    
    Args:
        content: File content to analyze for potential delimiter conflicts
        
    Returns:
        Analysis results and pattern recommendations
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

if __name__ == "__main__":
    mcp.run()
