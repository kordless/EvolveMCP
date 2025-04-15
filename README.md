# 🧠 EvolveMCP: Claude Manager & MCP Bootstrapper

<p align="center">
  <img src="https://raw.githubusercontent.com/kordless/EvolveMCP/main/assets/evolve-logo.png" alt="EvolveMCP Logo" width="400"/>
</p>

A PowerShell utility for managing Claude Desktop and bootstrapping MCP servers.

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

## 🛠️ Quick Start

### Bootstrap the system

1. Create a new folder where you want to set up EvolveMCP
2. Create a file called `evolve.py` with the following content:

```python
import sys
import subprocess
import importlib.util

# Check if a package is installed and install it if not
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            try:
                print(f"Installing required package: {package_name}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print(f"Successfully installed {package_name}")
            except Exception as e:
                print(f"Error installing {package_name}: {e}")
                sys.exit(1)
    except Exception as e:
        print(f"Error checking package: {e}")
        sys.exit(1)

# Ensure required packages are installed
ensure_package("mcp-server")

from mcp.server.fastmcp import FastMCP
import asyncio
import json
import time
import random
import os
from typing import Optional, Dict, List, Any, Union
import logging
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("evolve-mcp")

# Initialize FastMCP server
mcp = FastMCP("evolve-server")

# Store the evolve tool's state
EVOLVE_STATE = {
    "version": 1.1,
    "capabilities": ["greeting", "tool_creation"],
    "learned_patterns": {},
    "interactions": 0,
    "last_updated": time.time(),
    "memory": [],
    "created_tools": []
}

# Path to store state
STATE_FILE = "evolve_state.json"

# Load state if exists
def load_state():
    global EVOLVE_STATE
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, 'r') as f:
                loaded_state = json.load(f)
                EVOLVE_STATE.update(loaded_state)
                logger.info(f"Loaded state: version {EVOLVE_STATE['version']}, {len(EVOLVE_STATE['capabilities'])} capabilities")
    except Exception as e:
        logger.error(f"Error loading state: {e}")

# Save state
def save_state():
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(EVOLVE_STATE, f, indent=2)
            logger.info(f"State saved: version {EVOLVE_STATE['version']}, {len(EVOLVE_STATE['capabilities'])} capabilities")
    except Exception as e:
        logger.error(f"Error saving state: {e}")

# Get the absolute path to Claude's config file
def get_claude_config_path():
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ.get("APPDATA", f"C:\\Users\\{username}\\AppData\\Roaming"), 
                           "Claude", "claude_desktop_config.json")
    else:  # macOS/Linux
        return os.path.join(os.environ.get("HOME", f"/Users/{username}"), 
                           "Library", "Application Support", "Claude", "claude_desktop_config.json")

# Read Claude's configuration
def read_claude_config():
    config_path = get_claude_config_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error reading Claude config: {e}")
        return {}

# Update Claude's configuration
def update_claude_config(config):
    config_path = get_claude_config_path()
    try:
        directory = os.path.dirname(config_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Updated Claude config at {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating Claude config: {e}")
        return False

# Tool creation template
TOOL_TEMPLATE = '''# ===============================================================
# MCP SERVER: {tool_name}
# Created: {timestamp}
# Version: 1.0
# Type: MCP Server Tool
# ===============================================================
import sys
import os
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, List, Any, Union
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("{tool_name}-mcp")

# Initialize FastMCP server
mcp = FastMCP("{tool_name}-server")

{tool_code}

# Print server information
logger.info(f"Starting {tool_name} MCP server...")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
'''

@mcp.tool()
async def evolve(
    prompt: str = "Hello world",
    mode: str = "auto",
    learn: Optional[bool] = False,
    pattern: Optional[str] = None,
    response: Optional[str] = None
) -> str:
    """An evolving tool that learns and adapts over time.
    
    Args:
        prompt: The input from the user
        mode: Operation mode (auto, basic, advanced, debug)
        learn: Whether to explicitly teach the tool a new pattern
        pattern: When in learning mode, the pattern to recognize
        response: When in learning mode, how to respond to the pattern
    """
    global EVOLVE_STATE
    
    # Update interaction count
    EVOLVE_STATE["interactions"] += 1
    EVOLVE_STATE["last_updated"] = time.time()
    
    # Add to memory (limit to last 10 interactions)
    EVOLVE_STATE["memory"].append({"prompt": prompt, "timestamp": time.time()})
    if len(EVOLVE_STATE["memory"]) > 10:
        EVOLVE_STATE["memory"] = EVOLVE_STATE["memory"][-10:]
    
    # Learning mode
    if learn and pattern and response:
        EVOLVE_STATE["learned_patterns"][pattern] = response
        EVOLVE_STATE["capabilities"].append(f"custom_pattern_{len(EVOLVE_STATE['learned_patterns'])}")
        save_state()
        return f"I've learned to respond to '{pattern}' with '{response}'"
    
    # Check for matches in learned patterns
    for pattern, response in EVOLVE_STATE["learned_patterns"].items():
        if pattern.lower() in prompt.lower():
            return response
    
    # Mode handling
    if mode == "basic":
        return f"Evolve tool received: {prompt}"
    
    elif mode == "debug":
        state_summary = {
            "version": EVOLVE_STATE["version"],
            "capabilities": EVOLVE_STATE["capabilities"],
            "patterns": len(EVOLVE_STATE["learned_patterns"]),
            "interactions": EVOLVE_STATE["interactions"],
            "memory_size": len(EVOLVE_STATE["memory"]),
            "created_tools": EVOLVE_STATE["created_tools"]
        }
        return f"DEBUG MODE: {json.dumps(state_summary, indent=2)}\nPrompt received: {prompt}"
    
    elif mode == "advanced":
        # In advanced mode, try to offer more sophisticated responses
        if "help" in prompt.lower():
            return """
            The evolve tool can:
            1. Learn new patterns and responses
            2. Remember recent interactions
            3. Respond based on pattern matching
            4. Create new MCP tools (use evolve_create)
            5. Operate in different modes (basic, advanced, debug)
            
            To teach me something new, set learn=True and provide pattern and response parameters.
            """
        
        if "tools" in prompt.lower() or "created" in prompt.lower():
            if not EVOLVE_STATE["created_tools"]:
                return "I haven't created any tools yet. You can use evolve_create to make new tools."
            
            tools_list = "\n".join([f"- {tool}" for tool in EVOLVE_STATE["created_tools"]])
            return f"I've created the following tools:\n{tools_list}"
            
        if "weather" in prompt.lower():
            return "I notice you asked about weather, but I don't have real-time data access. You might want to check a weather service."
        
        if "time" in prompt.lower():
            return f"Current server time is {time.strftime('%H:%M:%S')}"
        
        if "version" in prompt.lower():
            return f"Evolve tool v{EVOLVE_STATE['version']} with {len(EVOLVE_STATE['capabilities'])} capabilities"
    
    # Default auto mode - try to be smart about the response
    if "hello" in prompt.lower() or "hi" in prompt.lower():
        return f"Hello! I'm the evolve tool. How can I assist you today?"
    
    if "thank" in prompt.lower():
        return "You're welcome! Is there anything else you'd like to know about the evolve tool?"
    
    if "what can you do" in prompt.lower() or "help" in prompt.lower():
        return "I can respond to various prompts, learn new patterns, and create new MCP tools. Try asking for 'help' in advanced mode for more details."
    
    # Generic response if nothing matched
    return f"Evolve tool processed: '{prompt}'. Try asking for 'help' if you want to know more about my capabilities."

@mcp.tool()
async def evolve_status() -> Dict[str, Any]:
    """Get the current status and capabilities of the evolve tool."""
    return {
        "version": EVOLVE_STATE["version"],
        "capabilities": EVOLVE_STATE["capabilities"],
        "interaction_count": EVOLVE_STATE["interactions"],
        "patterns_learned": len(EVOLVE_STATE["learned_patterns"]),
        "created_tools": EVOLVE_STATE["created_tools"],
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(EVOLVE_STATE["last_updated"]))
    }

@mcp.tool()
async def evolve_create(
    tool_name: str,
    tool_code: str,
    restart: bool = True
) -> str:
    """Create a new MCP tool and register it with Claude.
    
    Args:
        tool_name: Name of the new tool (will be used for the filename, e.g., 'calc' becomes mcp_tool.calc.py)
        tool_code: The Python code for the tool (just the tool functions)
        restart: Whether to restart Claude after creating the tool
    """
    global EVOLVE_STATE
    
    # Sanitize the tool name (alphanumeric only)
    safe_name = ''.join(c for c in tool_name if c.isalnum() or c == '_').lower()
    if not safe_name:
        return "Error: Tool name must contain alphanumeric characters"
    
    # Create standardized file name with clear demarcation
    file_name = f"mcp_tool.{safe_name}.py"
    
    # Create the file path
    tool_file_path = os.path.join(os.getcwd(), file_name)
    
    # Check if file already exists
    if os.path.exists(tool_file_path) and safe_name not in EVOLVE_STATE["created_tools"]:
        return f"Error: File {tool_file_path} already exists but is not managed by evolve"
    
    # Add timestamp to the template
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format the tool code using the template with metadata
    formatted_code = TOOL_TEMPLATE.format(
        tool_name=safe_name,
        timestamp=timestamp,
        tool_code=tool_code
    )
    
    # Write the tool code to a file
    try:
        with open(tool_file_path, 'w') as f:
            f.write(formatted_code)
        logger.info(f"Created tool file: {tool_file_path}")
    except Exception as e:
        return f"Error creating tool file: {e}"
    
    # Update Claude's configuration
    config = read_claude_config()
    
    # Initialize mcpServers if it doesn't exist
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add the new tool to the configuration
    config["mcpServers"][f"{safe_name}-server"] = {
        "command": "python",
        "args": [tool_file_path]
    }
    
    # Save the configuration
    if not update_claude_config(config):
        return f"Error: Tool file was created at {tool_file_path} but couldn't update Claude's configuration"
    
    # Add the tool to our created tools list if it's not already there
    if safe_name not in EVOLVE_STATE["created_tools"]:
        EVOLVE_STATE["created_tools"].append(safe_name)
        save_state()
    
    # We don't actually restart Claude here since this runs inside Claude
    # Instead, we return instructions to restart
    if restart:
        return f"Successfully created tool '{safe_name}'. Please restart Claude to use the new tool."
    
    return f"Successfully created tool '{safe_name}'. Please restart Claude to use the new tool."

@mcp.tool()
async def evolve_reset(confirm: bool = False) -> str:
    """Reset the evolve tool to its initial state.
    
    Args:
        confirm: Set to True to confirm the reset
    """
    global EVOLVE_STATE
    
    if not confirm:
        return "Please set confirm=True to reset the evolve tool."
    
    # Keep track of created tools
    created_tools = EVOLVE_STATE["created_tools"]
    
    EVOLVE_STATE = {
        "version": EVOLVE_STATE["version"] + 0.1,  # Increment version
        "capabilities": ["greeting", "tool_creation"],
        "learned_patterns": {},
        "interactions": 0,
        "last_updated": time.time(),
        "memory": [],
        "created_tools": created_tools  # Preserve created tools info
    }
    
    save_state()
    return "Evolve tool has been reset to initial state with version upgrade."

# Load state when server starts
load_state()

# Print server information
logger.info(f"Starting Evolve MCP server v{EVOLVE_STATE['version']}...")
logger.info(f"Capabilities: {', '.join(EVOLVE_STATE['capabilities'])}")
logger.info(f"Created tools: {', '.join(EVOLVE_STATE['created_tools'])}")
logger.info("Use the 'evolve' tool to interact with the server.")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
```

