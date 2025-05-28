# File Diff Editor - Advanced Pattern-Based File Editing Tool

## Overview

The **File Diff Editor v2.1.1** is a revolutionary MCP (Model Context Protocol) tool that provides advanced file editing capabilities with powerful regex support, fuzzy matching, and enterprise-grade versioning. This tool enables Claude to perform sophisticated file modifications with safety, precision, and rollback capabilities.

## Key Features

- ✅ **Fixed Regex Backreferences** - `\1`, `\2`, etc. work correctly
- 🔍 **Advanced Pattern Matching** - Custom regex patterns and conflict detection  
- 🎯 **Fuzzy Text Search** - Multiple matching algorithms
- 📝 **Diff Block Processing** - Multiple format support (ToolKami, Git, custom)
- 💾 **Session-Based Versioning** - Automatic backups with restore capability
- ⚡ **Bulk Operations** - Process multiple files simultaneously
- 🛡️ **Safe Operations** - Preview changes before applying
- 📊 **Performance Optimization** - Pattern analysis and recommendations

## Installation

### Quick Install with Gnosis Evolve

If you have **Gnosis Evolve** installed and running in Claude Desktop, you can install this tool instantly:

```
Install the file diff editor
```

Just say that to Claude and the tool will be automatically added to your system! You will need to restart Claude after to load the new tool server.

### Manual Installation (Without Evolve)

If you want to run this tool without Evolve, then follow these steps:

### Step 1: Install MCP Dependencies

Before setting up the File Diff Editor, you need to install the required MCP packages:

```bash
pip install mcp fastmcp
```

Or if you're using Python 3 specifically:
```bash
pip3 install mcp fastmcp
```

### Step 2: Download the Tool

Copy the `file_diff_editor.py` file to your local MCP tools directory:

```
# Recommended location:
Windows: C:\mcp-tools\file_diff_editor.py
Mac/Linux: ~/mcp-tools/file_diff_editor.py
```

