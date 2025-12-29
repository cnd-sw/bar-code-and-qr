
import sys
from pathlib import Path
sys.path.append(str(Path.cwd()))

from pyzbar.pyzbar import decode
from PIL import Image
import os

def test_environment():
    print("Testing environment setup...")
    
    # 1. Test Image Loading
    image_path = "qr_data/1002-v1.png"
    if not os.path.exists(image_path):
        print(f"Error: Test image not found at {image_path}")
        return False
        
    try:
        img = Image.open(image_path)
        print(f"Image loaded successfully: {image_path}")
    except Exception as e:
        print(f"Error loading image: {e}")
        return False

    # 2. Test zbar shared library linking
    try:
        decoded_objects = decode(img)
        if decoded_objects:
            print(f"pyzbar detected {len(decoded_objects)} code(s)")
            print(f"   Data: {decoded_objects[0].data.decode('utf-8')}")
            print("zbar shared library is correctly installed and linked.")
        else:
            print("Warning: pyzbar ran but found no codes (this might be an image issue, but the library works).")
            
    except ImportError:
        print("ImportError: Could not import pyzbar. Check pip install.")
        return False
    except Exception as e:
        print(f"Error using pyzbar: {e}")
        print("Hint: On macOS, you might need to run: brew install zbar")
        return False
        
    return True

if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
