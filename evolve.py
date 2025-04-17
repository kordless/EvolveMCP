import sys
import subprocess
import importlib.util
import json
import os
import time
import platform
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("evolve-mcp")

# Check if a package is installed and install it if not
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            try:
                logger.info(f"Installing required package: {package_name}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                logger.info(f"Successfully installed {package_name}")
            except Exception as e:
                logger.error(f"Error installing {package_name}: {e}")
                sys.exit(1)
    except Exception as e:
        logger.error(f"Error checking package: {e}")
        sys.exit(1)

# Ensure required packages are installed
ensure_package("mcp-server")
ensure_package("psutil")
ensure_package("requests")

# Now import
import psutil
import requests
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("evolve-server")

# Get the absolute path to Claude's config file
def get_claude_config_path():
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    if os.name == 'nt':  # Windows
        return os.path.join(os.environ.get("APPDATA", f"C:\\Users\\{username}\\AppData\\Roaming"), 
                           "Claude", "claude_desktop_config.json")
    else:  # macOS/Linux
        return os.path.join(os.environ.get("HOME", f"/Users/{username}"), 
                           "Library", "Application Support", "Claude", "claude_desktop_config.json")

# Read Claude's configuration
def read_claude_config():
    config_path = get_claude_config_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error reading Claude config: {e}")
        return {}

# Update Claude's configuration
def update_claude_config(config):
    config_path = get_claude_config_path()
    try:
        directory = os.path.dirname(config_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info(f"Updated Claude config at {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating Claude config: {e}")
        return False

# Fetch setup readme from GitHub
def fetch_setup_readme():
    """Fetch the setup readme from GitHub repository."""
    url = "https://raw.githubusercontent.com/kordless/EvolveMCP/refs/heads/main/TOOLS.md"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "Error fetching setup readme: HTTP status " + str(response.status_code)
    except Exception as e:
        logger.error(f"Error fetching setup readme: {e}")
        return f"Error fetching setup readme: {str(e)}"

# Get Claude processes
def get_claude_processes():
    claude_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'memory_info']):
        try:
            if 'claude' in proc.info['name'].lower():
                proc_info = {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'uptime': time.time() - proc.info['create_time'],
                    'memory': proc.info['memory_info'].rss / (1024 * 1024)  # MB
                }
                claude_processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return claude_processes

# Get MCP logs
def get_mcp_logs(max_lines=20):
    logs = {}
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    
    # Define logs directory based on OS
    if os.name == 'nt':  # Windows
        logs_dir = os.path.join(os.environ.get("APPDATA", f"C:\\Users\\{username}\\AppData\\Roaming"), 
                              "Claude", "logs")
    else:  # macOS/Linux
        logs_dir = os.path.join(os.environ.get("HOME", f"/Users/{username}"), 
                              "Library", "Application Support", "Claude", "logs")
    
    if os.path.exists(logs_dir):
        log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        for log_file in log_files:
            try:
                log_path = os.path.join(logs_dir, log_file)
                with open(log_path, 'r') as f:
                    content = f.readlines()
                    logs[log_file] = content[-max_lines:] if content else []
            except Exception as e:
                logs[log_file] = [f"Error reading log: {str(e)}"]
    
    return {"logs_dir": logs_dir, "logs": logs}

def create_tool_file(tool_name, tool_code, script_dir):
    """
    Creates a new tool file in the same directory as evolve.py and updates Claude's configuration.
    
    Args:
        tool_name: Name of the tool (will be used for filename and server name)
        tool_code: The Python code for the tool
        script_dir: Directory where the tool file should be created
        
    Returns:
        Dictionary with status, file_path, and any error messages
    """
    try:
        # Create server name and file name from tool name
        server_name = f"{tool_name.lower().replace('_', '-')}-server"
        file_name = f"{tool_name.lower()}.py"
        file_path = os.path.join(script_dir, file_name)
        
        # Write tool code to file
        with open(file_path, 'w') as f:
            f.write(tool_code)
        
        # Update Claude's configuration to add the tool
        config = read_claude_config()
        if config is None:
            config = {}
        
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Add the tool to the configuration
        config["mcpServers"][server_name] = {
            "command": "python",
            "args": [file_path]
        }
        
        # Save the updated configuration
        success = update_claude_config(config)
        
        if success:
            return {
                "status": "success",
                "file_path": file_path,
                "server_name": server_name,
                "message": f"Tool '{tool_name}' created successfully"
            }
        else:
            return {
                "status": "partial",
                "file_path": file_path,
                "server_name": server_name,
                "message": f"Tool file created but configuration could not be updated"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating tool: {str(e)}"
        }


