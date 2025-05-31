#!/usr/bin/env python3
"""
SewageMapAI Upload Functionality Validation Script
Tests the complete upload pipeline from image upload to AI processing
"""

import requests
import json
import os
import time
from pathlib import Path

# Configuration
BACKEND_URL = "http://127.0.0.1:5000"
UPLOAD_ENDPOINT = f"{BACKEND_URL}/upload-image"
UPLOADS_DIR = Path("backend/data/uploads")

def test_upload_functionality():
    """Test the upload functionality with real image files"""
    print("🧪 Testing SewageMapAI Upload Functionality")
    print("=" * 50)
    
    # Find test images in uploads directory
    test_images = list(UPLOADS_DIR.glob("*Screenshot*.png"))
    if not test_images:
        print("❌ No test images found in uploads directory")
        return False
    
    test_image = test_images[0]
    print(f"📸 Using test image: {test_image.name}")
    
    try:
        # Test upload
        print("\n🚀 Testing image upload and AI processing...")
        with open(test_image, 'rb') as f:
            files = {'file': (test_image.name, f, 'image/png')}
            response = requests.post(UPLOAD_ENDPOINT, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful!")
            
            # Validate response structure
            print("\n📊 Validating response structure...")
            required_fields = ['success', 'original_image', 'segmentation_mask', 'detection_results', 'dimensions']
            for field in required_fields:
                if field in result:
                    print(f"  ✅ {field}: ✓")
                else:
                    print(f"  ❌ {field}: Missing")
                    return False
            
            # Display detection results
            detection = result['detection_results']
            print(f"\n🧠 AI Detection Results:")
            print(f"  • Model Type: {detection.get('model_type', 'Unknown')}")
            print(f"  • Sewage Lines Detected: {detection.get('sewage_lines_detected', False)}")
            print(f"  • Coverage Percentage: {detection.get('coverage_percentage', 0)}%")
            print(f"  • Detected Pixels: {detection.get('detected_pixels', 0):,}")
            print(f"  • Total Pixels: {detection.get('total_pixels', 0):,}")
            print(f"  • Confidence Threshold: {detection.get('confidence_threshold', 0)}")
            
            # Test file accessibility
            print(f"\n🌐 Testing file accessibility...")
            original_url = f"{BACKEND_URL}{result['original_image']}"
            mask_url = f"{BACKEND_URL}{result['segmentation_mask']}"
            
            # Test original image access
            img_response = requests.head(original_url, timeout=10)
            if img_response.status_code == 200:
                print(f"  ✅ Original image accessible: {original_url}")
            else:
                print(f"  ❌ Original image not accessible: {img_response.status_code}")
                return False
            
            # Test mask access
            mask_response = requests.head(mask_url, timeout=10)
            if mask_response.status_code == 200:
                print(f"  ✅ Segmentation mask accessible: {mask_url}")
            else:
                print(f"  ❌ Segmentation mask not accessible: {mask_response.status_code}")
                return False
            
            print(f"\n🎉 ALL TESTS PASSED!")
            print(f"📈 Upload functionality is working correctly with real AI processing")
            return True
            
        else:
            print(f"❌ Upload failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to backend server. Is it running on http://127.0.0.1:5000?")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        return False

def test_backend_health():
    """Test if backend server is responsive"""
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        return response.status_code in [200, 404]  # 404 is OK, means server is running
    except:
        return False

if __name__ == "__main__":
    print("🏥 Checking backend server health...")
    if test_backend_health():
        print("✅ Backend server is responsive")
        test_upload_functionality()
    else:
        print("❌ Backend server is not responsive. Please start the Flask server first:")
        print("   cd backend && python app.py")
