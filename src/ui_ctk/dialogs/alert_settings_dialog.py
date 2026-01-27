"""Alert settings dialog for configuring warning thresholds."""

from pathlib import Path
from typing import Optional

import customtkinter as ctk

from employee.alert_settings import AlertSettingsManager
from ui_ctk.constants import APP_TITLE


class AlertSettingsDialog(ctk.CTkToplevel):
    """Dialog for configuring alert thresholds per document category."""

    def __init__(self, parent, settings_manager: Optional[AlertSettingsManager] = None):
        """
        Initialize alert settings dialog.

        Args:
            parent: Parent window
            settings_manager: Optional settings manager instance (creates new if None)
        """
        super().__init__(parent)

        # Settings manager
        self.settings_manager = settings_manager or AlertSettingsManager()
        self.original_settings = self._load_current_settings()

        # Result
        self.settings_changed = False

        # Window setup
        self.title(f"{APP_TITLE} - Configuration des Alertes")
        self.geometry("800x700")
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

    def _load_current_settings(self) -> dict:
        """Load current settings for comparison."""
        current = {}
        for category in self.settings_manager.get_all_categories():
            cat_settings = self.settings_manager.get_category_settings(category)
            if cat_settings:
                current[category] = {
                    "enabled": cat_settings.enabled,
                    "info_days": cat_settings.info.days,
                    "warning_days": cat_settings.warning.days,
                    "alert_days": cat_settings.alert.days,
                    "critical_days": cat_settings.critical.days if cat_settings.critical else None,
                }
        return current

    def create_widgets(self):
        """Create dialog widgets."""
        # Main container with scrollable frame
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_container, text="Configuration des Seuils d'Alerte", font=("Arial", 18, "bold")
        )
        title_label.pack(pady=(0, 10))

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            main_container,
            text="Personnalisez les seuils d'alerte pour chaque type de document",
            font=("Arial", 11),
            text_color="gray",
        )
        subtitle_label.pack(pady=(0, 20))

        # Scrollable frame for categories
        scrollable_frame = ctk.CTkScrollableFrame(main_container, height=450)
        scrollable_frame.pack(fill="both", expand=True, pady=(0, 20))

        # Create category frames
        self.category_vars = {}
        categories = [
            ("caces", "CACES", "Certificats d'aptitude à la conduite en sécurité"),
            ("medical", "Visites Médicales", "Visites médicales obligatoires"),
            ("training", "Formations", "Formations en ligne et sécurité"),
            ("contracts", "Contrats", "Contrats de travail"),
        ]

        for cat_id, cat_name, cat_desc in categories:
            self._create_category_frame(scrollable_frame, cat_id, cat_name, cat_desc)

        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10, 0))

        # Save button
        self.save_btn = ctk.CTkButton(
            buttons_frame,
            text="Enregistrer",
            width=150,
            command=self._on_save,
        )
        self.save_btn.pack(side="left", padx=(0, 10))

        # Reset button
        self.reset_btn = ctk.CTkButton(
            buttons_frame,
            text="Réinitialiser",
            width=150,
            fg_color=("gray70", "gray30"),
            command=self._on_reset,
        )
        self.reset_btn.pack(side="left", padx=(0, 10))

        # Cancel button
        self.cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            width=120,
            fg_color=("gray70", "gray30"),
            command=self._on_close,
        )
        self.cancel_btn.pack(side="left")

        # Status label
        self.status_label = ctk.CTkLabel(
            main_container, text="", font=("Arial", 11)
        )
        self.status_label.pack(pady=(10, 0))

    def _create_category_frame(self, parent, category_id: str, category_name: str, category_desc: str):
        """
        Create frame for a category with its settings.

        Args:
            parent: Parent widget
            category_id: Category identifier
            category_name: Display name
            category_desc: Description
        """
        # Get current settings
        cat_settings = self.settings_manager.get_category_settings(category_id)
        if not cat_settings:
            return

        # Category frame
        cat_frame = ctk.CTkFrame(parent)
        cat_frame.pack(fill="x", pady=(0, 15))

        # Header
        header_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        # Enabled checkbox
        enabled_var = ctk.BooleanVar(value=cat_settings.enabled)
        enabled_checkbox = ctk.CTkCheckBox(
            header_frame,
            text="",
            variable=enabled_var,
            width=20,
        )
        enabled_checkbox.pack(side="left", padx=(0, 10))

        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text=category_name,
            font=("Arial", 14, "bold"),
        )
        title_label.pack(side="left")

        # Description
        desc_label = ctk.CTkLabel(
            header_frame,
            text=f" - {category_desc}",
            font=("Arial", 11),
            text_color="gray",
        )
        desc_label.pack(side="left", padx=(5, 0))

        # Thresholds frame
        thresholds_frame = ctk.CTkFrame(cat_frame, fg_color="transparent")
        thresholds_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Create threshold inputs
        self.category_vars[category_id] = {
            "enabled": enabled_var,
            "info": ctk.StringVar(value=str(cat_settings.info.days)),
            "warning": ctk.StringVar(value=str(cat_settings.warning.days)),
            "alert": ctk.StringVar(value=str(cat_settings.alert.days)),
            "critical": (
                ctk.StringVar(value=str(cat_settings.critical.days))
                if cat_settings.critical
                else None
            ),
        }

        thresholds = [
            ("Info", "info", "Information (jours)"),
            ("Warning", "warning", "Avertissement (jours)"),
            ("Alert", "alert", "Alerte (jours)"),
            ("Critical", "critical", "Critique (jours)"),
        ]

        for i, (level_en, level_id, label_fr) in enumerate(thresholds):
            # Skip critical if not supported
            if level_id == "critical" and self.category_vars[category_id][level_id] is None:
                continue

            # Label
            label = ctk.CTkLabel(thresholds_frame, text=label_fr, width=150, anchor="w")
            label.grid(row=i, column=0, sticky="w", padx=(0, 10), pady=5)

            # Entry
            entry = ctk.CTkEntry(
                thresholds_frame,
                width=100,
                textvariable=self.category_vars[category_id][level_id],
                placeholder_text="Jours",
            )
            entry.grid(row=i, column=1, sticky="w", padx=(0, 10), pady=5)

            # Color indicator
            color = self._get_level_color(level_id)
            color_label = ctk.CTkLabel(
                thresholds_frame,
                text="■",
                text_color=color,
                font=("Arial", 20),
            )
            color_label.grid(row=i, column=2, sticky="w", padx=(0, 20), pady=5)

        # Column configuration
        thresholds_frame.grid_columnconfigure(0, weight=0)
        thresholds_frame.grid_columnconfigure(1, weight=0)
        thresholds_frame.grid_columnconfigure(2, weight=1)

    def _get_level_color(self, level: str) -> str:
        """Get color for alert level."""
        colors = {
            "info": "#FFFF00",      # Yellow
            "warning": "#FFA500",   # Orange
            "alert": "#FF0000",     # Red
            "critical": "#8B0000",  # Dark Red
        }
        return colors.get(level, "#000000")

    def _on_save(self):
        """Save settings and close dialog."""
        # Validate and save each category
        for category, vars_dict in self.category_vars.items():
            try:
                # Get values
                info_days = int(vars_dict["info"].get())
                warning_days = int(vars_dict["warning"].get())
                alert_days = int(vars_dict["alert"].get())
                critical_str = vars_dict["critical"].get()
                critical_days = int(critical_str) if critical_str else None
                enabled = vars_dict["enabled"].get()

                # Validate thresholds
                if info_days <= 0 or warning_days <= 0 or alert_days <= 0:
                    self.status_label.configure(
                        text=f"✗ Les seuils doivent être positifs ({category})",
                        text_color="red",
                    )
                    return

                if not (info_days > warning_days > alert_days):
                    self.status_label.configure(
                        text=f"✗ Les seuils doivent être décroissants ({category})",
                        text_color="red",
                    )
                    return

                if critical_days is not None and critical_days >= alert_days:
                    self.status_label.configure(
                        text=f"✗ Le seuil critique doit être inférieur à l'alerte ({category})",
                        text_color="red",
                    )
                    return

                # Update category
                success = self.settings_manager.update_category(
                    category=category,
                    info_days=info_days,
                    warning_days=warning_days,
                    alert_days=alert_days,
                    critical_days=critical_days,
                    enabled=enabled,
                )

                if not success:
                    self.status_label.configure(
                        text=f"✗ Erreur lors de la sauvegarde ({category})",
                        text_color="red",
                    )
                    return

            except ValueError:
                self.status_label.configure(
                    text=f"✗ Valeurs invalides ({category})",
                    text_color="red",
                )
                return

        # All saved successfully
        self.settings_changed = True
        self.status_label.configure(
            text="✓ Paramètres enregistrés avec succès!",
            text_color="green",
        )

        # Close dialog after short delay
        self.after(1000, self._on_close)

    def _on_reset(self):
        """Reset all settings to defaults."""
        for category, vars_dict in self.category_vars.items():
            # Get default settings
            default_settings = self.settings_manager.DEFAULT_SETTINGS.get(category)
            if default_settings:
                vars_dict["enabled"].set(default_settings.enabled)
                vars_dict["info"].set(str(default_settings.info.days))
                vars_dict["warning"].set(str(default_settings.warning.days))
                vars_dict["alert"].set(str(default_settings.alert.days))
                if default_settings.critical and vars_dict["critical"]:
                    vars_dict["critical"].set(str(default_settings.critical.days))

        self.status_label.configure(
            text="Paramètres réinitialisés aux valeurs par défaut",
            text_color="gray",
        )

    def _on_close(self):
        """Handle dialog close."""
        # Check if settings changed
        current_settings = self._load_current_settings()
        if current_settings != self.original_settings:
            # Settings changed but not saved - confirm
            # For now, just close (could add confirmation dialog)
            pass

        self.destroy()

    def run(self) -> bool:
        """
        Show dialog and return result.

        Returns:
            True if settings were changed and saved, False otherwise
        """
        self.wait_window()
        return self.settings_changed