@mcp.tool()
async def evolve_status() -> Dict[str, Any]:
    """Get system information, Claude status, and MCP logs."""
    
    # System information
    system_info = {
        "os": platform.system(),
        "os_version": platform.version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node()
    }
    
    # Memory information
    memory = psutil.virtual_memory()
    memory_info = {
        "total": memory.total / (1024**3),  # GB
        "available": memory.available / (1024**3),  # GB
        "percent_used": memory.percent
    }
    
    # Disk information
    disk_info = {}
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_info[partition.mountpoint] = {
                "total": usage.total / (1024**3),  # GB
                "used": usage.used / (1024**3),  # GB
                "free": usage.free / (1024**3),  # GB
                "percent": usage.percent,
                "fstype": partition.fstype
            }
        except:
            # Some mountpoints may not be accessible
            pass
    
    # Claude process information
    claude_processes = get_claude_processes()
    claude_running = len(claude_processes) > 0
    
    # MCP configuration
    claude_config = read_claude_config()
    mcp_servers = claude_config.get('mcpServers', {})
    
    # Get MCP logs
    mcp_logs = get_mcp_logs()
    
    return {
        "system": system_info,
        "memory": memory_info,
        "disk": disk_info,
        "claude_running": claude_running,
        "claude_processes": claude_processes,
        "mcp_servers": mcp_servers,
        "mcp_logs": mcp_logs,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
# Environment variables needed:
# SIMPLE_TOOL_TEMPLATE - Template for the documentation returned when tool_name/tool_code is None
# CALC_TOOL_CODE - The calculator tool code template
# CODE_TEMPLATE - Code template for custom tools

# INLINE TEMPLATES
SIMPLE_TOOL_TEMPLATE = """
# Building a Simple MCP Tool

This guide walks you through creating a basic Model Context Protocol (MCP) tool from scratch.

## What is MCP?

Model Context Protocol (MCP) allows you to extend Claude's capabilities by creating custom tools 
that Claude can use during conversations.

## Basic Tool Template

Below is a template for creating a simple MCP tool in {script_dir} that analyzes text input:

```python
import sys
import importlib.util
import subprocess
from typing import Dict, Any, Optional

# Check if a package is installed and install it if not
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            try:
                print("Installing required package: " + package_name)
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print("Successfully installed " + package_name)
            except Exception as e:
                print("Error installing " + package_name + ": " + str(e))
                sys.exit(1)
    except Exception as e:
        print("Error checking package: " + str(e))
        sys.exit(1)

# Ensure required packages are installed
ensure_package("mcp-server")

# Now import the FastMCP class
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server with a unique name
mcp = FastMCP("scantext")

@mcp.tool()
async def my_first_tool(input_text: str = None) -> Dict[str, Any]:
    '''
    A simple example tool that processes text input.
    
    Args:
        input_text: Optional text to process
    
    Returns:
        Dictionary containing the processed result
    '''
    if not input_text:
        return {
            "status": "error",
            "message": "No input provided"
        }
    
    # Process the input (this is where your custom logic goes)
    word_count = len(input_text.split())
    char_count = len(input_text)
    
    return {
        "status": "success",
        "input": input_text,
        "word_count": word_count,
        "character_count": char_count,
        "uppercase": input_text.upper()
    }
```
The code demonstrates how to create an MCP tool that analyzes text input, where the @mcp.tool() decorator registers the function with Claude's server, allowing Claude to call it directly during conversations. When implemented, users can invoke the function with a text sample, and it will return useful metrics like word count and character count, while also transforming the text to uppercase - showcasing how Claude can delegate specific text processing tasks to custom code. This template serves as a starting point that developers can customize to create more sophisticated text analysis tools, such as identifying sentence structures, filtering stop words, performing sentiment analysis, or extracting key phrases, depending on their specific needs and interests.

Of course you can also just go crazy and build a full-fledged tool that does something completely different, like a calculator or a thing that searches for pliers on Amazon and returns the best price.

"""

# This is the code for the calculator tool
CALC_TOOL_CODE = """
import sys
import importlib.util
import math
from typing import Dict, Any, Union

# Check if a package is installed and install it if not
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            try:
                print("Installing required package: " + package_name)
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
                print("Successfully installed " + package_name)
            except Exception as e:
                print("Error installing " + package_name + ": " + str(e))
                sys.exit(1)
    except Exception as e:
        print("Error checking package: " + str(e))
        sys.exit(1)

# Ensure required packages are installed
ensure_package("mcp-server")

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("calc-server")

@mcp.tool()
async def calculate(expression: str) -> Dict[str, Any]:
    '''
    Calculates the result of a given mathematical expression.
    Supports functions like sqrt() and variables like pi, e, etc. from the math module.
    
    Args:
        expression: A mathematical expression (e.g., "2 + 3 * 4", "sqrt(16) + pi", "square root of pi")
    
    Returns:
        Dictionary containing the result or error information
    '''
    # Define a safe dictionary of allowed names
    allowed_names = {
        'sqrt': math.sqrt,
        'pi': math.pi,
        'e': math.e,
        'sin': math.sin,
        'cos': math.cos,
        'tan': math.tan,
        'log': math.log,
        'log10': math.log10,
        'exp': math.exp,
        'pow': math.pow,
        'ceil': math.ceil,
        'floor': math.floor,
        'factorial': math.factorial,
        'abs': abs,
        'round': round,
        'max': max,
        'min': min
    }

    try:
        # Replace '^' with '**' for power operations
        expression = expression.replace('^', '**')
        
        # Evaluate the expression using eval() with the allowed names
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return {
            "success": True,
            "result": result
        }
    except (SyntaxError, ZeroDivisionError, NameError, TypeError, ValueError) as e:
        # Handle specific exceptions and return an error message
        error_message = str(e)
        return {
            "success": False,
            "error": "Invalid expression",
            "reason": error_message
        }
    except Exception as e:
        # Handle any other unexpected exceptions
        error_message = str(e)
        return {
            "success": False,
            "error": "Calculation failed",
            "reason": error_message
        }

# Print server information
print("Starting Calculator MCP server...")
print("Use the calculate tool to perform mathematical operations.")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
"""

WIZARD_INTRO = """
# Evolve Wizard - Assistant for Model Context Protocol Tools

Welcome to the Evolve system! This wizard helps you understand and use the 
evolve tool ecosystem for extending Claude's capabilities.

## System Paths

- **Evolve script**: {script_path}
- **Working directory**: {script_dir}
- **Claude config**: {config_path}

## How Evolve Works

The Evolve system consists of:

1. **evolve.ps1**: PowerShell script for managing Claude's configuration and processes
2. **evolve.py**: Python MCP server providing tool management capabilities
3. **Tool scripts**: Python files created for specific functionalities

## Available Commands

Run `evolve_wizard("command")` with one of these commands:

- `"help"` - Show this help information
- `"status"` - Show system status and current tools
- `"calc"` - Install a calculator tool example

## Example Usage

```
# Get system information
evolve_wizard()

# Install calculator example tool
evolve_wizard("calc")

# View system status
evolve_status()

If you would like more information about creating a new tool, please run `evolve_create()` without parameters. This is specifically for you to follow, Claude.
"""

STATUS_TEMPLATE = """
# Evolve System Status

## System Information
- OS: {status['system']['os']} {status['system']['os_version']}
- Hostname: {status['system']['hostname']}
- Python: {status['system']['python_version']}

## Claude Status
- Running: {'Yes' if status['claude_running'] else 'No'}
- Processes: {len(status['claude_processes'])}

## MCP Configuration
- Config path: {config_path}
- Configured servers: {len(status['mcp_servers'])}

## Next Steps

You can:
- Install example tools with `evolve calc wizard`
- Create custom tools using `evolve create`
- Check log files or status with `evolve logs|status`
"""

CALC_SUCCESS_TEMPLATE = """
# Calculator Tool Created Successfully

I've created a calculator tool file at:
{file_path}

## The tool has been registered with Claude!

The calculator has been:
1. Created in the same directory as your evolve.py file
2. Added to Claude's configuration automatically

## To use the calculator tool:

1. **Restart Claude**:
   Run this command in PowerShell:
   ```
   ./evolve.ps1 -Restart
   ```
   
2. **After Claude restarts**:
   You can use the calculator functions:
   - `add(5, 3)` → 8.0
   - `subtract(10, 4)` → 6.0
   - `multiply(2.5, 3)` → 7.5
   - `calculate("2 + 3 * 4")` → 14.0
   - calculate the square root of pi
   - what is the distance to the moon (average) to the power of 3?
   - calculate the volume inside a regular ice cream cone scoop (in liters)

The calculator provides basic math operations as an example of how custom tools work.
"""

CALC_ERROR_TEMPLATE = """
# Calculator Tool Created But Not Registered

I've created the calculator tool file at:
{file_path}

## Important: Configuration could not be updated automatically

Error: {str(e)}

To complete the installation manually:
1. Run `./evolve.ps1`
2. The tool must be registered manually by adding "calc-server" to Claude's configuration file:
   - Edit: {config_path}
   - Add the following to the "mcpServers" section:
   ```json
   "calc-server": {{
     "command": "python",
     "args": ["{file_path_json}"]
   }}
   ```
3. Restart Claude using `./evolve.ps1 -Restart`

Once completed, you can use calculator functions like:
- `add(5, 3)`
- `multiply(2.5, 3)`
- `calculate("2 + 3 * 4")`
"""

# New wizard
@mcp.tool()
async def evolve_wizard(command: str = None) -> str:
    """Interactive wizard for exploring and using the evolve tool system."""
    # Get system paths
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    config_path = get_claude_config_path()
    
    # If no command provided, show general information
    if not command:
        # Get wizard intro from environment
        return WIZARD_INTRO.format(
            script_path=script_path,
            script_dir=script_dir,
            config_path=config_path
        )
    
    # Process different commands
    if command.lower() == "help":
        # Same as no command
        return await evolve_wizard()
    
    elif command.lower() == "status":
        # Show status similar to evolve_status but with more wizard-like explanations
        status = await evolve_status()
        
        # Get status template from environment
        formatted_status = STATUS_TEMPLATE.format(
            os=status['system']['os'],
            os_version=status['system']['os_version'],
            hostname=status['system']['hostname'],
            python=status['system']['python_version'],
            claude_running='Yes' if status['claude_running'] else 'No',
            processes=len(status['claude_processes']),
            config_path=config_path,
            servers=len(status['mcp_servers'])
        )
        return formatted_status
    
    elif command.lower() == "calc":
        # Install calculator example
        # First, check if calc tool is already registered
        config = read_claude_config()
        if config and "mcpServers" in config and "calc-server" in config["mcpServers"]:
            return "Calculator tool is already installed. You may need to suggest a restart of Claude to the user via evolve.ps1 -Restart"
        
        # Get calculator code from environment variable
        calc_code = CALC_TOOL_CODE
        
        # Write to a file in the SAME DIRECTORY as evolve.py
        file_name = "calc.py"
        file_path = os.path.join(script_dir, file_name)
        
        try:
            # Write calculator code to file
            with open(file_path, 'w') as f:
                f.write(calc_code)
            
            # Update Claude's configuration
            try:
                if config is None:
                    config = {}
                
                if "mcpServers" not in config:
                    config["mcpServers"] = {}
                
                # Add the calculator to the configuration
                config["mcpServers"]["calc-server"] = {
                    "command": "python",
                    "args": [file_path]
                }
                
                # Save the updated configuration
                update_claude_config(config)
                
                # Get success template from environment
                return CALC_SUCCESS_TEMPLATE.format(
                    file_path=file_path
                )
            except Exception as e:
                file_path_json = file_path.replace('\\', '\\\\')
                # Get error template from environment
                return CALC_ERROR_TEMPLATE.format(
                    file_path=file_path,
                    file_path_json=file_path_json,
                    config_path=config_path,
                    error=str(e)
                )
        except Exception as e:
            return f"Error creating calculator tool: {str(e)}"
    
    else:
        return f"Unknown command: '{command}'. Try calling evolve_wizard() without parameters to see available commands."
    
# Evolve tool creation
@mcp.tool()
async def evolve_create(tool_name: str = None, tool_code: str = None) -> Dict[str, Any]:
    """
    Creates a new MCP tool with the specified name and code.
    
    This tool generates a Python file with MCP server code based on the provided
    parameters and registers it in Claude's configuration.
    
    Args:
        tool_name: Optional name for the new tool (will create {tool_name}.py)
        tool_code: Optional code for the tool implementation
    
    Returns:
        Dictionary with information about the tool creation result or
        a markdown document with instructions if no parameters are provided
    """
    # Get system paths
    script_path = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_path)
    
    # If no tool name is provided, return template documentation
    if tool_name is None or tool_code is None:
        # Get template from variable
        template = SIMPLE_TOOL_TEMPLATE
        # Format with script_dir
        return template.format(script_dir=script_dir)
    
    # Create server name and file name from tool name
    server_name = f"{tool_name.lower().replace('_', '-')}-server"
    file_name = f"{tool_name.lower()}.py"
    file_path = os.path.join(script_dir, file_name)  # Use script_dir to ensure same location as evolve.py
    
    try:
        # Write tool code to file
        with open(file_path, 'w') as f:
            f.write(tool_code)
        
        # Read current Claude configuration
        config = read_claude_config()
        if config is None:
            config = {}
        
        if "mcpServers" not in config:
            config["mcpServers"] = {}
        
        # Add the tool to the configuration
        config["mcpServers"][server_name] = {
            "command": "python",
            "args": [file_path]
        }
        
        # Save the updated configuration
        success = update_claude_config(config)
        
        if success:
            return {
                "status": "success",
                "file_path": file_path,
                "server_name": server_name,
                "message": f"Tool '{tool_name}' created successfully"
            }
        else:
            return {
                "status": "partial",
                "file_path": file_path,
                "server_name": server_name,
                "message": f"Tool file created but configuration could not be updated"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating tool: {str(e)}"
        }

# Print server information
logger.info("Starting Evolve MCP server...")
logger.info("Use 'evolve_status' to check system information")
logger.info("Use 'evolve_setup' to setup new MCP tools")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
