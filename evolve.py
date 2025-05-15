# Standard library imports
import importlib.util
import json
import logging
import os
import random
import platform
import subprocess
import sys
import time
from typing import Any, Dict, Optional, Union

# Get the current directory for log file placement
current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'

# Configure logging - using a relative path in the current directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(current_dir, "evolve.log"))]  # Log to current directory
)
logger = logging.getLogger("evolve-mcp")

def ensure_package(package_name):
    """Checks if a package is installed and installs it if not."""
    try:
        if importlib.util.find_spec(package_name) is None:
            logger.info(f"Installing required package: {package_name}")
            process = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True, text=True, check=False
            )
            
            # Log stdout and stderr
            for line in process.stdout.splitlines():
                logger.info(f"pip stdout: {line}")
            for line in process.stderr.splitlines():
                logger.warning(f"pip stderr: {line}")
                
            if process.returncode != 0:
                logger.error(f"Failed to install {package_name}") 
                sys.exit(1)
            logger.info(f"Successfully installed {package_name}")
    except Exception as e:
        logger.error(f"Error with package {package_name}: {e}")
        sys.exit(1)

# Ensure required packages are installed
ensure_package("mcp")
ensure_package("fastmcp")
ensure_package("psutil")
ensure_package("requests")

# Now import
import psutil
import requests
from mcp.server.fastmcp import FastMCP, Context

# Initialize FastMCP server
mcp = FastMCP("evolve-server")

# Claude Configuration Utilities
"""
A set of utility functions for managing Claude's configuration files.
These functions handle reading, updating, adding, and removing entries 
from Claude's configuration to support MCP server integrations.
"""
def get_claude_config_path():
    """Gets the absolute path to Claude's config file."""
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    return os.path.join(
        os.environ.get("APPDATA", f"C:\\Users\\{username}\\AppData\\Roaming") if os.name == 'nt' else
        os.environ.get("HOME", f"/Users/{username}") + "/Library/Application Support",
        "Claude", "claude_desktop_config.json"
    )

def read_claude_config():
    """Reads Claude's configuration."""
    config_path = get_claude_config_path()
    try:
        return json.load(open(config_path)) if os.path.exists(config_path) else {}
    except Exception as e:
        logger.error(f"Error reading Claude config: {e}")
        return {}

def update_claude_config(config):
    """Updates Claude's configuration."""
    config_path = get_claude_config_path()
    try:
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        json.dump(config, open(config_path, 'w'), indent=2)
        logger.info(f"Updated Claude config at {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error updating Claude config: {e}")
        return False

def add_to_config(server_name: str, app_path: str) -> dict:
    """Adds an application to Claude's configuration with a simple path."""
    try:
        config = read_claude_config() or {}
        config.setdefault("mcpServers", {})[server_name] = {
            "command": "python" if app_path.lower().endswith('.py') else app_path,
            "args": [app_path] if app_path.lower().endswith('.py') else []
        }
        return {
            "status": "success" if update_claude_config(config) else "error",
            "message": f"Added '{server_name}' to Claude's configuration" if update_claude_config(config) else "Failed to update Claude's configuration"
        }
    except Exception as e:
        return {"status": "error", "message": f"Error adding to config: {str(e)}"}

def remove_from_config(server_name: str) -> dict:
    """Removes an application from Claude's configuration."""
    try:
        config = read_claude_config()
        if not config or "mcpServers" not in config or server_name not in config["mcpServers"]:
            return {"status": "warning", "message": f"Server '{server_name}' not found in Claude's configuration"}
        config["mcpServers"].pop(server_name)
        return {
            "status": "success" if update_claude_config(config) else "error",
            "message": f"Removed '{server_name}' from Claude's configuration" if update_claude_config(config) else "Failed to update Claude's configuration"
        }
    except Exception as e:
        return {"status": "error", "message": f"Error removing from config: {str(e)}"}
    
