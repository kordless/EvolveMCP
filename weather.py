import sys
import importlib.util
import subprocess
import logging
import json
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("weather_tool.log")]
)
logger = logging.getLogger("weather_tool")

# Ensure required packages
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
ensure_package("requests")

# Import MCP after ensuring it's installed
from mcp.server.fastmcp import FastMCP
import requests

# Create MCP server
mcp = FastMCP("weather_tool")

@mcp.tool()
async def get_weather(
    latitude: float,
    longitude: float,
    hourly: Optional[List[str]] = ["temperature_2m", "precipitation_probability", "weather_code"],
    daily: Optional[List[str]] = None,
    current: Optional[List[str]] = None,
    timezone: str = "auto",
    forecast_days: int = 7,
    temperature_unit: str = "celsius",
    wind_speed_unit: str = "kmh",
    precipitation_unit: str = "mm"
) -> Dict[str, Any]:
    '''
    Gets weather forecast data from Open-Meteo API.
    
    Args:
        latitude: Geographical WGS84 latitude
        longitude: Geographical WGS84 longitude
        hourly: List of hourly weather variables
        daily: List of daily weather variable aggregations
        current: List of current weather variables
        timezone: Local time zone
        forecast_days: Number of days to forecast (0-16)
        temperature_unit: Unit for temperature (celsius, fahrenheit)
        wind_speed_unit: Unit for wind speed (kmh, ms, mph, kn)
        precipitation_unit: Unit for precipitation (mm, inch)
        
    Returns:
        Weather forecast data dictionary
    '''
    try:
        # Construct API URL and parameters
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone,
            "forecast_days": forecast_days,
            "temperature_unit": temperature_unit,
            "wind_speed_unit": wind_speed_unit,
            "precipitation_unit": precipitation_unit
        }
        
        # Add optional parameters if provided
        if hourly:
            params["hourly"] = ",".join(hourly)
        if daily:
            params["daily"] = ",".join(daily)
        if current:
            params["current"] = ",".join(current)
            
        # Make API request
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Get the JSON response
        data = response.json()
        
        # Add friendly weather descriptions
        data = add_weather_descriptions(data)
        
        # Return the enhanced JSON response
        return data
    except Exception as e:
        logger.error(f"Error getting weather data: {str(e)}")
        return {"error": str(e)}

