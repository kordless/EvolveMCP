# 🧠 EvolveMCP: Claude Manager & MCP Bootstrapper

A PowerShell utility for managing Claude Desktop and bootstrapping MCP servers.

## 🌟 Overview

This tool provides convenient management of Claude Desktop processes and simplifies the setup of MCP (Model Context Protocol) servers, with a focus on the Evolve tool implementation.

MCP (Model Context Protocol) is a powerful interface for extending AI capabilities, but setting it up—especially on Windows using Python or PowerShell—can be challenging due to limited documentation. This tool bridges that gap by automating the configuration process and providing a streamlined experience for developers.

## 💡 Background & Vision

EvolveMCP was born from the idea of using AI to create and manage its own tools. The core concept is to leverage AI capabilities to:

1. Generate the necessary MCP server code
2. Manage configuration files for seamless integration
3. Create a bootstrapping process that gets everything running quickly

The Evolve function is designed to be more than just a static tool - it's built to iteratively develop and refine itself over time. As you work with Evolve, it learns patterns and capabilities that allow it to:

- Adapt to your specific needs
- Generate new tools based on learned patterns
- Incrementally improve its functionality
- Remember interactions and build upon them

This creates a feedback loop where the AI helps build better tools for working with AI, streamlining the development process and reducing configuration complexity.

## ✨ Features

- **🔄 Claude Process Management:** Kill and restart Claude Desktop processes
- **📋 Log Viewer:** Access MCP logs directly from Claude's logs directory
- **🚀 MCP Bootstrapper:** Quickly configure and deploy the Evolve MCP server
- **⚙️ Single Configuration:** Manages Claude's configuration file for MCP server integration
- **🧠 Evolve Function:** A learning tool that adapts to patterns and creates custom responses

## 🛠️ Usage

```powershell
# Run the script
.\claude-manager.ps1
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

### Why This Matters

Setting up MCP servers on Windows presents several challenges:
- Lack of comprehensive Windows-specific documentation
- Path handling complications between Python and Windows
- Configuration file locations that aren't clearly documented
- Process management complexities on Windows systems

MCP-Commander handles these issues automatically, making the process accessible even to those who aren't familiar with all the technical details of MCP implementation.

## 🧠 Evolve: The Self-Improving Tool

The Evolve function serves as the foundation for AI-assisted tool creation:

- **Pattern Learning:** Recognizes input patterns and creates customized responses
- **Multiple Modes:** Supports basic, advanced, and debug operation modes
- **Memory:** Maintains state between sessions to build on previous interactions
- **Extensibility:** Designed as a framework for creating more specialized tools
- **Iteration:** As you build with it, it adapts and improves its capabilities

## 📋 Requirements

- 🖥️ Windows with PowerShell
- 🤖 Claude Desktop application
- 🐍 Python installation
- 📦 MCP server package (`pip install mcp-server`)
