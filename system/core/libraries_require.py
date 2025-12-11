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
        # --- Core Calculation & Data ---
        'numpy': 'numpy',
        'scipy': 'scipy',
        'matplotlib': 'matplotlib',
        'sklearn': 'scikit-learn',  # Import: sklearn, Pip: scikit-learn
        
        # --- 3D Geometry & Visualization ---
        'trimesh': 'trimesh',
        'shapely': 'shapely',
        'pyvista': 'pyvista',       # <--- MỚI: Thư viện 3D High Performance
        
        # --- Trimesh Dependencies ---
        'pyglet': 'pyglet<2',       # GUI backend cũ cho trimesh (nếu không dùng pyvista)
        'manifold3d': 'manifold3d', # Boolean engine (Cực mạnh để cắt/gộp khối 3D)
        'rtree': 'rtree',           # Giúp trimesh tính toán va chạm nhanh hơn
        
        # --- Utilities ---
        'tqdm': 'tqdm',             # Thanh tiến trình
        'imageio': 'imageio',
        'pympler': 'pympler',       # Đo lường bộ nhớ
        
        # --- Automation & Engineering ---
        'win32com.client': 'pywin32',
        'ansys.motorcad.core': 'ansys-motorcad-core',
        'pyamg': 'pyamg'
    }

    installed_modules = []
    print("Checking libraries...")

    for module_name, pypi_package_name in PACKAGES_TO_INSTALL.items():
        try:
            # Check if the package already exists by attempting to import it
            importlib.import_module(module_name)
            installed_modules.append(module_name)
            
        except ImportError:
            # Module not found. Proceed to install using the correct PyPI name
            print(f"[-] '{module_name}' not found. Installing '{pypi_package_name}'...")
            
            try:
                # Run pip install using the current Python executable
                subprocess.check_call([sys.executable, "-m", "pip", "install", pypi_package_name])
                print(f"[+] Successfully installed '{pypi_package_name}'.")
                installed_modules.append(module_name)
            
            except subprocess.CalledProcessError as e:
                # Log the failure without crashing the script
                print(f"[!] WARNING: Installation of '{pypi_package_name}' FAILED with code {e.returncode}. Skipping.")
                continue
    
    print("\nAll library checks completed.")
    return installed_modules


install_library() # Auto install library while imported

if __name__ == "__main__":
    install_library()