# Tool Development Guide

Learn how to create custom tools that extend Claude's capabilities in Gnosis Evolve.

## Tool Creation Process

1. **Design your tool**: Decide what functionality you want to add to Claude.
2. **Write the Python code**: Create a new Python file with your tool's code.
3. **Install the tool**: Use Claude to install your new tool.
4. **Restart Claude**: Restart Claude to load your new tool.
5. **Use your tool**: Ask Claude to use your newly created tool.

## Example 1: Hello World Tool

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

## Example 2: Quote Generator Tool

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

## Installing Your Custom Tool

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
   .\evolve.ps1 -StartClaude

   # macOS
   ./evolve.sh --restart
   ```

4. **Use your new tool**:
   ```
   Claude, can you use the hello_tool to greet me by name?
   ```

## Tool Structure Guidelines

- **Imports**: Include necessary imports at the top.
- **Logging**: Configure logging to a file, not to stdout.
- **MCP Server**: Create an MCP server with a unique name.
- **Tool Functions**: Define functions with the `@mcp.tool()` decorator.
- **Documentation**: Include descriptive docstrings for each function.
- **Error Handling**: Add try-except blocks for robustness.
- **Return Format**: Return dictionaries with at least a success indicator.

## Tool Development Best Practices

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

## Tool Interaction Patterns

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

## Advanced Tool Features

### Multi-Function Tools

You can create tools with multiple related functions:

```python
@mcp.tool()
async def create_task(title: str, description: str) -> Dict[str, Any]:
    # Create a new task
    pass

@mcp.tool()
async def list_tasks() -> Dict[str, Any]:
    # List all tasks
    pass

@mcp.tool()
async def complete_task(task_id: int) -> Dict[str, Any]:
    # Mark a task as complete
    pass
```

### Database Integration

Tools can connect to databases for persistent storage:

```python
import sqlite3

@mcp.tool()
async def save_data(key: str, value: str) -> Dict[str, Any]:
    try:
        conn = sqlite3.connect('tool_data.db')
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS data (key TEXT PRIMARY KEY, value TEXT)')
        cursor.execute('INSERT OR REPLACE INTO data (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Data saved"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### External API Integration

Tools can integrate with external APIs:

```python
import httpx

@mcp.tool()
async def get_weather(city: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://api.weather.com/v1/current?city={city}")
            data = response.json()
            return {"success": True, "weather": data}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Debugging Tools

### Logging Best Practices

```python
import logging
import os

# Set up logging with rotation
from logging.handlers import RotatingFileHandler

def setup_logging(tool_name: str):
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    handler = RotatingFileHandler(
        os.path.join(log_dir, f'{tool_name}.log'),
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[handler]
    )
    
    return logging.getLogger(tool_name)
```

### Error Reporting

```python
@mcp.tool()
async def example_tool(param: str) -> Dict[str, Any]:
    try:
        # Tool logic here
        result = process_data(param)
        logger.info(f"Successfully processed: {param}")
        return {"success": True, "result": result}
    except ValueError as e:
        logger.error(f"Invalid parameter: {param}, error: {str(e)}")
        return {
            "success": False, 
            "error": "Invalid input parameter",
            "details": str(e)
        }
    except Exception as e:
        logger.exception(f"Unexpected error processing {param}")
        return {
            "success": False,
            "error": "An unexpected error occurred",
            "details": str(e)
        }
```

## Publishing and Sharing Tools

### Tool Documentation Template

Create a README for your tool:

```markdown
# My Awesome Tool

## Description
Brief description of what your tool does.

## Installation
```bash
# Install via Claude
"Please install the my_awesome_tool from the code I'm providing"
```

## Usage Examples
```
"Use my awesome tool to process this data"
"Generate a report using my awesome tool"
```

## Functions Available
- `function_name(param1, param2)` - Description of what it does
- `another_function()` - Description

## Requirements
- Python packages needed
- External services required
- File permissions needed
```

### Contributing to Gnosis Evolve

If you create a useful tool, consider contributing it back to the community:

1. Test your tool thoroughly
2. Add comprehensive documentation
3. Follow the coding standards
4. Submit a pull request with your tool in the `contrib_tools/` directory

## Troubleshooting Tool Development

### Common Issues

1. **Import Errors**: Make sure all required packages are installed
2. **MCP Server Name Conflicts**: Use unique server names
3. **Logging Issues**: Ensure log directories exist and are writable
4. **Function Signature Problems**: Check parameter types and return values

### Testing Tools Locally

Before installing a tool in Claude, test it locally:

```bash
# Test your tool directly
python my_tool.py

# Check for syntax errors
python -m py_compile my_tool.py

# Test specific functions
python -c "import my_tool; print(my_tool.my_function('test'))"
```

### Performance Considerations

- **Async Functions**: Use async/await for I/O operations
- **Resource Cleanup**: Always close files, connections, etc.
- **Memory Usage**: Be mindful of large data structures
- **Timeout Handling**: Set reasonable timeouts for external calls

## Next Steps

1. **Start with simple tools** to get familiar with the process
2. **Explore existing tools** in the `tools/` directory for inspiration
3. **Join the community** to share your creations and get help
4. **Contribute back** by sharing useful tools you create

Happy tool building! 🛠️