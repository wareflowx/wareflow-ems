"""Export dialog for Excel export configuration."""

from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk
import tkinter.filedialog as filedialog

from controllers.export_controller import ExportController
from database.models import Employee
from ui_ctk.constants import APP_TITLE


class ExportDialog(ctk.CTkToplevel):
    """Dialog for configuring and executing Excel export."""

    def __init__(
        self,
        parent,
        employees: list[Employee],
        title: str = "Export to Excel",
        default_filename: str = "employees_export.xlsx",
    ):
        """
        Initialize export dialog.

        Args:
            parent: Parent window
            employees: List of employees to export
            title: Dialog title
            default_filename: Default filename for export
        """
        super().__init__(parent)

        self.employees = employees
        self.default_filename = default_filename
        self.controller = ExportController()
        self.output_path: Optional[Path] = None
        self.export_completed = False

        # Window setup
        self.title(f"{APP_TITLE} - {title}")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()

        # Center dialog
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

        # Create UI
        self.create_widgets()

        # Bind window close protocol
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def create_widgets(self):
        """Create dialog widgets."""
        # Main container
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame, text="Export Employees to Excel", font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 20))

        # Employee count
        count_label = ctk.CTkLabel(
            main_frame,
            text=f"Employees to export: {len(self.employees)}",
            font=("Arial", 12),
            text_color="gray",
        )
        count_label.pack(pady=(0, 20))

        # Options frame
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=(0, 20))

        # Include options
        self.include_caces_var = ctk.BooleanVar(value=True)
        self.include_visits_var = ctk.BooleanVar(value=True)
        self.include_trainings_var = ctk.BooleanVar(value=True)

        caces_checkbox = ctk.CTkCheckBox(
            options_frame, text="Include CACES", variable=self.include_caces_var
        )
        caces_checkbox.pack(anchor="w", padx=20, pady=10)

        visits_checkbox = ctk.CTkCheckBox(
            options_frame, text="Include Medical Visits", variable=self.include_visits_var
        )
        visits_checkbox.pack(anchor="w", padx=20, pady=10)

        trainings_checkbox = ctk.CTkCheckBox(
            options_frame, text="Include Trainings", variable=self.include_trainings_var
        )
        trainings_checkbox.pack(anchor="w", padx=20, pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame, text="Choose export location", font=("Arial", 11)
        )
        self.status_label.pack(pady=(0, 10))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(main_frame, width=400)
        self.progress_bar.pack(pady=(0, 20))
        self.progress_bar.set(0)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(0, 10))

        # Export button
        self.export_btn = ctk.CTkButton(
            buttons_frame,
            text="Choose Location & Export",
            width=200,
            command=self._start_export,
        )
        self.export_btn.pack(side="left", padx=(0, 10))

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancel",
            width=120,
            fg_color=("gray70", "gray30"),
            command=self._on_close,
        )
        self.cancel_btn.pack(side="left")

    def _start_export(self):
        """Start the export process."""
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            title="Save Excel file",
            defaultextension=".xlsx",
            initialfile=self.default_filename,
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        )

        if not file_path:
            # User cancelled
            return

        self.output_path = Path(file_path)

        # Disable buttons during export
        self.export_btn.configure(state="disabled")
        self.cancel_btn.configure(state="disabled")

        # Start export in background
        self.controller.export_employees(
            output_path=self.output_path,
            employees=self.employees,
            include_caces=self.include_caces_var.get(),
            include_visits=self.include_visits_var.get(),
            include_trainings=self.include_trainings_var.get(),
            progress_callback=self._on_progress,
            completion_callback=self._on_completion,
        )

    def _on_progress(self, message: str, percentage: int):
        """
        Handle export progress updates.

        Args:
            message: Progress message
            percentage: Progress percentage (0-100)
        """
        self.status_label.configure(text=message)
        self.progress_bar.set(percentage / 100)

    def _on_completion(self, success: bool, message: str):
        """
        Handle export completion.

        Args:
            success: Whether export succeeded
            message: Success or error message
        """
        if success:
            self.status_label.configure(
                text=f"✓ {message}", text_color="green"
            )
            self.export_completed = True
            self.progress_bar.set(1.0)

            # Enable cancel button to close dialog
            self.cancel_btn.configure(state="normal", text="Close")
        else:
            self.status_label.configure(text=f"✗ {message}", text_color="red")
            self.progress_bar.set(0)

            # Re-enable buttons
            self.export_btn.configure(state="normal")
            self.cancel_btn.configure(state="normal", text="Cancel")

    def _on_close(self):
        """Handle dialog close."""
        # If export is in progress, show warning
        if self.controller.is_exporting():
            # Don't allow closing during export
            return

        self.destroy()

    def run(self) -> tuple[bool, Optional[Path]]:
        """
        Show dialog and return result.

        Returns:
            Tuple of (success, output_path) where output_path is None if cancelled
        """
        self.wait_window()
        return (self.export_completed, self.output_path if self.export_completed else None)
