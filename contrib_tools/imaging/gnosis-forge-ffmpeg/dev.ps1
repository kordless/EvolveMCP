# Gnosis Forge - Local Development Script (PowerShell 5.1 Compatible)
# Usage: .\dev.ps1 [build|run|test|logs|shell|stop|clean|status|help]

param(
    [Parameter(Position=0)]
    [string]$Command = "run"
)

$ServiceName = "gnosis-forge"
$Port = 8000

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    # PowerShell 5.1 compatible color output
    switch ($Color) {
        "Green" { Write-Host $Message -ForegroundColor Green }
        "Yellow" { Write-Host $Message -ForegroundColor Yellow }
        "Red" { Write-Host $Message -ForegroundColor Red }
        "Cyan" { Write-Host $Message -ForegroundColor Cyan }
        default { Write-Host $Message -ForegroundColor White }
    }
}

function Test-DockerRunning {
    try {
        docker version | Out-Null
        return $true
    }
    catch {
        Write-ColorOutput "[ERROR] Docker is not running or not installed. Please start Docker first." "Red"
        return $false
    }
}

function Test-ImageExists {
    $images = docker images --format "{{.Repository}}:{{.Tag}}" | Where-Object { $_ -eq "${ServiceName}:latest" }
    return $images.Count -gt 0
}

function Build-Image {
    Write-ColorOutput "[BUILD] Building Docker image for local development..." "Green"
    
    if (-not (Test-DockerRunning)) {
        return
    }
    
    Write-ColorOutput "This may take several minutes as FFmpeg is compiled from source..." "Yellow"
    
    try {
        docker build -t $ServiceName .
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "[SUCCESS] Image built successfully!" "Green"
        } else {
            Write-ColorOutput "[ERROR] Build failed with exit code $LASTEXITCODE" "Red"
        }
    }
    catch {
        Write-ColorOutput "[ERROR] Build failed: $($_.Exception.Message)" "Red"
    }
}

function Stop-Container {
    Write-ColorOutput "[STOP] Stopping any running containers..." "Yellow"
    
    try {
        # Stop container if running
        $running = docker ps --filter "name=$ServiceName" --format "{{.Names}}"
        if ($running -eq $ServiceName) {
            docker stop $ServiceName | Out-Null
            Write-ColorOutput "[SUCCESS] Container stopped" "Green"
        }
        
        # Remove container if exists
        $exists = docker ps -a --filter "name=$ServiceName" --format "{{.Names}}"
        if ($exists -eq $ServiceName) {
            docker rm $ServiceName | Out-Null
            Write-ColorOutput "[SUCCESS] Container removed" "Green"
        }
    }
    catch {
        Write-ColorOutput "[WARNING]  Error stopping container: $($_.Exception.Message)" "Yellow"
    }
}

function Run-Container {
    if (-not (Test-DockerRunning)) {
        return
    }
    
    # Check if image exists
    if (-not (Test-ImageExists)) {
        Write-ColorOutput "[WARNING]  Image '$ServiceName' not found. Building it first..." "Yellow"
        Build-Image
        if (-not (Test-ImageExists)) {
            Write-ColorOutput "[ERROR] Failed to build image. Cannot run container." "Red"
            return
        }
    }
    
    # Stop any existing container
    Stop-Container
    
    Write-ColorOutput "[RUN] Starting Gnosis Forge locally on port $Port..." "Green"
    Write-ColorOutput "[DOCS] API Documentation will be available at: http://localhost:$Port/" "Cyan"
    Write-ColorOutput "[HEALTH] Health check: http://localhost:$Port/health" "Cyan"
    Write-ColorOutput "[DOCS] OpenAPI docs: http://localhost:$Port/docs" "Cyan"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Press Ctrl+C to stop the container" "Yellow"
    Write-ColorOutput "" "White"
    
    try {
        docker run --rm -p "${Port}:8000" --name $ServiceName -v "${PWD}:/app/workspace" $ServiceName
    }
    catch {
        Write-ColorOutput "[ERROR] Failed to run container: $($_.Exception.Message)" "Red"
    }
}

function Test-Service {
    Write-ColorOutput "[TEST] Testing Gnosis Forge service..." "Green"
    
    # Wait for service to be ready
    Write-ColorOutput "Waiting for service to start..." "Yellow"
    Start-Sleep -Seconds 5
    
    $baseUrl = "http://localhost:$Port"
    $testsPassed = 0
    $totalTests = 2
    
    # Test health endpoint
    Write-ColorOutput "Testing health endpoint..." "Yellow"
    try {
        $response = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 10
        if ($response.status -eq "healthy") {
            Write-ColorOutput "[SUCCESS] Health check passed: $($response.status)" "Green"
            $testsPassed++
        } else {
            Write-ColorOutput "[ERROR] Health check failed: unexpected status" "Red"
        }
    }
    catch {
        Write-ColorOutput "[ERROR] Health check failed: $($_.Exception.Message)" "Red"
    }
    
    # Test documentation endpoint
    Write-ColorOutput "Testing documentation endpoint..." "Yellow"
    try {
        $response = Invoke-WebRequest -Uri $baseUrl -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-ColorOutput "[SUCCESS] Documentation endpoint accessible" "Green"
            $testsPassed++
        } else {
            Write-ColorOutput "[ERROR] Documentation endpoint failed: Status $($response.StatusCode)" "Red"
        }
    }
    catch {
        Write-ColorOutput "[ERROR] Documentation endpoint failed: $($_.Exception.Message)" "Red"
    }
    
    Write-ColorOutput "" "White"
    Write-ColorOutput "Test Results: $testsPassed/$totalTests tests passed" "Cyan"
    
    if ($testsPassed -eq $totalTests) {
        Write-ColorOutput "[PARTY] All tests passed! Service is running correctly." "Green"
    } else {
        Write-ColorOutput "[WARNING]  Some tests failed. Check the container logs." "Yellow"
    }
}