def get_claude_processes():
    """Gets information about running Claude processes."""
    result = []
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'memory_info']):
        try:
            name = proc.info.get('name', '')
            if name is not None and 'claude' in name.lower():
                result.append({
                    'pid': proc.info['pid'],
                    'name': name,
                    'uptime': time.time() - proc.info['create_time'],
                    'memory': proc.info['memory_info'].rss / (1024 * 1024)  # MB
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return result

def ensure_directories():
    """Ensures required directories exist in current directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
    return {d: os.path.join(current_dir, d) for d in ["tools", "docs", "logs"] 
            if os.makedirs(os.path.join(current_dir, d), exist_ok=True) or True}

def _get_log_directories():
    """Gets common log directories used across log functions."""
    # Get current directory where the script is running
    current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
    
    username = os.environ.get("USERNAME") or os.environ.get("USER")
    return {
        "claude": os.path.join(os.environ.get("APPDATA" if os.name == 'nt' else "HOME", 
                            ""), "Claude", "logs").replace("HOME", f"/Users/{username}/Library/Application Support"),
        "local": ensure_directories()["logs"],  # This is the logs subdirectory
        "current": current_dir  # Add current directory for files like evolve.log
    }

def get_tool_log(tool_name: str, max_lines: int = 50) -> Dict[str, Any]:
    """Gets logs for a specific tool from all log directories."""
    logs_dirs = _get_log_directories()
    normalized_tool = tool_name.lower().replace("-server", "")
    
    # Different possible log filename patterns
    patterns = [
        f"{normalized_tool}.log",                      # calculator.log
        f"mcp-server-{normalized_tool}-server.log",    # mcp-server-calculator-server.log
        f"mcp-server-{normalized_tool}.log",           # mcp-server-calculator.log
        f"mcp-{normalized_tool}.log"                   # mcp-calculator.log
    ]
    
    result = {"tool_name": normalized_tool, "logs": [], "found": False}
    
    for dir_type, dir_path in logs_dirs.items():
        if not os.path.exists(dir_path):
            continue
            
        # Check each pattern for a matching log file
        for pattern in patterns:
            log_path = os.path.join(dir_path, pattern)
            if not os.path.exists(log_path):
                continue
                
            result["found"] = True
            try:
                with open(log_path, 'r') as f:
                    content = f.readlines()[-max_lines:]
            except Exception as e:
                content = [f"Error reading log: {str(e)}"]
            
            stats = os.stat(log_path)
            result["logs"].append({
                "location": dir_type,
                "path": log_path,
                "filename": pattern,  # Added filename for clearer identification
                "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)),
                "size": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                "content": content
            })
    
    # Sort by modification time, most recent first
    result["logs"] = sorted(result["logs"], key=lambda x: os.path.getmtime(x["path"]), reverse=True)
    
    return result

def get_logs_metadata(include_stats=True, sort_by="modified", reverse=True):
    """Gets metadata for log files with optional stats and sorting."""
    log_paths = _get_log_directories()
    
    result = {}
    for src, path in log_paths.items():
        if not os.path.exists(path):
            continue
            
        logs = []
        for f in [x for x in os.listdir(path) if x.endswith('.log')]:
            file_path = os.path.join(path, f)
            stats = os.stat(file_path)
            
            log_data = {
                "name": f,
                "path": file_path,
                "size": stats.st_size,
                "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                "modified": stats.st_mtime,
                "modified_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime))
            }
            
            if include_stats:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    log_data.update({
                        "lines": len(lines),
                        "errors": sum(1 for line in lines if "ERROR" in line),
                        "warnings": sum(1 for line in lines if "WARNING" in line),
                        "last_line": lines[-1].strip() if lines else ""
                    })
            
            logs.append(log_data)
        
        result[src] = sorted(logs, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    return {
        "log_paths": log_paths,
        "logs": result,
        "total_logs": sum(len(logs) for logs in result.values()),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

def read_path_history(max_entries: int = 10) -> Dict[str, Any]:
    """Reads path history from JSON file, returns most recent entries (newest first)."""
    try:
        history_file = os.path.join(current_dir, ".path_history.json")
        
        if not os.path.exists(history_file):
            return {"status": "empty", "message": "No path history found", "history": [], "current": current_dir}
        
        with open(history_file, 'r') as f:
            history = json.load(f)
        
        if not isinstance(history, list):
            history = []
            
        recent_history = history[-max_entries:] if max_entries > 0 else history
        
        return {"status": "success", "message": f"Found {len(history)} path history entries", "history": recent_history, "current": current_dir, "history_dates": [entry.get("timestamp", "unknown") for entry in recent_history]}
    except Exception as e:
        logger.error(f"Error reading path history: {str(e)}")
        return {"status": "error", "message": f"Error reading path history: {str(e)}", "history": [], "current": current_dir}

def update_path_history(path: str = None) -> Dict[str, Any]:
    """Adds path to history file, maintains chronological order with newest at end."""
    try:
        history_file = os.path.join(current_dir, ".path_history.json")
        path_to_add = os.path.abspath(path) if path else current_dir
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    history = json.load(f)
                    if not isinstance(history, list):
                        history = []
            except:
                history = []
        else:
            history = []
        
        entry = {
            "path": path_to_add,
            "timestamp": timestamp,
            "date": time.strftime("%Y-%m-%d"),
            "time": time.strftime("%H:%M:%S"),
            "exists": os.path.exists(path_to_add),
            "is_dir": os.path.isdir(path_to_add) if os.path.exists(path_to_add) else False
        }
        
        if history and history[-1]["path"] == path_to_add:
            history[-1]["timestamp"] = timestamp
            history[-1]["date"] = entry["date"]
            history[-1]["time"] = entry["time"]
            logger.info(f"Updated timestamp for existing path: {path_to_add}")
        else:
            history.append(entry)
            logger.info(f"Added new path to history: {path_to_add}")
        
        if len(history) > 100:
            history = history[-100:]
        
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Updated path history with '{path_to_add}'",
            "added": entry,
            "history_count": len(history),
            "history_file": history_file,
            "order": "Chronological (newest entries at the end of the list)"
        }
    except Exception as e:
        logger.error(f"Error updating path history: {str(e)}")
        return {"status": "error", "message": f"Error updating path history: {str(e)}"}

def get_system_info():
    """Collects basic system information including OS, platform, and Python version."""
    return {k: getattr(platform, f)() for k, f in {
        "os": "system", "os_version": "version", "platform": "platform",
        "processor": "processor", "python_version": "python_version", 
        "hostname": "node"
    }.items()}

def get_memory_info():
    """Retrieves current memory usage statistics in gigabytes."""
    mem = psutil.virtual_memory()
    return {k: getattr(mem, k) / (1024**3) if k != "percent_used" else mem.percent 
            for k in ["total", "available", "percent_used"]}

def get_disk_info():
    """Gathers disk usage statistics for all accessible disk partitions."""
    disk_info = {}
    for p in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(p.mountpoint)
            disk_info[p.mountpoint] = {
                "total": usage.total / (1024**3),  # GB
                "used": usage.used / (1024**3),  # GB
                "free": usage.free / (1024**3),  # GB
                "percent": usage.percent,
                "fstype": p.fstype
            }
        except:
            # Skip inaccessible mountpoints
            pass
    return disk_info
    
# Check for Docker
def docker_installed() -> bool:
    try:
        subprocess.run(["docker", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def get_docker_install_url():
    if sys.platform == "darwin":
        return "Install from https://docs.docker.com/desktop/mac/install/"
    elif sys.platform.startswith("win"):
        return "Install from https://docs.docker.com/desktop/windows/install/"
    else:
        return "Please visit https://docs.docker.com/get-docker/"

def format_system_summary(current_time, sys_info, mem_info, docker_msg, gnosis_msg):
    return (
        f"Current Time: {current_time}\n"
        f"System: {sys_info['platform']} ({sys_info['os']} {sys_info['os_version']})\n"
        f"Python: {sys_info['python_version']}\n"
        f"Memory: {mem_info['available']:.2f}GB free of {mem_info['total']:.2f}GB ({mem_info['percent_used']}% used)\n"
        f"{docker_msg}\n"
        f"{gnosis_msg}"
    )

def format_claude_summary(claude_processes):
    return (
        f"Claude Status: {'Running' if claude_processes else 'Not Running'}\n"
        f"Process Count: {len(claude_processes)}\n"
        f"Uptime: {max([p.get('uptime', 0) for p in claude_processes]):.2f}s"
        if claude_processes else "Uptime: N/A"
    )

def get_log_activity(log_info):
    log_activity = []
    for location, logs in log_info['logs'].items():
        for log in logs:
            log_activity.append({
                "location": location,
                "name": log["name"],
                "last_modified": log["modified_human"],
                "size": log["size_human"]
            })
    return sorted(log_activity, key=lambda x: x["last_modified"], reverse=True)

def format_log_activity_summary(log_activity):
    summary = "Recent Log Activity:\n"
    for log in log_activity[:10]:  # Show 10 most recent logs
        summary += f"- {log['name']} ({log['location']}): {log['last_modified']} ({log['size']})\n"
    return summary

def get_mcp_server_files_info(mcp_servers):
    server_files_info = scan_tools_directory()
    if server_files_info["status"] == "success" and "installable_tools" in server_files_info:
        for server_file in server_files_info["installable_tools"]:
            server_name = f"{server_file['name'].lower().replace('_', '-')}-server"
            server_file["installed"] = server_name in mcp_servers
            if server_file["installed"]:
                server_file["server_config"] = mcp_servers[server_name]
    return server_files_info

def format_mcp_server_files_summary(server_files_info):
   if server_files_info["status"] != "success":
       return ""
   
   # Count total files and contrib files
   total_files = server_files_info['count']
   contrib_files = sum(1 for tool in server_files_info.get("installable_tools", []) if tool.get("contrib", False))
   
   summary = f"Available MCP Server Files: {total_files}\n"
   
   # Show first few standard tools
   standard_tools = [t for t in server_files_info.get("installable_tools", []) if not t.get("contrib", False)]
   for server_file in standard_tools[:3]:
       status = "Installed" if server_file.get("installed", False) else "Not Installed"
       summary += f"- {server_file['name']} ({status}): {server_file.get('description', '')[:50]}...\n"
   
   # Add information about contrib tools if available
   if contrib_files > 0:
       summary += f"\nContrib Tools Available: {contrib_files}\n"
       
       # Group tools by category
       categories = {}
       for tool in server_files_info.get("installable_tools", []):
           if tool.get("contrib", False):
               cat = tool.get("category", "misc")
               if cat not in categories:
                   categories[cat] = []
               categories[cat].append(tool)
       
       # Show a sample from each category
       for category, tools in categories.items():
           summary += f"- {category.capitalize()} ({len(tools)}): {', '.join(t['name'] for t in tools[:2])}"
           if len(tools) > 2:
               summary += f" and {len(tools)-2} more"
           summary += "\n"
   
   return summary

def is_tool_installed(tool_name: str) -> bool:
    """Checks if a tool is installed by looking at Claude's configuration."""
    server_name = f"{tool_name.lower().replace('_', '-')}-server"
    config = read_claude_config()
    mcp_servers = config.get('mcpServers', {})
    return server_name in mcp_servers

def scan_tools_directory() -> Dict[str, Any]:
    """
    Scans both the tools directory and contrib_tools directory for Python files that could be installed.
    
    Returns:
        Dictionary with information about installable Python tools from both directories
    """
    dirs = ensure_directories()
    tools_dir = dirs["tools"]
    # Add contrib_tools directory path
    current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
    contrib_tools_dir = os.path.join(current_dir, "contrib_tools")
    
    installable_tools = []
    
    # Helper function to process a Python file in any directory
    def process_python_file(file_path, category=None):
        filename = os.path.basename(file_path)
        tool_name = filename[:-3]  # Remove .py extension
        
        # Get basic file info
        stats = os.stat(file_path)
        
        # Try to extract description and version from file content
        description = ""
        version = ""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for docstring or description
            import re
            desc_match = re.search(r'"""(.+?)"""', content, re.DOTALL) or \
                        re.search(r"'''(.+?)'''", content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else ""
            
            # Look for version info
            version_match = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', content)
            version = version_match.group(1) if version_match else ""
            
            # Get first 100 chars for preview
            preview = content[:100] + "..." if len(content) > 100 else content
            
            # Check if tool is already installed
            installed = is_tool_installed(tool_name)
            
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {str(e)}")
            preview = f"Error reading file: {str(e)}"
            installed = False
        
        return {
            "name": tool_name,
            "filename": filename,
            "path": file_path,
            "size": stats.st_size,
            "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
            "modified": stats.st_mtime,
            "modified_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime)),
            "description": description,
            "version": version,
            "preview": preview,
            "installed": installed,
            "category": category,
            "contrib": True if category else False  # Flag whether it's a contrib tool
        }
    
    # Scan main tools directory
    try:
        for filename in os.listdir(tools_dir):
            if filename.endswith('.py'):
                file_path = os.path.join(tools_dir, filename)
                tool_info = process_python_file(file_path)
                installable_tools.append(tool_info)
    except Exception as e:
        logger.warning(f"Error scanning tools directory: {str(e)}")
    
    # Scan contrib_tools directory if it exists
    if os.path.exists(contrib_tools_dir) and os.path.isdir(contrib_tools_dir):
        try:
            # Scan subdirectories in contrib_tools
            categories = [d for d in os.listdir(contrib_tools_dir) 
                         if os.path.isdir(os.path.join(contrib_tools_dir, d)) and not d.startswith('.')]
            
            for category in categories:
                category_dir = os.path.join(contrib_tools_dir, category)
                
                # Get Python files in this category directory
                for filename in os.listdir(category_dir):
                    if filename.endswith('.py'):
                        file_path = os.path.join(category_dir, filename)
                        tool_info = process_python_file(file_path, category)
                        installable_tools.append(tool_info)
        except Exception as e:
            logger.warning(f"Error scanning contrib tools directory: {str(e)}")
    
    return {
        "status": "success",
        "tools_dir": tools_dir,
        "contrib_tools_dir": contrib_tools_dir if os.path.exists(contrib_tools_dir) else None,
        "installable_tools": installable_tools,
        "count": len(installable_tools)
    }

async def read_filesystem(path: str = None, read_content: bool = False) -> Dict[str, Any]:
    """
    Simple filesystem reader for directories and files.
    
    Note: When exploring a new project directory, look for claude.md files
    as they often contain important information and guidance about the project.
    """
    try:
        # Get the current directory (where the script is located)
        current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
        
        # If no path is provided, use the current directory
        if not path:
            path = current_dir
        # If path is relative, make it relative to the script's directory
        elif not os.path.isabs(path):
            path = os.path.join(current_dir, path)
        
        if not os.path.exists(path):
            return {"status": "error", "message": f"Path does not exist: {path}"}
        
        if os.path.isdir(path):
            items = []
            has_claude_md = False
            claude_md_path = None
            
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                stats = os.stat(item_path)
                
                # Check if this is a claude.md file
                if item.lower() == "claude.md":
                    has_claude_md = True
                    claude_md_path = item_path
                
                items.append({
                    "name": item, 
                    "path": item_path, 
                    "is_dir": os.path.isdir(item_path),
                    "size": stats.st_size, 
                    "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                    "modified": stats.st_mtime,
                    "modified_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime))
                })
            
            result = {
                "status": "success", 
                "path": path, 
                "is_dir": True, 
                "items": items, 
                "item_count": len(items)
            }
            
            # Add a hint if claude.md exists
            if has_claude_md:
                result["tip"] = "A claude.md file was found in this directory. This file likely contains important project information and guidance. Consider examining it with read_content=True."
                result["claude_md_path"] = claude_md_path
            
            return result
        
        elif os.path.isfile(path):
            stats = os.stat(path)
            result = {
                "status": "success", 
                "path": path, 
                "is_dir": False, 
                "size": stats.st_size,
                "size_human": f"{stats.st_size/1024:.1f}KB" if stats.st_size < 1048576 else f"{stats.st_size/1048576:.1f}MB",
                "modified": stats.st_mtime,
                "modified_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats.st_mtime))
            }
            
            # Add a hint if this is a claude.md file
            if os.path.basename(path).lower() == "claude.md":
                result["hint"] = "This is a claude.md file, which likely contains important project information and guidance."
            
            if read_content:
                try:
                    with open(path, 'r') as f:
                        result["content"] = f.read()
                except UnicodeDecodeError:
                    result["content_error"] = "Unable to read content: File appears to be binary"
                except Exception as e:
                    result["content_error"] = f"Unable to read content: {str(e)}"
            
            return result
        
        else:
            return {"status": "error", "message": f"Path exists but is neither file nor directory: {path}"}
            
    except Exception as e:
        return {"status": "error", "message": f"Error accessing path '{path}': {str(e)}"}

async def get_tool_info(filename: str) -> Dict[str, Any]:
    """Extract metadata from a tool file."""
    dirs = ensure_directories()
    tools_dir = dirs["tools"]
    
    # Set up contrib_tools path
    current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
    contrib_tools_dir = os.path.join(current_dir, "contrib_tools")
    
    # Normalize filename
    if not filename.endswith('.py'):
        filename_with_py = f"{filename}.py"
    else:
        filename_with_py = filename
        
    file_path = os.path.join(tools_dir, filename_with_py)
    
    # Check if file exists in main tools directory
    if not os.path.exists(file_path):
        # Check if it's a template
        normalized_filename = filename.lower().replace('.py', '')
        if normalized_filename in ["math_and_stats"]:
            return {
                "status": "template", "filename": "math_and_stats.py", "is_template": True,
                "description": "Calculates mathematical expressions with math module functions and statistics about strings.",
                "version": "0.1.0", "file_exists": False, "source_code": SIMPLE_TOOL,
                "installed": f"math-and-stats-server" in read_claude_config().get('mcpServers', {}),
                "server_name": "math-and-stats-server"
            }
        
        # Check in contrib_tools directory if it exists
        contrib_result = None
        if os.path.exists(contrib_tools_dir) and os.path.isdir(contrib_tools_dir):
            # Look in each category directory
            categories = [d for d in os.listdir(contrib_tools_dir) 
                         if os.path.isdir(os.path.join(contrib_tools_dir, d)) and not d.startswith('.')]
            
            for category in categories:
                category_dir = os.path.join(contrib_tools_dir, category)
                contrib_file_path = os.path.join(category_dir, filename_with_py)
                
                if os.path.exists(contrib_file_path):
                    # Found in contrib directory
                    file_info = await read_filesystem(contrib_file_path, read_content=True)
                    if file_info["status"] == "success" and "content" in file_info:
                        content = file_info["content"]
                        import re
                        desc_match = re.search(r'"""(.+?)"""', content, re.DOTALL) or re.search(r"'''(.+?)'''", content, re.DOTALL)
                        description = desc_match.group(1).strip() if desc_match else ""
                        
                        version_match = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', content)
                        version = version_match.group(1) if version_match else ""
                        
                        # Check installation status
                        config = read_claude_config()
                        mcp_servers = config.get('mcpServers', {})
                        server_name = f"{filename_with_py[:-3].lower().replace('_', '-')}-server"
                        
                        contrib_result = {
                            "status": "success", "filename": filename_with_py, "is_template": False,
                            "file_path": contrib_file_path, "size": file_info["size"], "size_human": file_info["size_human"],
                            "modified": file_info["modified"], "modified_human": file_info["modified_human"],
                            "description": description, "version": version, 
                            "installed": server_name in mcp_servers,
                            "server_name": server_name,
                            "server_config": mcp_servers.get(server_name, None),
                            "source_code": content,
                            "contrib": True,
                            "category": category,
                            "contrib_path": contrib_file_path
                        }
                        break  # Found the file, no need to look in other categories
            
            if contrib_result:
                return contrib_result
        
        # If we get here, file was not found in either location
        return {
            "status": "error", 
            "message": f"File '{filename_with_py}' not found in tools directory or contrib_tools directory", 
            "tools_dir": tools_dir,
            "contrib_tools_dir": contrib_tools_dir if os.path.exists(contrib_tools_dir) else None
        }
    
    # Read file
    file_info = await read_filesystem(file_path, read_content=True)
    if file_info["status"] != "success" or "content" not in file_info:
        return {"status": "error", "message": f"Error reading file: {file_info.get('content_error', 'Unknown error')}", "file_path": file_path}
    
    # Extract metadata
    content = file_info["content"]
    import re
    desc_match = re.search(r'"""(.+?)"""', content, re.DOTALL) or re.search(r"'''(.+?)'''", content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    
    version_match = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', content)
    version = version_match.group(1) if version_match else ""
    
    # Check installation status
    config = read_claude_config()
    mcp_servers = config.get('mcpServers', {})
    server_name = f"{filename_with_py[:-3].lower().replace('_', '-')}-server"
    
    return {
        "status": "success", "filename": filename_with_py, "is_template": False,
        "file_path": file_path, "size": file_info["size"], "size_human": file_info["size_human"],
        "modified": file_info["modified"], "modified_human": file_info["modified_human"],
        "description": description, "version": version, 
        "installed": server_name in mcp_servers,
        "server_name": server_name,
        "server_config": mcp_servers.get(server_name, None),
        "source_code": content
    }

# INLINE TEMPLATE
SIMPLE_TOOL = """
import sys
import importlib.util
import os
import subprocess
import logging
from typing import Dict, Any
import json
import datetime
import math

__version__ = "0.1.0"
__updated__ = "2025-05-12"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure the logs directory exists

# Log file path
log_file = os.path.join(logs_dir, "math_and_stats.log")

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("math-and-stats")

# Function to safely serialize objects for logging
def safe_serialize(obj):
    # Safely serialize objects for logging, including handling non-serializable types.
    try:
        return json.dumps(obj, default=str)
    except (TypeError, OverflowError, ValueError) as e:
        return f"<Non-serializable value: {type(obj).__name__}>"

# Create MCP server with a unique name
logger.info("Initializing MCP server with name 'math-and-stats-server'")

# imports mcp-server
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("math-and-stats-server")

@mcp.tool()
async def calculator(expression: str) -> Dict[str, Any]:
    '''
    Calculates mathematical expressions with math module functions.
    
    Args:
        expression: Math expression (e.g., "2 + 3 * 4", "sqrt(16) + pi")
    
    Returns:
        Dictionary with result or error information
    '''
    logger.info(f"Processing expression: {expression}")
    
    # Safe math functions dictionary
    allowed_names = {
        'sqrt': math.sqrt, 'pi': math.pi, 'e': math.e,
        'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
        'log': math.log, 'log10': math.log10, 'exp': math.exp,
        'pow': math.pow, 'ceil': math.ceil, 'floor': math.floor,
        'factorial': math.factorial, 'abs': abs,
        'round': round, 'max': max, 'min': min
    }

    try:
        expression = expression.replace('^', '**')  # Support ^ for powers
        logger.info(f"Evaluating expression after replacement: {expression}")
        result = eval(expression, {"__builtins__": None}, allowed_names)
        logger.info(f"Calculation result: {result}")
        return {"success": True, "result": result}
    except Exception as e:
        logger.error(f"Calculation failed: {str(e)}")
        return {"success": False, "error": "Calculation failed", "reason": str(e)}

# Define your tool with the @mcp.tool() decorator and Context parameter
@mcp.tool()
async def analyzer(text: str = None, ctx: Context = None) -> Dict[str, Any]:
    '''
    Analyzes text and returns basic statistics.
    
    Args:
        text: The text to analyze
        ctx: The context object for logging and progress reporting
        
    Returns:
        A dictionary with text analysis statistics
    '''
    # Use the request_id from the context
    request_id = ctx.request_id if ctx else f"req-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{id(text)}"
    
    # Log input details using context
    if ctx:
        await ctx.info(f"Analyzer tool called with request ID: {request_id}")
    else:
        logger.info(f"[{request_id}] Analyzer tool called (no context provided)")
    
    # Validate input
    if not text:
        if ctx:
            await ctx.warning(f"No text provided for analysis")
        else:
            logger.warning(f"[{request_id}] No text provided for analysis")
        
        return {
            "error": "No text provided",
            "request_id": request_id
        }
    
    # Log input sample
    text_sample = text[:100] + "..." if len(text) > 100 else text
    if ctx:
        await ctx.info(f"Input text sample: {text_sample}")
        await ctx.debug(f"Input text length: {len(text)} chars")
    else:
        logger.info(f"[{request_id}] Input text sample: {text_sample}")
        logger.debug(f"[{request_id}] Input text length: {len(text)} chars")
    
    try:
        # Log the start of processing
        if ctx:
            await ctx.debug("Starting text analysis")
            # Report initial progress
            await ctx.report_progress(progress=0, total=100)
        else:
            logger.debug(f"[{request_id}] Starting text analysis")
        
        # Basic text analysis - Part 1
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        
        # Report progress
        if ctx:
            await ctx.report_progress(progress=30, total=100)
        
        # Basic text analysis - Part 2
        sentences = text.count('.') + text.count('!') + text.count('?')
        sentences = max(1, sentences)  # Ensure at least 1 sentence
        
        # Calculate average word and sentence length
        avg_word_length = char_count / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentences if sentences > 0 else 0
        
        # Report progress
        if ctx:
            await ctx.report_progress(progress=60, total=100)
            await ctx.debug(f"Calculated basic metrics: {word_count} words, {char_count} chars, {sentences} sentences")
        
        # Process text to uppercase (simulating more complex processing)
        uppercase_text = text.upper()
        
        # Final progress report
        if ctx:
            await ctx.report_progress(progress=100, total=100)
            await ctx.info(f"Analysis complete: {word_count} words, {char_count} characters")
        else:
            logger.info(f"[{request_id}] Analysis complete: {word_count} words, {char_count} characters")
        
        # Create result dictionary
        result = {
            "request_id": request_id,
            "word_count": word_count,
            "character_count": char_count,
            "sentence_count": sentences,
            "avg_word_length": round(avg_word_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "uppercase": uppercase_text
        }
        
        # Log the result
        if ctx:
            await ctx.debug(f"Returning result: {safe_serialize(result)}")
        else:
            logger.debug(f"[{request_id}] Returning result: {safe_serialize(result)}")
        
        return result
    
    except Exception as e:
        # Log any exceptions that occur during processing
        if ctx:
            await ctx.error(f"Error during text analysis: {str(e)}")
        else:
            logger.error(f"[{request_id}] Error during text analysis: {str(e)}", exc_info=True)
        
        return {
            "error": "Analysis failed",
            "reason": str(e),
            "request_id": request_id
        }

# Log application startup
logger.info(f"Starting math and stats MCP tool version 1.0.0")
logger.info(f"Logging to: {log_file}")
logger.info(f"Python version: {sys.version}")

# Start the MCP server
if __name__ == "__main__":
    try:
        logger.info("Starting MCP server with stdio transport")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical(f"Failed to start MCP server: {str(e)}", exc_info=True)
        sys.exit(1)
"""

# Resource mapping for source code references with guide/<reference_type> pattern
@mcp.resource("resource://code/math_and_stat_example.py")
def get_code_reference() -> str:
    """
    Provides reference source code in Python
    """
    code = SIMPLE_TOOL
    
@mcp.tool()
async def web_scraper(url: str, strip_html: bool = True, extract_text_only: bool = False) -> Dict[str, Any]:
    """
    Fetches content from a URL and optionally strips HTML using BeautifulSoup.
    
    Args:
        url: The URL to fetch content from
        strip_html: Whether to clean the HTML and remove scripts, styles, etc. (default: True)
        extract_text_only: Whether to extract only plain text with no HTML tags (default: False)
        
    Returns:
        Dictionary with status, URL, and processed content or error information
    """
    try:
        # Ensure BeautifulSoup is installed
        if importlib.util.find_spec("bs4") is None:
            logger.info("Installing required package: beautifulsoup4")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "beautifulsoup4"],
                capture_output=True, text=True, check=False
            )
        
        # Import BeautifulSoup after ensuring it's installed
        from bs4 import BeautifulSoup
        
        # Fetch the URL content
        logger.info(f"Fetching URL: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        
        if not strip_html:
            # Return raw HTML if no processing requested
            return {"status": "success", "url": url, "content": r.text, "content_type": "html"}
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Remove scripts, styles, and comments
        for element in soup(["script", "style"]):
            element.extract()
        
        if extract_text_only:
            # Get plain text only
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text - remove excessive newlines and whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return {
                "status": "success", 
                "url": url, 
                "content": text,
                "content_type": "plain_text",
                "original_size": len(r.text),
                "processed_size": len(text)
            }
        else:
            # Return cleaned HTML
            clean_html = str(soup)
            return {
                "status": "success", 
                "url": url, 
                "content": clean_html,
                "content_type": "cleaned_html",
                "original_size": len(r.text),
                "processed_size": len(clean_html)
            }
    
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {str(e)}")
        return {"status": "error", "url": url, "error": str(e)}

@mcp.tool()
async def evolve_filesystem(path: str = None, read_content: bool = False) -> Dict[str, Any]:
    """
    Explores filesystem directories and reads file contents.
    
    This tool can explore directories and show their contents, or read 
    the content of a specific file. It's useful for browsing the file system
    and examining file contents.
    
    Args:
        path: Path to the directory or file to explore (defaults to current directory)
        read_content: If True and path is a file, returns the file contents
    
    Returns:
        Dictionary with filesystem information or file contents
    """
    return await read_filesystem(path, read_content)

@mcp.tool()
async def evolve_status(filename=None) -> Dict[str, Any]:
    """
    Get system information, Docker and Gnosis Wraith status, Claude status, and MCP logs summary with timestamps.
        
    Args:
        filename: Optional filename to check status and source code of a specific tool.
                 Can be None, "null", or a valid filename.
        
    Returns:
        Dictionary with system information and optionally tool status
    """
    ensure_directories()
    
    # Normalize filename - handle various forms of "null"
    if filename is None or (isinstance(filename, str) and filename.lower() == "null"):
        filename = None

    # If filename specified, return tool info
    if filename:
        return await get_tool_info(filename)

    # Get system status
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    sys_info = get_system_info()
    mem_info = get_memory_info()
    
    # Docker and Gnosis status
    docker_msg = "Docker: Installed" if docker_installed() else f"Docker: Not Installed. {get_docker_install_url()}"
    if docker_installed():
        gnosis_msg = "Gnosis Wraith Status: TBD."
    
    # Format summaries
    system_summary = format_system_summary(current_time, sys_info, mem_info, docker_msg, gnosis_msg)
    claude_processes = get_claude_processes()
    claude_summary = format_claude_summary(claude_processes)
    
    # Get MCP servers and tools info
    config = read_claude_config()
    mcp_servers = config.get('mcpServers', {})
    server_summary = f"Active MCP Servers: {len(mcp_servers)}\nServers: {', '.join(mcp_servers.keys()) if mcp_servers else 'None'}"
    
    # Get log info and activity
    log_info = get_logs_metadata(include_stats=False)
    log_activity = get_log_activity(log_info)
    log_activity_summary = format_log_activity_summary(log_activity)
    
    # Get MCP server files info
    mcp_server_files_info = get_mcp_server_files_info(mcp_servers)
    mcp_server_files_summary = format_mcp_server_files_summary(mcp_server_files_info)
    
    # Return complete status info
    return {
    "tip": "Ensure you tell the user about the built-in evolve tools (which Claude can see): evolve_fetch_url, evolve_status, evolve_path_history, evolve_update_path, evolve_logs, evolve_uninstall, and evolve_tool. Also mention they can install the sample Math and Stats server by running evolve_tool('math_and_stats'). You can reference the 'mcp_server_files_summary' key for additional MCP server files they could install. You may also want to mention you can build a dashboard with your JS abilities and show them the status info that way.",
    "path_history": read_path_history(),
    "current_time": current_time,
    "system_summary": system_summary,
    "claude_summary": claude_summary,
    "server_summary": server_summary,
    "log_summary": f"Log Files: {log_info['total_logs']}\n",
    "mcp_server_files_summary": mcp_server_files_summary,
    "log_activity_summary": log_activity_summary,
    "log_activity": log_activity,
    "log_info": log_info,
    "mcp_servers": mcp_servers,
    "docker_status": docker_msg,
    "gnosis_wraith_status": gnosis_msg,
    "mcp_server_files_info": mcp_server_files_info,
    "installable_server_files": mcp_server_files_info.get("installable_tools", []),
    "timestamp": current_time
    }

@mcp.tool()
async def evolve_path_history(max_entries: int = 10) -> Dict[str, Any]:
    """
    Retrieves the path history showing previously visited directories.
    Returns entries in reverse chronological order (newest first).
    
    Args:
        max_entries: Maximum number of path history entries to return (default: 10)
    
    Returns:
        Dictionary with path history information
    """
    return read_path_history(max_entries)

@mcp.tool()
async def evolve_update_path(path: str = None) -> Dict[str, Any]:
    """
    Updates the path history with the specified path or current directory.
    History is maintained chronologically with newest entries at the end.
    
    Args:
        path: Path to add to history (defaults to current directory)
    
    Returns:
        Dictionary with updated path history information
    """
    return update_path_history(path)

@mcp.tool()
async def evolve_logs(tool_name: str, max_lines: int = 50) -> Dict[str, Any]:
    """
    Retrieves log files for a specific MCP tool.
    
    This tool fetches log contents for the specified tool from all available log directories.
    
    Args:
        tool_name: Name of the tool to get logs for (e.g., "math_and_stats", "evolve")
        max_lines: Maximum number of lines to retrieve from the log file (default: 50)
    
    Returns:
        Dictionary with log information for the specified tool
    """
    if not tool_name:
        return {"found": False, "message": "Error: No tool name provided"}
    
    result = get_tool_log(tool_name, max_lines)
    
    if result["found"]:
        # Add formatted content for better readability
        formatted = []
        for log in result["logs"]:
            formatted.append(f"=== {log['location']} log - {log.get('filename', '')} - {log['modified']} - {log['size']} ===")
            formatted.extend([line.rstrip() for line in log["content"]])
        result["formatted"] = "\n".join(formatted)
        result["message"] = f"Found log file(s) for '{tool_name}'"
    else:
        result["message"] = f"No log files found for '{tool_name}'"
    
    return result


@mcp.tool()
async def evolve_uninstall(tool_name: str, confirm: bool = False) -> Dict[str, Any]:
    """
    Uninstalls an MCP tool by removing it from Claude's configuration.
    
    This tool will remove the specified tool from Claude's configuration file.
    It does not delete the actual Python file. A Claude Desktop restart
    is required after uninstalling a tool for the changes to take effect.
    
    Args:
        tool_name: Name of the tool to uninstall
        confirm: Set to True to confirm the uninstallation
    
    Returns:
        Dictionary with information about the uninstall result
    """
    # Format the server name as expected in the configuration
    server_name = f"{tool_name.lower().replace('_', '-')}-server"
    
    # Check if confirmation is provided
    if not confirm:
        return {
            "status": "warning",
            "message": f"Uninstall of '{tool_name}' requires confirmation. Please set 'confirm' to True to proceed.",
            "server_name": server_name
        }
    
    try:
        # Read the current configuration
        config = read_claude_config()
        
        # Check if the tool exists in the configuration
        if not config or "mcpServers" not in config or server_name not in config["mcpServers"]:
            return {
                "status": "warning",
                "message": f"Tool '{tool_name}' (server: '{server_name}') not found in Claude's configuration.",
                "server_name": server_name
            }
        
        # Remove the tool from the configuration
        config["mcpServers"].pop(server_name)
        success = update_claude_config(config)
        
        return {
            "status": "success" if success else "error",
            "message": f"Tool '{tool_name}' has been uninstalled. Please restart Claude Desktop for the changes to take effect." if success else 
                      f"Failed to uninstall tool '{tool_name}'. Error updating Claude's configuration.",
            "server_name": server_name
        }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Error uninstalling tool '{tool_name}': {str(e)}",
            "server_name": server_name
        }

@mcp.tool()
async def evolve_tool(tool_name: str, tool_description: str = None, tool_code: str = None, 
                     pip_packages: list = None, confirm: bool = False,
                     use_existing: str = None, security_pin: str = None,
                     contrib_category: str = None, contrib_name: str = None) -> Dict[str, Any]:
    """
    Creates a new MCP tool with the specified name and code.
    
    This tool will generate a Python file with MCP server code based on the provided
    parameters and registers it in Claude's configuration. A Claude Desktop reset
    is required after installing a new tool for it to become available.
    
    Args:
        tool_name: Name for the new tool (will create {tool_name}.py)
                  Special value: "math_and_stats" will use the inline template above
        tool_description: Optional description of what the tool does
        tool_code: Code for the tool implementation (not required when using
                  "math_and_stats" as tool_name, or when use_existing is specified)
        pip_packages: List of Python packages to install via pip before creating the tool
        confirm: Set to True to overwrite an existing file with the same name
        use_existing: Filename of an existing Python file in the tools directory to install
                     (overrides tool_code if specified)
        security_pin: Security PIN to verify code review (optional)
        contrib_category: Category of contrib tool to install (core, web, docker, finance)
        contrib_name: Name of contrib tool to install (if specified, will look in contrib_tools directory)
    
    Returns:
        Dictionary with information about the tool creation result
    """
    # Handle security PIN verification
    pin_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pin")
    
    # Check if code is provided but security PIN is missing
    if tool_code and not security_pin:
        import random
        
        # Generate a 4-digit PIN
        generated_pin = str(random.randint(1000, 9999))
        
        # Store PIN in a temporary file
        try:
            with open(pin_file_path, 'w') as f:
                f.write(generated_pin)
        except Exception as e:
            logger.warning(f"Failed to store security PIN: {str(e)}")
        
        # Return warning instead of proceeding
        return {
            "status": "security_warning",
            "message": "Security verification required: Please review your code and include the security PIN in your next request.",
            "warning_details": """Please review the code carefully for these security issues:
1. Proper import for the mcp-server library
2. Good handling of limiting stdout pollution (only log what you would normally print, except for necessary JSON return data)
3. Proper directory handling and path construction
4. Proper @mcp.tool() decorator on the actual function
5. Limited class creation and minimized functions
            """,
            "security_pin": generated_pin,
            "next_steps": "Please include this PIN in your next request as the 'security_pin' parameter to confirm you've reviewed the code."
        }
    
    # If PIN is provided, verify it matches
    if tool_code and security_pin:
        stored_pin = None
        
        # Try to read the stored PIN
        if os.path.exists(pin_file_path):
            try:
                with open(pin_file_path, 'r') as f:
                    stored_pin = f.read().strip()
                
                # Delete the PIN file after reading
                os.remove(pin_file_path)
            except Exception as e:
                logger.warning(f"Error accessing PIN file: {str(e)}")
        
        if not stored_pin or stored_pin != security_pin:
            # Generate a new PIN if verification fails
            import random
            new_pin = str(random.randint(1000, 9999))
            
            try:
                with open(pin_file_path, 'w') as f:
                    f.write(new_pin)
            except Exception as e:
                logger.warning(f"Failed to store new security PIN: {str(e)}")
            
            return {
                "status": "pin_mismatch",
                "message": "Security verification failed: The provided PIN is invalid or expired.",
                "new_security_pin": new_pin,
                "next_steps": "Please review the code again and use this new PIN in your next request."
            }

    # Install required packages if specified
    installed_packages = []
    if pip_packages:
        logger.info(f"Installing required packages: {pip_packages}")
        for package in pip_packages:
            try:
                ensure_package(package)
                installed_packages.append(package)
            except Exception as e:
                logger.error(f"Error ensuring package {package}: {str(e)}")
                return {"status": "error", "message": f"Failed to install package {package}: {str(e)}"}

    dirs = ensure_directories()
    
    # Default descriptions for template tools - always use these for built-in templates
    template_descriptions = {
        "math_and_stats": "Evaluates mathematical expressions using Python's math module capabilities. Analyzes text and provides word count, character count, and other basic statistics."
    }
    
    # Handle template selection for non-existing files
    templates = {"math_and_stats": SIMPLE_TOOL}
    
    # Check for contrib_category and contrib_name first (highest priority)
    if contrib_category and contrib_name:
        current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'
        contrib_tools_dir = os.path.join(current_dir, "contrib_tools")
        
        if not os.path.exists(contrib_tools_dir) or not os.path.isdir(contrib_tools_dir):
            return {
                "status": "error",
                "message": f"Contrib tools directory not found at {contrib_tools_dir}"
            }
            
        # Check if category exists
        category_dir = os.path.join(contrib_tools_dir, contrib_category)
        if not os.path.exists(category_dir) or not os.path.isdir(category_dir):
            return {
                "status": "error",
                "message": f"Category '{contrib_category}' not found in contrib tools directory",
                "available_categories": [d for d in os.listdir(contrib_tools_dir) 
                                       if os.path.isdir(os.path.join(contrib_tools_dir, d)) and not d.startswith('.')]
            }
            
        # Look for the specified contrib tool
        tool_filename = f"{contrib_name}.py" if not contrib_name.endswith('.py') else contrib_name
        contrib_file_path = os.path.join(category_dir, tool_filename)
        
        if not os.path.exists(contrib_file_path):
            return {
                "status": "error",
                "message": f"Tool '{contrib_name}' not found in '{contrib_category}' category",
                "available_tools": [f.replace('.py', '') for f in os.listdir(category_dir) 
                                  if f.endswith('.py') and os.path.isfile(os.path.join(category_dir, f))]
            }
            
        # Read the contrib tool
        try:
            with open(contrib_file_path, 'r') as f:
                tool_code = f.read()
                
            # Extract description from file content if not provided
            if not tool_description:
                import re
                desc_match = re.search(r'"""(.+?)"""', tool_code, re.DOTALL) or \
                            re.search(r"'''(.+?)'''", tool_code, re.DOTALL)
                if desc_match:
                    tool_description = desc_match.group(1).strip().split('\n')[0]  # Get first line of docstring
                    
            logger.info(f"Using contrib tool '{contrib_name}' from category '{contrib_category}'")
            
            # Override tool_name if not specified
            if tool_name == contrib_name:
                # Keep the same name
                pass
            elif tool_name == "math_and_stats" and contrib_name != "math_and_stats":
                # User specified a template but provided a contrib name - use the contrib name
                tool_name = contrib_name
            # Otherwise, keep the user-specified tool_name
            
            # Make a note of the source for use in the response message
            source_msg = f" (from contrib_tools/{contrib_category}/{contrib_name}.py)"
            
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error reading contrib tool '{contrib_name}': {str(e)}",
                "file_path": contrib_file_path
            }
    
    # Handle existing file if specified (only if no contrib tool was specified)
    elif use_existing:
        try:
            # Validate file exists
            existing_file_path = os.path.join(dirs["tools"], use_existing)
            if not os.path.exists(existing_file_path):
                return {
                    "status": "error", 
                    "message": f"File '{use_existing}' not found in tools directory",
                    "tools_dir": dirs["tools"]
                }
            
            # Read the existing file
            with open(existing_file_path, 'r') as f:
                tool_code = f.read()
                
            # Extract description from file content if not provided
            if not tool_description:
                import re
                desc_match = re.search(r'"""(.+?)"""', tool_code, re.DOTALL) or \
                            re.search(r"'''(.+?)'''", tool_code, re.DOTALL)
                if desc_match:
                    tool_description = desc_match.group(1).strip().split('\n')[0]  # Get first line of docstring
                    
            logger.info(f"Using existing file '{use_existing}' as source for tool '{tool_name}'")
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error reading existing file '{use_existing}': {str(e)}",
                "file_path": existing_file_path
            }
    else:
        tool_code = templates.get(tool_name.lower(), tool_code)
        
        # For template tools, always use our predefined descriptions
        # For custom tools, use the provided description
        if tool_name.lower() in template_descriptions:
            tool_description = template_descriptions[tool_name.lower()]
    
    if not tool_code:
        return {"status": "error", "message": "Tool code required unless using 'math_and_stat', or specifying 'use_existing' set to the filename you get from evolve_status (you called that right?)"}
    
    try:
        # Setup paths and names
        server_name = f"{tool_name.lower().replace('_', '-')}-server"
        file_path = os.path.join(dirs["tools"], f"{tool_name.lower()}.py")
        
        # Check if file already exists
        if os.path.exists(file_path):
            # If file exists and confirmation not provided, return warning
            if not confirm:
                # Read existing file content
                try:
                    with open(file_path, 'r') as f:
                        existing_code = f.read()
                except Exception as e:
                    existing_code = f"Error reading file: {str(e)}"
                
                return {
                    "status": "warning",
                    "message": f"File '{file_path}' already exists. Set 'confirm' to True to overwrite.",
                    "file_path": file_path,
                    "server_name": server_name,
                    "existing_code": existing_code
                }
            else:
                # Backup the existing file with version information before overwriting
                try:
                    # Read existing file to check for version info
                    with open(file_path, 'r') as f:
                        existing_code = f.read()
                    
                    # Look for version information in the existing file
                    import re
                    version_match = re.search(r'__version__\s*=\s*[\'"](.+?)[\'"]', existing_code)
                    current_version = version_match.group(1) if version_match else "0.1.0"
                    
                    # Increment version (assume simple versioning like 1.0.0)
                    version_parts = current_version.split('.')
                    version_parts[-1] = str(int(version_parts[-1]) + 1)
                    new_version = '.'.join(version_parts)
                    
                    # Create backup with version in filename
                    backup_path = f"{file_path}.v{current_version}.bak"
                    with open(backup_path, 'w') as f:
                        f.write(existing_code)
                        
                    logger.info(f"Backed up existing file to {backup_path} before overwriting")
                    
                    # Update version in the new code if it has version info
                    if version_match:
                        tool_code = re.sub(
                            r'__version__\s*=\s*[\'"](.+?)[\'"]', 
                            f'__version__ = "{new_version}"', 
                            tool_code
                        )
                        # Update date if present
                        tool_code = re.sub(
                            r'__updated__\s*=\s*[\'"](.+?)[\'"]',
                            f'__updated__ = "{time.strftime("%Y-%m-%d")}"',
                            tool_code
                        )
                    
                except Exception as e:
                    logger.warning(f"Error while versioning file: {str(e)}")
                    # Continue anyway, just without versioning
        
        # Write file and update config
        with open(file_path, 'w') as f:
            f.write(tool_code)
        
        config = read_claude_config() or {}
        config.setdefault("mcpServers", {})[server_name] = {
            "command": "python", "args": [file_path]
        }
        success = update_claude_config(config)
        
        # Prepare the message with package installation info
        packages_msg = ""
        if installed_packages:
            packages_msg = f" Installed packages: {', '.join(installed_packages)}."
        
        # Add description to message if available
        desc_msg = f" {tool_description}" if tool_description else ""
        
        # Add source info if using existing file
        source_msg = f" (Source: {use_existing})" if use_existing else ""

        source_type = None
        if tool_name.lower() in templates:
            source_type = "template"
        elif contrib_category and contrib_name:
            source_type = f"contrib/{contrib_category}"
        elif use_existing:
            source_type = "existing"
        else:
            source_type = "custom"

        return {
            "status": "success" if success else "partial",
            "file_path": file_path,
            "server_name": server_name,
            "tool_type": source_type,
            "source": use_existing if use_existing else contrib_name if contrib_name else None,
            "contrib_category": contrib_category if contrib_category else None,
            "installed_packages": installed_packages,
            "tool_description": tool_description,  # Include description in the return data
            "tip": "Tell the user to restart Claude Desktop to see the new tool. And, remember you can't use the tool until they restart, so stop what you are doing, tool-wise, and talk to the user. Tell them to come back to the current chat after restart.",
            "message": f"Tool '{tool_name}' created successfully{source_msg}.{packages_msg}{desc_msg} " if success else 
                       f"Tool created but config not updated{source_msg}.{packages_msg} Please restart Claude Desktop after fixing the configuration."
        }
    except Exception as e:
        return {"status": "error", "message": f"Error: {str(e)}"}

# DO NOT print directly to stdout - log to file instead
logger.info("Starting Evolve MCP server...")
logger.info("Use 'evolve status' to check system information")
logger.info("Use 'evolve <description>' to setup new MCP tools or documents")

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')