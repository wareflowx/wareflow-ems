"""Test CustomTkinter installation (headless)."""

import sys

# Test imports
try:
    import customtkinter as ctk
    print(f"[OK] CustomTkinter imported (version {ctk.__version__})")
except ImportError as e:
    print(f"[FAIL] Failed to import CustomTkinter: {e}")
    sys.exit(1)

# Test Pillow
try:
    from PIL import Image
    print("[OK] Pillow imported")
except ImportError as e:
    print(f"[FAIL] Failed to import Pillow: {e}")
    sys.exit(1)

# Test theme modes
try:
    for mode in ["System", "Dark", "Light"]:
        ctk.set_appearance_mode(mode)
    print("[OK] Theme modes work")
except Exception as e:
    print(f"[FAIL] Theme modes failed: {e}")
    sys.exit(1)

# Test color themes
try:
    for theme in ["blue", "green", "dark-blue"]:
        ctk.set_default_color_theme(theme)
    print("[OK] Color themes work")
except Exception as e:
    print(f"[FAIL] Color themes failed: {e}")
    sys.exit(1)

print("\n[OK] ALL TESTS PASSED")
print("CustomTkinter is properly installed and configured.")