def add_weather_descriptions(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add human-readable weather code descriptions to the weather data.
    
    Args:
        data: Weather data dictionary from Open-Meteo API
        
    Returns:
        Enhanced weather data dictionary with descriptions
    """
    # WMO Weather interpretation codes mapping
    wmo_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    
    # Add descriptions for current weather
    if "current" in data and "weather_code" in data["current"]:
        code = data["current"]["weather_code"]
        if code in wmo_codes:
            data["current"]["weather_description"] = wmo_codes[code]
    
    # Add descriptions for hourly weather
    if "hourly" in data and "weather_code" in data["hourly"]:
        weather_codes = data["hourly"]["weather_code"]
        weather_descriptions = []
        
        for code in weather_codes:
            if code in wmo_codes:
                weather_descriptions.append(wmo_codes[code])
            else:
                weather_descriptions.append("Unknown")
                
        data["hourly"]["weather_description"] = weather_descriptions
    
    # Add descriptions for daily weather
    if "daily" in data and "weather_code" in data["daily"]:
        weather_codes = data["daily"]["weather_code"]
        weather_descriptions = []
        
        for code in weather_codes:
            if code in wmo_codes:
                weather_descriptions.append(wmo_codes[code])
            else:
                weather_descriptions.append("Unknown")
                
        data["daily"]["weather_description"] = weather_descriptions
        
    return data

@mcp.tool()
async def get_weather_variables() -> Dict[str, List[str]]:
    '''
    Returns available weather variables for the Open-Meteo API.
    
    Returns:
        Dictionary of available weather variables categorized by type
    '''
    return {
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "dew_point_2m", 
            "apparent_temperature", "precipitation_probability", "precipitation",
            "rain", "showers", "snowfall", "snow_depth", "weather_code",
            "pressure_msl", "surface_pressure", "cloud_cover",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
        ],
        "daily": [
            "weather_code", "temperature_2m_max", "temperature_2m_min",
            "apparent_temperature_max", "apparent_temperature_min",
            "sunrise", "sunset", "precipitation_sum", "rain_sum",
            "showers_sum", "snowfall_sum", "precipitation_hours",
            "precipitation_probability_max", "wind_speed_10m_max",
            "wind_gusts_10m_max", "wind_direction_10m_dominant"
        ],
        "current": [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "is_day", "precipitation", "rain", "showers", "snowfall",
            "weather_code", "cloud_cover", "pressure_msl", "surface_pressure",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"
        ]
    }

@mcp.tool()
async def format_weather_report(
    weather_data: Dict[str, Any],
    format_type: str = "basic"
) -> Dict[str, Union[str, Dict]]:
    '''
    Formats weather data into a more human-readable report.
    
    Args:
        weather_data: Weather data from get_weather function
        format_type: Type of formatting (basic, detailed, html)
        
    Returns:
        Formatted weather report
    '''
    try:
        if "error" in weather_data:
            return {"error": weather_data["error"]}
            
        location_info = {
            "latitude": weather_data.get("latitude"),
            "longitude": weather_data.get("longitude"),
            "elevation": weather_data.get("elevation"),
            "timezone": weather_data.get("timezone")
        }
        
        if format_type == "basic":
            report = {"location": location_info, "report": ""}
            
            # Current weather if available
            if "current" in weather_data:
                current = weather_data["current"]
                current_report = "Current Weather:\n"
                
                if "temperature_2m" in current:
                    unit = weather_data.get("current_units", {}).get("temperature_2m", "�C")
                    current_report += f"Temperature: {current['temperature_2m']}{unit}\n"
                
                if "weather_description" in current:
                    current_report += f"Conditions: {current['weather_description']}\n"
                    
                if "relative_humidity_2m" in current:
                    unit = weather_data.get("current_units", {}).get("relative_humidity_2m", "%")
                    current_report += f"Humidity: {current['relative_humidity_2m']}{unit}\n"
                
                if "wind_speed_10m" in current:
                    unit = weather_data.get("current_units", {}).get("wind_speed_10m", "km/h")
                    current_report += f"Wind: {current['wind_speed_10m']}{unit}\n"
                
                report["report"] += current_report + "\n"
            
            # Daily forecast if available
            if "daily" in weather_data:
                daily = weather_data["daily"]
                if "time" in daily:
                    daily_report = "7-Day Forecast:\n"
                    
                    for i, date in enumerate(daily["time"]):
                        daily_report += f"{date}: "
                        
                        if "weather_description" in daily:
                            daily_report += f"{daily['weather_description'][i]}, "
                            
                        if "temperature_2m_max" in daily and "temperature_2m_min" in daily:
                            temp_unit = weather_data.get("daily_units", {}).get("temperature_2m_max", "�C")
                            daily_report += f"{daily['temperature_2m_min'][i]}{temp_unit} to {daily['temperature_2m_max'][i]}{temp_unit}"
                            
                        if "precipitation_probability_max" in daily:
                            prob_unit = weather_data.get("daily_units", {}).get("precipitation_probability_max", "%")
                            daily_report += f", {daily['precipitation_probability_max'][i]}{prob_unit} precip. probability"
                            
                        daily_report += "\n"
                        
                    report["report"] += daily_report
            
            return report
            
        elif format_type == "detailed":
            # Return a more detailed report (similar structure but with more data points)
            # Implementation would be similar to basic but with more fields
            return {"error": "Detailed format not yet implemented"}
            
        elif format_type == "html":
            # Return data formatted as HTML
            return {"error": "HTML format not yet implemented"}
            
        else:
            return {"error": f"Unknown format type: {format_type}"}
            
    except Exception as e:
        logger.error(f"Error formatting weather report: {str(e)}")
        return {"error": str(e)}

# Log to file, NOT to stdout
logger.info("Starting weather_tool MCP tool")

# Start the MCP server
if __name__ == "__main__":
    mcp.run(transport='stdio')
