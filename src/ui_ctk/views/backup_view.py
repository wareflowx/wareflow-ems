"""
Backup View Module

Provides UI for:
- Manual backup creation
- Backup restoration
- Backup verification
- Backup history and statistics
- Automated scheduler management
- Backup configuration
- Data export (Excel, CSV)
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import filedialog, messagebox
import logging
from datetime import datetime
from typing import Optional

from src.utils.backup_service import BackupService
from src.export.data_exporter import DataExporter

logger = logging.getLogger(__name__)


class BackupView(ctk.CTkFrame):
    """Backup and export management view with automation."""

    def __init__(self, master, **kwargs):
        """
        Initialize backup view.

        Args:
            master: Parent widget (typically MainWindow)
            **kwargs: Additional arguments for CTkFrame
        """
        super().__init__(master, **kwargs)

        # Initialize backup service (integrates all backup components)
        self.backup_service = BackupService()

        self.exporter = DataExporter()

        # Track scheduler state
        self._scheduler_running = False

        # Build UI
        self.create_ui()
        self.refresh_backup_list()
        self.update_scheduler_status()

    def create_ui(self):
        """Create backup management UI."""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Backup and Export Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=20)

        # Create main container with scrollbar
        main_container = ctk.CTkScrollableFrame(
            self,
            label_text=""
        )
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Statistics section
        self._create_statistics_section(main_container)

        # Scheduler control section
        self._create_scheduler_section(main_container)

        # Backup management section
        self._create_backup_management_section(main_container)

        # Configuration section
        self._create_configuration_section(main_container)

        # Backup history section
        self._create_backup_history_section(main_container)

        # Export section
        self._create_export_section(main_container)

    def _create_statistics_section(self, parent):
        """Create statistics display section."""
        section = self._create_section_frame(parent, "Backup Statistics")

        # Create stats labels
        stats_frame = ctk.CTkFrame(section, fg_color="transparent")
        stats_frame.pack(pady=10, padx=10, fill="x")

        self.stats_count_label = self._create_stat_label(
            stats_frame,
            "Total Backups:",
            "0"
        )
        self.stats_count_label.pack(side="left", padx=20, pady=5)

        self.stats_size_label = self._create_stat_label(
            stats_frame,
            "Total Size:",
            "0.00 MB"
        )
        self.stats_size_label.pack(side="left", padx=20, pady=5)

        self.stats_last_label = self._create_stat_label(
            stats_frame,
            "Last Backup:",
            "Never"
        )
        self.stats_last_label.pack(side="left", padx=20, pady=5)

        # Refresh stats
        self.refresh_statistics()

    def _create_stat_label(self, parent, label_text: str, value_text: str):
        """Create a statistic label with key-value pair."""
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(side="left")

        label = ctk.CTkLabel(
            container,
            text=label_text,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        label.pack(side="left", padx=(0, 5))

        value = ctk.CTkLabel(
            container,
            text=value_text,
            font=ctk.CTkFont(size=12)
        )
        value.pack(side="left")

        # Store reference to value label for updates
        container.value_label = value

        return container

    def _create_scheduler_section(self, parent):
        """Create scheduler control section."""
        section = self._create_section_frame(parent, "Automated Backup Scheduler")

        # Controls frame
        controls_frame = ctk.CTkFrame(section, fg_color="transparent")
        controls_frame.pack(pady=10, padx=10, fill="x")

        # Scheduler status label
        self.scheduler_status_label = ctk.CTkLabel(
            controls_frame,
            text="Status: Stopped",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="red"
        )
        self.scheduler_status_label.pack(side="left", padx=20, pady=10)

        # Start/Stop button
        self.scheduler_toggle_btn = ctk.CTkButton(
            controls_frame,
            text="Start Scheduler",
            command=self.toggle_scheduler,
            width=150,
            height=35
        )
        self.scheduler_toggle_btn.pack(side="left", padx=10, pady=10)

        # Schedule info label
        config = self.backup_service.get_config()
        schedule_time = config.get("backup_time", "02:00")
        enabled = config.get("enabled", True)

        info_text = f"Scheduled: {schedule_time}" if enabled else "Scheduler disabled"
        self.scheduler_info_label = ctk.CTkLabel(
            controls_frame,
            text=info_text,
            font=ctk.CTkFont(size=11)
        )
        self.scheduler_info_label.pack(side="left", padx=20, pady=10)

    def _create_backup_management_section(self, parent):
        """Create backup management buttons section."""
        section = self._create_section_frame(parent, "Manual Backup Operations")

        # Buttons frame
        buttons_frame = ctk.CTkFrame(section, fg_color="transparent")
        buttons_frame.pack(pady=10, padx=10, fill="x")

        # Create backup button
        create_backup_btn = ctk.CTkButton(
            buttons_frame,
            text="Create Backup",
            command=self.create_backup,
            width=150,
            height=35
        )
        create_backup_btn.pack(side="left", padx=5, pady=10)

        # Restore backup button
        restore_backup_btn = ctk.CTkButton(
            buttons_frame,
            text="Restore Backup",
            command=self.restore_backup,
            width=150,
            height=35
        )
        restore_backup_btn.pack(side="left", padx=5, pady=10)

        # Verify backup button
        verify_backup_btn = ctk.CTkButton(
            buttons_frame,
            text="Verify Backup",
            command=self.verify_backup,
            width=150,
            height=35
        )
        verify_backup_btn.pack(side="left", padx=5, pady=10)

    def _create_configuration_section(self, parent):
        """Create configuration management section."""
        section = self._create_section_frame(parent, "Backup Configuration")

        # Config frame
        config_frame = ctk.CTkFrame(section, fg_color="transparent")
        config_frame.pack(pady=10, padx=10, fill="x")

        # Backup time setting
        time_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        time_frame.pack(side="left", padx=10)

        time_label = ctk.CTkLabel(
            time_frame,
            text="Backup Time:",
            font=ctk.CTkFont(size=11)
        )
        time_label.pack(side="left", padx=(0, 5))

        self.backup_time_entry = ctk.CTkEntry(
            time_frame,
            width=80,
            placeholder_text="HH:MM"
        )
        self.backup_time_entry.pack(side="left", padx=5)

        # Retention days setting
        retention_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        retention_frame.pack(side="left", padx=10)

        retention_label = ctk.CTkLabel(
            retention_frame,
            text="Retention (days):",
            font=ctk.CTkFont(size=11)
        )
        retention_label.pack(side="left", padx=(0, 5))

        self.retention_entry = ctk.CTkEntry(
            retention_frame,
            width=60,
            placeholder_text="30"
        )
        self.retention_entry.pack(side="left", padx=5)

        # Enabled checkbox
        self.enabled_checkbox = ctk.CTkCheckBox(
            config_frame,
            text="Enable Automatic Backups"
        )
        self.enabled_checkbox.pack(side="left", padx=20)

        # Save config button
        save_config_btn = ctk.CTkButton(
            config_frame,
            text="Save Configuration",
            command=self.save_configuration,
            width=150,
            height=35
        )
        save_config_btn.pack(side="left", padx=10)

        # Load current configuration
        self.load_configuration()

    def _create_backup_history_section(self, parent):
        """Create backup history display section."""
        section = self._create_section_frame(parent, "Backup History")

        # Backup list display
        self.backup_listbox = ctk.CTkTextbox(
            section,
            height=300,
            font=ctk.CTkFont(family="Consolas", size=11)
        )
        self.backup_listbox.pack(pady=10, fill="both", expand=True, padx=10)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            section,
            text="Refresh List",
            command=self.refresh_backup_list,
            width=150
        )
        refresh_btn.pack(pady=5)

    def _create_export_section(self, parent):
        """Create data export section."""
        section = self._create_section_frame(parent, "Data Export")

        # Buttons frame
        buttons_frame = ctk.CTkFrame(section, fg_color="transparent")
        buttons_frame.pack(pady=10, padx=10, fill="x")

        # Export to Excel button
        export_excel_btn = ctk.CTkButton(
            buttons_frame,
            text="Export to Excel",
            command=self.export_excel,
            width=150,
            height=35
        )
        export_excel_btn.pack(side="left", padx=5, pady=10)

        # Export to CSV button
        export_csv_btn = ctk.CTkButton(
            buttons_frame,
            text="Export to CSV",
            command=self.export_csv,
            width=150,
            height=35
        )
        export_csv_btn.pack(side="left", padx=5, pady=10)

    def _create_section_frame(self, parent, title: str) -> ctk.CTkFrame:
        """
        Create a section frame with title.

        Args:
            parent: Parent widget
            title: Section title

        Returns:
            CTkFrame widget
        """
        frame = ctk.CTkFrame(parent)
        frame.pack(pady=10, fill="x", padx=10)

        # Title label
        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(pady=(10, 5), padx=10, anchor="w")

        return frame

    def toggle_scheduler(self):
        """Toggle scheduler start/stop."""
        try:
            if self._scheduler_running:
                # Stop scheduler
                self.backup_service.stop_scheduler()
                self._scheduler_running = False
                self.scheduler_status_label.configure(
                    text="Status: Stopped",
                    text_color="red"
                )
                self.scheduler_toggle_btn.configure(text="Start Scheduler")
                logger.info("Backup scheduler stopped")
            else:
                # Start scheduler
                result = self.backup_service.start_scheduler()
                if result:
                    self._scheduler_running = True
                    self.scheduler_status_label.configure(
                        text="Status: Running",
                        text_color="green"
                    )
                    self.scheduler_toggle_btn.configure(text="Stop Scheduler")
                    logger.info("Backup scheduler started")
                else:
                    messagebox.showwarning(
                        "Scheduler Disabled",
                        "Automatic backups are disabled in configuration.\n"
                        "Enable them in the Configuration section."
                    )
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to toggle scheduler:\n{e}"
            )
            logger.error(f"Failed to toggle scheduler: {e}")

    def update_scheduler_status(self):
        """Update scheduler status display."""
        is_running = self.backup_service.is_scheduler_running()
        self._scheduler_running = is_running

        if is_running:
            self.scheduler_status_label.configure(
                text="Status: Running",
                text_color="green"
            )
            self.scheduler_toggle_btn.configure(text="Stop Scheduler")
        else:
            self.scheduler_status_label.configure(
                text="Status: Stopped",
                text_color="red"
            )
            self.scheduler_toggle_btn.configure(text="Start Scheduler")

    def refresh_statistics(self):
        """Refresh backup statistics display."""
        try:
            stats = self.backup_service.get_backup_stats()

            # Update count
            self.stats_count_label.value_label.configure(
                text=str(stats['total_count'])
            )

            # Update size
            self.stats_size_label.value_label.configure(
                text=f"{stats['total_size_mb']:.2f} MB"
            )

            # Update last backup
            if stats['newest_backup']:
                last_backup = stats['newest_backup']
                self.stats_last_label.value_label.configure(
                    text=last_backup.strftime('%Y-%m-%d %H:%M')
                )
            else:
                self.stats_last_label.value_label.configure(text="Never")

        except Exception as e:
            logger.error(f"Failed to refresh statistics: {e}")

    def load_configuration(self):
        """Load current configuration into UI fields."""
        try:
            config = self.backup_service.get_config()

            self.backup_time_entry.delete(0, "end")
            self.backup_time_entry.insert(0, config.get("backup_time", "02:00"))

            self.retention_entry.delete(0, "end")
            self.retention_entry.insert(0, str(config.get("retention_days", 30)))

            self.enabled_checkbox.configure(
                state="normal" if config.get("enabled", True) else "normal"
            )
            # Note: CTkCheckBox doesn't have a direct set method, need to use select/deselect
            if config.get("enabled", True):
                self.enabled_checkbox.select()
            else:
                self.enabled_checkbox.deselect()

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")

    def save_configuration(self):
        """Save configuration from UI fields."""
        try:
            backup_time = self.backup_time_entry.get().strip()
            retention_days = self.retention_entry.get().strip()
            enabled = self.enabled_checkbox.get()

            # Validate inputs
            try:
                # Validate time format
                hour, minute = map(int, backup_time.split(":"))
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError("Invalid time")

                # Validate retention
                retention = int(retention_days)
                if retention < 1:
                    raise ValueError("Retention must be at least 1 day")
            except ValueError as e:
                messagebox.showerror(
                    "Invalid Configuration",
                    f"Please check your inputs:\n{e}"
                )
                return

            # Update configuration
            updates = {
                "backup_time": backup_time,
                "retention_days": retention,
                "enabled": enabled
            }

            result = self.backup_service.update_config(updates)

            if result:
                messagebox.showinfo(
                    "Success",
                    "Configuration saved successfully!\n\n"
                    "Note: If scheduler is running, restart it for changes to take effect."
                )
                logger.info(f"Backup configuration updated: {updates}")

                # Update scheduler info
                self.scheduler_info_label.configure(
                    text=f"Scheduled: {backup_time}" if enabled else "Scheduler disabled"
                )
            else:
                messagebox.showerror(
                    "Error",
                    "Failed to save configuration."
                )

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to save configuration:\n{e}"
            )
            logger.error(f"Failed to save configuration: {e}")

    def create_backup(self):
        """Create a new backup."""
        try:
            backup_path = self.backup_service.create_backup(description="manual")

            size_mb = backup_path.stat().st_size / (1024 * 1024)

            messagebox.showinfo(
                "Success",
                f"Backup created successfully:\n{backup_path.name}\n\n"
                f"Size: {size_mb:.2f} MB"
            )

            self.refresh_backup_list()
            self.refresh_statistics()
            logger.info(f"Manual backup created: {backup_path}")

        except FileNotFoundError as e:
            messagebox.showerror(
                "Error",
                f"Database file not found:\n{e}"
            )
            logger.error(f"Backup failed - database not found: {e}")

        except IOError as e:
            messagebox.showerror(
                "Error",
                f"Failed to create backup:\n{e}"
            )
            logger.error(f"Backup failed: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unexpected error creating backup:\n{e}"
            )
            logger.error(f"Unexpected error during backup: {e}")

    def verify_backup(self):
        """Verify a selected backup file."""
        try:
            # Show file dialog to select backup
            backup_path_str = filedialog.askopenfilename(
                title="Select Backup to Verify",
                initialdir=str(self.backup_service.backup_manager.backup_dir),
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
            )

            if not backup_path_str:
                return

            backup_path = Path(backup_path_str)

            # Perform verification
            verification = self.backup_service.verify_backup(backup_path)

            # Show results
            if verification['valid']:
                message = "Backup is valid! ✓\n\n"
                message += f"File: {backup_path.name}\n"
                message += f"Size: {verification['size_bytes'] / (1024*1024):.2f} MB\n"
                message += f"Employees: {verification['employee_count']}\n"
                message += f"CACES: {verification['cace_count']}\n"
                message += f"Visits: {verification['visit_count']}\n"
                message += f"Trainings: {verification['training_count']}"

                messagebox.showinfo("Verification Successful", message)
            else:
                messagebox.showerror(
                    "Verification Failed",
                    f"Backup file is invalid or corrupted:\n{backup_path.name}"
                )

            logger.info(f"Backup verification: {backup_path.name} - {'Valid' if verification['valid'] else 'Invalid'}")

        except FileNotFoundError as e:
            messagebox.showerror(
                "Error",
                f"Backup file not found:\n{e}"
            )
            logger.error(f"Verification failed - file not found: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to verify backup:\n{e}"
            )
            logger.error(f"Verification failed: {e}")

    def refresh_backup_list(self):
        """Refresh the backup list display."""
        try:
            backups = self.backup_service.list_backups()

            if not backups:
                text = "No backups available.\nClick 'Create Backup' to create your first backup."
            else:
                stats = self.backup_service.get_backup_stats()

                text = f"Total backups: {stats['total_count']}\n"
                text += f"Total size: {stats['total_size_mb']:.2f} MB\n"
                text += f"Oldest: {stats['oldest_backup'].strftime('%Y-%m-%d %H:%M') if stats['oldest_backup'] else 'N/A'}\n"
                text += f"Newest: {stats['newest_backup'].strftime('%Y-%m-%d %H:%M') if stats['newest_backup'] else 'N/A'}\n\n"
                text += "=" * 80 + "\n\n"

                for i, backup in enumerate(backups, 1):
                    text += f"[{i}] {backup['name']}\n"
                    text += f"    Size: {backup['size_mb']:.2f} MB\n"
                    text += f"    Created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            self.backup_listbox.delete("1.0", "end")
            self.backup_listbox.insert("1.0", text)

        except Exception as e:
            self.backup_listbox.delete("1.0", "end")
            self.backup_listbox.insert("1.0", f"Error loading backups: {e}")
            logger.error(f"Failed to load backup list: {e}")

    def restore_backup(self):
        """Restore selected backup."""
        try:
            # Show file dialog to select backup
            backup_path_str = filedialog.askopenfilename(
                title="Select Backup to Restore",
                initialdir=str(self.backup_service.backup_manager.backup_dir),
                filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
            )

            if not backup_path_str:
                return

            # Confirm restoration
            confirm = messagebox.askyesno(
                "Confirm Restore",
                "Are you sure you want to restore this backup?\n\n"
                "The current database will be replaced.\n"
                "A pre-restore backup will be created automatically.\n\n"
                "Continue?"
            )

            if not confirm:
                return

            # Perform restore
            self.backup_service.restore_backup(Path(backup_path_str))

            messagebox.showinfo(
                "Success",
                "Database restored successfully!\n\n"
                "The application will now close. Please restart to load the restored database."
            )

            logger.info(f"Backup restored from: {backup_path_str}")

            # Close application (user will need to restart)
            self.winfo_toplevel().destroy()

        except FileNotFoundError as e:
            messagebox.showerror(
                "Error",
                f"Backup file not found:\n{e}"
            )
            logger.error(f"Restore failed - file not found: {e}")

        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Invalid backup file:\n{e}"
            )
            logger.error(f"Restore failed - invalid file: {e}")

        except IOError as e:
            messagebox.showerror(
                "Error",
                f"Failed to restore backup:\n{e}"
            )
            logger.error(f"Restore failed: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unexpected error restoring backup:\n{e}"
            )
            logger.error(f"Unexpected error during restore: {e}")

    def export_excel(self):
        """Export all data to Excel."""
        try:
            save_path = filedialog.asksaveasfilename(
                title="Export to Excel",
                defaultextension=".xlsx",
                filetypes=[
                    ("Excel Files", "*.xlsx"),
                    ("All Files", "*.*")
                ],
                initialfile=f"employee_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )

            if not save_path:
                return

            self.exporter.export_all_to_excel(Path(save_path))

            messagebox.showinfo(
                "Success",
                f"Data exported successfully to:\n{save_path}"
            )

            logger.info(f"Excel export completed: {save_path}")

        except IOError as e:
            messagebox.showerror(
                "Error",
                f"Failed to export to Excel:\n{e}"
            )
            logger.error(f"Excel export failed: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unexpected error exporting to Excel:\n{e}"
            )
            logger.error(f"Unexpected error during Excel export: {e}")

    def export_csv(self):
        """Export to CSV."""
        try:
            save_path = filedialog.asksaveasfilename(
                title="Export to CSV",
                defaultextension=".csv",
                filetypes=[
                    ("CSV Files", "*.csv"),
                    ("All Files", "*.*")
                ],
                initialfile=f"employee_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            if not save_path:
                return

            self.exporter.export_to_csv(Path(save_path))

            messagebox.showinfo(
                "Success",
                f"Data exported successfully to:\n{save_path}"
            )

            logger.info(f"CSV export completed: {save_path}")

        except IOError as e:
            messagebox.showerror(
                "Error",
                f"Failed to export to CSV:\n{e}"
            )
            logger.error(f"CSV export failed: {e}")

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Unexpected error exporting to CSV:\n{e}"
            )
            logger.error(f"Unexpected error during CSV export: {e}")
