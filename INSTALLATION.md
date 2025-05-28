# Installation Guide

Complete installation instructions for Gnosis Evolve on Windows and macOS.

## Quick Start (Recommended)

### Download
1. **[Download the ZIP file directly](https://github.com/kordless/gnosis-evolve/archive/refs/tags/v1.1.0.zip)**
2. Extract the ZIP:
   - **Windows**: Right-click the ZIP and select "Extract All..."
   - **macOS**: Double-click the ZIP file
3. Open Terminal/PowerShell in the extracted folder

### Windows Setup

```powershell
# Run the setup script
.\evolve.ps1 -Setup
```

### macOS Setup

```bash
# Make the script executable
chmod +x ./evolve.sh

# Run the setup
./evolve.sh --setup
```

## Detailed Installation

### Prerequisites

#### Windows
- **Windows 10 or 11**
- **PowerShell 5.1+** (usually pre-installed)
- **Python 3.8+** (will be installed automatically if missing)

#### macOS
- **macOS 10.15+** (Catalina or newer)
- **Bash or Zsh** (pre-installed)
- **Xcode Command Line Tools** (required for Python compilation)
- **Python 3.8+** (will be installed via Homebrew if missing)

### Step-by-Step Installation

#### Windows Detailed Setup

1. **Download and Extract**
   ```powershell
   # Download to your preferred location
   cd C:\Users\YourName\Downloads
   # Extract gnosis-evolve-1.1.0.zip to a permanent location like:
   # C:\Users\YourName\Code\gnosis-evolve
   ```

2. **Open PowerShell as Administrator** (recommended)
   - Press `Win + X` and select "Windows PowerShell (Admin)"
   - Navigate to your extracted folder

3. **Run Setup**
   ```powershell
   # Navigate to the folder
   cd "C:\Users\YourName\Code\gnosis-evolve"
   
   # Run setup
   .\evolve.ps1 -Setup
   ```

4. **What the Setup Does**
   - Installs Python 3.11+ if not present
   - Installs required Python packages
   - Sets up Claude Desktop configuration
   - Creates necessary directories
   - Installs core MCP tools

5. **Launch Claude**
   ```powershell
   .\evolve.ps1 -StartClaude
   ```

#### macOS Detailed Setup

1. **Install Xcode Command Line Tools** (if not already installed)
   ```bash
   xcode-select --install
   ```
   - Click "Install" when prompted
   - Wait for installation to complete

2. **Download and Extract**
   ```bash
   # Download to your preferred location
   cd ~/Downloads
   # Extract and move to a permanent location
   unzip gnosis-evolve-1.1.0.zip
   mv gnosis-evolve-1.1.0 ~/Code/gnosis-evolve
   cd ~/Code/gnosis-evolve
   ```

3. **Make Script Executable**
   ```bash
   chmod +x ./evolve.sh
   ```

4. **Run Setup**
   ```bash
   ./evolve.sh --setup
   ```

5. **What the Setup Does**
   - Installs Homebrew if not present
   - Installs Python 3.11+ via Homebrew
   - Installs required Python packages
   - Sets up Claude Desktop configuration
   - Creates necessary directories
   - Installs core MCP tools

6. **Launch Claude**
   ```bash
   ./evolve.sh --restart
   ```

## Configuration Details

### Claude Desktop Configuration

The setup automatically configures Claude Desktop's `claude_desktop_config.json` file:

**Windows Location**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS Location**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Directory Structure

After installation, you'll have:

```
gnosis-evolve/
├── evolve.py              # Main evolve server
├── evolve.ps1            # Windows management script
├── evolve.sh             # macOS management script
├── tools/                # Individual MCP tools
├── contrib_tools/        # Community contributed tools
├── logs/                 # Tool logs
└── docs/                 # Documentation
```

## Manual Configuration

If automatic setup fails, you can manually configure Claude Desktop:

### Manual Claude Desktop Config

Edit your Claude Desktop configuration file and add:

```json
{
  "mcpServers": {
    "evolve-server": {
      "command": "python",
      "args": ["/full/path/to/gnosis-evolve/evolve.py"]
    }
  }
}
```

**Important**: Replace `/full/path/to/gnosis-evolve/` with your actual installation path.

### Python Environment Setup

If you prefer to manage Python dependencies manually:

```bash
# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install mcp fastmcp requests python-dotenv
```

## Verification

### Test Installation

1. **Launch Claude Desktop**
2. **Start a new conversation**
3. **Test evolve tools**:
   ```
   What tools do you have available?
   Can you run evolve_status?
   Show me the current system status
   ```

4. **You should see**:
   - List of available tools
   - System status information
   - No error messages

### Expected Tools

After successful installation, Claude should have access to:

- **evolve_status** - System status and health monitoring
- **evolve_filesystem** - File and directory exploration
- **evolve_tool** - Create and install new tools
- **file_diff_editor** - Advanced file editing
- **file_writer** - File creation with versioning
- **file_explorer** - Enhanced directory navigation
- **Plus 15+ additional tools**

## Troubleshooting

### Common Issues

#### Windows Issues

**PowerShell Execution Policy Error**
```powershell
# Fix execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Python Not Found**
```powershell
# Install Python manually
winget install Python.Python.3.11
# or download from python.org
```

**Claude Desktop Not Found**
- Install Claude Desktop from: https://claude.ai/download
- Restart the setup after installation

#### macOS Issues

**Xcode Command Line Tools Error**
```bash
# Reinstall command line tools
sudo xcode-select --reset
xcode-select --install
```

**Homebrew Installation Issues**
```bash
# Manual Homebrew installation
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Permission Denied Errors**
```bash
# Fix script permissions
chmod +x ./evolve.sh
# Run with proper permissions
sudo ./evolve.sh --setup
```

#### General Issues

**Claude Desktop Configuration Not Working**
1. Manually locate your Claude Desktop config file
2. Back up the existing configuration
3. Add the evolve server configuration manually
4. Restart Claude Desktop

**Tools Not Loading**
1. Check that Python path is correct in config
2. Verify all Python dependencies are installed
3. Check log files for error messages
4. Restart Claude Desktop completely

**Import Errors**
```bash
# Reinstall dependencies
pip install --force-reinstall mcp fastmcp requests python-dotenv
```

### Getting Help

1. **Check Log Files**
   ```bash
   # Windows
   .\evolve.ps1 -ViewLogs
   
   # macOS
   ./evolve.sh --view-logs
   ```

2. **Community Support**
   - Join our [Discord community](https://discord.gg/AQnAn9XgFJ)
   - Create an issue on GitHub
   - Check existing issues for solutions

3. **Debugging Steps**
   - Test Python installation: `python --version`
   - Test MCP installation: `python -c "import mcp"`
   - Check Claude Desktop config file location and contents
   - Verify file permissions and paths

## Advanced Installation

### Development Installation

For contributors or advanced users:

```bash
# Clone the repository
git clone https://github.com/kordless/gnosis-evolve.git
cd gnosis-evolve

# Install in development mode
pip install -e .

# Run tests (if available)
python -m pytest tests/
```

### Custom Tool Installation

After basic installation, you can install additional tools:

```bash
# Install specific tools via Claude
"Please install the bitcoin_price tool"
"Install the weather_resource tool for me"

# Or use the command line
python evolve.py --install-tool bitcoin_price
```

### Multiple Environment Setup

You can run multiple Gnosis Evolve installations:

1. **Create separate directories** for each environment
2. **Use different port numbers** in configurations
3. **Modify server names** to avoid conflicts
4. **Point Claude Desktop** to the desired environment

## Updating

### Update Gnosis Evolve

```bash
# Windows
.\evolve.ps1 -Update

# macOS
./evolve.sh --update
```

### Manual Update

1. **Backup your configuration**
2. **Download the latest release**
3. **Extract to a new folder**
4. **Copy your custom tools** from the old installation
5. **Re-run setup**

## Uninstallation

### Complete Removal

```bash
# Windows
.\evolve.ps1 -Uninstall

# macOS
./evolve.sh --uninstall
```

### Manual Removal

1. **Remove Claude Desktop configuration**
   - Edit `claude_desktop_config.json`
   - Remove evolve-server entries
2. **Delete installation directory**
3. **Remove Python virtual environment** (if created)

## Next Steps

After installation:

1. **Read the [Getting Started Guide](README.md#getting-started-tips)**
2. **Explore [Tool Development](TOOL_DEVELOPMENT.md)**
3. **Check out [Security Guidelines](SECURITY.md)**
4. **Join the [Community Discord](https://discord.gg/AQnAn9XgFJ)**

Need help? The community is here to assist! 🚀