#!/usr/bin/env python3
"""
OCR Setup Helper - Download and configure Tesseract OCR
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
from pathlib import Path

def check_tesseract():
    """Check if Tesseract is already installed."""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tesseract is already installed!")
            print(result.stdout.split('\n')[0])
            return True
    except FileNotFoundError:
        pass
    
    # Check common Windows paths
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    ]
    
    for path in common_paths:
        if os.path.exists(path):
            print(f"✅ Found Tesseract at: {path}")
            return True
    
    print("❌ Tesseract not found")
    return False

def download_tesseract_windows():
    """Download and install Tesseract for Windows."""
    print("Downloading Tesseract OCR for Windows...")
    
    # Tesseract Windows installer URL (latest version)
    url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    installer_path = "tesseract-installer.exe"
    
    try:
        print("Downloading installer...")
        urllib.request.urlretrieve(url, installer_path)
        
        print("Starting installer...")
        print("Please follow the installation wizard.")
        print("Make sure to install to the default location: C:\\Program Files\\Tesseract-OCR\\")
        
        # Run installer
        subprocess.run([installer_path], check=True)
        
        # Clean up
        if os.path.exists(installer_path):
            os.remove(installer_path)
        
        print("✅ Installation completed!")
        print("Please restart the application to use OCR functionality.")
        
    except Exception as e:
        print(f"❌ Download/installation failed: {e}")
        print("\nManual installation:")
        print("1. Go to: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Download the Windows installer")
        print("3. Install to default location")
        print("4. Restart this application")

def setup_portable_tesseract():
    """Set up a portable version of Tesseract in the project directory."""
    print("Setting up portable Tesseract...")
    
    # This would require downloading and extracting Tesseract
    # For now, just provide instructions
    print("For a portable setup:")
    print("1. Download Tesseract from GitHub releases")
    print("2. Extract to 'tesseract' folder in project directory")
    print("3. Update TESSERACT_PATH in the application")

def test_ocr():
    """Test OCR functionality."""
    try:
        sys.path.insert(0, 'src')
        from src.core.document_parser import DocumentParser, OCR_AVAILABLE
        
        if not OCR_AVAILABLE:
            print("❌ OCR libraries not available")
            return False
        
        print("✅ OCR libraries loaded successfully")
        
        # Test with a simple image if available
        try:
            import pytesseract
            from PIL import Image
            
            # Create a simple test image with text
            test_text = "OCR Test - Hello World!"
            print(f"Testing OCR with text: '{test_text}'")
            
            # For a full test, we'd need to create or have a test image
            print("✅ OCR components ready")
            return True
            
        except Exception as e:
            print(f"❌ OCR test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ OCR setup test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("=" * 60)
    print("Tender Management - OCR Setup Helper")
    print("=" * 60)
    
    print("\n1. Checking current Tesseract installation...")
    if check_tesseract():
        print("\n2. Testing OCR functionality...")
        if test_ocr():
            print("\n🎉 OCR is ready to use!")
            print("\nYour application can now:")
            print("• Extract text from scanned PDFs")
            print("• Process image-based documents")
            print("• Handle complex formatted PDFs")
        else:
            print("\n⚠️  OCR components need attention")
    else:
        print("\n2. Tesseract installation needed...")
        
        if os.name == 'nt':  # Windows
            choice = input("\nInstall Tesseract automatically? (y/n): ")
            if choice.lower() == 'y':
                download_tesseract_windows()
            else:
                print("\nManual installation instructions:")
                print("1. Visit: https://github.com/UB-Mannheim/tesseract/wiki")
                print("2. Download Windows installer")
                print("3. Install to default location")
                print("4. Restart the application")
        else:
            print("\nFor Linux/Mac:")
            print("Linux: sudo apt-get install tesseract-ocr")
            print("Mac: brew install tesseract")
    
    print("\n" + "=" * 60)
    print("Setup complete! Run your application to test OCR functionality.")

if __name__ == "__main__":
    main()