function Show-Logs {
    Write-ColorOutput "[LOGS] Showing container logs..." "Green"
    
    try {
        $running = docker ps --filter "name=$ServiceName" --format "{{.Names}}"
        if ($running -eq $ServiceName) {
            docker logs $ServiceName -f
        } else {
            Write-ColorOutput "[ERROR] Container '$ServiceName' is not running" "Red"
            Write-ColorOutput "Available containers:" "Yellow"
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        }
    }
    catch {
        Write-ColorOutput "[ERROR] Failed to show logs: $($_.Exception.Message)" "Red"
    }
}

function Open-Shell {
    Write-ColorOutput "[SHELL] Opening shell in container..." "Green"
    
    try {
        $running = docker ps --filter "name=$ServiceName" --format "{{.Names}}"
        if ($running -eq $ServiceName) {
            docker exec -it $ServiceName /bin/bash
        } else {
            Write-ColorOutput "[ERROR] Container '$ServiceName' is not running" "Red"
            Write-ColorOutput "Start the container first with: .\dev.ps1 run" "Yellow"
        }
    }
    catch {
        Write-ColorOutput "[ERROR] Failed to open shell: $($_.Exception.Message)" "Red"
    }
}

function Clean-Everything {
    Write-ColorOutput "[CLEAN] Cleaning up Docker resources..." "Green"
    
    # Stop and remove container
    Stop-Container
    
    # Remove image
    try {
        if (Test-ImageExists) {
            docker rmi $ServiceName
            Write-ColorOutput "[SUCCESS] Image removed" "Green"
        }
    }
    catch {
        Write-ColorOutput "[WARNING]  Could not remove image: $($_.Exception.Message)" "Yellow"
    }
    
    # Clean up Docker system
    try {
        docker system prune -f | Out-Null
        Write-ColorOutput "[SUCCESS] Docker system cleaned" "Green"
    }
    catch {
        Write-ColorOutput "[WARNING]  Could not clean Docker system: $($_.Exception.Message)" "Yellow"
    }
}

function Show-Status {
    Write-ColorOutput "[STATUS] Gnosis Forge Status" "Cyan"
    Write-ColorOutput "==============================" "White"
    
    # Check Docker
    if (Test-DockerRunning) {
        Write-ColorOutput "[SUCCESS] Docker: Running" "Green"
    } else {
        Write-ColorOutput "[ERROR] Docker: Not running" "Red"
        return
    }
    
    # Check Image
    if (Test-ImageExists) {
        Write-ColorOutput "[SUCCESS] Image: Built" "Green"
    } else {
        Write-ColorOutput "[ERROR] Image: Not built" "Red"
    }
    
    # Check Container
    $running = docker ps --filter "name=$ServiceName" --format "{{.Names}}"
    if ($running -eq $ServiceName) {
        Write-ColorOutput "[SUCCESS] Container: Running on port $Port" "Green"
        Write-ColorOutput "   [DOCS] Documentation: http://localhost:$Port/" "Cyan"
        Write-ColorOutput "   [HEALTH] Health: http://localhost:$Port/health" "Cyan"
    } else {
        Write-ColorOutput "[ERROR] Container: Not running" "Red"
    }
    
    Write-ColorOutput "" "White"
}

function Show-Help {
    Write-ColorOutput "Gnosis Forge - Local Development Commands" "Yellow"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Commands:" "Cyan"
    Write-ColorOutput "  build   - Build Docker image" "White"
    Write-ColorOutput "  run     - Build (if needed) and run container locally" "White"
    Write-ColorOutput "  test    - Test the running service" "White"
    Write-ColorOutput "  logs    - Show container logs" "White"
    Write-ColorOutput "  shell   - Open shell in running container" "White"
    Write-ColorOutput "  stop    - Stop and remove container" "White"
    Write-ColorOutput "  clean   - Clean up all Docker resources" "White"
    Write-ColorOutput "  status  - Show current status" "White"
    Write-ColorOutput "  help    - Show this help" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Examples:" "Cyan"
    Write-ColorOutput "  .\dev.ps1 build" "White"
    Write-ColorOutput "  .\dev.ps1 run" "White"
    Write-ColorOutput "  .\dev.ps1 test" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "URLs (when running):" "Cyan"
    Write-ColorOutput "  API Documentation: http://localhost:$Port/" "White"
    Write-ColorOutput "  Health Check: http://localhost:$Port/health" "White"
    Write-ColorOutput "  OpenAPI Docs: http://localhost:$Port/docs" "White"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Note: The first build will take 10-15 minutes as FFmpeg is compiled from source." "Yellow"
}

# Main command processing
switch ($Command.ToLower()) {
    "build" { Build-Image }
    "run" { Run-Container }
    "test" { Test-Service }
    "logs" { Show-Logs }
    "shell" { Open-Shell }
    "stop" { Stop-Container }
    "clean" { Clean-Everything }
    "status" { Show-Status }
    "help" { Show-Help }
    default { 
        Write-ColorOutput "Unknown command: $Command" "Red"
        Write-ColorOutput "" "White"
        Show-Help
    }
}
