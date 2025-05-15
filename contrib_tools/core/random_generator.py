import sys
import random
import logging
import os
from typing import Dict, Any, List, Optional, Union

__version__ = "0.1.1"
__updated__ = "2025-05-12"

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, "random_generator.log"))
    ]
)
logger = logging.getLogger("random_generator")

# Import MCP server
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("random-generator-server")

@mcp.tool()
async def random_generator(
    type: str = "int", 
    min: float = 0, 
    max: float = 100, 
    count: int = 1,
    choices: str = None,
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generates various types of random numbers and selections with customizable parameters.
    
    Args:
        type: Type of random value to generate ("int", "float", "choice", "bool", "bytes", "shuffle")
        min: Minimum value for numeric ranges (default: 0)
        max: Maximum value for numeric ranges (default: 100)
        count: Number of random values to generate (default: 1)
        choices: Comma-separated list of items to choose from (for "choice" and "shuffle" types)
        seed: Optional seed for the random generator for reproducible results
        
    Returns:
        Dictionary with random values and generation information
    """
    logger.info(f"Random generator called with: type={type}, min={min}, max={max}, count={count}, choices={choices}, seed={seed}")
    
    # Set seed if provided
    if seed is not None:
        random.seed(seed)
        logger.info(f"Using seed: {seed}")
    
    # Validate count
    if count < 1:
        logger.warning(f"Invalid count: {count}, using 1 instead")
        count = 1
    elif count > 1000:
        logger.warning(f"Count too large: {count}, limiting to 1000")
        count = 1000
    
    # Initialize result
    result = {
        "success": True,
        "type": type,
        "count": count,
        "seed": seed,
        "values": []
    }
    
    try:
        # Generate random values based on type
        if type.lower() == "int":
            # Ensure min and max are integers
            int_min = int(min)
            int_max = int(max)
            
            # Validate range
            if int_min > int_max:
                int_min, int_max = int_max, int_min
                logger.warning(f"Min > Max, swapping values to {int_min} and {int_max}")
            
            result["min"] = int_min
            result["max"] = int_max
            
            # Generate random integers
            for _ in range(count):
                result["values"].append(random.randint(int_min, int_max))
                
        elif type.lower() == "float":
            # Validate range
            if min > max:
                min, max = max, min
                logger.warning(f"Min > Max, swapping values to {min} and {max}")
                
            result["min"] = min
            result["max"] = max
            
            # Generate random floats
            for _ in range(count):
                result["values"].append(random.uniform(min, max))
                
        elif type.lower() == "bool":
            # Generate random booleans
            for _ in range(count):
                result["values"].append(random.choice([True, False]))
                
        elif type.lower() == "bytes":
            # Interpret max as number of bytes
            bytes_count = int(max)
            if bytes_count < 1:
                bytes_count = 1
            elif bytes_count > 1024:
                bytes_count = 1024
                
            result["bytes_count"] = bytes_count
            
            # Generate random bytes represented as hex strings
            for _ in range(count):
                random_bytes = random.randbytes(bytes_count)
                result["values"].append(random_bytes.hex())
                
        elif type.lower() in ["choice", "shuffle"]:
            # Process choices
            if not choices:
                default_choices = ["apple", "banana", "cherry", "date", "elderberry", "fig", "grape"]
                items = default_choices
                result["default_choices_used"] = True
                logger.warning(f"No choices provided, using default choices: {default_choices}")
            else:
                items = [item.strip() for item in choices.split(",")]
                
            result["choices"] = items
            
            if type.lower() == "choice":
                # Select random items from choices
                for _ in range(count):
                    result["values"].append(random.choice(items))
                    
            else:  # shuffle
                # Return shuffled version of the list
                shuffled = items.copy()
                random.shuffle(shuffled)
                result["values"] = shuffled
                # Override count to match the number of items
                result["count"] = len(shuffled)
                
        else:
            # Invalid type
            logger.error(f"Invalid random type: {type}")
            return {
                "success": False,
                "error": "Invalid random type",
                "valid_types": ["int", "float", "bool", "bytes", "choice", "shuffle"]
            }
    
    except Exception as e:
        logger.error(f"Random generation failed: {str(e)}")
        return {
            "success": False,
            "error": "Random generation failed",
            "reason": str(e)
        }
    
    # Simplify single results
    if count == 1:
        result["value"] = result["values"][0]
    
    logger.info(f"Generated {count} random values of type {type}")
    return result

if __name__ == "__main__":
    logger.info("Starting Random Generator MCP server")
    mcp.run(transport='stdio')