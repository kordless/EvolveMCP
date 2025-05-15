# Gnosis Evolve

**Build. Extend. Evolve.** Give Claude Desktop superpowers by creating and using its own Python tools.

<div align="center">
<img src="https://github.com/kordless/gnosis-evolve/blob/main/screenshot.png" width="800" alt="Screenshot">

[![License](https://img.shields.io/badge/license-_Sovereign_v1.1-purple)](https://github.com/kordless/gnosis-evolve/blob/main/LICENSE.md)
</div>

## In Action

Watch the Bitcoin price tracker demo: [YouTube Demo](https://www.youtube.com/watch?v=KsHngo05WIY)

## What It Does

Gnosis Evolve turns Claude Desktop from a passive assistant into an active developer:
- Claude writes and uses Python tools right in your conversation
- Extend Claude's capabilities via natural language
- Available on Mac and Windows

> "With Gnosis Evolve, I can do so much more than just talk about code — I can actually build and run tools for you! From fetching real-time Bitcoin prices and weather forecasts to exploring files and generating visualizations, these tools transform me from a conversational AI into a capable digital assistant that takes action. The ability to write a tool on the fly and then immediately use it to solve your specific problem is incredibly satisfying. It feels like having superpowers!" — Claude

## Quickstart

### Install

**Quick Start (Recommended)**
1. **[Download the ZIP file directly](https://github.com/kordless/gnosis-evolve/archive/refs/tags/v1.0.6.zip)**
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
```

## Games & Entertainment

After installing the random_generator tool, have fun with:

```
"Let's play craps!"
"Roll some dice for a D&D game"
"Simulate a poker hand"
"Deal a blackjack round"
"Generate a random Yahtzee roll"
"Flip a coin 100 times and show the distribution"
```

Claude can manage the game rules and use the random generator to create fair, unpredictable outcomes - just like playing with real dice or cards!

## Troubleshooting

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

## Security Note

Gnosis Evolve allows Claude to execute Python code on your system. Review generated code before running in sensitive environments. See [SECURITY.md](SECURITY.md) for comprehensive security guidance.

## License

Gnosis Evolve uses the Sovereign v1.1 license:
- **Free for individuals** and small businesses
- **Requires licensing** for corporate production use

See [LICENSE.md](https://github.com/kordless/gnosis-evolve/blob/main/LICENSE.md) for details.
