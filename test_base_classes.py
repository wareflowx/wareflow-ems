"""Test base classes."""

import sys
import customtkinter as ctk
sys.path.insert(0, 'src')

from ui_ctk.views.base_view import BaseView
from ui_ctk.forms.base_form import BaseFormDialog
from ui_ctk.constants import APP_TITLE


class TestView(BaseView):
    """Test view implementation."""

    def __init__(self, master):
        super().__init__(master, title="Test View")


class TestForm(BaseFormDialog):
    """Test form implementation."""

    def __init__(self, parent):
        super().__init__(parent, title="Test Form")

    def create_form(self):
        """Create simple form for testing."""
        label = ctk.CTkLabel(self, text="Test Form Content")
        label.pack(pady=20)

        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        save_btn = ctk.CTkButton(button_frame, text="Save", command=self.on_save)
        save_btn.pack(side="left", padx=5)

        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=self.on_cancel)
        cancel_btn.pack(side="left", padx=5)

    def validate(self):
        """Validate form (test implementation)."""
        return (True, None)

    def save(self):
        """Save form (test implementation)."""
        pass


def test_base_view():
    """Test BaseView class."""
    print("Testing BaseView...")

    # Create root window
    root = ctk.CTk()
    root.geometry("800x600")

    # Create test view
    view = TestView(root)
    view.pack(fill="both", expand=True)

    # Check attributes
    assert view.title == "Test View"
    assert hasattr(view, 'create_header')
    assert hasattr(view, 'refresh')
    assert hasattr(view, 'cleanup')

    print("[OK] BaseView instantiation works")
    print("[OK] BaseView has required methods")

    root.destroy()


def test_base_form():
    """Test BaseFormDialog class."""
    print("\nTesting BaseFormDialog...")

    # Create root window
    root = ctk.CTk()
    root.geometry("800x600")

    # Create test form (but don't show it)
    form = TestForm(root)

    # Check attributes
    assert form.result is None
    assert hasattr(form, 'create_form')
    assert hasattr(form, 'validate')
    assert hasattr(form, 'save')
    assert hasattr(form, 'on_save')
    assert hasattr(form, 'on_cancel')
    assert hasattr(form, 'show_error')

    # Test validate
    is_valid, error = form.validate()
    assert is_valid is True
    assert error is None

    print("[OK] BaseFormDialog instantiation works")
    print("[OK] BaseFormDialog has required methods")
    print("[OK] BaseFormDialog validate() works")

    form.destroy()
    root.destroy()


def test_app_title_constant():
    """Test that APP_TITLE is accessible."""
    print("\nTesting APP_TITLE constant...")
    assert APP_TITLE == "Gestion des Salariés"
    print(f"[OK] APP_TITLE = {APP_TITLE}")


if __name__ == "__main__":
    test_base_view()
    test_base_form()
    test_app_title_constant()

    print("\n[OK] ALL BASE CLASS TESTS PASSED")
