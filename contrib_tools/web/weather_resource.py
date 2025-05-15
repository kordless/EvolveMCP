
import sys
import os
import logging
import json
import httpx
import asyncio
from typing import Dict, Any, Optional, List, Tuple

__version__ = "0.1.2"
__updated__ = "2025-05-12"  # Today's date

# Define log path in the logs directory parallel to tools
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")

# Ensure logs directory exists
os.makedirs(logs_dir, exist_ok=True)

# Configure logging to file in the logs directory
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(logs_dir, "weather_resource.log"))
    ]
)
logger = logging.getLogger("weather_resource")

# Import mcp-server
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("weather-resource-server")

async def fetch_weather_data(
    latitude: float,
    longitude: float,
    forecast_type: str = "forecast"
) -> Dict[str, Any]:
    """
    Helper function to fetch weather data from the National Weather Service API.
    """
    try:
        # Validate input parameters
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return {
                "status": "error",
                "message": "Latitude and longitude must be numeric values"
            }
        
        if latitude < -90 or latitude > 90:
            return {
                "status": "error",
                "message": "Latitude must be between -90 and 90 degrees"
            }
            
        if longitude < -180 or longitude > 180:
            return {
                "status": "error",
                "message": "Longitude must be between -180 and 180 degrees"
            }
        
        valid_forecast_types = ["forecast", "hourly", "alerts"]
        if forecast_type not in valid_forecast_types:
            return {
                "status": "error",
                "message": f"Forecast type must be one of: {', '.join(valid_forecast_types)}"
            }
        
        # Initialize HTTP client with appropriate headers and follow_redirects=True
        headers = {
            "User-Agent": "Weather Resource Tool/1.0 (claude-desktop)",
            "Accept": "application/geo+json"
        }
        
        async with httpx.AsyncClient(headers=headers, timeout=30.0, follow_redirects=True) as client:
            # First get the grid point information from the coordinates
            # Round coordinates to 4 decimal places to avoid precision issues
            rounded_lat = round(latitude, 4)
            rounded_lon = round(longitude, 4)
            point_url = f"https://api.weather.gov/points/{rounded_lat},{rounded_lon}"
            logger.info(f"Requesting point data from {point_url}")
            
            try:
                response = await client.get(point_url)
                response.raise_for_status()
                point_data = response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from NWS API: {e}")
                if e.response.status_code == 404:
                    return {
                        "status": "error",
                        "message": "Location not found. The National Weather Service API only covers the United States."
                    }
                return {
                    "status": "error",
                    "message": f"HTTP error: {e.response.status_code} - {e.response.reason_phrase}"
                }
            except httpx.RequestError as e:
                logger.error(f"Request error: {e}")
                return {
                    "status": "error",
                    "message": f"Request error: {str(e)}"
                }
            except Exception as e:
                logger.error(f"Error fetching point data: {e}")
                return {
                    "status": "error",
                    "message": f"Error processing point data: {str(e)}"
                }
            
            # Extract needed data from point response
            office = point_data.get("properties", {}).get("gridId")
            grid_x = point_data.get("properties", {}).get("gridX")
            grid_y = point_data.get("properties", {}).get("gridY")
            
            if not all([office, grid_x, grid_y]):
                return {
                    "status": "error",
                    "message": "Could not determine grid point from coordinates"
                }
            
            # Get station information for observations
            stations_url = point_data.get("properties", {}).get("observationStations")
            forecast_url = None
            
            # Determine which forecast URL to use
            if forecast_type == "forecast":
                forecast_url = point_data.get("properties", {}).get("forecast")
            elif forecast_type == "hourly":
                forecast_url = point_data.get("properties", {}).get("forecastHourly")
            elif forecast_type == "alerts":
                # For alerts, we'll use the state/zone information
                state = point_data.get("properties", {}).get("relativeLocation", {}).get("properties", {}).get("state")
                if state:
                    forecast_url = f"https://api.weather.gov/alerts/active?area={state}"
                else:
                    # Fall back to coordinates if state isn't available
                    forecast_url = f"https://api.weather.gov/alerts/active?point={rounded_lat},{rounded_lon}"
            
            if not forecast_url:
                return {
                    "status": "error",
                    "message": f"Could not determine {forecast_type} URL for coordinates"
                }
            
            # Fetch the current observations if available
            current_conditions = None
            if stations_url and forecast_type != "alerts":
                try:
                    # Get stations list
                    stations_response = await client.get(stations_url)
                    stations_response.raise_for_status()
                    stations_data = stations_response.json()
                    
                    # Get the first station
                    if stations_data.get("features") and len(stations_data["features"]) > 0:
                        station_url = stations_data["features"][0]["id"] + "/observations/latest"
                        
                        # Get observation data
                        observation_response = await client.get(station_url)
                        if observation_response.status_code == 200:
                            observation_data = observation_response.json()
                            current_conditions = format_observation(observation_data)
                except Exception as e:
                    logger.warning(f"Error fetching observation data: {e}")
                    # Continue without observation data
            
            # Fetch the forecast data
            logger.info(f"Requesting forecast from {forecast_url}")
            try:
                forecast_response = await client.get(forecast_url)
                forecast_response.raise_for_status()
                forecast_data = forecast_response.json()
                
                # Format the response data based on the type
                if forecast_type in ["forecast", "hourly"]:
                    forecast_result = format_forecast(forecast_data, forecast_type)
                else:  # alerts
                    forecast_result = format_alerts(forecast_data)
                
                # Build the final response
                result = {
                    "status": "success",
                    "type": forecast_type,
                    "coordinates": {
                        "latitude": latitude,
                        "longitude": longitude
                    },
                    "location": extract_location_info(point_data),
                    forecast_type: forecast_result
                }
                
                # Add current conditions if available
                if current_conditions:
                    result["current"] = current_conditions
                
                return result
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error fetching {forecast_type}: {e}")
                return {
                    "status": "error",
                    "message": f"Error fetching {forecast_type}: HTTP {e.response.status_code} - {e.response.reason_phrase}"
                }
            except Exception as e:
                logger.error(f"Error processing {forecast_type} data: {e}")
                return {
                    "status": "error",
                    "message": f"Error processing {forecast_type} data: {str(e)}"
                }
                
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }

