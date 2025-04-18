
import sys
import importlib.util
import subprocess
import logging
import base64
import io
from typing import Dict, Any

# Configure logging to file instead of stdout to avoid interfering with MCP JSON communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("mandelbrot.log")]
)
logger = logging.getLogger("mandelbrot")

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
ensure_package("numpy")
ensure_package("matplotlib")
ensure_package("pillow")

# Import MCP after ensuring it's installed
from mcp.server.fastmcp import FastMCP
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

# Create MCP server with a unique name
mcp = FastMCP("mandelbrot")

def mandelbrot_set(width, height, x_min, x_max, y_min, y_max, max_iter):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    c = x.reshape((1, width)) + 1j * y.reshape((height, 1))
    z = np.zeros_like(c, dtype=np.complex128)
    mask = np.ones_like(c, dtype=bool)
    result = np.zeros_like(c, dtype=int)
    
    for i in range(max_iter):
        z[mask] = z[mask]**2 + c[mask]
        mask_new = np.abs(z) < 2.0
        mask_iter = mask & (~mask_new)
        result[mask_iter] = i
        mask = mask_new
    
    return result

def generate_mandelbrot_image(width=800, height=600, x_min=-2.5, x_max=1.0, 
                               y_min=-1.2, y_max=1.2, max_iter=100, color_map='viridis'):
    try:
        data = mandelbrot_set(width, height, x_min, x_max, y_min, y_max, max_iter)
        
        # Create figure with specific size
        plt.figure(figsize=(width/100, height/100), dpi=100)
        
        # Plot the mandelbrot set with the specified colormap
        plt.imshow(data, cmap=color_map, extent=(x_min, x_max, y_min, y_max))
        plt.axis('off')  # Hide axes
        
        # Save to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        buf.seek(0)
        
        # Convert to base64 for sending over JSON
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return img_base64
    except Exception as e:
        logger.error(f"Error generating Mandelbrot image: {str(e)}")
        return None

@mcp.tool()
async def generate_mandelbrot(
    width: int = 800, 
    height: int = 600, 
    x_min: float = -2.5, 
    x_max: float = 1.0, 
    y_min: float = -1.2, 
    y_max: float = 1.2, 
    max_iter: int = 100,
    color_map: str = 'viridis'
) -> Dict[str, Any]:
    '''
    Generates a Mandelbrot set fractal image with the specified parameters.
    
    Args:
        width: Width of the image in pixels (default: 800)
        height: Height of the image in pixels (default: 600)
        x_min: Minimum x-coordinate in the complex plane (default: -2.5)
        x_max: Maximum x-coordinate in the complex plane (default: 1.0)
        y_min: Minimum y-coordinate in the complex plane (default: -1.2)
        y_max: Maximum y-coordinate in the complex plane (default: 1.2)
        max_iter: Maximum number of iterations for each point (default: 100)
        color_map: Matplotlib colormap to use (default: 'viridis')
        
    Returns:
        A dictionary with the base64-encoded PNG image and parameter information
    '''
    logger.info(f"Generating Mandelbrot with params: width={width}, height={height}, "
                f"x_min={x_min}, x_max={x_max}, y_min={y_min}, y_max={y_max}, "
                f"max_iter={max_iter}, color_map={color_map}")
    
    img_base64 = generate_mandelbrot_image(
        width, height, x_min, x_max, y_min, y_max, max_iter, color_map
    )
    
    if img_base64:
        return {
            "image": img_base64,
            "settings": {
                "width": width,
                "height": height,
                "x_min": x_min,
                "x_max": x_max,
                "y_min": y_min,
                "y_max": y_max,
                "max_iter": max_iter,
                "color_map": color_map
            }
        }
    else:
        return {
            "error": "Failed to generate Mandelbrot image"
        }

# Log to file, NOT to stdout
logger.info("Starting mandelbrot MCP tool")

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
