"""
Gnosis Forge - FFmpeg API Service
A lightweight FFmpeg processing API for media transformation.
"""

import os
import tempfile
import subprocess
import base64
import shlex
import time
import logging
from pathlib import Path
from typing import Optional, Union
import magic
import asyncio
import json

from fastapi import FastAPI, File, UploadFile, Form, Header, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gnosis Forge",
    description="FFmpeg API Service for media processing and transformation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Request models
class ProcessImageRequest(BaseModel):
    ffmpeg_command: str
    image_data: str  # base64 encoded
    input_filename: Optional[str] = "input.jpg"

class ProcessResponse(BaseModel):
    success: bool
    output_image: Optional[str] = None
    output_filename: Optional[str] = None
    content_type: Optional[str] = None
    processing_time: Optional[float] = None
    message: str
    error: Optional[str] = None

class VideoSliceRequest(BaseModel):
    filename: str
    start_time: str  # "00:10:30" format
    duration: Optional[str] = None  # "00:00:30" format
    end_time: Optional[str] = None  # "00:11:00" format
    output_filename: Optional[str] = None

class WorkspaceProcessRequest(BaseModel):
    filename: str
    ffmpeg_command: str
    output_filename: Optional[str] = None

# Security: Allowed FFmpeg operations (whitelist approach)
ALLOWED_OPERATIONS = [
    '-vf', '-af', '-f', '-c:v', '-c:a', '-b:v', '-b:a', '-r', '-s', '-t', '-ss',
    'scale', 'crop', 'rotate', 'flip', 'flop', 'brightness', 'contrast', 'saturation',
    'hue', 'grayscale', 'sepia', 'blur', 'sharpen', 'noise', 'format', 'fps'
]

def validate_ffmpeg_command(command: str) -> bool:
    """Validate FFmpeg command for security."""
    # Basic security checks
    dangerous_patterns = [
        '../', '..\\', '/etc/', '/proc/', '/sys/', '/dev/',
        '&&', '||', ';', '|', '`', '$', '>', '<', '&'
    ]
    
    for pattern in dangerous_patterns:
        if pattern in command:
            logger.warning(f"Dangerous pattern detected in command: {pattern}")
            return False
    
    # Check if command starts with ffmpeg
    if not command.strip().startswith('ffmpeg'):
        logger.warning("Command doesn't start with ffmpeg")
        return False
    
    return True

def get_output_extension(ffmpeg_command: str) -> str:
    """Extract output file extension from FFmpeg command."""
    parts = shlex.split(ffmpeg_command)
    
    # Look for common output formats
    format_mappings = {
        'mp4': 'mp4',
        'avi': 'avi',
        'mov': 'mov',
        'webm': 'webm',
        'gif': 'gif',
        'png': 'png',
        'jpg': 'jpg',
        'jpeg': 'jpg',
        'webp': 'webp'
    }
    
    # Check for explicit format specification
    for i, part in enumerate(parts):
        if part == '-f' and i + 1 < len(parts):
            fmt = parts[i + 1].lower()
            if fmt in format_mappings:
                return format_mappings[fmt]
    
    # Check output filename extension
    if parts:
        last_part = parts[-1].lower()
        for ext in format_mappings:
            if last_part.endswith(f'.{ext}'):
                return format_mappings[ext]
    
    # Default to jpg for images
    return 'jpg'

async def process_with_ffmpeg(input_path: str, output_path: str, ffmpeg_command: str) -> dict:
    """Process file with FFmpeg."""
    start_time = time.time()
    
    try:
        # Replace input/output placeholders in command
        command = ffmpeg_command.replace('input.jpg', input_path)
        command = command.replace('input.png', input_path)
        command = command.replace('input.', input_path)
        
        # Replace output placeholders
        for ext in ['jpg', 'png', 'gif', 'mp4', 'webm']:
            command = command.replace(f'output.{ext}', output_path)
        
        # Parse command
        args = shlex.split(command)
        
        # Ensure we're using the correct ffmpeg binary
        if args[0] == 'ffmpeg':
            args[0] = '/root/bin/ffmpeg'
        
        logger.info(f"Executing FFmpeg command: {' '.join(args)}")
        
        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        processing_time = time.time() - start_time
        
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8') if stderr else "FFmpeg processing failed"
            logger.error(f"FFmpeg error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "processing_time": processing_time
            }
        
        # Check if output file was created
        if not os.path.exists(output_path):
            return {
                "success": False,
                "error": "Output file was not created",
                "processing_time": processing_time
            }
        
        return {
            "success": True,
            "processing_time": processing_time
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"FFmpeg processing exception: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "processing_time": processing_time
        }