def extract_location_info(point_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract location information from point data response"""
    props = point_data.get("properties", {})
    rel_location = props.get("relativeLocation", {}).get("properties", {})
    
    return {
        "name": f"{rel_location.get('city', 'Unknown')}, {rel_location.get('state', 'Unknown')}",
        "city": rel_location.get("city"),
        "state": rel_location.get("state"),
        "county": props.get("county", "").split("/")[-1] if props.get("county") else None,
        "timezone": props.get("timeZone"),
        "radar_station": props.get("radarStation")
    }

def format_observation(observation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Format the observation data into a consistent structure"""
    props = observation_data.get("properties", {})
    
    # Extract temperature in both F and C
    temp_f = props.get("temperature", {}).get("value")
    temp_c = temp_f
    
    if temp_c is not None:
        # Convert to Fahrenheit if value is in Celsius
        if props.get("temperature", {}).get("unitCode", "") == "wmoUnit:degC":
            temp_f = (temp_c * 9/5) + 32
        # Convert to Celsius if value is in Fahrenheit
        elif props.get("temperature", {}).get("unitCode", "") == "wmoUnit:degF":
            temp_c = (temp_f - 32) * 5/9
    
    # Process other values
    humidity = props.get("relativeHumidity", {}).get("value")
    
    wind_speed_value = props.get("windSpeed", {}).get("value")
    wind_speed_unit = props.get("windSpeed", {}).get("unitCode", "")
    wind_speed_mph = None
    
    if wind_speed_value is not None:
        # Convert to mph if needed
        if "km_h-1" in wind_speed_unit:
            wind_speed_mph = wind_speed_value * 0.621371
        elif "m_s-1" in wind_speed_unit:
            wind_speed_mph = wind_speed_value * 2.23694
        else:
            wind_speed_mph = wind_speed_value
    
    # Format the response
    return {
        "timestamp": props.get("timestamp"),
        "text_description": props.get("textDescription"),
        "temperature": {
            "fahrenheit": round(temp_f, 1) if temp_f is not None else None,
            "celsius": round(temp_c, 1) if temp_c is not None else None
        },
        "humidity": round(humidity, 1) if humidity is not None else None,
        "wind": {
            "speed_mph": round(wind_speed_mph, 1) if wind_speed_mph is not None else None,
            "direction": props.get("windDirection", {}).get("value"),
            "gust_mph": round(props.get("windGust", {}).get("value", 0) * 0.621371, 1) 
                if props.get("windGust", {}).get("value") is not None else None
        },
        "barometric_pressure": {
            "value": props.get("barometricPressure", {}).get("value"),
            "unit": props.get("barometricPressure", {}).get("unitCode", "")
        },
        "visibility": {
            "value": props.get("visibility", {}).get("value"),
            "unit": props.get("visibility", {}).get("unitCode", "")
        },
        "precipitation_last_hour": props.get("precipitationLastHour", {}).get("value"),
        "heat_index": {
            "fahrenheit": props.get("heatIndex", {}).get("value"),
            "unit": props.get("heatIndex", {}).get("unitCode", "")
        },
        "wind_chill": {
            "fahrenheit": props.get("windChill", {}).get("value"),
            "unit": props.get("windChill", {}).get("unitCode", "")
        }
    }

def format_forecast(forecast_data: Dict[str, Any], forecast_type: str) -> List[Dict[str, Any]]:
    """Format the forecast data into a consistent structure"""
    periods = forecast_data.get("properties", {}).get("periods", [])
    formatted_periods = []
    
    for period in periods:
        formatted_period = {
            "name": period.get("name"),
            "start_time": period.get("startTime"),
            "end_time": period.get("endTime"),
            "is_daytime": period.get("isDaytime"),
            "temperature": {
                "value": period.get("temperature"),
                "unit": period.get("temperatureUnit")
            },
            "temperature_trend": period.get("temperatureTrend"),
            "wind_speed": period.get("windSpeed"),
            "wind_direction": period.get("windDirection"),
            "short_forecast": period.get("shortForecast"),
            "detailed_forecast": period.get("detailedForecast")
        }
        
        if forecast_type == "hourly":
            # Add extra details for hourly forecasts if available
            formatted_period["probability_of_precipitation"] = period.get("probabilityOfPrecipitation", {}).get("value")
            formatted_period["relative_humidity"] = period.get("relativeHumidity", {}).get("value")
        
        formatted_periods.append(formatted_period)
    
    return formatted_periods

def format_alerts(alerts_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Format the alerts data into a consistent structure"""
    features = alerts_data.get("features", [])
    formatted_alerts = []
    
    for feature in features:
        props = feature.get("properties", {})
        
        alert = {
            "id": props.get("id"),
            "event": props.get("event"),
            "headline": props.get("headline"),
            "description": props.get("description"),
            "severity": props.get("severity"),
            "certainty": props.get("certainty"),
            "urgency": props.get("urgency"),
            "onset": props.get("onset"),
            "expires": props.get("expires"),
            "status": props.get("status"),
            "message_type": props.get("messageType"),
            "category": props.get("category"),
            "response_type": props.get("responseType"),
            "affected_zones": props.get("affectedZones", []),
            "instruction": props.get("instruction")
        }
        
        formatted_alerts.append(alert)
    
    return formatted_alerts

async def get_geocode_from_address(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode an address string to coordinates using multiple geocoding services.
    """
    try:
        # Try OSM Nominatim first, which has better coverage
        import urllib.parse
        encoded_address = urllib.parse.quote(address)
        
        # Use the OpenStreetMap Nominatim geocoder
        osm_url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1"
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            # Add a proper User-Agent header
            headers = {
                "User-Agent": "Weather Resource Tool/1.0 (claude-desktop)",
                "Accept": "application/json"
            }
            
            response = await client.get(osm_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    # OSM returns lat/lon as strings
                    latitude = float(data[0].get("lat"))
                    longitude = float(data[0].get("lon"))
                    logger.info(f"Successfully geocoded with OSM: {address} -> {latitude}, {longitude}")
                    return latitude, longitude
            
        # If OSM fails, fall back to Census.gov (US only)
        census_url = f"https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address={encoded_address}&benchmark=2020&format=json"
        
        response = await client.get(census_url)
        
        if response.status_code != 200:
            logger.error(f"Census geocoding error: HTTP {response.status_code}")
            return None, None
        
        data = response.json()
        matches = data.get("result", {}).get("addressMatches", [])
        
        if not matches:
            logger.warning(f"No Census geocoding matches found for address: {address}")
            return None, None
        
        # Get the first match
        match = matches[0]
        coordinates = match.get("coordinates", {})
        
        # Note: Census API returns (y, x) format
        latitude = coordinates.get("y")
        longitude = coordinates.get("x")
        
        logger.info(f"Successfully geocoded with Census: {address} -> {latitude}, {longitude}")
        return latitude, longitude
    
    except Exception as e:
        logger.error(f"Error geocoding address: {e}")
        return None, None

# Common US cities and their coordinates for fallback
COMMON_US_CITIES = {
    "new braunfels": (29.703, -98.1245),
    "new braunfels tx": (29.703, -98.1245),
    "new braunfels texas": (29.703, -98.1245),
    "austin": (30.2672, -97.7431),
    "san antonio": (29.4252, -98.4946),
    "houston": (29.7604, -95.3698),
    "dallas": (32.7767, -96.7970),
    "fort worth": (32.7555, -97.3308),
    "el paso": (31.7619, -106.4850),
    "arlington tx": (32.7357, -97.1081),
    "corpus christi": (27.8006, -97.3964),
    "plano": (33.0198, -96.6989),
    "laredo": (27.5306, -99.4803),
    "lubbock": (33.5779, -101.8552),
    "garland": (32.9126, -96.6389),
    "irving": (32.8140, -96.9489),
    "amarillo": (35.2220, -101.8313),
    "grand prairie": (32.7459, -97.0072),
    "brownsville": (25.9017, -97.4975),
    "pasadena tx": (29.6910, -95.2091),
    "mesquite": (32.7668, -96.5990),
    "mcallen": (26.2034, -98.2300),
    "killeen": (31.1171, -97.7278),
    "frisco": (33.1507, -96.8236),
    "waco": (31.5493, -97.1467),
    "san angelo": (31.4638, -100.4370),
    "wichita falls": (33.9137, -98.4934),
    "abilene": (32.4487, -99.7331),
    "galveston": (29.3013, -94.7977),
    "college station": (30.6280, -96.3344),
    "harlingen": (26.1906, -97.6961)
}

@mcp.tool()
async def weather_resource(
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    forecast_type: str = "forecast"
) -> Dict[str, Any]:
    """
    Fetches weather data from the National Weather Service API for a given location.
    
    Args:
        location: Address, city, or place name (US only)
        latitude: Latitude coordinate (decimal degrees)
        longitude: Longitude coordinate (decimal degrees)
        forecast_type: Type of forecast to retrieve ("forecast", "hourly", or "alerts")
        
    Returns:
        Dictionary with weather information
    """
    try:
        # Check if we have either location or coordinates
        if location is None and (latitude is None or longitude is None):
            return {
                "status": "error",
                "message": "Either location or both latitude and longitude must be provided"
            }
        
        # If we have a location string but no coordinates, try to find them
        if location and (latitude is None or longitude is None):
            # First check our common cities dictionary for faster resolution and better reliability
            location_lower = location.lower().strip()
            
            if location_lower in COMMON_US_CITIES:
                latitude, longitude = COMMON_US_CITIES[location_lower]
                logger.info(f"Found {location} in common cities dictionary: {latitude}, {longitude}")
            else:
                # Try geocoding services
                latitude, longitude = await get_geocode_from_address(location)
                
                if latitude is None or longitude is None:
                    return {
                        "status": "error",
                        "message": f"Could not geocode location: {location}. Try providing explicit coordinates or ensure location is in the US."
                    }
        
        # Now fetch the weather data using the coordinates
        return await fetch_weather_data(latitude, longitude, forecast_type)
    
    except Exception as e:
        logger.error(f"Error in weather_resource: {e}")
        return {
            "status": "error",
            "message": f"Error fetching weather data: {str(e)}"
        }

if __name__ == "__main__":
    logger.info("Starting Weather Resource MCP server")
    mcp.run(transport='stdio')
