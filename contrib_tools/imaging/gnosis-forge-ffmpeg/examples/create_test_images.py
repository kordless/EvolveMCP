#!/usr/bin/env python3
"""
Create test images for Gnosis Forge examples.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_images():
    """Create various test images for API examples."""
    
    # Create examples directory if it doesn't exist
    os.makedirs("examples/test_images", exist_ok=True)
    
    # Test image 1: Simple colored rectangle
    img1 = Image.new('RGB', (400, 300), color='#3498db')
    draw1 = ImageDraw.Draw(img1)
    draw1.text((50, 50), "Gnosis Forge Test", fill='white')
    img1.save("examples/test_images/test_blue.jpg")
    
    # Test image 2: Gradient-like effect
    img2 = Image.new('RGB', (300, 300))
    pixels = []
    for y in range(300):
        for x in range(300):
            r = int((x / 300) * 255)
            g = int((y / 300) * 255)
            b = 128
            pixels.append((r, g, b))
    img2.putdata(pixels)
    img2.save("examples/test_images/test_gradient.jpg")
    
    # Test image 3: Pattern
    img3 = Image.new('RGB', (200, 200), color='white')
    draw3 = ImageDraw.Draw(img3)
    for i in range(0, 200, 20):
        draw3.line([(i, 0), (i, 200)], fill='black', width=2)
        draw3.line([(0, i), (200, i)], fill='black', width=2)
    img3.save("examples/test_images/test_pattern.png")
    
    # Test image 4: Circle
    img4 = Image.new('RGB', (250, 250), color='#ecf0f1')
    draw4 = ImageDraw.Draw(img4)
    draw4.ellipse([50, 50, 200, 200], fill='#e74c3c', outline='#c0392b', width=3)
    img4.save("examples/test_images/test_circle.jpg")
    
    print("✅ Created test images:")
    print("   - examples/test_images/test_blue.jpg")
    print("   - examples/test_images/test_gradient.jpg")
    print("   - examples/test_images/test_pattern.png")
    print("   - examples/test_images/test_circle.jpg")

if __name__ == "__main__":
    create_test_images()
