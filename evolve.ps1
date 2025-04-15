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
    [switch]$ListTools
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
                Write-Host "🚀 Starting Claude from: $claudeExe" -ForegroundColor Green
                try {
                    Start-Process -FilePath $claudeExe -ErrorAction Stop
                    
                    # Verify Claude started successfully
                    Start-Sleep -Seconds 5
                    $newClaudeProcesses = Get-Process -Name "*claude*" -ErrorAction SilentlyContinue
                    
                    if ($newClaudeProcesses) {
                        Write-Host "✅ Claude has been successfully started." -ForegroundColor Green
                        foreach ($process in $newClaudeProcesses) {
                            Write-Host "  - 🚀 Started $($process.Name) (PID: $($process.Id))" -ForegroundColor Green
                        }
                        return $true
                    } else {
                        Write-Host "❌ Failed to detect Claude processes after start." -ForegroundColor Red
                        return $false
                    }
                }
                catch {
                    Write-Host "❌ Error starting Claude: $_" -ForegroundColor Red
                    return $false
                }
            } else {
                Write-Host "❌ Could not find Claude.exe to start. Please start manually." -ForegroundColor Red
                return $false
            }
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

# Function to write Claude's configuration file
function Write-ClaudeConfig {
    param (
        [PSCustomObject]$Config
    )
    
    try {
        $configDir = Split-Path -Path $configPath -Parent
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        $Config | ConvertTo-Json -Depth 10 | Set-Content -Path $configPath
        Write-Host "✅ Updated Claude configuration at $configPath" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "❌ Error updating Claude configuration: $_" -ForegroundColor Red
        return $false
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

# No longer using a separate function to configure MCP servers - this will be done by evolve_setup in Python

# Setup Evolve Server for the first time
function Setup-Evolve-Server {
    Write-Host "`n🚀 Setting up Evolve MCP Server" -ForegroundColor Yellow
    
    # Get the current directory to save evolve.py with absolute path
    $currentDir = Get-Location
    $evolveScriptPath = Join-Path -Path $currentDir -ChildPath "evolve.py"
    
    # Check if evolve.py already exists in the current directory
    if (Test-Path $evolveScriptPath) {
        Write-Host "✅ Found evolve.py at: $evolveScriptPath" -ForegroundColor Green
    } else {
        Write-Host "❌ evolve.py not found at: $evolveScriptPath" -ForegroundColor Red
        Write-Host "Please make sure evolve.py is in the current directory before continuing." -ForegroundColor Yellow
        return $false
    }
    
    # Create a backup of the existing config
    $backupPath = "$configPath.backup"
    try {
        if (Test-Path $configPath) {
            Copy-Item -Path $configPath -Destination $backupPath -Force
            Write-Host "✅ Created configuration backup at: $backupPath" -ForegroundColor Green
        }
    } catch {
        Write-Host "⚠️ Warning: Failed to create backup of configuration file: $_" -ForegroundColor Yellow
    }
    
    # Read existing configuration
    $config = Read-ClaudeConfig
    
    if ($null -eq $config) {
        $config = @{}
    }
    
    if (-not $config.mcpServers) {
        $config | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{} -Force
    }
    
    # Check if other MCP servers exist
    $hasOtherServers = $false
    if ($config.mcpServers.PSObject.Properties.Count -gt 0) {
        $otherServers = $config.mcpServers.PSObject.Properties | Where-Object { $_.Name -ne "evolve-server" }
        
        if ($otherServers -and $otherServers.Count -gt 0) {
            $hasOtherServers = $true
            Write-Host "`n⚠️ The following MCP servers are currently configured:" -ForegroundColor Yellow
            
            foreach ($server in $otherServers) {
                Write-Host "  - $($server.Name)" -ForegroundColor Cyan
            }
            
            Write-Host "`n⚠️ Setting up evolve will REMOVE all other MCP servers from the configuration." -ForegroundColor Yellow
            Write-Host "   All tools will need to be reconfigured through evolve_setup." -ForegroundColor Yellow
            
            $confirmation = Read-Host "`n❓ Are you sure you want to continue? (y/n)"
            if ($confirmation -ne "y") {
                Write-Host "❌ Setup aborted." -ForegroundColor Red
                return $false
            }
        }
    }
    
    # Create a new configuration with only evolve-server
    $newConfig = @{
        mcpServers = @{
            "evolve-server" = @{
                command = "python"
                args = @($evolveScriptPath)
            }
        }
    }
    
    # Write the configuration
    try {
        $configDir = Split-Path -Path $configPath -Parent
        if (-not (Test-Path $configDir)) {
            New-Item -ItemType Directory -Path $configDir -Force | Out-Null
        }
        
        # Convert to JSON and save
        $newConfig | ConvertTo-Json -Depth 10 | Set-Content -Path $configPath
        
        if ($hasOtherServers) {
            Write-Host "✅ Removed all previous MCP servers and configured evolve-server." -ForegroundColor Green
        } else {
            Write-Host "✅ Configured evolve-server." -ForegroundColor Green
        }
        
        Write-Host "📄 Config uses absolute path to evolve.py: $evolveScriptPath" -ForegroundColor Green
        
        Write-Host "`n✅ Evolve MCP server setup completed successfully!" -ForegroundColor Green
        
        $restartOption = Read-Host "🔄 Would you like to restart Claude now? (y/n)"
        if ($restartOption -eq "y") {
            Restart-Claude
        } else {
            Write-Host "ℹ️ Remember to restart Claude for the changes to take effect." -ForegroundColor Yellow
        }
        
        return $true
    } catch {
        Write-Host "❌ Failed to update Claude configuration: $_" -ForegroundColor Red
        
        # Offer to restore backup
        if (Test-Path $backupPath) {
            $restoreBackup = Read-Host "🔄 Would you like to restore the backup configuration? (y/n)"
            if ($restoreBackup -eq "y") {
                try {
                    Copy-Item -Path $backupPath -Destination $configPath -Force
                    Write-Host "✅ Restored configuration from backup." -ForegroundColor Green
                } catch {
                    Write-Host "❌ Failed to restore backup: $_" -ForegroundColor Red
                }
            }
        }
        
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
    Write-Host "5. 📋 List Current MCP Servers" -ForegroundColor Cyan
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

# Removed Configure parameter handling

# If no parameters, or Menu parameter is specified, show the menu
if ($Menu -or ($PSBoundParameters.Count -eq 0)) {
    # Start the script by showing the menu
    Write-Host "🔧 EvolveMCP - Claude Manager Tool" -ForegroundColor Yellow
    Write-Host "Logs Path: $logsPath" -ForegroundColor Yellow
    Write-Host "Config Path: $configPath" -ForegroundColor Yellow
    Show-ClaudeManagerMenu
}
