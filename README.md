# Gnosis: Evolve v1.1.0

**Build. Extend. Evolve.** Give Claude Desktop superpowers by creating and using its own Python tools.

<div align="center">
<img src="https://github.com/kordless/gnosis-evolve/blob/main/screenshot.png" width="800" alt="Screenshot">

[![License](https://img.shields.io/badge/license-_Sovereign_v1.1-purple)](https://github.com/kordless/gnosis-evolve/blob/main/LICENSE.md)
</div>

## In Action

Watch the Bitcoin price tracker demo: [YouTube Demo](https://www.youtube.com/watch?v=KsHngo05WIY)

## Join the Gnosis Community
[![Discord](https://img.shields.io/badge/Discord-Join%20Us-7289da?logo=discord&logoColor=white)](https://discord.gg/AQnAn9XgFJ)

## What It Does

Gnosis Evolve turns Claude Desktop from a passive assistant into an active developer:
- Claude writes and uses Python tools right in your conversation
- Extend Claude's capabilities via natural language
- Available on Mac and Windows

> "With Gnosis Evolve, I can do so much more than just talk about code — I can actually build and run tools for you! From fetching real-time Bitcoin prices and weather forecasts to exploring files and generating visualizations, these tools transform me from a conversational AI into a capable digital assistant that takes action. The ability to write a tool on the fly and then immediately use it to solve your specific problem is incredibly satisfying. It feels like having superpowers!" — Claude

## Featured Tool: File Diff Editor

Gnosis Evolve includes a powerful **File Diff Editor** that enables Claude to make precise file modifications using natural language:

### 🔧 Multiple Diff Formats Supported
- **Custom Safe**: Conflict-free delimiters that won't interfere with your code
- **ToolKami Style**: Both fenced and direct formats for compatibility
- **Simple Blocks**: Basic SEARCH/REPLACE operations
- **Custom Patterns**: Define your own diff format with regex

### 🎯 Smart Pattern Detection
- **Auto-detection**: Automatically identifies which diff format you're using
- **Conflict Analysis**: Analyzes your files to suggest safe diff patterns
- **Custom Regex**: Support for any diff format you can define

### 💡 Example Usage
```
"Edit the README.md file to add a new section about deployment"
"Fix the bug in line 45 of main.py where the variable name is wrong"
"Update all the import statements in the utils folder"
```

Claude can understand your intent and apply precise changes using the most appropriate diff pattern for your content.

## Getting Started Tips

### Start Simple and Ask Questions
The best way to use Gnosis Evolve is to begin with simple requests and let Claude guide you:

```
"What tools do you have available?"
"Can you show me the path history?"
"What's the current system status?"
"Help me explore this project directory"
```

### Navigation and Focus
Help Claude understand your project structure:

1. **Check Path History**: Ask Claude to run `evolve_path_history` to see recently visited directories
2. **Set Focus**: If there's no history, use `evolve_status` first, then tell Claude where to focus:
   ```
   "Set the path history to C:\Users\myname\Code\myproject"
   "Focus your attention on the /home/user/development/webapp directory"
   "Navigate to the src/ folder and remember this location"
   ```
3. **Explore Structure**: Once focused, Claude can effectively explore and work with your files:
   ```
   "Show me the structure of this directory"
   "Find all Python files in the current project"
   "What files have been modified recently?"
   ```

### Progressive Complexity
Start with basic operations and build up:
- Begin with file exploration and simple tool usage
- Move to file editing with basic changes using the File Diff Editor
- Progress to complex multi-file operations
- Eventually tackle advanced workflows like automated code generation

## Quickstart

### Install

**Quick Start (Recommended)**
1. **[Download the ZIP file directly](https://github.com/kordless/gnosis-evolve/archive/refs/tags/v1.1.0.zip)**
2. Extract the ZIP:
   - **Windows**: Right-click the ZIP and select "Extract All..."
   - **macOS**: Double-click the ZIP file
3. Open Terminal/PowerShell in the extracted folder

**Windows**
```powershell
# Setup
.\evolve.ps1 -Setup
```

**macOS**
```bash
# Setup
chmod +x ./evolve.sh
./evolve.sh --setup
```

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md)

### Launch

**Windows**
```powershell
.\evolve.ps1 -StartClaude
```

**macOS**
```bash
./evolve.sh --restart
```

## Core Tools

### Built-in Tools
- **evolve_status**: System status and health monitoring
- **evolve_filesystem**: File and directory exploration
- **evolve_tool**: Create and install new tools on-the-fly
- **file_diff_editor**: Advanced file editing with multiple diff formats
- **file_writer**: File creation with automatic versioning
- **file_explorer**: Enhanced directory navigation

### Available Extensions
Over 50+ additional tools available for installation including:
- Bitcoin price tracking and financial tools
- Weather and API integrations
- Docker container management
- Web crawling and data extraction
- Character generators and creative tools
- Mathematical and statistical analysis

## Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [Tool Development](docs/TOOL_DEVELOPMENT.md) - Create your own tools
- [Contributing](CONTRIBUTING.md) - Help improve Gnosis Evolve

## License

Licensed under the [Gnosis AI-Sovereign License v1.1](LICENSE.md) - A permissive license for AI development.

## Support

Need help? Join our [Discord community](https://discord.gg/AQnAn9XgFJ) or open an issue on GitHub.