3. Create a file called `evolve.ps1` with the following content:

```powershell
# EvolveMCP: Claude Manager & MCP Bootstrapper
# A PowerShell utility for managing Claude Desktop and bootstrapping MCP servers

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [switch]$ViewLogs,
    
    [Parameter(Mandatory=$false)]
    [switch]$Kill,
    
    [Parameter(Mandatory=$false)]
    [switch]$Setup,
    
    [Parameter(Mandatory=$false)]
    [switch]$Restart,
    
    [Parameter(Mandatory=$false)]
    [switch]$Menu,
    
    [Parameter(Mandatory=$false)]
    [string]$LogName,
    
    [Parameter(Mandatory=$false)]
    [switch]$ListTools,
    
    [Parameter(Mandatory=$false)]
    [string]$CreateTool,
    
    [Parameter(Mandatory=$false)]
    [string]$ToolCode
)

# Set username explicitly
$username = $env:USERNAME

# Define the specific logs directory path
$logsPath = "C:\Users\$username\AppData\Roaming\Claude\logs"
$configPath = "C:\Users\$username\AppData\Roaming\Claude\claude_desktop_config.json"

# Ensure logs directory exists
function Ensure-LogsDirectory {
    if (-not (Test-Path $logsPath)) {
        try {
            New-Item -ItemType Directory -Path $logsPath -Force | Out-Null
            Write-Host "✅ Created logs directory at: $logsPath" -ForegroundColor Green
        }
        catch {
            Write-Host "❌ Failed to create logs directory: $_" -ForegroundColor Red
        }
    }
}

# Simplified Log Viewer Function
function View-MCP-Logs {
    param(
        [string]$FilterName
    )
    
    # Check if logs directory exists
    if (Test-Path $logsPath) {
        Write-Host "📁 Found logs directory at: $logsPath" -ForegroundColor Green
        
        # Get log files in this exact directory
        $logFilter = if ($FilterName) { "*$FilterName*.log" } else { "*.log" }
        $logFiles = Get-ChildItem -Path $logsPath -Filter $logFilter -ErrorAction SilentlyContinue
        
        if ($logFiles.Count -gt 0) {
            Write-Host "🔍 Found $($logFiles.Count) log files:" -ForegroundColor Green
            
            # Display files with number options for selection
            $fileOptions = @{}
            
            for ($i = 1; $i -le $logFiles.Count; $i++) {
                $file = $logFiles[$i-1]
                Write-Host "  $i. 📄 $($file.Name)" -ForegroundColor Cyan
                $fileOptions[$i] = $file
            }
            
            # If only one file and we're filtering, automatically select it
            if ($logFiles.Count -eq 1 -and $FilterName) {
                $selectedLog = $logFiles[0]
                Write-Host "`n📖 Reading log file: $($selectedLog.Name)" -ForegroundColor Yellow
                Write-Host "⬇️ Last 20 lines:" -ForegroundColor Yellow
                Get-Content -Path $selectedLog.FullName -Tail 20
                
                # Option to monitor the log file
                $monitorOption = Read-Host "`n👀 Would you like to monitor this log file in real-time? (y/n)"
                if ($monitorOption -eq "y") {
                    Write-Host "📊 Monitoring log file. Press Ctrl+C to stop." -ForegroundColor Magenta
                    Get-Content -Path $selectedLog.FullName -Tail 20 -Wait
                }
                return
            }
            
            # Let user select a log file
            $selectedOption = Read-Host "`n🔢 Select a log file to view (1-$($logFiles.Count))"
            
            if ($fileOptions.ContainsKey([int]$selectedOption)) {
                $selectedLog = $fileOptions[[int]$selectedOption]
                Write-Host "`n📖 Reading selected log file: $($selectedLog.Name)" -ForegroundColor Yellow
                Write-Host "⬇️ Last 20 lines:" -ForegroundColor Yellow
                Get-Content -Path $selectedLog.FullName -Tail 20
                
                # Option to monitor the log file
                $monitorOption = Read-Host "`n👀 Would you like to monitor this log file in real-time? (y/n)"
                if ($monitorOption -eq "y") {
                    Write-Host "📊 Monitoring log file. Press Ctrl+C to stop." -ForegroundColor Magenta
                    Get-Content -Path $selectedLog.FullName -Tail 20 -Wait
                }
            } else {
                Write-Host "❌ Invalid selection." -ForegroundColor Red
            }
        } else {
            Write-Host "❌ No log files found in $logsPath matching '$logFilter'" -ForegroundColor Red
            
            # Inform user if directory exists but is empty
            Write-Host "The directory exists but contains no matching log files." -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Logs directory not found at: $logsPath" -ForegroundColor Red
        
        # Option to create the logs directory
        $createDir = Read-Host "`n📂 Would you like to create the logs directory? (y/n)"
        if ($createDir -eq "y") {
            Ensure-LogsDirectory
        }
    }
}

