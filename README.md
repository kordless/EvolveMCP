<div align="center">

# EvolveMCP: Build. Extend. Evolve.
<strong>Pythonic MCP development, supercharged by AI intelligence and your will to build something new.</strong>

[![PyPI - Version](https://img.shields.io/badge/pipy-_v1.0.0-blue)](https://pypi.org/project/evolvemcp)
[![License](https://img.shields.io/badge/license-_Sovereign_v1.1-purple)](https://github.com/kordless/EvolveMCP/blob/main/LICENSE.md)

<h1>🧠</h1>
</div>

EvolveMCP is a PowerShell utility and MCP server that helps you extend LLMs with custom tools. 

For now, EvolveMCP uses [FastMCP](https://github.com/jlowin/fastmcp) under the hood. You can read more about MCP [here](https://modelcontextprotocol.io/introduction).

## What can you do with EvolveMCP?

EvolveMCP makes it easy to:
- Manage Claude Desktop processes (restart, view logs)
- Create and install custom tools for Claude
- Set up MCP servers without complex configurations (or coding)

## Quick Start

### Requirements
Ensure you have or have installed these dependencies before starting.

- Windows
- PowerShell (comes with Windows)
- [Claude Desktop](https://claude.ai/download) installed
- Python installed (see troubleshooting for how to install)

### Installation
The fastest way to install is to [download Evolve](https://github.com/kordless/EvolveMCP/releases/tag/new) and unzip it in a directory. It can also be installed using 'git' if that is available on your computer.

#### Option 1: Using Git
```powershell
# Clone repository
git clone https://github.com/kordless/EvolveMCP.git
cd EvolveMCP

# Run setup
.\evolve.ps1 -Setup
```

#### Option 2: From Release
1. Download and unzip the latest release
2. Open PowerShell in the extracted folder
3. Run `.\evolve.ps1 -Setup`

### Creating Your First Tool

After setup and Claude restart:

1. Ask Claude to evolve a calculator tool:
![evolve_image]()

2. Restart Claude as instructed

3. Use your new tool (in Claude Desktop):
![calc_image]()

### Common Commands for the Evolve Configuration Tool

```powershell
# Show menu with all options
.\evolve.ps1

# Restart Claude
.\evolve.ps1 -Restart

# View logs
.\evolve.ps1 -ViewLogs

# List all tools
.\evolve.ps1 -ListTools
```

## Support and Troubleshooting

If you encounter issues, check the logs with `.\evolve.ps1 -ViewLogs` or open an issue on GitHub.

### Don't Have Python on Windows?
As of February 2025, Python 3.13.2 is the latest stable release with significant improvements over previous versions, including a new interactive interpreter with multi-line editing and color support, an experimental free-threaded build mode that disables the Global Interpreter Lock, and preliminary JIT functionality for performance improvements.

#### Installation Methods
There are three primary methods to install Python on Windows:

1. **Official Python Installer (Recommended)**: This involves downloading the installer directly from Python.org and is best for developers who need more control during setup. 
2. **Microsoft Store**: The quickest installation option, recommended for beginners looking for an easy-to-set-up interactive experience.
3. **Windows Subsystem for Linux (WSL)**: Allows you to run a Linux environment on Windows.

#### Step-by-Step Guide (Official Installer)
1. Visit the [official Python website](https://www.python.org/downloads/)
2. Download the latest Windows installer (Python 3.13.2)
3. Run the installer (.exe file) and make sure to check "Add Python to PATH" during installation to avoid having to set environment variables manually
4. Complete the installation process
5. Verify the installation by opening Command Prompt or PowerShell and typing:
   ```
   python --version
   ```
   

