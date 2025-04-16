# 🧠 EvolveMCP: Claude Desktop Tool Manager

EvolveMCP is a simple PowerShell utility that helps you extend Claude Desktop with custom tools.

See more about MCP [here](https://modelcontextprotocol.io/introduction).

## What is EvolveMCP?

EvolveMCP makes it easy to:
- Manage Claude Desktop processes (restart, view logs)
- Create and install custom tools for Claude
- Set up MCP servers without complex configuration

## Quick Start

### Requirements
- Windows
- PowerShell (comes with Windows)
- [Claude Desktop](https://claude.ai/download) installed
- Python installed (see bottom for how to install)

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
```
evolve calculator
```

```
I'd be happy to help you set up a calculator tool using the evolve system. Let me do that for you.View result from evolve_wizard from evolve-server (local){

# Calculator Tool Created Successfully

I've created a calculator tool file at:
C:\Users\kord\Code\mcptest\calc.py

## The tool has been registered with Claude!

The calculator has been:
1. Created in the same directory as your evolve.py file
2. Added to Claude's configuration automatically

## To use the calculator tool:

1. **Restart Claude**:
   Run this command in PowerShell:
   """
   ./evolve.ps1 -Restart
   """
   
2. **After Claude restarts**:
   You can use the calculator functions:
   - calculate the square root of pi
   - what is the distance to the moon (average) to the power of 3?
   - calculate the volume inside a regular ice cream cone scoop (in liters)

```

2. Restart Claude as instructed

3. Use your new tool (in Claude Desktop):
```
calculate the square root of pi
```

```
The square root of pi is 1.7724538509055159.
```

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

## Troubleshooting or Need Help?

### Installing Python on Windows in 2025: The Best Approach
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
   
If you encounter issues, check the logs with `.\evolve.ps1 -ViewLogs` or open an issue on GitHub.
