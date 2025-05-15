# Gnosis Evolve

**Build. Extend. Evolve.** Give Claude Desktop superpowers by creating and using its own Python tools.

<div align="center">
<img src="https://github.com/kordless/gnosis-evolve/blob/main/price.png" width="250" alt="Bitcoin Price Tracker">

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

**Windows**
```powershell
# Clone the repo
git clone https://github.com/kordless/gnosis-evolve.git
cd gnosis-evolve

# Setup
.\evolve.ps1 -Setup
```

**macOS**
```bash
# Clone the repo
git clone https://github.com/kordless/gnosis-evolve.git
cd gnosis-evolve

# Setup
chmod +x ./evolve.sh
./evolve.sh --setup
```

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

Gnosis Evolve allows Claude to execute Python code on your system. Review generated code before running in sensitive environments. [Full security details](#security-implications).

## License

Gnosis Evolve uses the Sovereign v1.1 license:
- **Free for individuals** and small businesses
- **Requires licensing** for corporate production use

See [LICENSE.md](https://github.com/kordless/gnosis-evolve/blob/main/LICENSE.md) for details.

---

### Security Implications

1. **Code Execution Risk**: Any code that runs on your computer has access to your system at the same permission level as the user running it.

2. **Review Generated Code**: While Claude aims to create safe tools, review any code it generates before running it in a sensitive environment.

3. **Recommended Precautions**:
   - Run in a dedicated user account with limited permissions
   - Backup important data before using new tools
   - Consider using a virtual machine for additional isolation
   - Keep your security software up to date
