#!/usr/bin/env python3
"""
Test script for Gnosis Forge FFmpeg API
Processes sample.png from the workspace directory
"""

import requests
import json
from pathlib import Path

# API endpoint
API_BASE = "http://localhost:8000"

def test_workspace_files():
    """List files in workspace to verify sample.png exists"""
    print("🔍 Listing workspace files...")
    response = requests.get(f"{API_BASE}/workspace-files")
    
    if response.status_code == 200:
        data = response.json()
        files = data.get('files', [])
        print(f"Found {len(files)} files:")
        for file in files:
            print(f"  - {file['name']} ({file['size']} bytes)")
        
        # Check if sample.png exists
        png_files = [f for f in files if f['name'].endswith('.png')]
        if png_files:
            print(f"✅ Found PNG files: {[f['name'] for f in png_files]}")
            return png_files[0]['name']  # Return first PNG file
        else:
            print("❌ No PNG files found in workspace")
            return None
    else:
        print(f"❌ Error listing files: {response.status_code}")
        return None

def test_workspace_processing(filename):
    """Process an image directly from workspace using the new endpoint"""
    print(f"\n🎨 Processing {filename} directly from workspace...")
    
    # FFmpeg command to:
    # 1. Resize to 320px wide (maintaining aspect ratio)
    # 2. Add a blue border
    # 3. Save as processed_[filename]
    output_name = f"processed_{filename}"
    
    # Use INPUT_FILE and OUTPUT_FILE placeholders
    ffmpeg_command = f'ffmpeg -i INPUT_FILE -vf "scale=320:-1,pad=340:ih+20:10:10:color=blue" -q:v 2 OUTPUT_FILE'
    
    payload = {
        "filename": filename,
        "ffmpeg_command": ffmpeg_command,
        "output_filename": output_name
    }
    
    print(f"📤 Sending workspace processing request...")
    print(f"   Input: {filename}")
    print(f"   Output: {output_name}")
    print(f"   Command: {ffmpeg_command}")
    
    response = requests.post(
        f"{API_BASE}/process-workspace-file", 
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            print(f"✅ Processing successful!")
            print(f"   Output: {result.get('output_filename', 'N/A')}")
            print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
            print(f"   Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            return False
    else:
        print(f"❌ API request failed: {response.status_code}")
        try:
            error_data = response.json()
            print(f"   Error: {error_data.get('detail', 'Unknown error')}")
        except:
            print(f"   Raw response: {response.text}")
        return False

def test_direct_workspace_processing():
    """Test processing a file directly in the workspace without upload"""
    print("\n🔧 Testing direct workspace file processing...")
    
    # Use a simpler approach - direct FFmpeg command on workspace files
    # This creates a grayscale version of any PNG file found
    
    response = requests.get(f"{API_BASE}/workspace-files")
    if response.status_code != 200:
        print("❌ Cannot list workspace files")
        return
    
    files = response.json().get('files', [])
    png_file = next((f['name'] for f in files if f['name'].endswith('.png')), None)
    
    if not png_file:
        print("❌ No PNG file found to process")
        return
    
    # Simple grayscale conversion command
    output_name = f"grayscale_{png_file}"
    ffmpeg_cmd = f"ffmpeg -y -i /app/workspace/{png_file} -vf grayscale /app/workspace/{output_name}"
    
    print(f"🎯 Processing: {png_file} -> {output_name}")
    print(f"Command: {ffmpeg_cmd}")
    
    # This won't work with the current API since it expects image data
    # But shows the concept - we need a workspace-specific endpoint
    
def main():
    print("🚀 Testing Gnosis Forge FFmpeg API")
    print("=" * 50)
    
    # Test 1: List workspace files
    png_file = test_workspace_files()
    
    if png_file:
        # Test 2: Process the image using the new workspace endpoint
        if test_workspace_processing(png_file):
            print("✅ Workspace processing successful!")
        else:
            print("❌ Workspace processing failed!")
    
    print("\n📋 Summary:")
    print("- Used the new /process-workspace-file endpoint")
    print("- No file uploads needed - processes files directly from workspace")
    print("- Check the workspace directory for processed output files")
    
    # List files again to see if anything was created
    print("\n🔍 Final workspace check...")
    test_workspace_files()

if __name__ == "__main__":
    main()
