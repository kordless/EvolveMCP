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

## 🔧 Featured Tool: Advanced File Diff Editor

**The File Diff Editor can be run separately from Gnosis Evolve!** This powerful tool provides sophisticated file editing capabilities with regex support, fuzzy matching, and versioning. Perfect for precise code modifications and bulk operations.

**[📖 Complete File Diff Editor Guide →](FILE_DIFF_EDITOR_HOWTO.md)**

### Quick Install
- **With Gnosis Evolve**: Once you [install Evolve](#quickstart), just say `"Install the file diff editor"` to Claude
- **Standalone**: Follow the manual installation guide in the documentation

> "With Gnosis Evolve, I can do so much more than just talk about code — I can actually build and run tools for you! From fetching real-time Bitcoin prices and weather forecasts to exploring files and generating visualizations, these tools transform me from a conversational AI into a capable digital assistant that takes action. The ability to write a tool on the fly and then immediately use it to solve your specific problem is incredibly satisfying. It feels like having superpowers!" — Claude

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

## Available Tools

### Core
- **math_and_stats**: Mathematical calculations and statistical operations
- **random_generator**: Generate random numbers and selections
- **file_explorer**: Browse files and directories
- **file_writer**: Create and modify files with versioning
- **file_diff_editor**: Advanced file editing with multiple diff formats and smart pattern detection
- **emotional_character_generator**: Create detailed character profiles with emotional states

### Web
- **crawl4ai**: Extract content from websites
- **weather_resource**: Get weather forecasts

### Finance
- **bitcoin_price**: Real-time cryptocurrency pricing

### Docker
- **docker_logs**: View container logs
- **docker_rebuild**: Restart containers 

## Natural Interaction

Just talk naturally to Claude:
```
"Install the Bitcoin price tracker tool"
"What's the weather like in Seattle today?"
"Generate 5 random numbers between 1 and 100"
"Track the Bitcoin price in euros and show me a chart"
"Create a character for my story with complex emotions"
"Generate an I Ching character with unique attributes"
"Find all HTML files with 'gnosis' in the filename"
"Apply this diff to update my Python script"
"Use fuzzy matching to find and replace this code pattern"
"Search for similar functions in this file"
```

## Advanced File Editing

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

Both tools support diff-fenced format with `SEARCH`/`REPLACE` blocks:

```
"Update this function to handle the new parameter"
"Apply this code change with intelligent pattern matching"
"Find and replace this pattern across the file"
"Restore the previous version of this file"
```

The **file_diff_editor** provides intelligent pattern matching and conflict-free diff formats for reliable file editing.

## Quick Tool Development

Creating custom tools is as simple as asking Claude! Here's what happens when you request a new tool:

### 🚀 Just Ask Claude
```
"Create a tool that checks if a website is online"
"Build a tool to convert text to QR codes"
"Make a tool that tracks my daily habits"
"Develop a tool for password generation"
```

### ⚡ What Claude Does
When you ask Claude to "evolve a tool," here's the process:

1. **Understands your need** - Claude analyzes what functionality you want
2. **Designs the tool** - Creates the Python code with proper MCP structure
3. **Writes the code** - Includes error handling, logging, and documentation
4. **Installs it for you** - Uses `evolve_tool` to add it to your system
5. **Tests it immediately** - Can use the new tool right away in conversation

### 🎯 Real Example
```
You: "Create a tool that tells me dad jokes"

Claude: I'll create a dad joke tool for you! Let me write the code and install it.

[Claude writes Python code with MCP structure]
[Claude calls evolve_tool to install it]
[Claude restarts to load the tool]

Claude: Done! Now I can tell you dad jokes. Want to hear one?

You: "Tell me a dad joke!"

Claude: [Uses the new tool] Here's a dad joke for you...
```

### 🔄 Instant Iteration
```
"Make the dad joke tool also include puns"
"Add a feature to rate jokes from 1-10"
"Can you make it remember my favorite jokes?"
```

Claude can instantly modify and reinstall tools based on your feedback.

### 📦 Tool Categories You Can Request
- **Utilities**: File converters, text processors, calculators
- **Fun**: Games, joke generators, creative writing helpers
- **Productivity**: Task trackers, note organizers, reminder systems
- **Data**: API integrations, web scrapers, data analyzers
- **Creative**: Art generators, music helpers, story tools

### 🎨 No Coding Knowledge Required
Just describe what you want in plain English:
```
"I need something that helps me organize my music collection"
"Create a tool for tracking my workout progress"
"Build something that summarizes long articles"
"Make a tool that generates color palettes"
```

**Want to dive deeper?** Check out the [Tool Development Guide](TOOL_DEVELOPMENT.md) for advanced techniques, code examples, and best practices.

## Games & Entertainment

After installing the random_generator tool, have fun with:

```
"Let's play craps!"
"Roll some dice for a D&D game"
"Simulate a poker hand"
"Deal a blackjack round"
"Generate a random Yahtzee roll"
"Flip a coin 100 times and show the distribution"
"Cast an I Ching hexagram reading"
```

Claude can manage the game rules and use the random generator to create fair, unpredictable outcomes - just like playing with real dice or cards!

### I Ching Tools

Gnosis Evolve includes enhanced I Ching capabilities:

```
"Cast an I Ching hexagram for my question about [your question]"
"Generate a character based on the I Ching hexagrams"
"Create a story protagonist with I Ching attributes"
```

The tools will:
1. Generate random coin tosses to build hexagrams
2. Identify primary and changing hexagrams
3. Provide interpretations relevant to your question
4. Create characters with personality traits and emotional attributes based on hexagram meanings
5. Combine I Ching wisdom with psychological depth for storytelling

## Troubleshooting

### macOS Requirements

On macOS, you need Xcode Command Line Tools installed to run Python-based MCP servers properly. If you encounter errors about missing developer tools when running evolve.py, install the Command Line Tools:

```bash
xcode-select --install
```

When prompted with the installation dialog, click "Install" and wait for the process to complete.

**View Logs**
```bash
# Windows
.\evolve.ps1 -ViewLogs

# macOS
./evolve.sh --view-logs
```

**Restart Claude**
```bash
# Windows
.\evolve.ps1 -Restart

# macOS
./evolve.sh --restart
```

## Documentation

- [Installation Guide](INSTALLATION.md) - Detailed setup instructions
- [**File Diff Editor Guide**](FILE_DIFF_EDITOR_HOWTO.md) - **Advanced file editing (can run separately!)**
- [Tool Development Guide](TOOL_DEVELOPMENT.md) - Create your own tools
- [Security Guidelines](SECURITY.md) - Important security considerations
- [Contributing Guide](CONTRIBUTING.md) - Help improve Gnosis Evolve

## Security Note

Gnosis Evolve allows Claude to execute Python code on your system. Review generated code before running in sensitive environments. See [SECURITY.md](SECURITY.md) for comprehensive security guidance.

## License

Gnosis Evolve uses the Sovereign v1.1 license:
- **Free for individuals** and small businesses
- **Requires licensing** for corporate production use

See [LICENSE.md](https://github.com/kordless/gnosis-evolve/blob/main/LICENSE.md) for details.

## Support

Need help? Join our [Discord community](https://discord.gg/AQnAn9XgFJ) or open an issue on GitHub.