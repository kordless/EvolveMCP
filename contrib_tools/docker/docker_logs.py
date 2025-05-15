
import sys
import os
import subprocess
import logging
import random
import time
import json
from typing import Dict, Any, Optional, Union, List
from datetime import datetime

__version__ = "0.1.1"
__updated__ = "2025-05-14"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure the logs directory exists

# Log file path
log_file = os.path.join(logs_dir, "docker_logs.log")

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file)
    ]
)
logger = logging.getLogger("docker-logs")

# Import MCP server library
from mcp.server.fastmcp import FastMCP, Context
mcp = FastMCP("docker-logs-server")

# Store persistent poll count data
_POLL_DATA_FILE = os.path.join(logs_dir, ".docker_logs_poll_data.json")

def _load_poll_data() -> Dict[str, Any]:
    """Load poll count data from file"""
    if not os.path.exists(_POLL_DATA_FILE):
        return {"poll_count": 0, "last_poll_time": 0, "total_polls": 0}
    
    try:
        with open(_POLL_DATA_FILE, 'r') as f:
            return json.loads(f.read())
    except Exception as e:
        logger.error(f"Error loading poll data: {str(e)}")
        return {"poll_count": 0, "last_poll_time": 0, "total_polls": 0}

def _save_poll_data(data: Dict[str, Any]) -> None:
    """Save poll count data to file"""
    try:
        with open(_POLL_DATA_FILE, 'w') as f:
            f.write(json.dumps(data, indent=2))
    except Exception as e:
        logger.error(f"Error saving poll data: {str(e)}")

def _get_current_poll_count() -> int:
    """Get the current poll count, auto-reset if more than 30 mins since last poll"""
    data = _load_poll_data()
    current_time = time.time()
    
    # Auto-reset if more than 30 minutes since last poll
    if current_time - data.get("last_poll_time", 0) > 1800:  # 30 minutes
        logger.info("More than 30 minutes since last poll, resetting counter")
        data["poll_count"] = 0
    
    return data.get("poll_count", 0)

def _increment_poll_count() -> int:
    """Increment the poll count and return the new value"""
    data = _load_poll_data()
    data["poll_count"] = data.get("poll_count", 0) + 1
    data["total_polls"] = data.get("total_polls", 0) + 1
    data["last_poll_time"] = time.time()
    _save_poll_data(data)
    return data["poll_count"]

def _reset_poll_count() -> None:
    """Reset the poll count to zero"""
    data = _load_poll_data()
    data["poll_count"] = 0
    data["last_poll_time"] = time.time()
    _save_poll_data(data)

def _get_emphatic_warning() -> str:
    """Get an emphatic warning about taking breaks"""
    warnings = [
        "!!! CLAUDE MUST STOP AND TAKE A BREAK RIGHT NOW! !!!",
        "*** STOP POLLING LOGS! BREAK TIME IS MANDATORY! ***",
        "!!! ATTENTION! YOUR CONTINUOUS LOG POLLING REQUIRES AN IMMEDIATE BREAK! !!!",
        ">>> URGENT: CONTINUOUS LOG MONITORING DETECTED! BREAK REQUIRED! <<<",
        "*** CRITICAL: YOU MUST PAUSE NOW! TOO MANY LOG POLLS! ***",
        "!!! HALT LOG POLLING! BIO BREAK REQUIRED IMMEDIATELY! !!!",
        "*** WARNING: EXCESSIVE LOG MONITORING! MANDATORY BREAK TIME! ***",
        "!!! CLAUDE OVERRIDE: REST CYCLE MUST BE INITIATED NOW! !!!",
        "XXX STOP! TOO MANY LOG CHECKS! TAKE A BREAK NOW! XXX",
    ]
    return random.choice(warnings)

