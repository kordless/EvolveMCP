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
3. **Claude Desktop**: The desktop application for Claude

## Step 1: Insall Calude Desktop
1. Visit the official Anthropic website to download Claude Desktop
2. Run the installer and follow the on-screen instructions
3. Launch Claude Desktop at least once to create initial configuration files

## Step 2: Download Evolve

### Option A: Download the Release Package (Easiest)

1. Go to [github.com/kordless/EvolveMCP/releases/tag/newer](https://github.com/kordless/EvolveMCP/releases/tag/newer)
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

### Viewing Logs

The EvolveMCP utility provides several ways to view logs, which can be helpful for troubleshooting issues with Claude Desktop and MCP servers.

#### Using the Command Line

You can view logs directly from the command line using the `-ViewLogs` parameter:

```powershell
.\EvolveMCP.ps1 -ViewLogs
```

This will list all available log files in the logs directory (`C:\Users\<username>\AppData\Roaming\Claude\logs`). You can then select a specific log file to view by entering its number.

To filter logs by name, use the `-LogName` parameter:

```powershell
.\EvolveMCP.ps1 -ViewLogs -LogName evolve
```

This will show only log files that contain "evolve" in their filename.

#### Using the Menu Interface

If you prefer a menu-based approach:

1. Run the script without parameters (or with `-Menu`):
   ```powershell
   .\EvolveMCP.ps1
   ```

2. Select option `1. View MCP Logs` from the menu
3. Choose a log file from the displayed list

#### Log Monitoring

When viewing a log file, the tool will initially show the last 20 lines. You'll then be prompted if you want to monitor the log file in real-time. Selecting `y` will continuously display new log entries as they are written, which is particularly useful when debugging active issues.

To stop monitoring, press `Ctrl+C`.

#### Log Location

Logs are stored in the following location:
```
C:\Users\<username>\AppData\Roaming\Claude\logs
```

If this directory doesn't exist, the tool will offer to create it for you.

### Common Issues

#### Claude Desktop Not Starting

If Claude Desktop fails to start after configuring MCP servers:

1. Check the logs for any error messages:
   ```powershell
   .\EvolveMCP.ps1 -ViewLogs
   ```

2. Verify that your configuration file is correct:
   ```
   C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json
   ```

3. Ensure the paths to your MCP server scripts are valid and accessible

#### Evolve Server Issues

If you're experiencing issues with the Evolve server:

1. View the Evolve-specific logs:
   ```powershell
   .\EvolveMCP.ps1 -ViewLogs -LogName evolve
   ```

2. Verify that `evolve.py` exists in the location specified in your configuration
3. Make sure Python is properly installed and accessible from the command line

#### Restarting Claude Desktop

If Claude Desktop becomes unresponsive or you need to apply configuration changes:

```powershell
.\EvolveMCP.ps1 -Restart
```

This will gracefully stop and restart Claude Desktop.

### Checking Tool Configuration

To verify which MCP tools are currently configured:

```powershell
.\EvolveMCP.ps1 -ListTools
```

This will display all configured MCP servers, including:
- Server name
- Command and arguments
- Whether the script exists
- For Evolve tools: version and creation date (if available)