<div align="center">

# EvolveMCP: Build. Extend. Evolve.
<strong>Pythonic MCP development, supercharged by AI intelligence and your will to build something new.</strong>

[![License](https://img.shields.io/badge/license-_Sovereign_v1.1-purple)](https://github.com/kordless/EvolveMCP/blob/main/LICENSE.md)

<h1>🧠</h1>
</div>

# Complete Beginner's Guide to Installing Evolve

This guide walks you through installing Evolve step by step, even if you're new to programming tools. EvolveMCP is a PowerShell utility and MCP server that helps you extend Claude Desktop with custom tools it writes for you and itself. 

## Prerequisites

Before starting, you'll need:

1. **Windows Computer**: Evolve is designed to work on Windows
2. **Internet Connection**: For downloading necessary files
3. **Python**: The programming language Evolve is built with (installation instructions below)

## Step 1: Install Python

If you don't already have Python installed:

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Click the yellow "Download Python" button (choose the latest version)
3. Run the installer after it downloads
4. **IMPORTANT**: Check the box that says "Add Python to PATH" before clicking Install
5. Click "Install Now"

## Step 2: Download Evolve

### Option A: Download the Release Package (Easiest)

1. Go to [github.com/kordless/EvolveMCP/releases/tag/new](https://github.com/kordless/EvolveMCP/releases/tag/new)
2. Under "Assets", click on the zip file (something like `EvolveMCP-[version].zip`)
3. Save the file to a location you can easily find (like your Downloads folder)
4. Right-click the downloaded zip file and select "Extract All..."
5. Choose where to extract the files (like your Documents folder) and click "Extract"

### Option B: Using Git (For Advanced Users)

If you're familiar with Git:

1. Install Git from [git-scm.com](https://git-scm.com/downloads) if you don't have it
2. Open PowerShell (see below for instructions)
3. Navigate to where you want to install Evolve
4. Run these commands:
   ```powershell
   git clone https://github.com/kordless/EvolveMCP.git
   cd EvolveMCP
   ```

## Step 3: Open PowerShell

1. Navigate to the folder where you extracted Evolve
2. Hold Shift and right-click in an empty area of the folder
3. Select "Open PowerShell window here" from the menu
   - If you don't see this option, see our [PowerShell Guide](powershell-guide.md) for alternatives

## Step 4: Run the Setup Script

1. In the PowerShell window, type the following command and press Enter:
   ```powershell
   .\evolve.ps1 -Setup
   ```

2. If you see an error message about execution policy, run this command and try again:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

3. Follow any on-screen instructions to complete the setup

## Step 5: Create Your First Tool

1. After setup completes, make sure you're still in PowerShell in the Evolve folder
2. Type this command to create your first tool:
   ```powershell
   .\evolve.ps1 -StartClaude
   ```
   This will start Claude with the Evolve tools available

3. In Claude, ask it to create a calculator tool:
   ```
   evolve_wizard("calc")
   ```
   
   You can also use conversational language like:
   ```
   Could you please install the calculator tool for me?
   ```

4. Claude will inform you that the calculator tool has been created and registered
5. Restart Claude to apply the changes:
   ```powershell
   .\evolve.ps1 -Restart
   ```

6. After Claude restarts, you can test the calculator using either direct commands or natural language:
   ```
   calculate("2 + 3 * 4")
   ```
   
   Or simply ask:
   ```
   What's 2 plus 3 times 4?
   ```

## Using Conversational Language with Evolve

One of the great features of Evolve is that you don't need to memorize exact command syntax. You can talk to Claude naturally, and it will understand what you're trying to do:

- Instead of `calculate("56 * 89")`, you can ask "What's 56 multiplied by 89?"
- Instead of `evolve_wizard("status")`, you can ask "Can you show me the status of the Evolve system?"
- Instead of formal parameter syntax, you can describe what you want in plain English

Claude will interpret your natural language requests and translate them into the appropriate tool calls as long as you provide enough information about what you want to accomplish.

## Troubleshooting

If you encounter issues during installation:

- **"Python is not recognized"**: Make sure you checked "Add Python to PATH" during Python installation. You may need to restart your computer.

- **PowerShell errors**: See our [PowerShell Guide](powershell-guide.md) for help with common PowerShell issues.

- **Permission errors**: Try running PowerShell as Administrator (right-click PowerShell in the Start menu and select "Run as administrator").

- **Package installation errors**: Make sure you have a good internet connection, and try running:
  ```powershell
  python -m pip install --upgrade pip
  ```

## Need More Help?

If you're having trouble with Python environments or want to use advanced tools like uv or Conda, see our [Advanced Environment Setup Guide](advanced-environment-setup.md).