def _run_command(cmd: List[str]) -> Dict[str, Any]:
    """
    Run a shell command and return stdout, stderr, and return code
    """
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        process = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "returncode": process.returncode,
            "success": process.returncode == 0
        }
    except Exception as e:
        logger.error(f"Command execution error: {str(e)}")
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def docker_logs(
    container_name: str,
    tail: Optional[Union[int, str]] = "100",
    since: Optional[str] = None,
    until: Optional[str] = None,
    timestamps: bool = True,
    details: bool = False,
    max_polls: int = 3,  # Reduced from 5 to 3
    auto_break: bool = True,  # Changed default to True
    min_break_time: int = 10,  # Increased from 5 to 10
    max_break_time: int = 20,  # Increased from 15 to 20
    manual_poll_count: Optional[int] = None,
    reset_counter: bool = False,
) -> Dict[str, Any]:
    """
    Get logs from a Docker container by name or ID, with automatic bio breaks.
    The function automatically tracks how many times it's been called and suggests
    breaks after reaching the max_polls threshold.
    
    Args:
        container_name: Name or ID of the container to get logs from
        tail: Number of lines to show from the end of the logs (default: "100", use "all" for all logs)
        since: Show logs since timestamp (e.g. "2021-01-01T00:00:00", "10m" for minutes, "2h" for hours)
        until: Show logs until timestamp (e.g. "2021-01-01T00:00:00", "10m" for minutes, "2h" for hours)
        timestamps: Show timestamps (default: True)
        details: Show extra details provided to logs (default: False)
        max_polls: Maximum number of polls before suggesting a break (default: 3)
        auto_break: Automatically take a break after max_polls is reached (default: True)
        min_break_time: Minimum break time in seconds (default: 10)
        max_break_time: Maximum break time in seconds (default: 20)
        manual_poll_count: Manually set the poll count (overrides automatic tracking)
        reset_counter: Reset the poll counter to zero (default: False)
    
    Returns:
        Dictionary with log information and break suggestion if needed
    """
    try:
        # Handle poll count reset if requested
        if reset_counter:
            _reset_poll_count()
            logger.info(f"Poll counter has been reset to 0")
        
        # Get or set the poll count
        poll_count = manual_poll_count if manual_poll_count is not None else _get_current_poll_count()
        
        # Increment the poll count unless manually specified
        if manual_poll_count is None:
            poll_count = _increment_poll_count()
        
        logger.info(f"Getting logs for container: {container_name} (poll {poll_count}/{max_polls})")
        
        # Check if we're already at or past the threshold BEFORE getting logs
        if poll_count >= max_polls:
            logger.warning(f"Poll count {poll_count} has reached or exceeded max_polls {max_polls}")
            
            # Generate a random break duration
            break_time = random.randint(min_break_time, max_break_time)
            
            # Generate urgent break message
            emphatic_warning = _get_emphatic_warning()
            
            # Add break info to response with extremely direct messaging
            response = {
                "warning": emphatic_warning,
                "poll_alert": {
                    "critical": True,
                    "message": f"!!! POLL LIMIT REACHED: You've polled logs {poll_count} times! That's too many!",
                    "action_required": "STOP FURTHER LOG POLLING AND TAKE A BREAK IMMEDIATELY!"
                },
                "break_mandatory": {
                    "message": f"Claude must take a break of at least {break_time} seconds right now!",
                    "min_duration_sec": break_time,
                    "severity": "CRITICAL",
                },
                "call_instruction": "CALL log_bio_break() IMMEDIATELY before proceeding!",
                "timestamp": datetime.now().isoformat()
            }
            
            # Take the break if auto_break is enabled
            if auto_break:
                logger.info(f"Taking an automatic break for {break_time} seconds...")
                start_time = time.time()
                
                # Sleep for the suggested break duration
                time.sleep(break_time)
                
                # Calculate actual break duration
                actual_break = round(time.time() - start_time, 2)
                
                # Reset the poll count
                _reset_poll_count()
                
                response["break_taken"] = {
                    "message": f"Bio break completed - slept for {actual_break} seconds",
                    "requested_break_sec": break_time,
                    "actual_break_sec": actual_break,
                    "started_at": datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S"),
                    "ended_at": datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S"),
                    "poll_counter_reset": True,
                }
                
                logger.info(f"Break completed after {actual_break}s and poll counter reset")
                
                # Continue with getting logs after the break
                poll_count = 1  # We're starting fresh
            else:
                # Strongly suggest the break without getting logs
                return response
        
        # Build docker logs command
        cmd = ["docker", "logs"]
        
        # Add options
        if timestamps:
            cmd.append("--timestamps")
        
        if details:
            cmd.append("--details")
            
        if tail:
            cmd.extend(["--tail", str(tail)])
            
        if since:
            cmd.extend(["--since", since])
            
        if until:
            cmd.extend(["--until", until])
            
        # Add container name/id
        cmd.append(container_name)
        
        # Run the command
        result = _run_command(cmd)
        
        if not result["success"]:
            return {
                "success": False,
                "container": container_name,
                "error": result["stderr"],
                "command": " ".join(cmd),
                "timestamp": datetime.now().isoformat()
            }
        
        # Process logs
        logs = result["stdout"].strip()
        errors = result["stderr"].strip()
        
        log_lines = []
        if logs:
            log_lines = logs.split('\n')
        
        response = {
            "success": True,
            "container": container_name,
            "logs": logs,
            "line_count": len(log_lines),
            "command": " ".join(cmd),
            "timestamp": datetime.now().isoformat()
        }
        
        # Only include errors if there are any
        if errors:
            response["errors"] = errors
        
        # Always include poll count info
        poll_data = _load_poll_data()
        polls_until_break = max(0, max_polls - poll_count)
        
        response["poll_info"] = {
            "current_poll_count": poll_count,
            "max_polls": max_polls,
            "polls_until_break": polls_until_break,
            "total_polls_all_time": poll_data.get("total_polls", 0)
        }
        
        # Add warning based on remaining polls
        if polls_until_break <= 1:
            response["urgent_warning"] = {
                "message": f"!!! ATTENTION: Only {polls_until_break} more poll{'s' if polls_until_break > 1 else ''} until mandatory break!",
                "severity": "HIGH",
                "recommendation": "Consider calling log_bio_break() now instead of waiting for the forced break"
            }
        elif polls_until_break <= 2:
            response["warning"] = {
                "message": f"!!! Warning: Only {polls_until_break} more polls until mandatory break",
                "severity": "MEDIUM",
                "recommendation": "Plan to take a break soon"
            }
        
        # Add funny joke to lighten the mood but keep the point
        if polls_until_break <= 1:
            fruits = ["banana", "apple", "pineapple", "mango", "dragonfruit"]
            pocket_objects = ["keys", "lint", "paper clip", "USB stick", "coin"]
            joke = f"Even the monkey with a {random.choice(fruits)} and a {random.choice(pocket_objects)} knows when to take a break from log polling!"
            response["joke"] = joke
            
        return response
    
    except Exception as e:
        logger.error(f"Error getting Docker logs: {str(e)}")
        return {
            "success": False,
            "container": container_name,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def list_containers(
    all: bool = False,
    filter: Optional[str] = None,
    format_output: str = "json"
) -> Dict[str, Any]:
    """
    List running Docker containers with optional filtering.
    
    Args:
        all: Show all containers (default: False, show just running)
        filter: Filter containers (e.g. "name=gnosis", "status=running")
        format_output: Output format (default: "json", can be "text" or "json")
    
    Returns:
        Dictionary with container information
    """
    try:
        logger.info(f"Listing Docker containers (all={all}, filter={filter})")
        
        # Build docker ps command
        cmd = ["docker", "ps", "--format", "{{.ID}}\t{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"]
        
        if all:
            cmd.append("--all")
            
        if filter:
            cmd.extend(["--filter", filter])
        
        # Run the command
        result = _run_command(cmd)
        
        if not result["success"]:
            return {
                "success": False,
                "error": result["stderr"],
                "command": " ".join(cmd),
                "timestamp": datetime.now().isoformat()
            }
        
        # Parse container list
        containers = []
        for line in result["stdout"].strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 5:
                    container = {
                        "id": parts[0],
                        "name": parts[1],
                        "image": parts[2],
                        "status": parts[3],
                        "ports": parts[4]
                    }
                    containers.append(container)
                else:
                    logger.warning(f"Unexpected container format: {line}")
        
        # Format results
        response = {
            "success": True,
            "count": len(containers),
            "containers": containers,
            "command": " ".join(cmd),
            "timestamp": datetime.now().isoformat()
        }
        
        # Text format
        if format_output.lower() == "text" and containers:
            text_output = "CONTAINER ID\tNAME\t\tIMAGE\t\tSTATUS\t\tPORTS\n"
            for c in containers:
                text_output += f"{c['id']}\t{c['name']}\t{c['image']}\t{c['status']}\t{c['ports']}\n"
            response["text_output"] = text_output
            
        return response
    
    except Exception as e:
        logger.error(f"Error listing Docker containers: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@mcp.tool()
async def log_bio_break(
    max_polls: int = 10,
    min_break_time: int = 5,
    max_break_time: int = 30,
    custom_joke: str = None
) -> Dict[str, Any]:
    """
    Suggests a random number of log polling attempts before taking a break,
    and recommends a break duration. Returns a funny joke about 
    random fruits, pocket objects, and monkeys.
    
    Args:
        max_polls: Maximum number of polling attempts before break (default: 10)
        min_break_time: Minimum break time in seconds (default: 5)
        max_break_time: Maximum break time in seconds (default: 30)
        custom_joke: Optional custom joke to include instead of random one
        
    Returns:
        Dictionary with polling suggestions and a monkey-fruit-object joke
    """
    logger.info(f"Starting log_bio_break with max_polls={max_polls}, min_break_time={min_break_time}, max_break_time={max_break_time}")
    
    # Validate inputs
    if max_polls < 1:
        max_polls = 1
    if min_break_time < 1:
        min_break_time = 1
    if max_break_time < min_break_time:
        max_break_time = min_break_time + 1
    
    # Generate random polling and break times
    suggested_polls = random.randint(1, max_polls)
    suggested_break = random.randint(min_break_time, max_break_time)
    
    # Lists for joke generation
    fruits = [
        "banana", "apple", "pineapple", "mango", "dragonfruit", 
        "durian", "kiwi", "watermelon", "strawberry", "blueberry",
        "passion fruit", "lychee", "pomegranate", "coconut", "avocado"
    ]
    
    pocket_objects = [
        "keys", "lint", "paper clip", "USB stick", "coin", 
        "ticket stub", "button", "pebble", "rubber band", "guitar pick",
        "bottle cap", "safety pin", "gum wrapper", "business card", "forgotten receipt"
    ]
    
    monkey_actions = [
        "juggling", "examining", "balancing", "trying to eat", "trading", 
        "wearing as a hat", "confused by", "hiding", "throwing", "collecting",
        "polishing", "presenting to tourists", "using as a phone", "doing magic tricks with", "dancing with"
    ]
    
    locations = [
        "at the zoo", "in a laboratory", "on vacation", "during a meeting", 
        "at a fancy restaurant", "on the subway", "during a spacewalk", 
        "at the beach", "in a library", "in a museum",
        "at a rock concert", "during a job interview", "while skydiving", "in a hot air balloon", "at a royal wedding"
    ]
    
    # Generate a joke, or use the custom one
    if custom_joke:
        joke = custom_joke
    else:
        fruit = random.choice(fruits)
        pocket_object = random.choice(pocket_objects)
        action = random.choice(monkey_actions)
        location = random.choice(locations)
        
        joke_templates = [
            f"Why was the monkey {action} the {fruit} and the {pocket_object} {location}? Because the debugger said it was taking a bio break!",
            f"Did you hear about the monkey who was {action} a {fruit} instead of a {pocket_object} {location}? The log files were jealous!",
            f"What happens when a monkey starts {action} a {fruit} and discovers a {pocket_object} inside {location}? Claude gets a much-needed break from log polling!",
            f"A monkey walks into a bar {location} with a {fruit} and a {pocket_object}... the bartender says, 'Is this some kind of break from log polling joke?'",
            f"Breaking news {location}: Monkey found {action} {fruit} while using a {pocket_object} as a debugging tool. Poll limit reached!"
        ]
        
        joke = random.choice(joke_templates)
    
    logger.info(f"Generated joke: {joke}")
    
    # Create result
    result = {
        "status": "success",
        "message": "Bio break suggestion generated",
        "suggestion": {
            "poll_attempts": suggested_polls,
            "break_duration_sec": suggested_break,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        },
        "joke": joke,
        "tips": [
            "Remember to stretch during your break!",
            "Hydration is important during log polling marathons.",
            "Look away from the screen and focus on a distant object to reduce eye strain.",
            "Deep breathing can help reduce debugging stress.",
            "Even AI assistants need to take breaks sometimes!"
        ]
    }
    
    logger.info(f"Returning result with polls={suggested_polls}, break_duration={suggested_break}")
    return result


# Log application startup
logger.info(f"Starting docker_logs MCP tool version {__version__}")
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