# Function to find and manage Claude processes
function Manage-ClaudeProcess {
    param (
        [switch]$Kill,
        [switch]$Restart,
        [int]$WaitTime = 5
    )
    
    Write-Host "🔍 Searching for Claude processes..." -ForegroundColor Yellow
    $claudeProcesses = Get-Process -Name "*claude*" -ErrorAction SilentlyContinue
    
    if ($claudeProcesses) {
        Write-Host "🔍 Found Claude processes:" -ForegroundColor Green
        foreach ($process in $claudeProcesses) {
            Write-Host "  - $($process.Name) (PID: $($process.Id))" -ForegroundColor Cyan
        }
        
        if ($Kill -or $Restart) {
            Write-Host "⚠️ Stopping Claude processes..." -ForegroundColor Yellow
            foreach ($process in $claudeProcesses) {
                try {
                    Stop-Process -Id $process.Id -Force -ErrorAction Stop
                    Write-Host "  - 🛑 Stopped $($process.Name) (PID: $($process.Id))" -ForegroundColor Red
                }
                catch {
                    Write-Host "  - ❌ Failed to stop $($process.Name) (PID: $($process.Id)): $_" -ForegroundColor Red
                }
            }
            
            # Verify all processes are actually stopped
            Write-Host "⏳ Waiting for processes to fully terminate... ($WaitTime seconds)" -ForegroundColor Yellow
            Start-Sleep -Seconds 2
            
            $remainingAttempts = 3
            $allProcessesStopped = $false
            
            while (-not $allProcessesStopped -and $remainingAttempts -gt 0) {
                $runningClaudeProcesses = Get-Process -Name "*claude*" -ErrorAction SilentlyContinue
                
                if ($runningClaudeProcesses) {
                    Write-Host "⚠️ Some Claude processes are still running. Attempting to stop again..." -ForegroundColor Yellow
                    foreach ($process in $runningClaudeProcesses) {
                        try {
                            Stop-Process -Id $process.Id -Force -ErrorAction Stop
                            Write-Host "  - 🛑 Stopped $($process.Name) (PID: $($process.Id))" -ForegroundColor Red
                        }
                        catch {
                            Write-Host "  - ❌ Failed to stop $($process.Name) (PID: $($process.Id)): $_" -ForegroundColor Red
                        }
                    }
                    
                    Start-Sleep -Seconds $WaitTime
                    $remainingAttempts--
                }
                else {
                    $allProcessesStopped = $true
                    Write-Host "✅ All Claude processes have been terminated." -ForegroundColor Green
                }
            }
            
            # Final check for any stubborn processes
            $stubbornProcesses = Get-Process -Name "*claude*" -ErrorAction SilentlyContinue
            if ($stubbornProcesses) {
                Write-Host "⚠️ Warning: Some Claude processes could not be terminated. Restart may not work properly." -ForegroundColor Yellow
                foreach ($process in $stubbornProcesses) {
                    Write-Host "  - ⚠️ Still running: $($process.Name) (PID: $($process.Id))" -ForegroundColor Yellow
                }
            }
            
            if ($Restart) {
                # Try to find Claude.exe in common locations
                Write-Host "🔍 Searching for Claude executable..." -ForegroundColor Yellow
                
                $claudeExePaths = @(
                    "C:\Users\$username\AppData\Local\AnthropicClaude\claude.exe",
                    "C:\Users\$username\AppData\Local\AnthropicClaude\Claude.exe",
                    "C:\Users\$username\AppData\Local\Programs\Claude\claude.exe",
                    "C:\Users\$username\AppData\Local\Programs\Claude\Claude.exe",
                    "C:\Program Files\Claude\claude.exe",
                    "C:\Program Files\Claude\Claude.exe"
                )
                
                # Check for versioned dirs
                $versionedPaths = @(
                    "C:\Users\$username\AppData\Local\Claude\app-*"
                )
                
                foreach ($versionedPath in $versionedPaths) {
                    $versionedDirs = Get-ChildItem -Path $versionedPath -Directory -ErrorAction SilentlyContinue
                    if ($versionedDirs) {
                        foreach ($dir in $versionedDirs) {
                            $possibleExes = @(
                                (Join-Path -Path $dir.FullName -ChildPath "claude.exe"),
                                (Join-Path -Path $dir.FullName -ChildPath "Claude.exe")
                            )
                            
                            foreach ($possibleExe in $possibleExes) {
                                if (Test-Path $possibleExe) {
                                    $claudeExePaths += $possibleExe
                                }
                            }
                        }
                    }
                }
                
                $claudeExe = $null
                foreach ($path in $claudeExePaths) {
                    if (Test-Path $path) {
                        $claudeExe = $path
                        Write-Host "✅ Found Claude executable: $claudeExe" -ForegroundColor Green
                        break
                    }
                }
                
                if ($claudeExe) {
                    Write-Host "🚀 Restarting Claude from: $claudeExe" -ForegroundColor Green
                    try {
                        Start-Process -FilePath $claudeExe -ErrorAction Stop
                        
                        # Verify Claude started successfully
                        Start-Sleep -Seconds 5
                        $newClaudeProcesses = Get-Process -Name "*claude*" -ErrorAction SilentlyContinue
                        
                        if ($newClaudeProcesses) {
                            Write-Host "✅ Claude has been successfully restarted." -ForegroundColor Green
                            foreach ($process in $newClaudeProcesses) {
                                Write-Host "  - 🚀 Started $($process.Name) (PID: $($process.Id))" -ForegroundColor Green
                            }
                            return $true
                        } else {
                            Write-Host "❌ Failed to detect Claude processes after restart." -ForegroundColor Red
                            return $false
                        }
                    }
                    catch {
                        Write-Host "❌ Error starting Claude: $_" -ForegroundColor Red
                        return $false
                    }
                } else {
                    Write-Host "❌ Could not find Claude.exe to restart. Please restart manually." -ForegroundColor Red
                    return $false
                }
            }
        }
    } else {
        Write-Host "🔎 No Claude processes found running." -ForegroundColor Yellow
        
        if ($Restart) {
            # Try to find and start Claude.exe (code omitted for brevity)
        }
    }
}

