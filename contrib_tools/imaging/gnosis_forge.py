"""
Gnosis Forge MCP Tool - FFmpeg API Interface
============================================

A comprehensive MCP tool for communicating with the Gnosis Forge FFmpeg API container
running locally on localhost:8000. This tool provides full access to FFmpeg's powerful
media processing capabilities through a clean REST API interface.

Features:
- Image processing (resize, crop, rotate, filters, effects)
- Format conversion (JPEG, PNG, WebP, GIF, and more)
- Video processing and manipulation
- Base64 and binary file handling
- Comprehensive error handling and validation
- Multiple input methods (form data, JSON, binary with headers)

The Gnosis Forge container must be running locally on port 8000 for this tool to function.
"""

import sys
import os
import logging
import json
import requests
import base64
import time
from typing import Dict, Any, Optional, Union
from mcp.server.fastmcp import FastMCP, Context
from pathlib import Path

__version__ = "1.0.1"
__updated__ = "2025-05-28"

# Setup logging
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
logs_dir = os.path.join(parent_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)

log_file = os.path.join(logs_dir, "gnosis_forge.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(log_file)]
)
logger = logging.getLogger("gnosis_forge")

# Initialize MCP server
mcp = FastMCP("gnosis-forge-server")

# Forge API configuration
FORGE_BASE_URL = "http://localhost:6789"
DEFAULT_TIMEOUT = 60

