# Claude Manager Tool

A PowerShell utility for managing Claude Desktop, with a focus on log viewing and MCP server configuration.

## Features

- View MCP logs from Claude's logs directory (`C:\Users\<Username>\AppData\Roaming\Claude\logs`)
- Kill and restart Claude Desktop processes
- Configure the Evolve MCP server for Claude
- Simple menu-driven interface

## Usage

```powershell
# Run the script
.\claude-manager.ps1
```

## Menu Options

1. **View MCP Logs** - View log files in the Claude logs directory
2. **Kill Claude Desktop** - Terminate all Claude-related processes
3. **Setup Evolve Server** - Configure the Evolve MCP server
4. **Restart Claude** - Restart the Claude application
5. **Exit** - Exit the tool

## Log Viewing

The log viewer:
- Only looks in `C:\Users\<Username>\AppData\Roaming\Claude\logs`
- Lists all log files in this directory
- Allows viewing the last 20 lines of any selected log
- Offers real-time monitoring of logs

## Evolve Server Setup

The Evolve Server setup:
- Creates an `evolve.py` file in the current directory
- Configures Claude to use this server via `claude_desktop_config.json`
- Uses absolute paths to prevent file location errors

## Requirements

- Windows with PowerShell
- Claude Desktop application
- Python (for MCP server functionality)
- MCP server package (`pip install mcp-server`)