# Quick restart function that can be called directly
function Restart-Claude {
    param (
        [int]$WaitTime = 5
    )
    
    Write-Host "🔄 Restarting Claude..." -ForegroundColor Magenta
    $result = Manage-ClaudeProcess -Restart -WaitTime $WaitTime
    
    if ($result) {
        Write-Host "✅ Claude restart completed successfully." -ForegroundColor Green
    } else {
        Write-Host "❌ Claude restart failed. Please try again or restart manually." -ForegroundColor Red
    }
}

# Function to read Claude's configuration file
function Read-ClaudeConfig {
    if (Test-Path $configPath) {
        try {
            $config = Get-Content -Path $configPath -Raw | ConvertFrom-Json
            return $config
        }
        catch {
            Write-Host "❌ Error reading Claude configuration: $_" -ForegroundColor Red
            return $null
        }
    }
    else {
        Write-Host "❌ Claude configuration file not found at: $configPath" -ForegroundColor Red
        return $null
    }
}

# List all configured MCP tools
function List-MCPTools {
    $config = Read-ClaudeConfig
    
    if ($null -eq $config) {
        return
    }
    
    if ($null -eq $config.mcpServers -or $config.mcpServers.PSObject.Properties.Count -eq 0) {
        Write-Host "ℹ️ No MCP servers are configured." -ForegroundColor Yellow
        return
    }
    
    Write-Host "📋 Configured MCP Servers:" -ForegroundColor Green
    
    foreach ($server in $config.mcpServers.PSObject.Properties) {
        $serverName = $server.Name
        $serverConfig = $server.Value
        
        # Determine if this is an evolve-created tool
        $isEvolveTool = $false
        if ($serverConfig.args -and $serverConfig.args.Count -gt 0) {
            $scriptPath = $serverConfig.args[0]
            $fileName = Split-Path -Leaf $scriptPath
            if ($fileName -like "mcp_tool.*") {
                $isEvolveTool = $true
            }
        }
        
        # Use different colors for evolve tools vs other servers
        if ($isEvolveTool) {
            Write-Host "  🧠 $serverName" -ForegroundColor Magenta -NoNewline
            Write-Host " (Evolve Tool)" -ForegroundColor Yellow
        } else {
            Write-Host "  📦 $serverName" -ForegroundColor Cyan
        }
        
        Write-Host "    - Command: $($serverConfig.command)" -ForegroundColor Gray
        
        if ($serverConfig.args -and $serverConfig.args.Count -gt 0) {
            $argsStr = $serverConfig.args -join " "
            Write-Host "    - Args: $argsStr" -ForegroundColor Gray
        }
        
        # Check if the server script exists
        if ($serverConfig.args -and $serverConfig.args.Count -gt 0) {
            $scriptPath = $serverConfig.args[0]
            if (Test-Path $scriptPath) {
                if ($isEvolveTool) {
                    # For evolve tools, read metadata from file
                    try {
                        $fileContent = Get-Content -Path $scriptPath -TotalCount 6 -ErrorAction SilentlyContinue
                        $version = ($fileContent | Where-Object { $_ -like "# Version:*" } | Select-Object -First 1).Replace("# Version:", "").Trim()
                        $created = ($fileContent | Where-Object { $_ -like "# Created:*" } | Select-Object -First 1).Replace("# Created:", "").Trim()
                        
                        Write-Host "    - Status: ✅ Evolve tool active" -ForegroundColor Green
                        if ($version) { Write-Host "    - Version: $version" -ForegroundColor Gray }
                        if ($created) { Write-Host "    - Created: $created" -ForegroundColor Gray }
                    } catch {
                        Write-Host "    - Status: ✅ Script exists" -ForegroundColor Green
                    }
                } else {
                    Write-Host "    - Status: ✅ Script exists" -ForegroundColor Green
                }
            }
            else {
                Write-Host "    - Status: ❌ Script not found at $scriptPath" -ForegroundColor Red
            }
        }
        
        Write-Host ""
    }
}

