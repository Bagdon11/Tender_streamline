#!/usr/bin/env python3
"""
Build script for Tender Management Application
Creates a standalone executable using PyInstaller
"""

import os
import subprocess
import shutil
import sys

def build_executable():
    """Build standalone executable using PyInstaller."""
    
    print("Building Tender Management Application...")
    
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("Cleaned previous dist directory")
    
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("Cleaned previous build directory")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',           # Single executable file
        '--windowed',          # No console window
        '--name', 'TenderManagement',  # Output name
        '--add-data', 'src;src',       # Include src directory
        '--add-data', 'assets;assets', # Include assets (if exists)
        '--clean',             # Clean cache
        'main.py'
    ]
    
    try:
        print("Running PyInstaller...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build completed successfully!")
        print(f"Executable created: dist/TenderManagement.exe")
        
        # Show file size
        exe_path = "dist/TenderManagement.exe"
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"Executable size: {size_mb:.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except FileNotFoundError:
        print("PyInstaller not found. Please install it with: pip install pyinstaller")
        return False

def create_installer_script():
    """Create a simple batch installer script."""
    
    installer_content = """@echo off
echo Installing Tender Management Application...

REM Create program directory
if not exist "C:\\Program Files\\TenderManagement" (
    mkdir "C:\\Program Files\\TenderManagement"
)

REM Copy executable
copy "TenderManagement.exe" "C:\\Program Files\\TenderManagement\\"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\Tender Management.lnk'); $Shortcut.TargetPath = 'C:\\Program Files\\TenderManagement\\TenderManagement.exe'; $Shortcut.Save()"

echo Installation completed!
echo You can now run Tender Management from your desktop.
pause
"""
    
    with open("dist/install.bat", "w") as f:
        f.write(installer_content)
    
    print("Created installer script: dist/install.bat")

def main():
    """Main build process."""
    
    print("=" * 60)
    print("Tender Management Application - Build Script")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("Error: main.py not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Warning: Virtual environment not detected.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    # Build executable
    if build_executable():
        print("\\n✅ Build successful!")
        
        # Create installer
        create_installer_script()
        print("\\n📦 Package created in 'dist' directory")
        
        # Show next steps
        print("\\nNext steps:")
        print("1. Test the executable: dist/TenderManagement.exe")
        print("2. Run installer (as admin): dist/install.bat")
        print("3. Distribute the files in 'dist' directory")
        
    else:
        print("\\n❌ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()