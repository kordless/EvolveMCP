"""
Gnosis Forge - API Usage Examples
Demonstrates various ways to use the FFmpeg API service.
"""

import requests
import base64
import json
from pathlib import Path

# Base URL for the service
BASE_URL = "http://localhost:8000"  # Change for production

def test_health():
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Health check passed:", response.json())
    else:
        print("❌ Health check failed:", response.status_code)

def example_multipart_upload():
    """Example: Upload image using multipart form data."""
    print("\n📤 Example: Multipart form upload")
    
    # Create a simple test image if it doesn't exist
    test_image_path = "test_input.jpg"
    if not Path(test_image_path).exists():
        print("Creating test image...")
        from PIL import Image
        img = Image.new('RGB', (400, 300), color='blue')
        img.save(test_image_path)
    
    # Upload with form data
    with open(test_image_path, 'rb') as f:
        files = {'file': f}
        data = {'ffmpeg_command': 'ffmpeg -i input.jpg -vf "scale=200:-1" output.jpg'}
        
        response = requests.post(f"{BASE_URL}/process", files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Processing successful!")
        print(f"   Processing time: {result['processing_time']:.2f}s")
        print(f"   Output filename: {result['output_filename']}")
        
        # Save the result
        if result['output_image']:
            output_data = base64.b64decode(result['output_image'])
            with open('output_multipart.jpg', 'wb') as f:
                f.write(output_data)
            print("   Saved to: output_multipart.jpg")
    else:
        print("❌ Processing failed:", response.status_code, response.text)

def example_json_base64():
    """Example: Send image as base64 JSON."""
    print("\n📦 Example: JSON with base64")
    
    # Create test image
    test_image_path = "test_input.jpg"
    if not Path(test_image_path).exists():
        from PIL import Image
        img = Image.new('RGB', (400, 300), color='red')
        img.save(test_image_path)
    
    # Read and encode image
    with open(test_image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Send JSON request
    payload = {
        "ffmpeg_command": "ffmpeg -i input.jpg -vf \"colorchannelmixer=.3:.4:.3:0:.3:.4:.3:0:.3:.4:.3\" output.jpg",
        "image_data": image_data,
        "input_filename": "input.jpg"
    }
    
    response = requests.post(
        f"{BASE_URL}/process",
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Processing successful!")
        print(f"   Processing time: {result['processing_time']:.2f}s")
        print(f"   Output type: {result['content_type']}")
        
        # Save the result
        if result['output_image']:
            output_data = base64.b64decode(result['output_image'])
            with open('output_json.jpg', 'wb') as f:
                f.write(output_data)
            print("   Saved to: output_json.jpg")
    else:
        print("❌ Processing failed:", response.status_code, response.text)

def example_binary_with_headers():
    """Example: Send binary data with command in headers."""
    print("\n🔧 Example: Binary with headers")
    
    # Create test image
    test_image_path = "test_input.jpg"
    if not Path(test_image_path).exists():
        from PIL import Image
        img = Image.new('RGB', (400, 300), color='green')
        img.save(test_image_path)
    
    # Send binary data with headers
    with open(test_image_path, 'rb') as f:
        response = requests.post(
            f"{BASE_URL}/process",
            data=f.read(),
            headers={
                'Content-Type': 'image/jpeg',
                'X-FFmpeg-Command': 'ffmpeg -i input.jpg -vf "boxblur=2:1" output.jpg'
            }
        )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Processing successful!")
        print(f"   Processing time: {result['processing_time']:.2f}s")
        print(f"   Output format: {result['output_filename']}")
        
        # Save the result
        if result['output_image']:
            output_data = base64.b64decode(result['output_image'])
            with open('output_binary.jpg', 'wb') as f:
                f.write(output_data)
            print("   Saved to: output_binary.jpg")
    else:
        print("❌ Processing failed:", response.status_code, response.text)

def example_format_conversion():
    """Example: Convert between image formats."""
    print("\n🔄 Example: Format conversion (JPEG to PNG)")
    
    # Create test JPEG
    test_image_path = "test_input.jpg"
    if not Path(test_image_path).exists():
        from PIL import Image
        img = Image.new('RGB', (300, 200), color='purple')
        img.save(test_image_path)
    
    # Convert to PNG
    with open(test_image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {
        "ffmpeg_command": "ffmpeg -i input.jpg -f png output.png",
        "image_data": image_data,
        "input_filename": "input.jpg"
    }
    
    response = requests.post(f"{BASE_URL}/process", json=payload)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Conversion successful!")
        print(f"   Input: JPEG, Output: {result['content_type']}")
        print(f"   Output filename: {result['output_filename']}")
        
        # Save the result
        if result['output_image']:
            output_data = base64.b64decode(result['output_image'])
            with open('output_converted.png', 'wb') as f:
                f.write(output_data)
            print("   Saved to: output_converted.png")
    else:
        print("❌ Conversion failed:", response.status_code, response.text)

def example_error_handling():
    """Example: Error handling with invalid command."""
    print("\n⚠️  Example: Error handling")
    
    payload = {
        "ffmpeg_command": "ffmpeg -i input.jpg -invalid_option output.jpg",
        "image_data": "dGVzdA==",  # Invalid base64
        "input_filename": "input.jpg"
    }
    
    response = requests.post(f"{BASE_URL}/process", json=payload)
    
    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        result = response.json()
        print("Expected error response:")
        print(f"   Detail: {result.get('detail', 'No detail')}")
    else:
        result = response.json()
        if not result['success']:
            print("FFmpeg error:")
            print(f"   Error: {result.get('error', 'No error message')}")

if __name__ == "__main__":
    print("🔥 Gnosis Forge - API Usage Examples")
    print("=" * 50)
    
    # Run examples
    test_health()
    example_multipart_upload()
    example_json_base64()
    example_binary_with_headers()
    example_format_conversion()
    example_error_handling()
    
    print("\n✅ All examples completed!")
    print("\n📚 Check the output files:")
    print("   - output_multipart.jpg")
    print("   - output_json.jpg") 
    print("   - output_binary.jpg")
    print("   - output_converted.png")