### Step 3: Locate Claude's Configuration File

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```
Full path example: `C:\Users\YourName\AppData\Roaming\Claude\claude_desktop_config.json`

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 4: Edit the Configuration File

Open the `claude_desktop_config.json` file in a text editor and add the File Diff Editor tool to the `mcpServers` section:

```json
{
  "mcpServers": {
    "file-diff-editor": {
      "command": "python",
      "args": ["C:\\mcp-tools\\file_diff_editor.py"],
      "env": {}
    }
  }
}
```

**For Mac/Linux, use the appropriate path:**
```json
{
  "mcpServers": {
    "file-diff-editor": {
      "command": "python3",
      "args": ["/Users/YourName/mcp-tools/file_diff_editor.py"],
      "env": {}
    }
  }
}
```

### Step 5: Restart Claude Desktop

Close and reopen Claude Desktop application for the changes to take effect.

## Usage Examples

### Basic File Editing

```
Please use file_diff_write to update my Python file:
- Change all function names from snake_case to camelCase
- File: /path/to/my_script.py
```

### Regex Pattern Replacement

```
Use replace_with_pattern to update version numbers:
- Pattern: VERSION_(\w+) = \d+
- Replace with: VERSION_\1 = 999
- File: config.py
```

### Fuzzy Search and Replace

```
Find and replace similar text using search_in_file_fuzzy:
- Search for functions that calculate something
- Replace with enhanced versions
- Use 80% similarity threshold
```

### Bulk Operations

```
Use bulk_pattern_replace to update multiple files:
- Update copyright headers across all Python files
- Replace old company name with new one
- Create session backup for rollback
```

## Advanced Features

### Custom Diff Patterns

When standard diff formats conflict with your code content, use custom patterns:

```
Create a custom pattern that won't conflict with my code:
- My code contains many ======= sequences
- Suggest safe delimiters for diff operations
```

### Session Management

```
Show me all change sessions and restore from a previous backup:
- List all tagged change sessions
- Restore files from session "refactor_database"
```

### Pattern Validation

```
Validate my custom regex pattern before using:
- Pattern: \[FIND\]\n(.*?)\n\[REPLACE\]\n(.*?)\n\[END\]
- Test against sample diff text
```

## Available Tools

### Core Operations
- `file_diff_write()` - Apply diff blocks to files
- `text_diff_edit()` - Edit text with detailed diagnostics
- `simple_text_diff()` - Simple text editing

### Search & Replace
- `search_in_file_regex()` - Regex search with capture groups
- `search_in_file_fuzzy()` - Fuzzy text matching
- `replace_with_pattern()` - Pattern-based replacement
- `bulk_pattern_replace()` - Multi-file operations

### Pattern Management
- `validate_custom_pattern()` - Test regex patterns
- `analyze_content_for_patterns()` - Detect conflicts
- `suggest_safe_pattern()` - Generate safe delimiters
- `test_diff_pattern()` - Test patterns against sample text

### Versioning & Backup
- `file_diff_versions()` - List file versions
- `file_diff_restore()` - Restore specific versions
- `create_file_backup_tool()` - Manual backup creation
- `list_change_sessions()` - Show all sessions
- `restore_change_session()` - Batch restore operations

### Utilities
- `get_diff_formats()` - Show supported diff formats
- `preview_diff_changes()` - Preview before applying
- `optimize_pattern_performance()` - Pattern analysis

## Troubleshooting

### Common Issues

**1. Tool not appearing in Claude:**
- Verify the file path in `claude_desktop_config.json`
- Ensure Python is installed and accessible
- **For manual installation: Ensure MCP packages are installed** (`pip install mcp fastmcp`)
- Restart Claude Desktop completely

**2. Regex not working:**
- Use double backslashes for backreferences: `\\1`, `\\2`
- Validate patterns with `validate_custom_pattern()`
- Check pattern syntax with `test_diff_pattern()`

**3. File permission errors:**
- Ensure Claude has read/write access to target files
- Run with appropriate permissions on Linux/Mac

**4. Diff conflicts:**
- Use `analyze_content_for_patterns()` to detect conflicts
- Generate safe patterns with `suggest_safe_pattern()`
- Use custom delimiters like `[CHANGE]`, `[TO]`, `[DONE]`

### Configuration Examples

**Full configuration with multiple tools:**
```json
{
  "mcpServers": {
    "file-diff-editor": {
      "command": "python",
      "args": ["C:\\mcp-tools\\file_diff_editor.py"],
      "env": {}
    },
    "other-tool": {
      "command": "python",
      "args": ["C:\\mcp-tools\\other_tool.py"],
      "env": {}
    }
  }
}
```

**Using virtual environment:**
```json
{
  "mcpServers": {
    "file-diff-editor": {
      "command": "C:\\venv\\Scripts\\python.exe",
      "args": ["C:\\mcp-tools\\file_diff_editor.py"],
      "env": {}
    }
  }
}
```

## Safety Features

- **Automatic Backups** - Every change creates a versioned backup
- **Preview Mode** - See changes before applying them
- **Pattern Validation** - Test patterns before use
- **Session Tracking** - Group related changes for batch restoration
- **Conflict Detection** - Identify problematic content patterns
- **Safe Delimiters** - Auto-generate conflict-free patterns

## Performance Tips

- Use `optimize_pattern_performance()` for complex regex patterns
- Preview changes with large files before applying
- Use specific patterns instead of greedy `.*` matches
- Leverage session tags for organized change management

## Requirements

- Python 3.7+
- Claude Desktop Application
- **MCP framework** (`pip install mcp fastmcp` - required for manual installation)
- Write permissions to target files
- No additional Python packages required (uses standard library)

## Support

This tool includes comprehensive error handling and detailed diagnostics. If you encounter issues:

1. Use `preview_diff_changes()` to test operations safely
2. Check pattern validity with `validate_custom_pattern()`
3. Review file versions with `file_diff_versions()`
4. Restore from backups using `file_diff_restore()`

The tool provides detailed error messages and suggestions for resolution.
