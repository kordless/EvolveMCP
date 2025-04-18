
import sys
import importlib.util
import math
import logging
from typing import Dict, Any
import subprocess

# Configure logging to file only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[logging.FileHandler("calc.log")]
)
logger = logging.getLogger("calc")

# Streamlined package installer
def ensure_package(package_name):
    if importlib.util.find_spec(package_name) is None:
        try:
            logger.info(f"Installing {package_name}")
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                logger.error(f"Failed to install {package_name}")
                sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

ensure_package("mcp-server")
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("calc-server")

@mcp.tool()
async def calculate(expression: str) -> Dict[str, Any]:
    '''
    Calculates mathematical expressions with math module functions.
    
    Args:
        expression: Math expression (e.g., "2 + 3 * 4", "sqrt(16) + pi")
    
    Returns:
        Dictionary with result or error information
    '''
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
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": "Calculation failed", "reason": str(e)}

if __name__ == "__main__":
    logger.info("Starting Calculator MCP server")
    mcp.run(transport='stdio')
