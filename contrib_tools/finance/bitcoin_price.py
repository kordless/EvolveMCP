
import sys
import os
import importlib.util
import subprocess
import logging
import json
import asyncio
from typing import Dict, Any, Optional

# Get the current directory for log file placement
current_dir = os.path.dirname(os.path.abspath(__file__)) or '.'

# Configure logging to file instead of stdout to avoid interfering with MCP JSON communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(os.path.join(current_dir, "bitcoin_price.log"))]
)
logger = logging.getLogger("bitcoin_price")

# This function checks if a package is installed and installs it if needed
def ensure_package(package_name):
    try:
        if importlib.util.find_spec(package_name) is None:
            logger.info(f"Installing {package_name}")
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
                logger.info(f"Successfully installed {package_name}")
            else:
                logger.error(f"Failed to install {package_name}")
                sys.exit(1)
    except Exception as e:
        logger.error(f"Error with package {package_name}: {str(e)}")
        sys.exit(1)

# Install required packages
ensure_package("mcp-server")
ensure_package("aiohttp")

# Import MCP after ensuring it's installed
from mcp.server.fastmcp import FastMCP
import aiohttp

# Create MCP server with a unique name
mcp = FastMCP("bitcoin-price-server")

@mcp.tool()
async def get_bitcoin_price(currency: str = "USD") -> Dict[str, Any]:
    '''
    Gets the current Bitcoin price from a public API.
    
    Args:
        currency: The currency to get the price in (default: USD)
        
    Returns:
        A dictionary with the current Bitcoin price and other details
    '''
    try:
        # CoinGecko API doesn't require authentication
        url = f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies={currency.lower()}&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if 'bitcoin' in data:
                        bitcoin_data = data['bitcoin']
                        currency_lower = currency.lower()
                        
                        price = bitcoin_data.get(currency_lower, 0)
                        market_cap = bitcoin_data.get(f"{currency_lower}_market_cap", 0)
                        vol_24h = bitcoin_data.get(f"{currency_lower}_24h_vol", 0)
                        change_24h = bitcoin_data.get(f"{currency_lower}_24h_change", 0)
                        last_updated = bitcoin_data.get("last_updated_at", 0)
                        
                        return {
                            "success": True,
                            "price": price,
                            "currency": currency.upper(),
                            "market_cap": market_cap,
                            "volume_24h": vol_24h,
                            "change_24h": change_24h,
                            "last_updated_timestamp": last_updated,
                            "source": "CoinGecko"
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Bitcoin data not found in response"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"API request failed with status code: {response.status}"
                    }
    except Exception as e:
        logger.error(f"Error fetching Bitcoin price: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to fetch Bitcoin price: {str(e)}"
        }

@mcp.tool()
async def list_supported_currencies() -> Dict[str, Any]:
    '''
    Lists currencies supported by the CoinGecko API.
    
    Returns:
        A dictionary with a list of supported currencies
    '''
    try:
        url = "https://api.coingecko.com/api/v3/simple/supported_vs_currencies"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    currencies = await response.json()
                    return {
                        "success": True,
                        "supported_currencies": currencies
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API request failed with status code: {response.status}"
                    }
    except Exception as e:
        logger.error(f"Error fetching supported currencies: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to fetch supported currencies: {str(e)}"
        }

@mcp.tool()
async def get_bitcoin_history(days: int = 7, currency: str = "USD") -> Dict[str, Any]:
    '''
    Gets Bitcoin price history for a specified number of days.
    
    Args:
        days: Number of days of history to retrieve (1, 7, 14, 30, 90, 180, 365, max)
        currency: The currency to get the price in (default: USD)
        
    Returns:
        A dictionary with Bitcoin price history data
    '''
    # Validate days parameter
    valid_days = [1, 7, 14, 30, 90, 180, 365, "max"]
    if days not in valid_days and str(days) != "max":
        days = 7  # Default to 7 if invalid
    
    try:
        url = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency={currency.lower()}&days={days}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Process the data to make it more usable
                    prices = []
                    if 'prices' in data:
                        # Only include a reasonable number of data points (max 30)
                        step = max(1, len(data['prices']) // 30)
                        for i in range(0, len(data['prices']), step):
                            timestamp, price = data['prices'][i]
                            prices.append({
                                "timestamp": timestamp,
                                "price": price
                            })
                    
                    return {
                        "success": True,
                        "currency": currency.upper(),
                        "days": days,
                        "price_history": prices,
                        "source": "CoinGecko"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API request failed with status code: {response.status}"
                    }
    except Exception as e:
        logger.error(f"Error fetching Bitcoin history: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to fetch Bitcoin history: {str(e)}"
        }

# Log to file, NOT to stdout
logger.info("Starting Bitcoin Price MCP tool")

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
