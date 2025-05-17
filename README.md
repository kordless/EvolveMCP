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
1. **[Download the ZIP file directly](https://github.com/kordless/gnosis-evolve/archive/refs/tags/v1.0.7.zip)**
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
"Cast an I Ching hexagram reading"
```

Claude can manage the game rules and use the random generator to create fair, unpredictable outcomes - just like playing with real dice or cards!

### I Ching Divination

The random_generator tool can be used to simulate I Ching readings:

```
"Cast an I Ching hexagram for my question about [your question]"
```

Claude will:
1. Generate random coin tosses to build a hexagram
2. Identify the primary and changing hexagrams
3. Provide an interpretation relevant to your question

## Evolving Your Own Tools

Gnosis Evolve's true power lies in having Claude create custom tools on demand through natural conversation. No need to write any code yourself—let Claude do the work!

### Tool Creation Process

1. **Describe your idea**: Tell Claude what you'd like the tool to do.
2. **Let Claude write the code**: Claude will generate appropriate Python code for the tool.
3. **Ask Claude to install it**: Claude will install the tool using the evolve_tool function.
4. **Restart Claude**: Restart Claude to activate your new tool.
5. **Use your new tool**: Ask Claude to use the tool in your conversation.

### Example 1: Creating a Hello World Tool

Instead of writing code yourself, simply ask Claude to create a tool:

```
Me: "Can you create a simple hello world tool that greets me with my name and shows the current time?"

Claude: "I'd be happy to create that tool for you! I'll write a simple tool that greets you by name and displays the current time."

[Claude writes the necessary Python code]

Claude: "I've created a hello_tool that can greet you by name with the current time. Would you like me to install it now?"

Me: "Yes, please install it."

[Claude installs the tool]

Claude: "The hello_tool has been installed! To activate it, please restart Claude using:
Windows: .\evolve.ps1 -Restart
macOS: ./evolve.sh --restart"

[After restarting Claude]

Me: "Can you greet me using the hello_tool? My name is Sarah."

Claude: "I'll use the hello_tool to greet you!
Hello, Sarah! The current time is 2025-05-17 12:15:32"
```

### Example 2: Creating a Quote Generator

For more complex tools, the process is just as seamless:

```
Me: "I'd like a tool that can give me random inspirational quotes and let me add my own quotes to the collection."

Claude: "That sounds great! I'll create a quote generator tool with two functions: one to retrieve random quotes and another to add new quotes to the collection."

[Claude writes the necessary Python code]

Claude: "I've created a quote_generator tool that can provide random inspirational quotes and allow you to add your own quotes. Should I install it for you?"

Me: "Yes, please install it."

[Claude installs the tool]

Claude: "The quote_generator has been installed! Please restart Claude to activate it."

[After restarting Claude]

Me: "Can I have an inspirational quote?"

Claude: "Here's an inspirational quote for you:
'The future belongs to those who believe in the beauty of their dreams.' - Eleanor Roosevelt"

Me: "I'd like to add my own quote: 'Every moment is a fresh beginning.' by T.S. Eliot"

Claude: "I've added your quote to the collection! 'Every moment is a fresh beginning.' by T.S. Eliot has been saved."
```

### What Types of Tools Can Claude Create?

1. **System Utilities**:
   - File browsers and managers
   - Status checkers
   - System monitors

2. **Data Tools**:
   - Data formatters and converters
   - Simple analyzers and calculators
   - Random generators

3. **Web Integrations**:
   - Weather information retrieval
   - Web content scrapers
   - API connectors

4. **Creative Tools**:
   - Character generators
   - Story assistants
   - Game helpers

5. **Productivity Tools**:
   - Task trackers
   - Note takers
   - Email formatters

### Tool Design Guidelines

When asking Claude to create a tool, consider these elements:

1. **Clear Purpose**: Define exactly what you want the tool to do.

2. **Input Parameters**: Specify what information the tool should accept.

3. **Output Format**: Describe what results you expect from the tool.

4. **Error Handling**: Consider potential issues and how they should be handled.

5. **Security Considerations**: Be mindful of file system access and network connections.

You don't need to worry about the implementation details—Claude will handle the code structure, logging, and proper MCP integration.

### Best Practices for Using Evolved Tools

1. **Start Simple**: Begin with basic tools before requesting complex functionality.

2. **Be Specific**: Clearly describe the tool's purpose and expected behavior.

3. **Test Thoroughly**: After installation, test the tool with various inputs to ensure it works as expected.

4. **Combine Tools**: Ask Claude to use multiple tools together to create more complex workflows.

5. **Iterative Development**: If a tool doesn't work perfectly, ask Claude to improve it based on your feedback.

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
