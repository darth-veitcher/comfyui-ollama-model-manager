"""
Installation script for ComfyUI Ollama Model Manager.

This script handles dependency installation for the custom node.
Prefers uv if available, falls back to pip.
"""

import sys
import subprocess
import shutil


def check_uv_available():
    """Check if uv is available on the system."""
    return shutil.which("uv") is not None


def install_dependencies():
    """Install required dependencies using uv or pip."""
    print("[Ollama Manager] Checking dependencies...")
    
    # Required packages
    requirements = [
        "httpx>=0.28.1",
        "loguru>=0.7.3",
        "rich>=14.2.0",
    ]
    
    try:
        # Check if packages are already installed
        import httpx  # noqa: F401
        import loguru  # noqa: F401
        import rich  # noqa: F401
        print("[Ollama Manager] ✅ All dependencies are already installed")
        return True
    except ImportError:
        pass
    
    print("[Ollama Manager] Installing dependencies...")
    
    # Determine the best installation method
    python_exe = sys.executable
    use_uv = check_uv_available()
    
    if use_uv:
        print("[Ollama Manager] Using uv for installation")
        install_cmd = ["uv", "pip", "install"]
    else:
        print("[Ollama Manager] Using pip for installation")
        install_cmd = [python_exe, "-m", "pip", "install"]
    
    try:
        for package in requirements:
            print(f"[Ollama Manager] Installing {package}...")
            subprocess.check_call(
                install_cmd + [package],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        
        print("[Ollama Manager] ✅ Dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[Ollama Manager] ❌ Failed to install dependencies: {e}")
        print("[Ollama Manager] Please install manually:")
        if use_uv:
            print("[Ollama Manager]   uv pip install httpx loguru rich")
        else:
            print(f"[Ollama Manager]   {python_exe} -m pip install httpx loguru rich")
        return False


if __name__ == "__main__":
    # When run directly
    install_dependencies()
else:
    # When imported by ComfyUI
    # Check and install if needed
    try:
        import httpx  # noqa: F401
        import loguru  # noqa: F401
        import rich  # noqa: F401
    except ImportError:
        install_dependencies()
