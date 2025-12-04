import importlib
import subprocess
import sys

def install_library():
    """
    Checks for required libraries and installs them via pip if they are missing.
    Returns a list of successfully present or installed module names.
    """
    
    # Mapping: { 'Module Name used in import': 'PyPI Package Name for pip install' }
    PACKAGES_TO_INSTALL = {
        'numpy': 'numpy',
        'matplotlib': 'matplotlib',
        'shapely': 'shapely',
        'trimesh': 'trimesh',  # Added 3D geometry library
        'pympler': 'pympler',
        'scipy': 'scipy',
        'tqdm': 'tqdm',
        'imageio': 'imageio',
        
        # Mapped Packages (Special cases where import name != package name)
        'win32com.client': 'pywin32',
        'ansys.motorcad.core': 'ansys-motorcad-core',
        'sklearn': 'scikit-learn', 
        'pyamg': 'pyamg'
    }

    installed_modules = []

    for module_name, pypi_package_name in PACKAGES_TO_INSTALL.items():
        
        try:
            # Check if the package already exists by attempting to import it
            importlib.import_module(module_name)
            installed_modules.append(module_name)
            
        except ImportError:
            # Module not found. Proceed to install using the correct PyPI name
            print(f"'{module_name}' not found. Installing '{pypi_package_name}'...")
            
            try:
                # Run pip install using the current Python executable
                subprocess.check_call([sys.executable, "-m", "pip", "install", pypi_package_name])
                installed_modules.append(module_name)
            
            except subprocess.CalledProcessError as e:
                # Log the failure without crashing the script, then continue to the next package
                print(f"WARNING: Installation of '{pypi_package_name}' FAILED with code {e.returncode}. Skipping.")
                continue
    
    return installed_modules