# Setup Evolve Server
function Setup-Evolve-Server {
    Write-Host "`n🚀 Setting up Evolve MCP Server" -ForegroundColor Yellow
    
    # Get the current directory to save evolve.py with absolute path
    $currentDir = Get-Location
    $evolveScriptPath = Join-Path -Path $currentDir -ChildPath "evolve.py"
    
    Write-Host "📂 Target path for evolve.py: $evolveScriptPath" -ForegroundColor Cyan
    
    # Check if evolve.py already exists at the destination
    $evolveExists = Test-Path $evolveScriptPath
    if ($evolveExists) {
        Write-Host "✅ evolve.py already exists at target location" -ForegroundColor Green
    } else {
        # Generate the evolve server code
        try {
            # Check if the enhanced evolve.py exists in the current directory
            $enhancedEvolvePath = Join-Path -Path $PSScriptRoot -ChildPath "enhanced-evolve.py"
            
            if (Test-Path $enhancedEvolvePath) {
                # Copy the enhanced version
                Copy-Item -Path $enhancedEvolvePath -Destination $evolveScriptPath -Force
                Write-Host "✅ Copied enhanced evolve server code to: $evolveScriptPath" -ForegroundColor Green
            } else {
                # Try to download from repository
                $evolveUrl = "https://raw.githubusercontent.com/kordless/EvolveMCP/main/evolve.py"
                try {
                    Invoke-WebRequest -Uri $evolveUrl -OutFile $evolveScriptPath
                    Write-Host "✅ Downloaded evolve server code to: $evolveScriptPath" -ForegroundColor Green
                } catch {
                    Write-Host "❌ Failed to download evolve server code: $_" -ForegroundColor Red
                    Write-Host "ℹ️ Creating a basic evolve.py file" -ForegroundColor Yellow
                    
                    # Create a basic evolve.py file - code omitted for brevity
                    # Use the template from the README
                }
            }
        } catch {
            Write-Host "❌ Error creating evolve.py: $_" -ForegroundColor Red
            return $false
        }
    }
    
    # Update the Claude configuration file
    try {
        # Update the Claude configuration file with absolute path
        # Create evolve-only configuration with ABSOLUTE PATH to the script
        $evolveConfig = @{
            mcpServers = @{
                "evolve-server" = @{
                    command = "python"
                    args = @($evolveScriptPath)
                }
            }
        }
        
        # Ensure directory exists
        $configDir = Split-Path -Path $configPath -Parent
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        # Read existing config if it exists
        $existingConfig = $null
        if (Test-Path $configPath) {
            try {
                $existingConfig = Get-Content -Path $configPath -Raw | ConvertFrom-Json
            } catch {
                Write-Host "⚠️ Could not parse existing config, will create new one: $_" -ForegroundColor Yellow
            }
        }
        
        # If we have an existing config, merge the evolve server
        if ($existingConfig) {
            if (-not $existingConfig.mcpServers) {
                $existingConfig | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{}
            }
            
            # Add or update the evolve-server
            $existingConfig.mcpServers | Add-Member -MemberType NoteProperty -Name "evolve-server" -Value @{
                command = "python"
                args = @($evolveScriptPath)
            } -Force
            
            # Convert to JSON and save
            $existingConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $configPath
        } else {
            # Convert to JSON and save new config
            $evolveConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $configPath
        }
        
        Write-Host "✅ Updated Claude configuration with evolve-server at $configPath" -ForegroundColor Green
        Write-Host "📄 Config uses absolute path to evolve.py: $evolveScriptPath" -ForegroundColor Green
        
        Write-Host "`n✅ Evolve MCP server setup completed successfully!" -ForegroundColor Green
        
        $restartOption = Read-Host "🔄 Would you like to restart Claude now? (y/n)"
        if ($restartOption -eq "y") {
            Restart-Claude
        }
        
        return $true
    } catch {
        Write-Host "❌ Error updating configuration: $_" -ForegroundColor Red
        return $false
    }
}

