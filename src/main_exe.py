"""PyInstaller entry point for Windows executable.

This module serves as the entry point for the PyInstaller-built executable.
It correctly sets up sys.path before importing the application.
"""

import sys
import os
from pathlib import Path

def setup_sys_path():
    """Configure sys.path to include src directory."""
    # Get the directory where the executable is located
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        # PyInstaller extracts to temp directory, get it from _MEIPASS
        if '_MEIPASS' in os.environ:
            base_path = Path(os.environ['_MEIPASS'])
        else:
            base_path = Path(sys.executable).parent

        # Look for src directory in multiple locations
        src_path = None
        for potential_base in [base_path, base_path.parent, base_path.parent.parent]:
            potential_src = potential_base / "src"
            if potential_src.exists():
                src_path = potential_src
                break

        if src_path:
            sys.path.insert(0, str(src_path))
            # Also add parent to sys.path for direct imports
            sys.path.insert(1, str(src_path.parent))
        else:
            # Last resort: try current directory
            sys.path.insert(0, str(Path.cwd()))

        # Force sys.path to be recognized
        sys.path = list(dict.fromkeys(sys.path))  # Remove duplicates while preserving order
    else:
        # Running from Python normally
        application_path = Path(__file__).parent
        src_path = application_path / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
        else:
            sys.path.insert(0, str(Path.cwd()))

# Setup path BEFORE any imports
setup_sys_path()

# Now import and run the application
if __name__ == "__main__":
    # Double-check that sys.path is correct
    import os
    if 'src' not in sys.path[0]:
        # Emergency fallback
        sys.path.insert(0, str(Path(os.getcwd()) / "src"))

    from ui_ctk.app import main

    main()