def validate_forge_connection() -> Dict[str, Any]:
    """Check if Gnosis Forge container is running and accessible."""
    try:
        response = requests.get(f"{FORGE_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            return {"connected": True, "service_info": response.json()}
        else:
            return {"connected": False, "error": f"Health check failed: {response.status_code}"}
    except requests.exceptions.ConnectionError:
        return {"connected": False, "error": "Connection refused - is Gnosis Forge container running on port 6789?"}
    except Exception as e:
        return {"connected": False, "error": f"Connection error: {str(e)}"}

def encode_file_to_base64(file_path: str) -> Optional[str]:
    """Read a file and encode it to base64."""
    try:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logger.error(f"Error encoding file {file_path}: {e}")
        return None

def save_base64_to_file(b64_data: str, output_path: str) -> bool:
    """Save base64 data to a file."""
    try:
        with open(output_path, 'wb') as f:
            f.write(base64.b64decode(b64_data))
        return True
    except Exception as e:
        logger.error(f"Error saving file {output_path}: {e}")
        return False

@mcp.tool()
async def process_image_ffmpeg(
    input_path: str,
    ffmpeg_command: str,
    output_path: Optional[str] = None,
    save_output: bool = True,
    timeout: int = DEFAULT_TIMEOUT,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Process an image file using FFmpeg commands through the Gnosis Forge API.
    
    Returns: {success, input_path, ffmpeg_command, processing_time, content_type, output_filename, message, output_path?, output_saved, output_image_b64?, save_error?}
    This tool reads a local image file, sends it to the Gnosis Forge container for processing
    with the specified FFmpeg command, and optionally saves the result back to disk.
    
    Args:
        input_path: Path to the input image file to process
        ffmpeg_command: FFmpeg command to execute (e.g., 'ffmpeg -i input.jpg -vf "scale=320:-1" output.jpg')
        output_path: Optional path to save the processed image (auto-generated if not provided)
        save_output: Whether to save the processed image to disk (default: True)
        timeout: Request timeout in seconds (default: 60)
        ctx: Context object for logging and progress reporting
        
    Returns:
        Dictionary containing processing results, output paths, and metadata
        
    Example:
        # Resize an image to 320px width maintaining aspect ratio
        result = await process_image_ffmpeg(
            input_path="photo.jpg",
            ffmpeg_command='ffmpeg -i input.jpg -vf "scale=320:-1" output.jpg'
        )
    """
    if ctx:
        await ctx.info(f"Processing image: {input_path}")
        await ctx.report_progress(progress=0, total=100)
    
    # Validate connection first
    connection = validate_forge_connection()
    if not connection["connected"]:
        error_msg = f"Gnosis Forge not accessible: {connection['error']}"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Check if input file exists
    if not os.path.exists(input_path):
        error_msg = f"Input file not found: {input_path}"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Encode input file to base64
    if ctx:
        await ctx.info("Encoding input file...")
        await ctx.report_progress(progress=20, total=100)
    
    b64_data = encode_file_to_base64(input_path)
    if not b64_data:
        error_msg = f"Failed to encode input file: {input_path}"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Prepare request payload
    input_filename = os.path.basename(input_path)
    payload = {
        "ffmpeg_command": ffmpeg_command,
        "image_data": b64_data,
        "input_filename": input_filename
    }
    
    try:
        if ctx:
            await ctx.info("Sending to Gnosis Forge for processing...")
            await ctx.report_progress(progress=40, total=100)
        
        # Send request to Forge API
        response = requests.post(
            f"{FORGE_BASE_URL}/process",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=timeout
        )
        
        if response.status_code != 200:
            error_msg = f"API request failed: {response.status_code} - {response.text}"
            if ctx:
                await ctx.error(error_msg)
            return {"success": False, "error": error_msg}
        
        result = response.json()
        
        if not result.get("success"):
            error_msg = f"Processing failed: {result.get('error', 'Unknown error')}"
            if ctx:
                await ctx.error(error_msg)
            return result
        
        if ctx:
            await ctx.info(f"Processing completed in {result.get('processing_time', 0):.2f}s")
            await ctx.report_progress(progress=80, total=100)
        
        # Handle output
        response_data = {
            "success": True,
            "input_path": input_path,
            "ffmpeg_command": ffmpeg_command,
            "processing_time": result.get("processing_time"),
            "content_type": result.get("content_type"),
            "output_filename": result.get("output_filename"),
            "message": result.get("message")
        }
        
        # Save output file if requested
        if save_output and result.get("output_image"):
            if not output_path:
                # Auto-generate output path
                input_name = Path(input_path).stem
                input_dir = Path(input_path).parent
                output_ext = result.get("output_filename", "output.jpg").split(".")[-1]
                output_path = str(input_dir / f"{input_name}_processed.{output_ext}")
            
            if save_base64_to_file(result["output_image"], output_path):
                response_data["output_path"] = output_path
                response_data["output_saved"] = True
                if ctx:
                    await ctx.info(f"Output saved to: {output_path}")
            else:
                response_data["output_saved"] = False
                response_data["save_error"] = f"Failed to save output to {output_path}"
        else:
            # Include base64 data for programmatic use
            response_data["output_image_b64"] = result.get("output_image")
            response_data["output_saved"] = False
        
        if ctx:
            await ctx.report_progress(progress=100, total=100)
        
        return response_data
        
    except requests.exceptions.Timeout:
        error_msg = f"Request timeout after {timeout} seconds"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Processing error: {str(e)}"
        if ctx:
            await ctx.error(error_msg)
        logger.error(error_msg, exc_info=True)
        return {"success": False, "error": error_msg}

@mcp.tool()
async def resize_image(
    input_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    maintain_aspect: bool = True,
    output_path: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Resize an image to specified dimensions using FFmpeg.
    
    Returns: {success, input_path, ffmpeg_command, processing_time, content_type, output_filename, message, output_path?, output_saved, output_image_b64?, save_error?}
    This is a convenience function that generates the appropriate FFmpeg scale command
    and processes the image through the Gnosis Forge API.
    
    Args:
        input_path: Path to the input image file
        width: Target width in pixels (optional if height is provided)
        height: Target height in pixels (optional if width is provided)
        maintain_aspect: Whether to maintain aspect ratio (default: True)
        output_path: Optional path to save the resized image
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary containing processing results and output information
        
    Example:
        # Resize to 800px width maintaining aspect ratio
        result = await resize_image("photo.jpg", width=800)
        
        # Resize to exact 800x600 dimensions
        result = await resize_image("photo.jpg", width=800, height=600, maintain_aspect=False)
    """
    if not width and not height:
        error_msg = "Either width or height must be specified"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Build FFmpeg scale command
    if maintain_aspect:
        if width and not height:
            scale_filter = f"scale={width}:-1"
        elif height and not width:
            scale_filter = f"scale=-1:{height}"
        else:
            # Both specified, use width and calculate height proportionally
            scale_filter = f"scale={width}:-1"
    else:
        # Exact dimensions
        w = width or -1
        h = height or -1
        scale_filter = f"scale={w}:{h}"
    
    ffmpeg_command = f'ffmpeg -i input.jpg -vf "{scale_filter}" output.jpg'
    
    if ctx:
        await ctx.info(f"Resizing image with command: {ffmpeg_command}")
    
    return await process_image_ffmpeg(
        input_path=input_path,
        ffmpeg_command=ffmpeg_command,
        output_path=output_path,
        ctx=ctx
    )

@mcp.tool()
async def convert_image_format(
    input_path: str,
    output_format: str,
    quality: Optional[int] = None,
    output_path: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Convert an image to a different format using FFmpeg.
    
    Returns: {success, input_path, ffmpeg_command, processing_time, content_type, output_filename, message, output_path?, output_saved, output_image_b64?, save_error?}
    Supports conversion between common image formats including JPEG, PNG, WebP, GIF, etc.
    
    Args:
        input_path: Path to the input image file
        output_format: Target format (jpeg, png, webp, gif, bmp, tiff)
        quality: Quality setting for lossy formats (1-31 for JPEG, lower is better)
        output_path: Optional path to save the converted image
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary containing conversion results and output information
        
    Example:
        # Convert JPEG to PNG
        result = await convert_image_format("photo.jpg", "png")
        
        # Convert to WebP with quality setting
        result = await convert_image_format("photo.jpg", "webp", quality=85)
    """
    # Validate format
    supported_formats = ["jpeg", "jpg", "png", "webp", "gif", "bmp", "tiff", "tif"]
    if output_format.lower() not in supported_formats:
        error_msg = f"Unsupported format: {output_format}. Supported: {', '.join(supported_formats)}"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Normalize format name
    format_name = output_format.lower()
    if format_name == "jpg":
        format_name = "jpeg"
    elif format_name == "tif":
        format_name = "tiff"
    
    # Build FFmpeg command
    command_parts = ["ffmpeg", "-i", "input.jpg"]
    
    if quality and format_name in ["jpeg", "webp"]:
        if format_name == "jpeg":
            command_parts.extend(["-q:v", str(quality)])
        elif format_name == "webp":
            command_parts.extend(["-quality", str(quality)])
    
    command_parts.extend(["-f", format_name, f"output.{format_name}"])
    ffmpeg_command = " ".join(command_parts)
    
    if ctx:
        await ctx.info(f"Converting to {output_format.upper()} with command: {ffmpeg_command}")
    
    return await process_image_ffmpeg(
        input_path=input_path,
        ffmpeg_command=ffmpeg_command,
        output_path=output_path,
        ctx=ctx
    )

@mcp.tool()
async def apply_image_filter(
    input_path: str,
    filter_type: str,
    intensity: Optional[float] = None,
    output_path: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Apply various visual filters and effects to an image using FFmpeg.
    
    Returns: {success, input_path, ffmpeg_command, processing_time, content_type, output_filename, message, output_path?, output_saved, output_image_b64?, save_error?}
    Supports common image filters like blur, sharpen, grayscale, sepia, brightness, contrast, etc.
    
    Args:
        input_path: Path to the input image file
        filter_type: Type of filter to apply (blur, sharpen, grayscale, sepia, brightness, contrast, saturation)
        intensity: Filter intensity/strength (meaning varies by filter type)
        output_path: Optional path to save the filtered image
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary containing filtering results and output information
        
    Example:
        # Apply blur effect
        result = await apply_image_filter("photo.jpg", "blur", intensity=2.0)
        
        # Convert to grayscale
        result = await apply_image_filter("photo.jpg", "grayscale")
        
        # Increase brightness
        result = await apply_image_filter("photo.jpg", "brightness", intensity=0.2)
    """
    # Define available filters
    filters = {
        "blur": "boxblur={intensity}:1",
        "sharpen": "unsharp=5:5:{intensity}:5:5:0.0",
        "grayscale": "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3",
        "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131",
        "brightness": "eq=brightness={intensity}",
        "contrast": "eq=contrast={intensity}",
        "saturation": "eq=saturation={intensity}",
        "hflip": "hflip",
        "vflip": "vflip"
    }
    
    if filter_type not in filters:
        error_msg = f"Unsupported filter: {filter_type}. Available: {', '.join(filters.keys())}"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Build filter string
    filter_str = filters[filter_type]
    
    # Apply intensity if required and provided
    if "{intensity}" in filter_str:
        if intensity is None:
            # Set defaults based on filter type
            defaults = {
                "blur": 2.0,
                "sharpen": 1.0,
                "brightness": 0.1,
                "contrast": 1.2,
                "saturation": 1.3
            }
            intensity = defaults.get(filter_type, 1.0)
        
        filter_str = filter_str.format(intensity=intensity)
    
    ffmpeg_command = f'ffmpeg -i input.jpg -vf "{filter_str}" output.jpg'
    
    if ctx:
        await ctx.info(f"Applying {filter_type} filter with command: {ffmpeg_command}")
    
    return await process_image_ffmpeg(
        input_path=input_path,
        ffmpeg_command=ffmpeg_command,
        output_path=output_path,
        ctx=ctx
    )

@mcp.tool()
async def crop_image(
    input_path: str,
    width: int,
    height: int,
    x_offset: int = 0,
    y_offset: int = 0,
    output_path: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Crop an image to specified dimensions and position using FFmpeg.
    
    Returns: {success, input_path, ffmpeg_command, processing_time, content_type, output_filename, message, output_path?, output_saved, output_image_b64?, save_error?}
    
    Args:
        input_path: Path to the input image file
        width: Width of the crop area in pixels
        height: Height of the crop area in pixels
        x_offset: Horizontal offset from left edge (default: 0)
        y_offset: Vertical offset from top edge (default: 0)
        output_path: Optional path to save the cropped image
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary containing cropping results and output information
        
    Example:
        # Crop 300x200 area from top-left corner
        result = await crop_image("photo.jpg", width=300, height=200)
        
        # Crop 400x300 area starting at position (50, 100)
        result = await crop_image("photo.jpg", width=400, height=300, x_offset=50, y_offset=100)
    """
    if width <= 0 or height <= 0:
        error_msg = "Width and height must be positive integers"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    
    if x_offset < 0 or y_offset < 0:
        error_msg = "Offsets must be non-negative"
        if ctx:
            await ctx.error(error_msg)
        return {"success": False, "error": error_msg}
    
    # Build crop filter
    crop_filter = f"crop={width}:{height}:{x_offset}:{y_offset}"
    ffmpeg_command = f'ffmpeg -i input.jpg -vf "{crop_filter}" output.jpg'
    
    if ctx:
        await ctx.info(f"Cropping image: {width}x{height} at ({x_offset}, {y_offset})")
    
    return await process_image_ffmpeg(
        input_path=input_path,
        ffmpeg_command=ffmpeg_command,
        output_path=output_path,
        ctx=ctx
    )

@mcp.tool()
async def rotate_image(
    input_path: str,
    angle: float,
    background_color: str = "black",
    output_path: Optional[str] = None,
    ctx: Context = None
) -> Dict[str, Any]:
    """
    Rotate an image by a specified angle using FFmpeg.
    
    Returns: {success, input_path, ffmpeg_command, processing_time, content_type, output_filename, message, output_path?, output_saved, output_image_b64?, save_error?}
    
    Args:
        input_path: Path to the input image file
        angle: Rotation angle in degrees (positive = clockwise, negative = counterclockwise)
        background_color: Background color for areas outside the rotated image (default: "black")
        output_path: Optional path to save the rotated image
        ctx: Context object for logging and progress
        
    Returns:
        Dictionary containing rotation results and output information
        
    Example:
        # Rotate 90 degrees clockwise
        result = await rotate_image("photo.jpg", angle=90)
        
        # Rotate 45 degrees with white background
        result = await rotate_image("photo.jpg", angle=45, background_color="white")
    """
    # Convert degrees to radians for FFmpeg
    radians = angle * 3.14159265359 / 180
    
    # Build rotate filter
    rotate_filter = f"rotate={radians}:fillcolor={background_color}"
    ffmpeg_command = f'ffmpeg -i input.jpg -vf "{rotate_filter}" output.jpg'
    
    if ctx:
        await ctx.info(f"Rotating image by {angle} degrees")
    
    return await process_image_ffmpeg(
        input_path=input_path,
        ffmpeg_command=ffmpeg_command,
        output_path=output_path,
        ctx=ctx
    )

@mcp.tool()
async def check_forge_status(ctx: Context = None) -> Dict[str, Any]:
    """
    Check the status and availability of the Gnosis Forge API container.
    
    Returns: {connected, service?, version?, status?, base_url, message, error?, troubleshooting?}
    This tool verifies that the Gnosis Forge container is running and accessible
    on localhost:8000, and returns service information.
    
    Args:
        ctx: Context object for logging
        
    Returns:
        Dictionary with connection status and service information
        
    Example:
        result = await check_forge_status()
        if result["connected"]:
            print("Gnosis Forge is ready!")
    """
    if ctx:
        await ctx.info("Checking Gnosis Forge container status...")
    
    connection = validate_forge_connection()
    
    if connection["connected"]:
        service_info = connection.get("service_info", {})
        result = {
            "connected": True,
            "service": service_info.get("service", "gnosis-forge"),
            "version": service_info.get("version", "unknown"),
            "status": service_info.get("status", "healthy"),
            "base_url": FORGE_BASE_URL,
            "message": "Gnosis Forge is running and accessible"
        }
        if ctx:
            await ctx.info("Gnosis Forge is ready for image processing")
    else:
        result = {
            "connected": False,
            "error": connection["error"],
            "base_url": FORGE_BASE_URL,
            "message": "Gnosis Forge container is not accessible",
            "troubleshooting": [
                "Ensure Docker is running",
                "Start Gnosis Forge container: docker run -p 6789:6789 gnosis-forge",
                "Check if port 6789 is available",
                "Verify container logs for errors"
            ]
        }
        if ctx:
            await ctx.error(f"Error: {connection['error']}")
    
    return result

# Start the MCP server
if __name__ == "__main__":
    try:
        logger.info(f"Starting Gnosis Forge MCP Tool v{__version__}")
        mcp.run(transport='stdio')
    except Exception as e:
        logger.critical(f"Failed to start: {str(e)}", exc_info=True)
        sys.exit(1)
