# 🧠 EvolveMCP: Claude Desktop Manager & MCP Bootstrapper

A PowerShell utility for managing Claude Desktop and bootstrapping MCP servers.

## 🌟 Overview

This tool provides convenient management of Claude Desktop processes and simplifies the setup of MCP (Model Context Protocol) servers, with a focus on the Evolve tool implementation.

## ✨ Features

- **🔄 Claude Process Management:** Kill and restart Claude Desktop processes
- **📋 Log Viewer:** Access MCP logs directly from Claude's logs directory
- **🚀 MCP Bootstrapper:** Quickly configure and deploy the Evolve MCP server
- **⚙️ Single Configuration:** Manages Claude's configuration file for MCP server integration

## 🛠️ Usage

```powershell
# Run the script
.\evolve.ps1
```

## 📋 Menu Options

1. **📜 View MCP Logs** - View log files from the Claude logs directory
2. **🛑 Kill Claude Desktop** - Terminate Claude processes
3. **🚀 Setup Evolve Server** - Bootstrap the Evolve MCP server
4. **🔄 Restart Claude** - Restart the Claude application
5. **🚪 Exit** - Exit the tool

## 💾 MCP Server Bootstrapping

The tool simplifies MCP server setup by:
- 📝 Generating the necessary Python server code
- 🔗 Setting up an evolve.py file with absolute path references
- 🔧 Creating the proper claude_desktop_config.json configuration
- 👆 Providing a one-click setup and restart process

## 📋 Requirements

- 🖥️ Windows with PowerShell
- 🤖 Claude Desktop application
- 🐍 Python installation
- 📦 MCP server package (`pip install mcp-server`)