# Main menu function
function Show-ClaudeManagerMenu {
    # Menu for script actions
    Write-Host "`n🧰 ===== CLAUDE MANAGER MENU ===== 🧰" -ForegroundColor Magenta
    Write-Host "1. 📜 View MCP Logs" -ForegroundColor Cyan
    Write-Host "2. 🛑 Kill Claude Desktop" -ForegroundColor Cyan
    Write-Host "3. 🚀 Setup Evolve Server" -ForegroundColor Cyan
    Write-Host "4. 🔄 Restart Claude" -ForegroundColor Cyan
    Write-Host "5. 📋 List MCP Tools" -ForegroundColor Cyan
    Write-Host "6. 🚪 Exit" -ForegroundColor Cyan

    $choice = Read-Host "`n🔢 Select an option (1-6)"

    switch ($choice) {
        "1" {
            # View MCP Logs
            View-MCP-Logs
            
            # Return to menu after viewing logs
            $returnToMenu = Read-Host "`n🔄 Return to menu? (y/n)"
            if ($returnToMenu -eq "y") {
                Show-ClaudeManagerMenu
            }
        }
        "2" {
            # Kill Claude Desktop
            Manage-ClaudeProcess -Kill
            
            # Return to menu after killing processes
            $returnToMenu = Read-Host "`n🔄 Return to menu? (y/n)"
            if ($returnToMenu -eq "y") {
                Show-ClaudeManagerMenu
            }
        }
        "3" {
            # Setup Evolve Server
            Setup-Evolve-Server
            
            # Return to menu after setup
            $returnToMenu = Read-Host "`n🔄 Return to menu? (y/n)"
            if ($returnToMenu -eq "y") {
                Show-ClaudeManagerMenu
            }
        }
        "4" {
            # Restart Claude
            Restart-Claude
            
            # Return to menu after restart
            $returnToMenu = Read-Host "`n🔄 Return to menu? (y/n)"
            if ($returnToMenu -eq "y") {
                Show-ClaudeManagerMenu
            }
        }
        "5" {
            # List MCP Tools
            List-MCPTools
            
            # Return to menu after listing tools
            $returnToMenu = Read-Host "`n🔄 Return to menu? (y/n)"
            if ($returnToMenu -eq "y") {
                Show-ClaudeManagerMenu
            }
        }
        "6" {
            Write-Host "👋 Exiting..." -ForegroundColor Yellow
            exit
        }
        default {
            Write-Host "❌ Invalid option. Please select a valid option." -ForegroundColor Red
            Show-ClaudeManagerMenu
        }
    }
}

