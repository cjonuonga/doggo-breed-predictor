# test_api.py - Updated for lunnnaaa.jpeg
import requests
import json
import os
from PIL import Image
import io

BASE_URL = "http://localhost:8000"

def test_startup_status():
    """Test if the model loaded correctly on startup"""
    print("Testing startup status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Model Loaded: {data.get('model_loaded', 'Unknown')}")
        print(f"Total Breeds: {data.get('total_breeds', 'Unknown')}")
        print(f"Message: {data.get('message', 'N/A')}")
        return data.get('model_loaded', False)
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        print("-" * 50)

def test_health_check():
    """Test health endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Model Status: {data.get('model_status', 'Unknown')}")
        print(f"GPU Available: {data.get('gpu_available', 'Unknown')}")
        print(f"TensorFlow Version: {data.get('tensorflow_version', 'Unknown')}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("-" * 50)

def test_with_dog_image(image_path=None):
    """Test with any dog image - auto-detects or uses provided path"""
    print("🐕 Testing with dog image...")
    
    # If no specific image provided, look for common dog image files
    if image_path is None:
        potential_images = [
            "dog_images/lunapt2.jpeg",  # Special test for Luna
        ]
        
        # Also scan directory for any image files
        for file in os.listdir('.'):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                potential_images.append(file)
        
        # Find first existing image
        image_path = None
        for img in potential_images:
            if os.path.exists(img):
                image_path = img
                break
    
    if image_path is None or not os.path.exists(image_path):
        print(f"No dog image found!")
        print("Please place a dog image in this directory with one of these names:")
        print("  - dog.jpg, dog.jpeg, dog.png")
        print("  - puppy.jpg, my_dog.jpg")
        print("  - Or any image file")
        print(f"Checked for: {image_path if image_path else 'various files'}")
        return None
    
    print(f"Using image: {image_path}")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path, f, 'image/jpeg')}
            response = requests.post(f"{BASE_URL}/predict", files=files)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("DOG BREED PREDICTION RESULTS:")
            print(f"Image: {data['filename']}")
            print(f"Size: {data['image_info']['width']}x{data['image_info']['height']} pixels")
            print(f"File Size: {data['image_info']['size_kb']} KB")
            print()
            print(f"PREDICTED BREED: {data['prediction']['breed']}")
            print(f"CONFIDENCE: {data['prediction']['confidence_percentage']}%")
            print()
            print("TOP 3 PREDICTIONS:")
            for i, pred in enumerate(data['top_3_predictions'], 1):
                print(f"  {i}. {pred['breed']}: {pred['confidence']:.1%}")
            print()
            print(f"Model: {data['model_info']['model_type']}")
            return data
        else:
            print(f"❌ Error Response: {response.json()}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        print("-" * 50)

def test_model_info():
    """Test error handling with invalid file"""
    print("Testing error handling with invalid file...")
    
    try:
        files = {'file': ('test.txt', b'This is not an image', 'text/plain')}
        response = requests.post(f"{BASE_URL}/predict", files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 400:
            print("Error handling working correctly")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("-" * 50)

def interactive_image_test():
    """Interactive test - ask user for image path"""
    print("Interactive Image Test")
    
    # Show available images
    print("Available image files in current directory:")
    image_files = []
    for file in os.listdir('.'):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            image_files.append(file)
            print(f"  - {file}")
    
    if not image_files:
        print("  No image files found!")
        return
    
    # Ask user to choose
    image_path = input(f"\nEnter image filename (or press Enter to use first found): ").strip()
    
    if not image_path and image_files:
        image_path = image_files[0]
        print(f"Using: {image_path}")
    
    if image_path:
        test_with_dog_image(image_path)
    else:
        print("No image selected.")
    
    
    """Test model information endpoint"""
    print("Testing model info...")
    try:
        response = requests.get(f"{BASE_URL}/model/info")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Input Shape: {data.get('input_shape', 'Unknown')}")
            print(f"Total Parameters: {data.get('total_parameters', 'Unknown'):,}")
            print(f"Total Breeds: {data.get('total_breeds', 'Unknown')}")
            print(f"Sample Breeds: {', '.join(data.get('sample_breeds', [])[:5])}")
        else:
            print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("-" * 50)

if __name__ == "__main__":
    print("Starting Dog Breed Predictor API Tests...")
    print("Special test for Lunna!")
    print("=" * 60)
    
    try:
        # Basic API tests
        model_loaded = test_startup_status()
        test_health_check()
        
        if model_loaded:
            test_model_info()
        
        # Test with any dog image found
        result = test_with_dog_image()
        
        if result:
            print("Dog breed prediction completed successfully!")
            print(f"Your dog appears to be a {result['prediction']['breed']}!")
        else:
            print("No dog image found for testing")
            print("To test with your dog:")
            print("1. Place any dog image in this directory")
            print("2. Run this test again")
            
        
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API.")
        print("Make sure the server is running:")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"Test failed with error: {e}")