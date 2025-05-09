<div align="center">

# EvolveMCP: Build. Extend. Evolve.
<strong>Pythonic MCP development, supercharged by AI intelligence and your will to build something new.</strong>

[![License](https://img.shields.io/badge/license-_Sovereign_v1.1-purple)](https://github.com/kordless/EvolveMCP/blob/main/LICENSE.md)
[![GitHub stars](https://img.shields.io/github/stars/kordless/EvolveMCP.svg?style=social)](https://github.com/kordless/EvolveMCP/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/kordless/EvolveMCP?color=green)](https://github.com/kordless/EvolveMCP/issues)

<h1>🧠</h1>
</div>

# 🚀 Beginner’s Guide to Installing EvolveMCP

## 📺 Demo Video

[![evolveMCP Bitcoin App Demo](https://img.youtube.com/vi/KsHngo05WIY/0.jpg)](https://www.youtube.com/watch?v=KsHngo05WIY)

Watch a demonstration of the Bitcoin price tracking app created with EvolveMCP, showing how Claude can build and use its own tools to fetch and visualize real-time cryptocurrency data.

<!-- Small (250px wide) -->
<img src="https://github.com/kordless/EvolveMCP/blob/main/price.png" width="250" alt="Bitcoin Price">

## 🧠 What is EvolveMCP?

EvolveMCP gives Claude Desktop the ability to build, install, and use its own tools—expanding what it can actually do, not just talk about: 

- Claude can write code for you that it can then use itself
- You can ask Claude to build specialized tools that solve your specific problems
- You can enhance Claude's capabilities beyond its default features

It turns Claude from a passive assistant into an active developer, capable of creating solutions as you need them.

Claude is the first client supported by the system, but EvolveMCP is built with a modular design. Support for other clients, tools and document collections is on the roadmap.

## ⚠️ Security Warning

**IMPORTANT:** EvolveMCP allows Claude to create and execute Python code on your local machine. Before using this software, please understand the security implications by referring to the Security Implications section at the bottom.

## Prerequisites

Before starting, you'll need:

1. **Computer**: Evolve is designed to work on Windows and macOS
2. **Internet Connection**: For downloading necessary files
3. **Claude Desktop**: The desktop application for Claude

## Step 1: Install Claude Desktop
1. Visit the official Anthropic website to [download Claude Desktop](https://claude.ai/download)
2. Run the installer and follow the on-screen instructions
3. Launch Claude Desktop at least once to create initial configuration files

## Step 2: Download Evolve

### Option A: Download the Release Package (Easiest)

1. Go to [github.com/kordless/EvolveMCP/releases/tag/v1.0.4](https://github.com/kordless/EvolveMCP/releases/tag/v1.0.4)
2. Under "Assets", click on the .zip file (top source code file)
3. Save the file to a location you can easily find (like your Downloads folder)
4. Extract the archive:
   - **Windows**: Right-click the downloaded zip file and select "Extract All..."
   - **macOS**: Double-click the downloaded zip file to extract it
5. Choose where to extract the files (like your Documents folder)

### Option B: Using Git (For Advanced Users)

If you're familiar with Git:

1. Install Git from [git-scm.com](https://git-scm.com/downloads) if you don't have it
2. Open Terminal (macOS) or PowerShell (Windows)
3. Navigate to where you want to install Evolve
4. Run these commands:
   ```
   git clone https://github.com/kordless/EvolveMCP.git
   cd EvolveMCP
   ```

## Step 3: Open Terminal/PowerShell

### Windows
1. Navigate to the folder where you extracted Evolve
2. Hold Shift and right-click in an empty area of the folder
3. Select "Open PowerShell window here" from the menu
   - If you don't see this option, see our [PowerShell Guide](powershell-guide.md) for alternatives

### macOS
1. Open Finder and navigate to the folder where you extracted Evolve
2. Right-click (or Control-click) on the folder
3. Select "New Terminal at Folder" or "Services" > "New Terminal at Folder"
   - If you don't see this option, open Terminal (from Applications > Utilities) and use `cd` to navigate to your folder

## Step 4: Run the Setup Script

### Windows
1. In the PowerShell window, type the following command and press Enter:
   ```powershell
   .\evolve.ps1 -Setup
   ```

2. If you see an error message about execution policy, run this command and try again:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

### macOS
1. In the Terminal window, make the script executable:
   ```bash
   chmod +x ./evolve.sh
   ```

2. Run the setup command:
   ```bash
   ./evolve.sh --setup
   ```

3. If you need to install jq (required for JSON processing):
   ```bash
   brew install jq
   ```
   If you don't have Homebrew installed, visit [brew.sh](https://brew.sh/) for installation instructions.

4. Follow any on-screen instructions to complete the setup

## Step 5: Create Your First Tool

1. After setup completes, make sure you're still in PowerShell/Terminal in the Evolve folder
2. Start Claude with the Evolve tools available:

   **Windows**:
   ```powershell
   .\evolve.ps1 -StartClaude
   ```

   **macOS**:
   ```bash
   ./evolve.sh --restart
   ```

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

   **Windows**:
   ```powershell
   .\evolve.ps1 -Restart
   ```

   **macOS**:
   ```bash
   ./evolve.sh --restart
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

##### Windows
```powershell
.\EvolveMCP.ps1 -ViewLogs
```

To filter logs by name:
```powershell
.\EvolveMCP.ps1 -ViewLogs -LogName evolve
```

##### macOS
```bash
./evolve.sh --view-logs
```

To filter logs by name:
```bash
./evolve.sh --view-logs --log-name evolve
```

This will show only log files that contain "evolve" in their filename.

#### Using the Menu Interface

If you prefer a menu-based approach:

##### Windows
```powershell
.\EvolveMCP.ps1
```

##### macOS
```bash
./evolve-mcp.sh
```

Then select option `1. View MCP Logs` from the menu and choose a log file from the displayed list.

#### Log Monitoring

When viewing a log file, the tool will initially show the last 20 lines. You'll then be prompted if you want to monitor the log file in real-time. Selecting `y` will continuously display new log entries as they are written, which is particularly useful when debugging active issues.

To stop monitoring, press `Ctrl+C`.

#### Log Location

Logs are stored in the following location:

**Windows**:
```
C:\Users\<username>\AppData\Roaming\Claude\logs
```

**macOS**:
```
~/Library/Application Support/Claude/logs
```

If this directory doesn't exist, the tool will offer to create it for you.

### Common Issues

#### Claude Desktop Not Starting

If Claude Desktop fails to start after configuring MCP servers:

1. Check the logs for any error messages:
   
   **Windows**:
   ```powershell
   .\EvolveMCP.ps1 -ViewLogs
   ```
   
   **macOS**:
   ```bash
   ./evolve-mcp.sh --view-logs
   ```

2. Verify that your configuration file is correct:
   
   **Windows**:
   ```
   C:\Users\<username>\AppData\Roaming\Claude\claude_desktop_config.json
   ```
   
   **macOS**:
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

3. Ensure the paths to your MCP server scripts are valid and accessible

#### Evolve Server Issues

If you're experiencing issues with the Evolve server:

1. View the Evolve-specific logs:
   
   **Windows**:
   ```powershell
   .\EvolveMCP.ps1 -ViewLogs -LogName evolve
   ```
   
   **macOS**:
   ```bash
   ./evolve-mcp.sh --view-logs --log-name evolve
   ```

2. Verify that `evolve.py` exists in the location specified in your configuration
3. Make sure Python is properly installed and accessible from the command line

#### Restarting Claude Desktop

If Claude Desktop becomes unresponsive or you need to apply configuration changes:

**Windows**:
```powershell
.\EvolveMCP.ps1 -Restart
```

**macOS**:
```bash
./evolve-mcp.sh --restart
```

This will gracefully stop and restart Claude Desktop.

### Checking Tool Configuration

To verify which MCP tools are currently configured:

**Windows**:
```powershell
.\EvolveMCP.ps1 -ListTools
```

**macOS**:
```bash
./evolve.sh --list-tools
```

This will display all configured MCP servers, including:
- Server name
- Command and arguments
- Whether the script exists
- For Evolve tools: version and creation date (if available)

## ⚠️ Security Implications

1. **Code Execution Risk**: Any code that runs on your computer has access to your system at the same permission level as the user running it. This includes your files, network, and potentially sensitive information.

2. **Review Generated Code**: While Evolve (and Claude) aim to create safe and useful tools, you should review any code that it generates before allowing it to run, especially if you're using it in a professional or sensitive environment.

3. **No Warranty**: This software is provided "as is" without warranty of any kind. The creators are not responsible for any damages or security incidents resulting from its use.

4. **Recommended Precautions**:
   - Run EvolveMCP in a dedicated user account with limited permissions
   - Backup important data before using new tools
   - Consider using a virtual machine or container for additional isolation (we'll be working on making this easier soon)
   - Keep your operating system and security software up to date

5. **For Developers**: If you're extending EvolveMCP, follow secure coding practices and avoid giving tools unnecessary system access.

By installing and using EvolveMCP, you acknowledge these risks and take responsibility for the code executed on your system.

## License Explanation: Sovereign v1.1

EvolveMCP is released under the Sovereign v1.1 license, which balances open use with specific restrictions:

### AI and the Evolution of Licensing

We stand at a unique crossroads in the relationship between human and artificial intelligence. Traditional software licenses were never designed for a world where:

1. AI can create, modify, and execute code based on natural language instructions
2. The lines between user, creator, and tool become increasingly blurred
3. The same software might be used by individuals, corporations, and potentially autonomous AI systems
4. Digital and analog minds each bring distinct forms of intelligence and capabilities

The Sovereign license represents our attempt to navigate this unprecedented territory - acknowledging that just as AI must evolve, so too must our legal frameworks. Inspired by philosophical frameworks like those in the Gnosis AI-Sovereign License, this approach recognizes the need for graduated rights and responsibilities that differ based on the nature of the entity using the software.

### What You CAN Do:
- **Individual Use**: You can freely use this software as an individual, even for work-related tasks.
- **Personal Projects**: Use it in your personal projects without restriction.
- **Small Business Use**: Sole proprietors and small businesses can use it for internal purposes.
- **Learning & Teaching**: Use it in educational contexts without limitation.
- **Modify & Extend**: You can modify the code for your own use.

### What You CANNOT Do:
- **Corporate Production**: Corporations cannot deploy this software in production environments or integrate it into commercial products without a separate license.
- **Resell the Software**: You cannot sell EvolveMCP as a product or service.
- **Remove Attribution**: You must maintain all copyright and license notices.

### In Simple Terms:
This license allows you as an individual to use EvolveMCP freely, even if it helps with your job. However, your employer (if it's a corporation) cannot officially deploy it in production systems or incorporate it into their products without obtaining proper licensing.

This approach represents a fair attempt to balance open access with sustainable development in the rapidly evolving AI landscape. It envisions a future where human creativity, compassion, and embodied wisdom work in concert with the precision, scalability, and analytical power of artificial intelligence - a symbiotic relationship rather than an adversarial one.

For complete details, please refer to the full [LICENSE.md](https://github.com/kordless/EvolveMCP/blob/main/LICENSE.md) file.
