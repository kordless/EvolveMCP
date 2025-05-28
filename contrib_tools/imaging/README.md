# Imaging Tools - Gnosis Evolve Contrib

Image processing, generation, and manipulation tools for AI agents and developers.

## Overview

The imaging category contains tools for visual content processing, transformation, and generation. These tools are designed to be easily consumable by AI agents while providing powerful image manipulation capabilities.

## Available Tools

### 🔥 Gnosis Forge FFmpeg (`gnosis-forge-ffmpeg/`)

**Purpose**: Comprehensive media processing API service using FFmpeg  
**Technology**: FastAPI + FFmpeg 7.1 + Docker  
**Status**: Production Ready ✅

#### Features
- **Multi-format Input**: Binary uploads, base64 JSON, direct binary with headers
- **Comprehensive Codecs**: H.264, H.265, VP8, VP9, AV1, MP3, AAC, Opus
- **Image Operations**: Resize, crop, rotate, filter, format conversion
- **Security**: Command validation, temporary file management
- **AI-Friendly**: Clear documentation, consistent API responses

#### Quick Start
```bash
cd gnosis-forge-ffmpeg/
docker build -t gnosis-forge-ffmpeg .
docker run -p 6789:6789 gnosis-forge-ffmpeg
curl http://localhost:6789/
```

#### Example Usage
```bash
# Resize image to 320px width (maintaining aspect ratio)
curl -X POST http://localhost:6789/process \
  -F "file=@input.jpg" \
  -F "ffmpeg_command=ffmpeg -i input.jpg -vf 'scale=320:-1' output.jpg"

# Convert PNG to JPEG
curl -X POST http://localhost:6789/process \
  -F "file=@input.png" \
  -F "ffmpeg_command=ffmpeg -i input.png -f jpeg output.jpg"

# Apply blur effect
curl -X POST http://localhost:6789/process \
  -F "file=@input.jpg" \
  -F "ffmpeg_command=ffmpeg -i input.jpg -vf 'boxblur=2:1' output.jpg"
```

#### Common Operations
- **Resize**: `-vf "scale=320:-1"` (width=320, auto height)
- **Crop**: `-vf "crop=300:200:10:10"` (width:height:x:y)
- **Rotate**: `-vf "rotate=90*PI/180"` (90 degrees)
- **Grayscale**: `-vf "colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3"`
- **Format**: `-f png`, `-f jpeg`, `-f webp`, `-f gif`

### 🛠️ Gnosis Forge MCP Tool (`gnosis_forge.py`)

**Purpose**: MCP tool interface for the Gnosis Forge FFmpeg API service  
**Technology**: FastMCP + Requests  
**Status**: Production Ready ✅

#### Features
- **Complete API Coverage**: All FFmpeg operations through clean MCP interface
- **Convenience Functions**: High-level tools for common operations
- **Error Handling**: Comprehensive validation and troubleshooting
- **Progress Reporting**: Real-time processing updates for AI agents
- **File Management**: Automatic encoding/decoding and path handling

#### Available Functions
```python
# Core processing function
await process_image_ffmpeg(input_path, ffmpeg_command, output_path=None)

# Convenience functions
await resize_image(input_path, width=800, height=600, maintain_aspect=True)
await convert_image_format(input_path, output_format="png", quality=85)
await apply_image_filter(input_path, filter_type="blur", intensity=2.0)
await crop_image(input_path, width=400, height=300, x_offset=50, y_offset=50)
await rotate_image(input_path, angle=90, background_color="white")
await check_forge_status()  # Health check
```

#### Usage Examples
```python
# Resize maintaining aspect ratio
result = await resize_image("photo.jpg", width=800)

# Convert format with quality
result = await convert_image_format("photo.jpg", "webp", quality=85)

# Apply multiple filters using raw FFmpeg
result = await process_image_ffmpeg(
    "photo.jpg", 
    'ffmpeg -i input.jpg -vf "scale=400:400,boxblur=1:1" output.jpg'
)
```

#### Response Format
All functions return consistent dictionaries:
```json
{
  "success": true,
  "input_path": "photo.jpg",
  "ffmpeg_command": "ffmpeg -i input.jpg -vf \"scale=800:-1\" output.jpg",
  "processing_time": 1.23,
  "content_type": "image/jpeg",
  "output_filename": "output.jpg",
  "output_path": "photo_processed.jpg",
  "output_saved": true,
  "message": "Processing completed successfully"
}
```

### 🌐 Gnosis Wraith (Coming Soon)

**Purpose**: Web screenshot and visual capture service  
**Technology**: Playwright + FastAPI + Docker  
**Status**: Migration in Progress 🚧