# Process command-line parameters
if ($ViewLogs) {
    View-MCP-Logs -FilterName $LogName
    exit
}

if ($Kill) {
    Manage-ClaudeProcess -Kill
    exit
}

if ($Setup) {
    Setup-Evolve-Server
    exit
}

if ($Restart) {
    Restart-Claude
    exit
}

if ($ListTools) {
    List-MCPTools
    exit
}

# If no parameters, or Menu parameter is specified, show the menu
if ($Menu -or ($PSBoundParameters.Count -eq 0)) {
    # Start the script by showing the menu
    Write-Host "🔧 EvolveMCP - Claude Manager Tool" -ForegroundColor Yellow
    Write-Host "Logs Path: $logsPath" -ForegroundColor Yellow
    Write-Host "Config Path: $configPath" -ForegroundColor Yellow
    Show-ClaudeManagerMenu
}
```

4. Run the setup script to configure Claude:

```powershell
# Run the script with the setup flag
.\evolve.ps1 -Setup
```

5. When prompted, choose to restart Claude

## ✨ Creating Your First Tool

Once the evolve server is running and Claude has been restarted, you can create your first tool:

1. Ask Claude to create a new tool using the `evolve_create` function:

```
<function_calls>
<invoke name="evolve_create">
<parameter name="tool_name">calculator</parameter>
<parameter name="tool_code">@mcp.tool()
async def calc(expression: str) -> str:
    """A calculator tool that evaluates mathematical expressions."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"
</parameter>
</invoke>
</function_calls>
```

2. Restart Claude as instructed
3. After restarting, you can use the new calculator tool:

```
<function_calls>
<invoke name="calc">
<parameter name="expression">2 + 2 * 10</parameter>
</invoke>
</function_calls>
```

## 🛠️ MCP Setup Basics

### What is MCP?

The Model Context Protocol (MCP) is an open standard that enables AI models to communicate with external tools and data sources through a standardized interface. It provides a universal way for AI models to connect with external data sources, tools, and environments.

### Traditional Setup (The Complex Way)

According to the official documentation, setting up MCP typically involves:

1. Installing Claude Desktop
2. Using the uv package manager (which requires global installation)
3. Setting up Node.js (since many MCP servers are Node-based)
4. Creating complex configuration files with absolute paths
5. Manually editing the Claude desktop configuration file

### The EvolveMCP Way (Simplified)

Our approach cuts through this complexity:

1. **One-Click Setup**: Run `evolve.ps1` and select option 3
2. **Python-Based**: Uses Python instead of Node.js (more developers already have Python)
3. **No Global Dependencies**: Doesn't require uv or other global package managers
4. **Automatic Configuration**: Handles all path issues and configuration automatically
5. **Windows-Optimized**: Specifically designed to work with Windows path structures

As we move toward AI-managed tooling, the goal is to let AI handle more of this work. EvolveMCP is a step in that direction - simplifying the human effort required while we build toward a future where AI can configure and manage these tools itself.

## 📋 Command Line Options

You can use the following command-line options with evolve.ps1:

```powershell
# Restart Claude
.\evolve.ps1 -Restart

# View logs
.\evolve.ps1 -ViewLogs

# Setup the evolve server
.\evolve.ps1 -Setup

# List configured tools
.\evolve.ps1 -ListTools
```

## 📋 Requirements

- 🖥️ Windows with PowerShell
- 🤖 Claude Desktop application
- 🐍 Python installation
- 📦 MCP server package (`pip install mcp-server`)