@app.get("/", response_class=HTMLResponse)
async def get_documentation():
    """Return interactive API documentation."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gnosis Forge - FFmpeg API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; margin-top: 30px; }
            .endpoint { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .method { background: #3498db; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
            .example { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
            @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔥 Gnosis Forge - FFmpeg API Service</h1>
            
            <p>A powerful FFmpeg processing API that transforms media files through simple HTTP requests. 
            Supports multiple input formats and provides comprehensive media processing capabilities.</p>
            
            <h2>📡 API Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">POST</span> <strong>/process</strong> - Process media with FFmpeg commands
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <strong>/health</strong> - Health check endpoint
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span> <strong>/docs</strong> - OpenAPI documentation
            </div>
            
            <h2>🚀 Usage Examples</h2>
            
            <div class="grid">
                <div>
                    <h3>Binary Upload (Multipart)</h3>
                    <div class="example">curl -X POST http://localhost:6789/process \\
  -F "file=@input.jpg" \\
  -F "ffmpeg_command=ffmpeg -i input.jpg -vf 'scale=320:-1' output.jpg"</div>
                </div>
                
                <div>
                    <h3>JSON with Base64</h3>
                    <div class="example">curl -X POST http://localhost:6789/process \\
  -H "Content-Type: application/json" \\
  -d '{
    "ffmpeg_command": "ffmpeg -i input.jpg -vf \\"scale=320:-1\\" output.jpg",
    "image_data": "base64_encoded_data",
    "input_filename": "input.jpg"
  }'</div>
                </div>
                
                <div>
                    <h3>Binary with Headers</h3>
                    <div class="example">curl -X POST http://localhost:6789/process \\
  -H "Content-Type: image/jpeg" \\
  -H "X-FFmpeg-Command: ffmpeg -i input.jpg -vf 'scale=320:-1' output.jpg" \\
  --data-binary @input.jpg</div>
                </div>
                
                <div>
                    <h3>Response Format</h3>
                    <div class="example">{
  "success": true,
  "output_image": "base64_encoded_result",
  "output_filename": "output.jpg",
  "content_type": "image/jpeg",
  "processing_time": 1.23,
  "message": "Processing completed"
}</div>
                </div>
            </div>
            
            <h2>🎯 Common FFmpeg Operations</h2>
            
            <div class="grid">
                <div>
                    <h4>Image Operations</h4>
                    <ul>
                        <li><strong>Resize:</strong> -vf "scale=320:-1"</li>
                        <li><strong>Crop:</strong> -vf "crop=300:200:10:10"</li>
                        <li><strong>Rotate:</strong> -vf "rotate=90*PI/180"</li>
                        <li><strong>Grayscale:</strong> -vf "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3"</li>
                        <li><strong>Blur:</strong> -vf "boxblur=2:1"</li>
                    </ul>
                </div>
                
                <div>
                    <h4>Format Conversions</h4>
                    <ul>
                        <li><strong>JPEG to PNG:</strong> -f png output.png</li>
                        <li><strong>PNG to JPEG:</strong> -f jpeg output.jpg</li>
                        <li><strong>To WebP:</strong> -f webp output.webp</li>
                        <li><strong>To GIF:</strong> -f gif output.gif</li>
                        <li><strong>Quality:</strong> -q:v 2 (1-31, lower=better)</li>
                    </ul>
                </div>
            </div>
            
            <h2>⚡ Features</h2>
            <ul>
                <li>✅ Multiple input formats (binary, base64, headers)</li>
                <li>✅ Comprehensive FFmpeg 6.1.1 with major codecs</li>
                <li>✅ Automatic format detection and validation</li>
                <li>✅ Security-hardened command execution</li>
                <li>✅ Detailed error handling and logging</li>
                <li>✅ Docker support for easy deployment</li>
                <li>✅ Cloud Run optimized</li>
            </ul>
            
            <p><em>Part of the Gnosis ecosystem - transforming media with the power of FFmpeg.</em></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "gnosis-forge", "version": "1.0.0"}

@app.post("/slice-video", response_model=ProcessResponse)
async def slice_video(request: VideoSliceRequest):
    """Slice a video file from the workspace directory."""
    try:
        # Build input path from workspace
        input_path = f"/app/workspace/{request.filename}"
        
        # Check if file exists
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail=f"Video file '{request.filename}' not found in workspace")
        
        # Generate output filename
        if request.output_filename:
            output_filename = request.output_filename
        else:
            name, ext = os.path.splitext(request.filename)
            output_filename = f"{name}_slice_{request.start_time.replace(':', '-')}{ext}"
        
        output_path = f"/app/workspace/{output_filename}"
        
        # Build FFmpeg command for slicing
        cmd_parts = ['/root/bin/ffmpeg', '-y', '-i', input_path, '-ss', request.start_time]
        
        if request.duration:
            cmd_parts.extend(['-t', request.duration])
        elif request.end_time:
            cmd_parts.extend(['-to', request.end_time])
        
        # Add codec copy for fast processing
        cmd_parts.extend(['-c', 'copy', output_path])
        
        start_time = time.time()
        
        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        processing_time = time.time() - start_time
        
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8') if stderr else "Video slicing failed"
            logger.error(f"FFmpeg error: {error_msg}")
            return ProcessResponse(
                success=False,
                message="Video slicing failed",
                error=error_msg,
                processing_time=processing_time
            )
        
        return ProcessResponse(
            success=True,
            output_filename=output_filename,
            processing_time=processing_time,
            message=f"Video sliced successfully: {output_filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Video slicing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/process-workspace-file", response_model=ProcessResponse)
async def process_workspace_file(request: WorkspaceProcessRequest):
    """Process a file from the workspace directory with custom FFmpeg command."""
    try:
        # Build input path from workspace
        input_path = f"/app/workspace/{request.filename}"
        
        # Check if file exists
        if not os.path.exists(input_path):
            raise HTTPException(status_code=404, detail=f"File '{request.filename}' not found in workspace")
        
        # Generate output filename
        if request.output_filename:
            output_filename = request.output_filename
        else:
            name, ext = os.path.splitext(request.filename)
            output_filename = f"processed_{name}{ext}"
        
        output_path = f"/app/workspace/{output_filename}"
        
        # Replace placeholders in FFmpeg command
        ffmpeg_command = request.ffmpeg_command
        ffmpeg_command = ffmpeg_command.replace("INPUT_FILE", input_path)
        ffmpeg_command = ffmpeg_command.replace("OUTPUT_FILE", output_path)
        
        # Also support the old placeholders for compatibility
        ffmpeg_command = ffmpeg_command.replace("/app/workspace/" + request.filename, input_path)
        ffmpeg_command = ffmpeg_command.replace("/app/workspace/" + output_filename, output_path)
        
        # Validate command
        if not validate_ffmpeg_command(ffmpeg_command):
            raise HTTPException(status_code=400, detail="Invalid or unsafe FFmpeg command")
        
        # Parse and execute command
        args = shlex.split(ffmpeg_command)
        if args[0] == 'ffmpeg':
            args[0] = '/root/bin/ffmpeg'
        
        # Add overwrite flag if not present
        if '-y' not in args:
            args.insert(1, '-y')
        
        start_time = time.time()
        logger.info(f"Executing FFmpeg command: {' '.join(args)}")
        
        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        processing_time = time.time() - start_time
        
        if process.returncode != 0:
            error_msg = stderr.decode('utf-8') if stderr else "FFmpeg processing failed"
            logger.error(f"FFmpeg error: {error_msg}")
            return ProcessResponse(
                success=False,
                message="FFmpeg processing failed",
                error=error_msg,
                processing_time=processing_time
            )
        
        # Check if output file was created
        if not os.path.exists(output_path):
            return ProcessResponse(
                success=False,
                message="Output file was not created",
                error="FFmpeg did not produce output file",
                processing_time=processing_time
            )
        
        return ProcessResponse(
            success=True,
            output_filename=output_filename,
            processing_time=processing_time,
            message=f"File processed successfully: {output_filename}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workspace file processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/workspace-files")
async def list_workspace_files():
    """List files in the workspace directory."""
    try:
        workspace_path = "/app/workspace"
        if not os.path.exists(workspace_path):
            return {"files": [], "message": "Workspace directory not found"}
        
        files = []
        for item in os.listdir(workspace_path):
            item_path = os.path.join(workspace_path, item)
            if os.path.isfile(item_path):
                stat = os.stat(item_path)
                files.append({
                    "name": item,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        
        return {"files": files, "workspace_path": workspace_path}
        
    except Exception as e:
        logger.error(f"Error listing workspace files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

@app.post("/process", response_model=ProcessResponse)
async def process_media(
    request: Request,
    # Multipart form data
    file: Optional[UploadFile] = File(None),
    ffmpeg_command: Optional[str] = Form(None),
    # Header-based binary upload
    x_ffmpeg_command: Optional[str] = Header(None),
    accept: str = Header("application/json")
):
    """Process media using FFmpeg commands."""
    
    input_data = None
    input_filename = "input"
    command = None
    
    try:
        content_type = request.headers.get("content-type", "").lower()
        
        # Determine input method and extract data
        if "multipart/form-data" in content_type:
            # Method 1: Multipart form upload
            if not file or not ffmpeg_command:
                raise HTTPException(status_code=400, detail="Missing file or ffmpeg_command in form data")
            
            input_data = await file.read()
            input_filename = file.filename or "input"
            command = ffmpeg_command
            
        elif "application/json" in content_type:
            # Method 2: JSON with base64
            json_data = await request.json()
            
            if not isinstance(json_data, dict):
                raise HTTPException(status_code=400, detail="Invalid JSON format")
            
            command = json_data.get("ffmpeg_command")
            image_data_b64 = json_data.get("image_data")
            input_filename = json_data.get("input_filename", "input")
            
            if not command or not image_data_b64:
                raise HTTPException(status_code=400, detail="Missing ffmpeg_command or image_data")
            
            try:
                input_data = base64.b64decode(image_data_b64)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64 data: {str(e)}")
                
        elif content_type.startswith("image/") or content_type.startswith("video/"):
            # Method 3: Binary data with headers
            if not x_ffmpeg_command:
                raise HTTPException(status_code=400, detail="Missing X-FFmpeg-Command header")
            
            input_data = await request.body()
            command = x_ffmpeg_command
            
            # Determine filename from content type
            ext_map = {
                "image/jpeg": "jpg",
                "image/png": "png", 
                "image/gif": "gif",
                "image/webp": "webp",
                "video/mp4": "mp4",
                "video/webm": "webm"
            }
            ext = ext_map.get(content_type, "jpg")
            input_filename = f"input.{ext}"
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported content type")
        
        # Validate command
        if not validate_ffmpeg_command(command):
            raise HTTPException(status_code=400, detail="Invalid or unsafe FFmpeg command")
        
        # Validate input data
        if not input_data:
            raise HTTPException(status_code=400, detail="No input data received")
        
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Input file
            input_path = os.path.join(temp_dir, input_filename)
            with open(input_path, 'wb') as f:
                f.write(input_data)
            
            # Output file
            output_ext = get_output_extension(command)
            output_filename = f"output.{output_ext}"
            output_path = os.path.join(temp_dir, output_filename)
            
            # Process with FFmpeg
            result = await process_with_ffmpeg(input_path, output_path, command)
            
            if not result["success"]:
                return ProcessResponse(
                    success=False,
                    message="FFmpeg processing failed",
                    error=result.get("error", "Unknown error"),
                    processing_time=result.get("processing_time")
                )
            
            # Read output file
            if not os.path.exists(output_path):
                return ProcessResponse(
                    success=False,
                    message="Output file not created",
                    error="FFmpeg did not produce output file"
                )
            
            with open(output_path, 'rb') as f:
                output_data = f.read()
            
            # Determine content type
            mime = magic.Magic(mime=True)
            detected_type = mime.from_buffer(output_data)
            
            # Return response
            return ProcessResponse(
                success=True,
                output_image=base64.b64encode(output_data).decode('utf-8'),
                output_filename=output_filename,
                content_type=detected_type,
                processing_time=result.get("processing_time"),
                message="Processing completed successfully"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6789)