Will provide:
- Full-page screenshots
- Element-specific captures  
- Mobile/desktop viewport simulation
- PDF generation from web pages
- Visual regression testing

## Installation in Gnosis Evolve

### Using evolve_tool command:

#### Option 1: Install MCP Tool (Recommended)
```bash
# Install the MCP tool for direct integration
python evolve.py tool gnosis_forge --contrib_category imaging --contrib_name gnosis_forge
```

#### Option 2: Install FFmpeg Service
```bash
# Install the standalone FFmpeg service
python evolve.py tool gnosis-forge-ffmpeg --contrib_category imaging --contrib_name gnosis-forge-ffmpeg
```

### Manual Installation:
1. Copy the tool files to your Evolve tools directory
2. Add to Claude's MCP configuration
3. Restart Claude Desktop

## Usage Patterns

### Two Ways to Use Gnosis Forge

#### 1. Direct MCP Tool (Recommended)
Use the `gnosis_forge.py` MCP tool for seamless integration:
```python
# Check if service is running
status = await check_forge_status()

# Process images with high-level functions
result = await resize_image("photo.jpg", width=800)
result = await apply_image_filter("photo.jpg", "blur", intensity=2.0)

# Or use raw FFmpeg commands
result = await process_image_ffmpeg(
    "input.jpg", 
    'ffmpeg -i input.jpg -vf "scale=320:-1,boxblur=1:1" output.jpg'
)
```

#### 2. Direct API Service
Use the FFmpeg service directly via REST API:
```bash
# Start the service
docker run -p 8000:8000 gnosis-forge-ffmpeg

# Make requests
curl -X POST http://localhost:6789/process \
  -F "file=@input.jpg" \
  -F "ffmpeg_command=ffmpeg -i input.jpg -vf 'scale=320:-1' output.jpg"
```

## API Integration Patterns

### For AI Agents
These tools are designed with AI consumption in mind:

```python
# Example AI agent integration
def process_image_with_ai(image_path: str, operation: str):
    """Process image using Gnosis Forge"""
    
    operations = {
        "resize_small": ("resize_image", {"width": 320}),
        "make_square": ("resize_image", {"width": 400, "height": 400, "maintain_aspect": False}),
        "convert_png": ("convert_image_format", {"output_format": "png"}),
        "add_blur": ("apply_image_filter", {"filter_type": "blur", "intensity": 2.0}),
        "grayscale": ("apply_image_filter", {"filter_type": "grayscale"}),
        "crop_center": ("crop_image", {"width": 300, "height": 300, "x_offset": 50, "y_offset": 50})
    }
    
    if operation not in operations:
        return {"error": "Unknown operation"}
    
    func_name, params = operations[operation]
    # Call the appropriate MCP tool function
    return globals()[func_name](image_path, **params)
```

### Batch Processing
```python
# Process multiple images
async def batch_process_images(image_paths: list, operation: str):
    results = []
    for path in image_paths:
        if operation == "resize":
            result = await resize_image(path, width=800)
        elif operation == "convert":
            result = await convert_image_format(path, "webp", quality=85)
        results.append(result)
    return results
```

## Security Considerations

- **Command Validation**: All FFmpeg commands are validated for safety
- **Temporary Files**: Automatic cleanup of processing files
- **Resource Limits**: Built-in protection against resource abuse
- **File Access**: Restricted to specified input/output paths
- **Trusted Environment**: Designed for internal/development use

## Development

### Adding New Imaging Tools
1. Create service directory in `contrib_tools/imaging/`
2. Follow the established patterns:
   - FastAPI application structure
   - Docker containerization
   - Clear documentation at root endpoint
   - Consistent request/response formats
3. Create corresponding MCP tool interface
4. Update this README with tool information
5. Add installation instructions

### Testing
Each tool should include:
- Unit tests for core functionality
- API integration tests
- Example usage scripts
- Performance benchmarks

## Future Tools

Planned additions to the imaging category:
- **AI Image Generation**: DALL-E/Stable Diffusion API wrapper
- **OCR Service**: Text extraction from images
- **Computer Vision**: Object detection and analysis
- **Image Optimization**: Compression and format optimization
- **Batch Processing**: Multi-image processing workflows

## GitHub Repository

The Gnosis Forge project is available on GitHub:
**https://github.com/kordless/gnosis-forge**

Contains:
- Complete source code
- Docker configuration
- API documentation
- Usage examples
- Contributing guidelines

## Part of Gnosis Ecosystem

- **Gnosis Forge**: Synthetic API generation and embodiment
- **Gnosis Wraith**: Web crawling and visual capture
- **Gnosis Evolve**: Code generation and tool evolution
- **Gnosis Wend**: Service marketplace

*Making visual processing accessible to AI agents through clean, consistent APIs.*
