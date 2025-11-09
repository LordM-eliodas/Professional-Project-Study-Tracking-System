"""
Build executable script for Crono Ders Takip Sistemi
Run this script to create a single executable file
"""

import PyInstaller.__main__
import os
import sys

# Application information
APP_NAME = "Crono_Ders_Takip_Sistemi"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "main.py"
ICON_FILE = "pngegg.png"  # PNG icon file in root directory

# Determine path separator based on OS
if sys.platform == 'win32':
    SEP = ';'
else:
    SEP = ':'

# PyInstaller options for single file executable
options = [
    MAIN_SCRIPT,
    '--name', APP_NAME,
    '--onefile',  # Create single executable file
    '--windowed',  # No console window (use --console for debugging)
    '--clean',  # Clean cache before building
    '--noconfirm',  # Overwrite output without asking
    
    # Include data directories
    '--add-data', f'locales{SEP}locales',
    '--add-data', f'data{SEP}data',
    '--add-data', f'sözler.json{SEP}.',  # Include quotes file in root
    
    # Hidden imports - all required modules
    '--hidden-import', 'customtkinter',
    '--hidden-import', 'matplotlib',
    '--hidden-import', 'matplotlib.backends.backend_tkagg',
    '--hidden-import', 'matplotlib.figure',
    '--hidden-import', 'tkinter',
    '--hidden-import', 'tkinter.messagebox',
    '--hidden-import', 'tkinter.filedialog',
    '--hidden-import', 'PIL',
    '--hidden-import', 'PIL.Image',
    '--hidden-import', 'PIL.ImageTk',
    '--hidden-import', 'pandas',
    '--hidden-import', 'openpyxl',
    '--hidden-import', 'reportlab',
    '--hidden-import', 'json',
    '--hidden-import', 'datetime',
    '--hidden-import', 'functools',
    '--hidden-import', 'os',
    '--hidden-import', 'sys',
    
    # Collect all submodules
    '--collect-all', 'customtkinter',
    '--collect-all', 'matplotlib',
    '--collect-all', 'PIL',
    '--collect-all', 'pandas',
    '--collect-all', 'openpyxl',
    '--collect-all', 'reportlab',
    
    # Exclude unnecessary modules to reduce size
    '--exclude-module', 'numpy.distutils',
    '--exclude-module', 'scipy',
    '--exclude-module', 'IPython',
    '--exclude-module', 'jupyter',
]

# Add icon if it exists (PNG or ICO)
if os.path.exists(ICON_FILE):
    options.extend(['--icon', ICON_FILE])
elif os.path.exists('pngegg.ico'):
    options.extend(['--icon', 'pngegg.ico'])

# Add version info (Windows)
if sys.platform == 'win32':
    version_info = f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'TEAM AURORA'),
        StringStruct(u'FileDescription', u'Crono Ders Takip Sistemi'),
        StringStruct(u'FileVersion', u'{APP_VERSION}'),
        StringStruct(u'InternalName', u'Crono'),
        StringStruct(u'LegalCopyright', u'Copyright (c) 2025 Chaster / TEAM AURORA'),
        StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
        StringStruct(u'ProductName', u'Crono Ders Takip Sistemi'),
        StringStruct(u'ProductVersion', u'{APP_VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    options.extend(['--version-file', 'version_info.txt'])

print("=" * 60)
print("Building single-file executable...")
print("=" * 60)
print(f"Application: {APP_NAME}")
print(f"Version: {APP_VERSION}")
print(f"Main script: {MAIN_SCRIPT}")
print(f"Icon: {ICON_FILE if os.path.exists(ICON_FILE) else 'Not found'}")
print("=" * 60)
print("\nThis may take a few minutes...\n")

try:
    PyInstaller.__main__.run(options)
    
    print("\n" + "=" * 60)
    print("Build complete!")
    print("=" * 60)
    print(f"\nExecutable location: dist\\{APP_NAME}.exe")
    print("\nThe executable is a single file containing everything.")
    print("You can distribute just this one .exe file!")
    print("=" * 60)
    
except Exception as e:
    print("\n" + "=" * 60)
    print("Build failed!")
    print("=" * 60)
    print(f"Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
    print("2. Make sure PyInstaller is installed: pip install pyinstaller")
    print("3. Check that main.py exists and is correct")
    print("=" * 60)
    sys.exit(1)

