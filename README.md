## 🛠️ MCP Setup Basics

### What is MCP?

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open "standard" or "protocol" that enables AI models to communicate with external tools and data sources through a standardized interface. "MCP is like a USB-C port for AI applications" - it provides a universal way for AI models to connect with external data sources, tools, and environments.

### Traditional Setup (The Complex Way)

According to the official documentation, setting up MCP typically involves:

1. Installing Claude Desktop (or other client)
2. Using the uv package manager (which requires global installation for Claude Desktop)
3. Setting up Node.js (since many MCP servers are Node-based)
4. Creating complex configuration files with absolute paths (for Claude Desktop)
5. Manually editing the Claude desktop configuration file
6. Restarting Claude Desktop to load the tools (servers)

### The EvolveMCP Way (Simplified)

Our approach cuts through this complexity:

1. **One-Click Setup**: Run `evolve.ps1` and select option 3
2. **Python-Based**: Uses Python instead of Node.js (more developers already have Python)
3. **No Global Dependencies**: Doesn't require uv or other global package managers
4. **Automatic Configuration**: Handles all path issues and configuration automatically
5. **Windows-Optimized**: Specifically designed to work with Windows path structures

## 🔧 Understanding MCP Setup

### The Reality: It's Simpler Than It Looks

MCP is fundamentally a protocol/standard/framework - it's just a way for AI models to communicate with external tools. The apparent complexity comes from:

1. Documentation that covers many possible implementation paths
2. Different language environments (JavaScript, Python, etc.)
3. Configuration quirks across operating systems and clients

### Our Approach: Keep It Simple

The `evolve.ps1` tool cuts through this complexity by:
- Using Python (which many developers already have)
- Creating a simple server without Node.js dependencies
- Auto-generating all necessary configuration files
- Handling the Windows-specific path issues automatically
apping MCP servers.

## 🌟 Overview

This tool (`evolve.ps1`) provides convenient management of Claude Desktop processes and simplifies the setup of MCP (Model Context Protocol) servers, with a focus on the Evolve tool implementation.

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
.\evolve.ps1
```

## 📋 Menu Options

Here's what you'll see when running `evolve.ps1`:

```
🧰 ===== CLAUDE MANAGER MENU ===== 🧰
1. 📜 View MCP Logs
2. 🛑 Kill Claude Desktop
3. 🚀 Setup Evolve Server
4. 🔄 Restart Claude
5. 🚪 Exit
```

Each option provides the following functionality:

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

The current evolve.py file is intentionally simple - it's the starting point in an evolutionary journey:

- **Initial Version:** The current implementation provides basic pattern matching and response capabilities
- **Future Development:** We'll be building and testing different versions to discover which approaches can most effectively bootstrap into more advanced capabilities
- **Evolutionary Approach:** Each iteration will build upon lessons learned from previous versions
- **Experimental Platform:** This serves as a testbed for exploring how AI can assist in evolving its own tools

The vision is to create a progression of increasingly sophisticated tools, with each version helping to create the next generation.

## 📋 Requirements

- 🖥️ Windows with PowerShell
- 🤖 Claude Desktop application
- 🐍 Python installation
- 📦 MCP server package (`pip install mcp-server`)
