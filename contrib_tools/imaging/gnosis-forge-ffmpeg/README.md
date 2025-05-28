# Gnosis Forge FFmpeg: Local Media Processing API

## What This Is

A Docker container that runs FFmpeg locally, providing a clean REST API for media processing operations. Designed to work seamlessly with Claude Desktop via [Gnosis Evolve](https://github.com/kordless/EvolveMCP).

**For Claude Desktop users:** Start the container in your working directory, and Claude can process your images/videos directly using natural language.

**For developers:** A comprehensive REST API wrapper around FFmpeg 7.1 with extensive codec support and multiple input methods.

## Quick Start for Claude Desktop Users

### Prerequisites
- **Docker Desktop** installed and running
- **[Gnosis Evolve](https://github.com/kordless/EvolveMCP)** installed and configured with Claude Desktop

**Install Docker Desktop:**
- Download from [docker.com](https://www.docker.com/products/docker-desktop/)
- Install and start Docker Desktop
- Verify it's running (Docker icon in system tray)

**Install Gnosis Evolve:**
1. Download and extract the [latest release](https://github.com/kordless/EvolveMCP/archive/refs/tags/v1.1.0.zip)
2. Run setup:
   - **Windows**: `.\evolve.ps1 -Setup`
   - **macOS**: `./evolve.sh --setup`
3. Install the Gnosis Forge MCP tool: Ask Claude to `"Install the Gnosis Forge FFmpeg tool"`

**Build the Container:**
1. Navigate to: `gnosis-forge/ffmpeg/`
2. Run the build script:
   - **Windows**: `.\dev.ps1`
   - **macOS**: Coming soon
3. Wait for the build to complete (this may take several minutes)

### Using with Claude Desktop
1. **Start the container in your project directory:**
```bash
cd /path/to/your/images
docker run -p 6789:6789 -v $(pwd):/workspace gnosis-forge-ffmpeg
```

2. **Talk to Claude Desktop:**
```
"Resize photo.jpg to 800px wide"
"Convert vacation.mp4 to a GIF" 
"Make headshot.png square and save as profile.png"
"Apply a blur effect to background.jpg"
```

That's it. Claude handles the FFmpeg commands, the container processes your files, and results appear in your current directory.

### What Claude Can Do For You
```
# Image operations
"Resize banner.jpg to 1920x1080"
"Convert screenshot.png to WebP format with 90% quality"
"Crop profile.jpg to 400x400 from the center"
"Rotate logo.png by 45 degrees"
"Make document.jpg grayscale"
"Apply a subtle blur to background.jpg"

# Video operations  
"Convert presentation.mp4 to a 10fps GIF"
"Extract frame 30 from video.mp4 as thumbnail.jpg"
"Resize movie.mp4 to 720p"

# Complex filter chains
"Apply blur and sharpen with brightness adjustment"
"Create thumbnail with rounded corners and shadow"
```

---

## For Developers: The REST API

## Why This Exists

**The Problem:** Every developer has been there. You need to resize an image, transcode a video, or apply a filter. So you:

1. Install multiple conflicting Python libraries
2. Write boilerplate code for what should be simple operations
3. Deal with dependency hell and version conflicts
4. Discover your "simple" image processing now requires 3GB of dependencies

**Our Solution:** One Docker container. Full FFmpeg power. Clean API. Zero dependencies.

## What This Actually Is

A containerized REST API that wraps FFmpeg 7.1 behind a clean interface designed for both direct use and AI agent consumption.

- **One Docker container** - No dependency management
- **Three input methods** - Multipart uploads, JSON+Base64, or binary+headers
- **Full FFmpeg capabilities** - Every codec, filter, and operation FFmpeg supports
- **Security built-in** - Command validation and sandboxed execution
- **AI-friendly design** - Clear documentation and consistent responses

## Performance Characteristics

Based on comprehensive benchmarking with our test suite (`python benchmark.py`):

| Operation Type | Average Time | Notes |
|---------------|--------------|-------|
| Image resize | ~175ms | Includes API overhead, validation, encoding |
| Filter effects | ~190-220ms | Blur, sharpen, brightness, contrast |
| Complex chains | ~190ms | Multiple filters in single operation |
| Simple operations | ~160ms | Basic crops, rotations |

**Performance Focus:** We prioritize capability and reliability over raw speed. Operations include full validation, proper error handling, and support for any FFmpeg operation - not just the basics.

**GPU Acceleration:** Container supports NVIDIA GPU acceleration when available, significantly improving performance for video operations.

**Comparison:** While specialized libraries like Pillow may be faster for basic operations, they can't handle the full spectrum of media processing tasks that FFmpeg enables.

## Three Ways to Use the API

### 1. Multipart Upload (For Humans)
```bash
curl -X POST localhost:6789/process \
  -F "file=@input.jpg" \
  -F "ffmpeg_command=ffmpeg -i input.jpg -vf 'scale=800:-1' output.jpg"
```

### 2. JSON + Base64 (For APIs)
```bash
curl -X POST localhost:6789/process \
  -H "Content-Type: application/json" \
  -d '{
    "ffmpeg_command": "ffmpeg -i input.jpg -vf \"scale=400:400\" output.jpg",
    "image_data": "'$(base64 -i input.jpg)'",
    "input_filename": "input.jpg"
  }'
```

### 3. Binary + Headers (For Minimalists)
```bash
curl -X POST localhost:6789/process \
  -H "Content-Type: image/jpeg" \
  -H "X-FFmpeg-Command: ffmpeg -i input.jpg -vf 'scale=320:-1' output.jpg" \
  --data-binary @input.jpg
```

## Container Setup Options

### Basic Usage (Files in Current Directory)
```bash
cd /path/to/your/media/files
docker run -p 6789:6789 -v $(pwd):/workspace gnosis-forge-ffmpeg
```

### Production Deployment
```bash
docker run -d \
  --name gnosis-forge \
  -p 6789:6789 \
  -v /path/to/media:/workspace \
  --restart unless-stopped \
  gnosis-forge-ffmpeg
```

### With GPU Support
```bash
docker run -d \
  --name gnosis-forge \
  --gpus all \
  -p 6789:6789 \
  -v /path/to/media:/workspace \
  gnosis-forge-ffmpeg
```

## FFmpeg Operations That Matter

```bash
# Image Operations
ffmpeg -i input.jpg -vf "scale=800:-1" output.jpg                    # Resize maintaining aspect
ffmpeg -i input.jpg -vf "crop=400:400:100:50" output.jpg            # Crop 400x400 from position
ffmpeg -i input.jpg -vf "rotate=PI/4:fillcolor=white" output.jpg     # Rotate 45 degrees

# Format Conversions
ffmpeg -i input.jpg -f webp -quality 85 output.webp                 # Convert to WebP
ffmpeg -i input.png -f jpeg -q:v 2 output.jpg                       # PNG to JPEG

# Filter Effects
ffmpeg -i input.jpg -vf "boxblur=2:1" output.jpg                    # Blur effect  
ffmpeg -i input.jpg -vf "unsharp=5:5:1.0:5:5:0.0" output.jpg       # Sharpen
ffmpeg -i input.jpg -vf "eq=brightness=0.2:contrast=1.5" output.jpg  # Brightness/contrast

# Complex Operations
ffmpeg -i input.jpg -vf "scale=400:400,boxblur=1:1,eq=brightness=0.1" output.jpg  # Chain multiple filters
ffmpeg -i video.mp4 -vf "fps=10,scale=320:-1:flags=lanczos" output.gif           # Video to optimized GIF
```

## What You Get Back

```json
{
  "success": true,
  "output_image": "base64_encoded_result",
  "output_filename": "output.jpg",
  "content_type": "image/jpeg",
  "processing_time": 0.175,
  "message": "Processing completed successfully"
}
```

Clean, consistent responses with all the data you need.

## Benchmarking & Validation

Run the included benchmark suite to validate performance on your hardware:

```bash
python benchmark.py
```

This generates detailed timing data and compares against common alternatives. Results are saved to `benchmark_results.json` for analysis.

## Security Model

- **Command Validation**: FFmpeg commands are validated against a whitelist
- **Sandboxed Execution**: All processing happens in isolated containers
- **Temporary Files**: Automatic cleanup after processing
- **Resource Limits**: Built-in protection against resource abuse
- **No Shell Access**: Commands are executed safely without shell interpretation

## Requirements

- Docker Desktop
- For Claude Desktop integration: [Gnosis Evolve](https://github.com/kordless/EvolveMCP)
- Optional: NVIDIA GPU for accelerated processing

## Part of the Gnosis Ecosystem

- **Gnosis Forge**: Synthetic API generation (this project)
- **Gnosis Wraith**: Web crawling and screenshots (`localhost:5678`)
- **Gnosis Evolve**: Code generation and tool evolution
- **Gnosis Wend**: AI service marketplace (coming soon)

---

**Local media processing. Full FFmpeg capabilities. AI-ready design.**
