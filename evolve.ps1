# Simplified Claude Manager Script
# Focuses on MCP logs in a single directory and simplified evolve server setup

# Set username explicitly
$username = $env:USERNAME

# Define the specific logs directory path
$logsPath = "C:\Users\$username\AppData\Roaming\Claude\logs"
$configPath = "C:\Users\$username\AppData\Roaming\Claude\claude_desktop_config.json"

# Simplified Log Viewer Function
# ONLY looks in the exact logs directory, nowhere else

function View-MCP-Logs {
    # Define the EXACT logs directory path - ONLY look here
    $logsPath = "C:\Users\$env:USERNAME\AppData\Roaming\Claude\logs"
    
    # Check if logs directory exists
    if (Test-Path $logsPath) {
        Write-Host "📁 Found logs directory at: $logsPath" -ForegroundColor Green
        
        # ONLY get log files in this exact directory - NO recursion, NO other locations
        $logFiles = Get-ChildItem -Path $logsPath -Filter "*.log" -ErrorAction SilentlyContinue
        
        if ($logFiles.Count -gt 0) {
            Write-Host "🔍 Found $($logFiles.Count) log files:" -ForegroundColor Green
            
            # Display files with number options for selection
            $fileOptions = @{}
            
            for ($i = 1; $i -le $logFiles.Count; $i++) {
                $file = $logFiles[$i-1]
                Write-Host "  $i. 📄 $($file.Name)" -ForegroundColor Cyan
                $fileOptions[$i] = $file
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
            Write-Host "❌ No log files found in $logsPath" -ForegroundColor Red
            
            # Inform user if directory exists but is empty
            Write-Host "The directory exists but contains no log files." -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Logs directory not found at: $logsPath" -ForegroundColor Red
        
        # Option to create the logs directory
        $createDir = Read-Host "`n📂 Would you like to create the logs directory? (y/n)"
        if ($createDir -eq "y") {
            try {
                New-Item -ItemType Directory -Path $logsPath -Force | Out-Null
                Write-Host "✅ Created logs directory at: $logsPath" -ForegroundColor Green
            }
            catch {
                Write-Host "❌ Failed to create logs directory: $_" -ForegroundColor Red
            }
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
            # Try to find and start Claude.exe
            # [Code omitted for brevity - same as above]
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

# Fixed Evolve Server Setup
function Setup-Evolve-Server {
    Write-Host "`n🚀 Setting up Evolve MCP Server" -ForegroundColor Yellow
    
    # Get the current directory to save evolve.py with absolute path
    $currentDir = Get-Location
    $evolveScriptPath = Join-Path -Path $currentDir -ChildPath "evolve.py"
    
    Write-Host "📂 Creating evolve.py at: $evolveScriptPath" -ForegroundColor Cyan
    
    # Generate the evolve server code
    try {
        # Create the evolve.py file with the server code
        $evolveCode = @'

import sys
import subprocess
import importlib.util

# Check if a package is installed and install it if not
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            try:
                # Use simple text, avoiding Unicode emojis that might cause encoding issues
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

# Initialize FastMCP server
mcp = FastMCP("evolve-server")

# Store the evolve tool's learning state
EVOLVE_STATE = {
    "version": 1.0,
    "capabilities": ["greeting"],
    "learned_patterns": {},
    "interactions": 0,
    "last_updated": time.time(),
    "memory": []
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
                print(f"Loaded state: version {EVOLVE_STATE['version']}, {len(EVOLVE_STATE['capabilities'])} capabilities")
    except Exception as e:
        print(f"Error loading state: {e}")

# Save state
def save_state():
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(EVOLVE_STATE, f, indent=2)
            print(f"State saved: version {EVOLVE_STATE['version']}, {len(EVOLVE_STATE['capabilities'])} capabilities")
    except Exception as e:
        print(f"Error saving state: {e}")

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
            "memory_size": len(EVOLVE_STATE["memory"])
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
            4. Operate in different modes (basic, advanced, debug)
            
            To teach me something new, set learn=True and provide pattern and response parameters.
            """
        
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
        return "I can respond to various prompts and learn new patterns. Try different questions or teach me by using the learn parameter."
    
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
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(EVOLVE_STATE["last_updated"]))
    }

@mcp.tool()
async def evolve_reset(confirm: bool = False) -> str:
    """Reset the evolve tool to its initial state.
    
    Args:
        confirm: Set to True to confirm the reset
    """
    global EVOLVE_STATE
    
    if not confirm:
        return "Please set confirm=True to reset the evolve tool."
    
    EVOLVE_STATE = {
        "version": EVOLVE_STATE["version"] + 0.1,  # Increment version
        "capabilities": ["greeting"],
        "learned_patterns": {},
        "interactions": 0,
        "last_updated": time.time(),
        "memory": []
    }
    
    save_state()
    return "Evolve tool has been reset to initial state with version upgrade."

# Load state when server starts
load_state()

# Print server information
print(f"Starting Evolve MCP server v{EVOLVE_STATE['version']}...")
print(f"Capabilities: {', '.join(EVOLVE_STATE['capabilities'])}")
print("Use the 'evolve' tool to interact with the server.")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
'@
        Set-Content -Path $evolveScriptPath -Value $evolveCode -Force
        Write-Host "✅ Evolve server code generated at: $evolveScriptPath" -ForegroundColor Green
        
        # Define the config path
        $configPath = "C:\Users\$env:USERNAME\AppData\Roaming\Claude\claude_desktop_config.json"
        
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
        
        # Convert to JSON and save
        $evolveConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $configPath
        Write-Host "✅ Updated Claude configuration with evolve-server at $configPath" -ForegroundColor Green
        Write-Host "📄 Config uses absolute path to evolve.py: $evolveScriptPath" -ForegroundColor Green
        
        Write-Host "`n✅ Evolve MCP server setup completed successfully!" -ForegroundColor Green
        
        $restartOption = Read-Host "🔄 Would you like to restart Claude now? (y/n)"
        if ($restartOption -eq "y") {
            Restart-Claude
        }
        
        return $true
    }
    catch {
        Write-Host "❌ Error setting up Evolve server: $_" -ForegroundColor Red
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
    Write-Host "5. 🚪 Exit" -ForegroundColor Cyan

    $choice = Read-Host "`n🔢 Select an option (1-5)"

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
            Write-Host "👋 Exiting..." -ForegroundColor Yellow
            exit
        }
        default {
            Write-Host "❌ Invalid option. Please select a valid option." -ForegroundColor Red
            Show-ClaudeManagerMenu
        }
    }
}

# Start the script by showing the menu
Write-Host "🔧 Claude Manager Tool - Simplified Version" -ForegroundColor Yellow
Write-Host "Logs Path: $logsPath" -ForegroundColor Yellow
Write-Host "Config Path: $configPath" -ForegroundColor Yellow
Show-ClaudeManagerMenu
