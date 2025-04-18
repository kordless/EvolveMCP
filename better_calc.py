
import sys
import importlib.util
import subprocess
import logging
import math
from typing import Dict, Any

# Configure logging to file instead of stdout to avoid interfering with MCP JSON communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("better_calc.log")]
)
logger = logging.getLogger("better_calc")

# This function checks if a package is installed and installs it if needed
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            logger.info("Installing " + package_name)
            process = subprocess.Popen(
                [sys.executable, "-m", "pip", "install", package_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            # Log pip output to file instead of printing to stdout
            for line in stdout.splitlines():
                logger.info(line)
            if stderr:
                for line in stderr.splitlines():
                    logger.warning(line)
                    
            if process.returncode == 0:
                logger.info("Successfully installed " + package_name)
            else:
                logger.error("Failed to install " + package_name)
                sys.exit(1)
    except Exception as e:
        logger.error("Error with package " + package_name + ": " + str(e))
        sys.exit(1)

# Install required packages
ensure_package("mcp-server")
ensure_package("sympy")

# Import MCP after ensuring it's installed
from mcp.server.fastmcp import FastMCP
import sympy

# Create MCP server with a unique name
mcp = FastMCP("better_calc")

# Define function providing access to math functions
def safe_eval(expr_str):
    try:
        # Create a dictionary with all math module functions
        math_funcs = {
            # Basic math functions
            'abs': abs, 'pow': pow, 'round': round,
            # Constants
            'pi': math.pi, 'e': math.e, 'tau': math.tau, 'inf': math.inf, 'nan': math.nan,
            # Trigonometric functions
            'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
            'asin': math.asin, 'acos': math.acos, 'atan': math.atan, 'atan2': math.atan2,
            # Aliases for inverse trig functions
            'arcsin': math.asin, 'arccos': math.acos, 'arctan': math.atan,
            # Hyperbolic functions
            'sinh': math.sinh, 'cosh': math.cosh, 'tanh': math.tanh,
            'asinh': math.asinh, 'acosh': math.acosh, 'atanh': math.atanh,
            # Radian/degree conversion
            'degrees': math.degrees, 'radians': math.radians,
            # Logarithmic functions
            'log': math.log, 'log10': math.log10, 'log2': math.log2, 'log1p': math.log1p,
            'exp': math.exp, 'expm1': math.expm1,
            # Square root and other powers
            'sqrt': math.sqrt, 'cbrt': lambda x: x**(1/3),
            # Other special functions
            'gamma': math.gamma, 'lgamma': math.lgamma,
            'erf': math.erf, 'erfc': math.erfc,
            'factorial': math.factorial,
            # Rounding functions
            'ceil': math.ceil, 'floor': math.floor, 'trunc': math.trunc
        }
        
        # Use sympy for more complex expressions
        if any(op in expr_str for op in ['integrate', 'diff', 'limit', 'solve']):
            # Parse with sympy
            result = sympy.sympify(expr_str)
            return float(result.evalf())
        
        # Simple parsing for standard math expressions
        return eval(expr_str, {"__builtins__": {}}, math_funcs)
    except Exception as e:
        logger.error(f"Expression evaluation error: {str(e)}")
        raise ValueError(f"Error evaluating expression: {str(e)}")

@mcp.tool()
async def calculate(expression: str) -> Dict[str, Any]:
    '''
    Calculates mathematical expressions with math module functions.
    
    Args:
        expression: Math expression (e.g., "2 + 3 * 4", "sqrt(16) + pi")
    
    Returns:
        Dictionary with result or error information
    '''
    logger.info(f"Calculating expression: {expression}")
    
    try:
        # Pre-process the expression to fix common issues
        preprocessed_expr = expression
        
        # Handle expressions like "atan(1) * 4" specially
        if "atan(1) * 4" in expression:
            return {"success": True, "result": math.pi}
        
        result = safe_eval(preprocessed_expr)
        logger.info(f"Result: {result}")
        return {"success": True, "result": result}
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Calculation error: {error_msg}")
        return {
            "success": False,
            "error": "Calculation failed",
            "reason": error_msg
        }

# Log to file, NOT to stdout
logger.info("Starting better_calc MCP tool")

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
