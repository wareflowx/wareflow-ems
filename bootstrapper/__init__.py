"""Bootstrapper module for creating new project instances.

This module re-exports functionality from src.bootstrapper for
backwards compatibility.
"""

import sys

# Import and register submodules for backwards compatibility
from src import bootstrapper as src_bootstrapper

# Create references to submodules
update_checker = src_bootstrapper.update_checker
wizard = src_bootstrapper.wizard

# Register in sys.modules for submodule imports
sys.modules["bootstrapper.update_checker"] = src_bootstrapper.update_checker
sys.modules["bootstrapper.wizard"] = src_bootstrapper.wizard

__all__ = ["update_checker", "wizard"]
