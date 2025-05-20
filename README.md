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

## Creating Your Own Tools

Gnosis Evolve allows you to create custom tools that extend Claude's capabilities. Here's how to create a simple tool:

### Tool Creation Process

1. **Design your tool**: Decide what functionality you want to add to Claude.
2. **Write the Python code**: Create a new Python file with your tool's code.
3. **Install the tool**: Use Claude to install your new tool.
4. **Restart Claude**: Restart Claude to load your new tool.
5. **Use your tool**: Ask Claude to use your newly created tool.

### Example 1: Hello World Tool

Let's create a basic "hello world" tool that returns a personalized greeting:

```python
import sys
import os
import logging
from typing import Dict, Any

# Configure logging
current_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(current_dir, "hello_tool.log"))]
)
logger = logging.getLogger("hello_tool")

# Import MCP after ensuring it's installed
from mcp.server.fastmcp import FastMCP

# Create MCP server with a unique name
mcp = FastMCP("hello-world-server")

@mcp.tool()
async def hello_world(name: str = "World") -> Dict[str, Any]:
    '''
    Returns a personalized greeting message.
    
    Args:
        name: The name to greet (default: "World")
        
    Returns:
        A dictionary with the greeting message
    '''
    try:
        message = f"Hello, {name}! The current time is {__import__('datetime').datetime.now()}"
        logger.info(f"Generated greeting: {message}")
        return {
            "success": True,
            "message": message
        }
    except Exception as e:
        logger.error(f"Error generating greeting: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to generate greeting: {str(e)}"
        }

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
```

### Example 2: Quote Generator Tool

Here's a more useful tool that fetches and returns random inspirational quotes:

```python
import sys
import os
import logging
import random
import json
from typing import Dict, Any, List, Optional

# Configure logging
current_dir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(current_dir, "quote_generator.log"))]
)
logger = logging.getLogger("quote_generator")

# Import MCP
from mcp.server.fastmcp import FastMCP

# Create MCP server with a unique name
mcp = FastMCP("quote-generator-server")

# Sample quotes database
QUOTES = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Life is what happens when you're busy making other plans.", "author": "John Lennon"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"text": "The only limit to our realization of tomorrow is our doubts of today.", "author": "Franklin D. Roosevelt"},
    {"text": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "Don't judge each day by the harvest you reap but by the seeds that you plant.", "author": "Robert Louis Stevenson"},
    {"text": "The journey of a thousand miles begins with one step.", "author": "Lao Tzu"},
    {"text": "Always remember that you are absolutely unique. Just like everyone else.", "author": "Margaret Mead"},
    {"text": "The best time to plant a tree was 20 years ago. The second best time is now.", "author": "Chinese Proverb"}
]

@mcp.tool()
async def get_random_quote(category: Optional[str] = None) -> Dict[str, Any]:
    '''
    Returns a random inspirational quote.
    
    Args:
        category: Optional category filter (not implemented in this basic version)
        
    Returns:
        A dictionary with a random quote and its author
    '''
    try:
        # In a real implementation, you might filter by category
        # For this example, we'll just select a random quote from our list
        quote = random.choice(QUOTES)
        
        logger.info(f"Selected quote: {quote['text']} - {quote['author']}")
        
        return {
            "success": True,
            "quote": quote['text'],
            "author": quote['author']
        }
    except Exception as e:
        logger.error(f"Error generating quote: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to generate quote: {str(e)}"
        }

@mcp.tool()
async def add_quote(text: str, author: str) -> Dict[str, Any]:
    '''
    Adds a new quote to the quotes collection.
    
    Args:
        text: The quote text
        author: The quote author
        
    Returns:
        A dictionary with success status
    '''
    try:
        # Validate input
        if not text or not author:
            return {
                "success": False,
                "error": "Both quote text and author must be provided"
            }
        
        # Add quote to the collection
        new_quote = {"text": text, "author": author}
        QUOTES.append(new_quote)
        
        logger.info(f"Added new quote: {text} - {author}")
        
        return {
            "success": True,
            "message": "Quote added successfully",
            "quote": new_quote
        }
    except Exception as e:
        logger.error(f"Error adding quote: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to add quote: {str(e)}"
        }

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
```

### Installing Your Custom Tool

1. **Ask Claude to install your tool**:
   ```
   Please create a new tool called "hello_tool" with the code I've provided.
   ```

2. **Claude will use the `evolve_tool` function**:
   ```
   evolve_tool("hello_tool", tool_code="...")
   ```

3. **Restart Claude**:
   ```bash
   # Windows
   .\evolve.ps1 -Restart

   # macOS
   ./evolve.sh --restart
   ```

4. **Use your new tool**:
   ```
   Claude, can you use the hello_tool to greet me by name?
   ```

### Tool Structure Guidelines

- **Imports**: Include necessary imports at the top.
- **Logging**: Configure logging to a file, not to stdout.
- **MCP Server**: Create an MCP server with a unique name.
- **Tool Functions**: Define functions with the `@mcp.tool()` decorator.
- **Documentation**: Include descriptive docstrings for each function.
- **Error Handling**: Add try-except blocks for robustness.
- **Return Format**: Return dictionaries with at least a success indicator.

### Tool Development Best Practices

1. **Start Small**: Begin with simple tools to understand the process before building complex ones.

2. **Test Locally**: Before installing the tool, test your Python code locally to ensure it works as expected.

3. **Documentation**: Include detailed docstrings and comments to make your tool easy to understand and use.

4. **Error Handling**: Implement comprehensive error handling to make your tool robust.

5. **Useful Return Values**: Return informative data that Claude can present to the user.

6. **Security Considerations**: 
   - Avoid executing arbitrary user input directly
   - Validate all inputs and parameters
   - Limit file system access to what's necessary
   - Be cautious with network connections to external services

7. **Resource Management**: Close files, network connections, and other resources properly.

8. **Versioning**: Include a version number in your tool to track changes.

### Tool Interaction Patterns

Claude can use your custom tools in various ways:

1. **Direct Calls**: Claude can call your tool directly with specific parameters.
   ```
   I'll use the quote generator to find an inspirational quote for you!
   ```

2. **Conversational Interaction**: Claude can process user requests and determine when to use your tool.
   ```
   User: "I need some inspiration today."
   Claude: "Let me find an inspirational quote for you..." (uses quote_generator tool)
   ```

3. **Multi-Tool Workflows**: Claude can combine multiple tools to solve complex tasks.
   ```
   User: "Create a personalized greeting with an inspirational quote."
   Claude: (uses both hello_tool and quote_generator tools to create a combined response)
   ```

4. **Tool Discovery**: Claude can suggest your tool when relevant to the conversation.
   ```
   User: "Do you have any features that can help me when I'm feeling down?"
   Claude: "I can offer inspirational quotes using the quote generator tool..."
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

Gnosis Evolve allows Claude to execute Python code on your system. Review generated code before running in sensitive environments. See [SECURITY.md](SECURITY.md) for comprehensive security guidance.

## License

Gnosis Evolve uses the Sovereign v1.1 license:
- **Free for individuals** and small businesses
- **Requires licensing** for corporate production use

See [LICENSE.md](https://github.com/kordless/gnosis-evolve/blob/main/LICENSE.md) for details.
