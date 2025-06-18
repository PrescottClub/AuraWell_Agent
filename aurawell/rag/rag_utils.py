import os
import platform

def get_download_path(default_path="./nutrition_article/"):
    """
    Get a cross-platform download path for nutrition articles
    
    Args:
        default_path (str): Default relative path to use (Linux/macOS style)
    
    Returns:
        str: Absolute path that works on current platform
    """
    # Expand relative path to absolute path
    abs_path = os.path.abspath(default_path)
    
    # Normalize path for Windows
    if platform.system() == "Windows":
        # Convert to Windows-style path
        abs_path = os.path.normpath(abs_path)
    
    # Create directory if it doesn't exist
    os.makedirs(abs_path, exist_ok=True)
    
    return abs_path
