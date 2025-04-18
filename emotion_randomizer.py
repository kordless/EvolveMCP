
import sys
import importlib.util
import subprocess
import logging
import random
from typing import Dict, Any

# Configure logging to file instead of stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("emotion_randomizer.log")]
)
logger = logging.getLogger("emotion_randomizer")

# Function to check and install packages
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

# Import MCP after ensuring it's installed
from mcp.server.fastmcp import FastMCP

# Create MCP server with a unique name
mcp = FastMCP("emotion_randomizer")

@mcp.tool()
async def randomize_emotion(seed: int = None) -> Dict[str, Any]:
    '''
    Randomizes between 8 primary and 8 secondary emotional states.
    
    Args:
        seed: Optional seed for random number generation for reproducibility
        
    Returns:
        A dictionary with primary and secondary emotional states
    '''
    # Define the 8 primary and 8 secondary emotional states
    primary_emotions = [
        "Joy", 
        "Sadness", 
        "Fear", 
        "Disgust", 
        "Anger", 
        "Surprise", 
        "Trust", 
        "Anticipation"
    ]
    
    secondary_emotions = [
        "Contentment", 
        "Melancholy", 
        "Anxiety", 
        "Revulsion", 
        "Frustration", 
        "Awe", 
        "Admiration", 
        "Excitement"
    ]
    
    # Set seed if provided for reproducibility
    if seed is not None:
        random.seed(seed)
    
    # Randomly select one primary and one secondary emotion
    primary = random.choice(primary_emotions)
    secondary = random.choice(secondary_emotions)
    
    # Return the selected emotions
    return {
        "primary_emotion": primary,
        "secondary_emotion": secondary,
        "emotion_combination": f"{primary}-{secondary}",
        "description": f"Primary emotion: {primary}, Secondary emotion: {secondary}. This combination might influence how to respond to questions with appropriate emotional tone."
    }

# Log to file, NOT to stdout
logger.info("Starting emotion_randomizer MCP tool")

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
