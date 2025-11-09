"""
Inno Setup Installer Creation Script
Creates installer using Inno Setup Compiler
"""

import os
import sys
import subprocess
import shutil

def find_inno_setup():
    """Find Inno Setup Compiler installation"""
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
        r"C:\Program Files\Inno Setup 5\ISCC.exe",
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None

def check_exe_exists():
    """Check if the executable exists"""
    exe_path = os.path.join("dist", "Crono_Ders_Takip_Sistemi.exe")
    if not os.path.exists(exe_path):
        print("ERROR: Executable not found!")
        print(f"Expected location: {os.path.abspath(exe_path)}")
        print("\nPlease build the executable first using: python build_exe.py")
        return False
    return True

def create_installer():
    """Create installer using Inno Setup"""
    print("=" * 60)
    print("Crono Ders Takip Sistemi - Installer Creation")
    print("=" * 60)
    
    # Check if exe exists
    if not check_exe_exists():
        return False
    
    # Find Inno Setup
    inno_path = find_inno_setup()
    if not inno_path:
        print("\nERROR: Inno Setup Compiler not found!")
        print("\nPlease install Inno Setup from: https://jrsoftware.org/isdl.php")
        print("\nOr manually compile installer.iss using Inno Setup Compiler")
        return False
    
    print(f"\nFound Inno Setup at: {inno_path}")
    
    # Check if installer.iss exists
    if not os.path.exists("installer.iss"):
        print("\nERROR: installer.iss not found!")
        return False
    
    # Create output directory
    output_dir = "installer_output"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    # Compile installer
    print("\nCompiling installer...")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            [inno_path, "installer.iss"],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        
        # Check if installer was created
        installer_files = [f for f in os.listdir(output_dir) if f.endswith('.exe')]
        if installer_files:
            installer_path = os.path.join(output_dir, installer_files[0])
            
            # Copy to test folder if it exists
            test_dir = "test"
            if os.path.exists(test_dir):
                test_installer_path = os.path.join(test_dir, installer_files[0])
                try:
                    shutil.copy2(installer_path, test_installer_path)
                    print(f"\n✓ Installer copied to test folder: {os.path.abspath(test_installer_path)}")
                except Exception as e:
                    print(f"\n⚠ Warning: Could not copy to test folder: {e}")
            
            print("\n" + "=" * 60)
            print("✓ Installer created successfully!")
            print("=" * 60)
            print(f"\nInstaller location: {os.path.abspath(installer_path)}")
            print(f"Size: {os.path.getsize(installer_path) / (1024*1024):.2f} MB")
            print("\nYou can now distribute this installer file!")
            return True
        else:
            print("\nERROR: Installer compilation completed but no installer file found!")
            return False
            
    except subprocess.CalledProcessError as e:
        print("\nERROR: Installer compilation failed!")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_installer()
    sys.exit(0 if success else 1)

