# PLAN DE DÉVELOPPEMENT - CUSTOMTKINTER UI

## 📋 STRUCTURE DU PLAN

Ce plan divise le développement en **7 phases séquentielles**, chacune avec des objectifs clairs et des livrables spécifiques.

**Estimation totale**: 5-7 jours de développement

---

## 🎯 PHASE 0 : PRÉPARATION & VALIDATION

### Objectifs
- Valider la stack technique
- Vérifier les dépendances
- Préparer l'environnement

### Tâches

#### 0.1. Stack Technique
**Outils à utiliser :**
- **UI Framework**: CustomTkinter (moderne, native look)
- **ORM**: Peewee (déjà en place)
- **Database**: SQLite (déjà en place)
- **Excel Import**: openpyxl (déjà dans pyproject.toml)
- **Build**: PyInstaller (à ajouter)

**Pourquoi CustomTkinter ?**
- Look moderne (dark mode natif)
- Widgets prêts à l'emploi
- Cross-platform (Windows, Linux, macOS)
- Léger (~500-700 lignes attendues)
- Pas de dépendances lourdes (contrairement à Flet)

#### 0.2. Dépendances
**À ajouter à pyproject.toml :**
```toml
dependencies = [
    # ... existantes ...
    "customtkinter>=5.2.0",  # UI framework
    "pillow>=10.0.0",        # Requis par CustomTkinter
]

[optional-dependencies]
build = [
    "pyinstaller>=6.0.0",    # Pour créer l'exe
]
```

#### 0.3. Structure des dossiers
**À créer :**
```
src/
└── ui_ctk/                    # Nouveau dossier CustomTkinter
    ├── __init__.py
    ├── app.py                 # Point d'entrée principal
    ├── main_window.py         # Fenêtre principale avec navigation
    ├── views/                 # Écrans de l'application
    │   ├── __init__.py
    │   ├── employee_list.py   # Liste des employés
    │   ├── employee_detail.py # Détail employé
    │   ├── alerts_view.py     # Vue des alertes
    │   └── import_view.py     # Import Excel
    ├── forms/                 # Formulaires de saisie
    │   ├── __init__.py
    │   ├── employee_form.py   # Formulaire employé
    │   ├── caces_form.py      # Formulaire CACES
    │   └── medical_form.py    # Formulaire visite médicale
    └── widgets/               # Widgets réutilisables
        ├── __init__.py
        ├── status_badge.py    # Badge de statut coloré
        └── date_picker.py     # Sélecteur de date
```

**Livrable :**
- ✅ Structure de dossiers validée
- ✅ Dépendances identifiées
- ✅ Environnement prêt

---

## 🗄️ PHASE 1 : MODÈLE DE DONNÉES & MIGRATION

### Objectifs
- Ajouter les champs contact au modèle Employee
- Créer la migration de base de données
- Valider les changements

### Tâches

#### 1.1. Mettre à jour le modèle Employee
**Changement dans `src/employee/models.py` :**
```python
class Employee(Model):
    # ... existants ...

    # Contact Information (NOUVEAUX)
    phone = CharField(null=True)      # Téléphone (optionnel)
    email = CharField(null=True)      # Email (optionnel)

    # ... reste existant ...
```

**Raison :**
- Nécessaire pour contacter les employés
- Demandé explicitement pour V1

#### 1.2. Créer le script de migration
**Fichier : `src/database/migrations/add_employee_contacts.py`**
```python
"""Migration: Add phone and email to Employee table."""

def upgrade():
    """Add phone and email columns to employees table."""
    db = database
    migrator = SqliteMigrator(db)

    # Add columns
    migrate(
        migrator.add_column('employees', 'phone', CharField(null=True)),
        migrator.add_column('employees', 'email', CharField(null=True)),
    )

def downgrade():
    """Remove phone and email columns."""
    db = database
    migrator = SqliteMigrator(db)

    migrate(
        migrator.drop_column('employees', 'phone'),
        migrator.drop_column('employees', 'email'),
    )
```

#### 1.3. Script de migration manuel
**Fichier : `scripts/migrate_add_contacts.py`**
```python
"""Migration manuelle SQLite pour les champs contact."""

import sqlite3
from pathlib import Path

def migrate(db_path: str):
    """Ajoute les colonnes phone et email à la table employees."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Ajouter phone
        cursor.execute("ALTER TABLE employees ADD COLUMN phone TEXT")
        print("✅ Colonne 'phone' ajoutée")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("⚠️ Colonne 'phone' existe déjà")
        else:
            raise

    try:
        # Ajouter email
        cursor.execute("ALTER TABLE employees ADD COLUMN email TEXT")
        print("✅ Colonne 'email' ajoutée")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print("⚠️ Colonne 'email' existe déjà")
        else:
            raise

    conn.commit()
    conn.close()
    print("✅ Migration terminée")
```

#### 1.4. Tester la migration
1. Backup la base de données existante
2. Exécuter la migration
3. Vérifier que les colonnes existent
4. Tester la création d'un employé avec phone/email

**Livrables :**
- ✅ Modèle Employee mis à jour avec phone/email
- ✅ Script de migration fonctionnel
- ✅ Migration testée sur la base de données
- ✅ Documentation de la migration

---

## 🖼️ PHASE 2 : STRUCTURE UI CUSTOMTKINTER

### Objectifs
- Créer la structure de base de l'application
- Implémenter la fenêtre principale avec navigation
- Mettre en place le système de navigation entre vues

### Tâches

#### 2.1. Point d'entrée (app.py)
**Fichier : `src/ui_ctk/app.py`**

**Responsabilités :**
- Initialiser CustomTkinter
- Créer la fenêtre principale
- Initialiser la connexion à la base de données
- Lancer la boucle principale

**Pseudo-code :**
```python
import customtkinter as ctk
from database.connection import database
from ui_ctk.main_window import MainWindow

def main():
    """Point d'entrée de l'application."""
    # Setup CustomTkinter
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    # Create main window
    app = ctk.CTk()
    app.title("Wareflow EMS - Gestion des Salariés")
    app.geometry("1200x800")

    # Connect to database
    database.connect()
    database.create_tables([Employee, Caces, MedicalVisit, OnlineTraining])

    # Create main window with navigation
    main_window = MainWindow(app)
    main_window.pack(fill="both", expand=True)

    # Run
    app.mainloop()

    # Cleanup
    database.close()
```

#### 2.2. Fenêtre principale avec navigation (main_window.py)
**Fichier : `src/ui_ctk/main_window.py`**

**Layout :**
```
┌────────────────────────────────────────────┐
│  Wareflow EMS - Gestion des Salariés       │
├────────────────────────────────────────────┤
│  [Employés] [Alertes] [Import]            │  ← Navigation Bar
├────────────────────────────────────────────┤
│                                            │
│                                            │
│            CONTENU DE LA VUE               │  ← View Container
│            (change dynamiquement)          │
│                                            │
│                                            │
└────────────────────────────────────────────┘
```

**Responsabilités :**
- Créer la barre de navigation
- Gérer le changement de vues
- Maintenir l'état global de l'application

**Pseudo-code :**
```python
import customtkinter as ctk
from ui_ctk.views.employee_list import EmployeeListView
from ui_ctk.views.alerts_view import AlertsView
from ui_ctk.views.import_view import ImportView

class MainWindow(ctk.CTkFrame):
    """Fenêtre principale avec navigation."""

    def __init__(self, master):
        super().__init__(master)

        # Navigation bar
        self.nav_bar = ctk.CTkFrame(self)
        self.nav_bar.pack(side="top", fill="x", padx=10, pady=10)

        # View container
        self.view_container = ctk.CTkFrame(self)
        self.view_container.pack(fill="both", expand=True)

        # Navigation buttons
        self.create_nav_buttons()

        # Show default view
        self.show_employee_list()

    def create_nav_buttons(self):
        """Crée les boutons de navigation."""
        btn_employees = ctk.CTkButton(
            self.nav_bar,
            text="👥 Employés",
            command=self.show_employee_list
        )
        btn_employees.pack(side="left", padx=5)

        btn_alerts = ctk.CTkButton(
            self.nav_bar,
            text="⚠️ Alertes",
            command=self.show_alerts
        )
        btn_alerts.pack(side="left", padx=5)

        btn_import = ctk.CTkButton(
            self.nav_bar,
            text="📥 Import Excel",
            command=self.show_import
        )
        btn_import.pack(side="left", padx=5)

    def show_employee_list(self):
        """Affiche la vue liste des employés."""
        self.clear_view()
        EmployeeListView(self.view_container).pack(fill="both", expand=True)

    def show_alerts(self):
        """Affiche la vue des alertes."""
        self.clear_view()
        AlertsView(self.view_container).pack(fill="both", expand=True)

    def show_import(self):
        """Affiche la vue d'import."""
        self.clear_view()
        ImportView(self.view_container).pack(fill="both", expand=True)

    def clear_view(self):
        """Supprime la vue actuelle."""
        for widget in self.view_container.winfo_children():
            widget.destroy()
```

**Livrables :**
- ✅ Point d'entrée créé (app.py)
- ✅ Fenêtre principale avec navigation
- ✅ Boutons de navigation fonctionnels
- ✅ Système de changement de vues opérationnel

---

## 👥 PHASE 3 : VUE EMPLOYÉS

### Objectifs
- Créer la vue liste des employés
- Créer la vue détail employé
- Créer les formulaires de saisie

### Tâches

#### 3.1. Vue Liste des Employés (employee_list.py)
**Fichier : `src/ui_ctk/views/employee_list.py`**

**Layout :**
```
┌────────────────────────────────────────────┐
│  👥 Liste des Employés                     │
├────────────────────────────────────────────┤
│  🔍 [Rechercher........................]    │
│  📊 [Actifs ▼]                             │
├────────────────────────────────────────────┤
│  │ Nom           │ Statut   │ Actions    │  ← TableHeader
│  ├───────────────┼──────────┼────────────┤
│  │ Jean Dupont   │ Actif    │ [Détail]   │  ← Row
│  │ Marie Martin  │ Actif    │ [Détail]   │  ← Row
│  │ Pierre Bernard│ Inactif  │ [Détail]   │  ← Row
│  └───────────────┴──────────┴────────────┘
│                     ↓                        ↓
│              [➕ Ajouter]             [🔄 Rafraîchir]
└────────────────────────────────────────────┘
```

**Responsabilités :**
- Afficher la liste des employés dans un tableau
- Permettre la recherche par nom
- Filtrer par statut (actif/inactif)
- Bouton pour voir le détail d'un employé
- Bouton pour ajouter un nouvel employé

**Pseudo-code :**
```python
import customtkinter as ctk
from employee.models import Employee
from ui_ctk.forms.employee_form import EmployeeFormDialog
from ui_ctk.views.employee_detail import EmployeeDetailView

class EmployeeListView(ctk.CTkFrame):
    """Vue liste des employés."""

    def __init__(self, master):
        super().__init__(master)

        # Header
        self.create_header()

        # Search and filter bar
        self.create_search_filter()

        # Employee table
        self.create_table()

        # Load employees
        self.refresh_employee_list()

    def create_header(self):
        """Crée le header."""
        header = ctk.CTkLabel(self, text="👥 Liste des Employés", font=("Arial", 20, "bold"))
        header.pack(pady=10)

    def create_search_filter(self):
        """Crée la barre de recherche et filtre."""
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=10)

        # Search
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search)
        search_entry = ctk.CTkEntry(
            control_frame,
            placeholder_text="🔍 Rechercher par nom...",
            textvariable=self.search_var
        )
        search_entry.pack(side="left", padx=5)

        # Filter
        self.filter_var = ctk.StringVar(value="all")
        filter_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["Tous", "Actifs", "Inactifs"],
            variable=self.filter_var,
            command=self.on_filter
        )
        filter_menu.pack(side="left", padx=5)

        # Refresh button
        refresh_btn = ctk.CTkButton(
            control_frame,
            text="🔄 Rafraîchir",
            command=self.refresh_employee_list
        )
        refresh_btn.pack(side="right", padx=5)

    def create_table(self):
        """Crée le tableau des employés."""
        # Scrollable frame
        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Header row
        self.create_table_header()

        # Data rows (placeholder)
        self.table_rows = []

    def create_table_header(self):
        """Crée l'entête du tableau."""
        header_frame = ctk.CTkFrame(self.table_frame)
        header_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(header_frame, text="Nom", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Email", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Téléphone", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Statut", font=("Arial", 12, "bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Actions", font=("Arial", 12, "bold")).pack(side="right", padx=10)

    def refresh_employee_list(self):
        """Charge la liste des employés."""
        # Clear existing rows
        for row in self.table_rows:
            row.destroy()
        self.table_rows.clear()

        # Fetch employees
        employees = Employee.select()

        # Apply filter
        filter_value = self.filter_var.get()
        if filter_value == "Actifs":
            employees = employees.where(Employee.current_status == "active")
        elif filter_value == "Inactifs":
            employees = employees.where(Employee.current_status == "inactive")

        # Apply search
        search_term = self.search_var.get().lower()
        if search_term:
            employees = employees.where(
                (Employee.first_name.contains(search_term)) |
                (Employee.last_name.contains(search_term))
            )

        # Create rows
        for employee in employees:
            row = self.create_employee_row(employee)
            row.pack(fill="x", pady=2)
            self.table_rows.append(row)

    def create_employee_row(self, employee):
        """Crée une ligne pour un employé."""
        row = ctk.CTkFrame(self.table_frame)

        name_label = ctk.CTkLabel(row, text=employee.full_name)
        name_label.pack(side="left", padx=10)

        email_label = ctk.CTkLabel(row, text=employee.email or "-")
        email_label.pack(side="left", padx=10)

        phone_label = ctk.CTkLabel(row, text=employee.phone or "-")
        phone_label.pack(side="left", padx=10)

        status_color = "green" if employee.is_active else "gray"
        status_label = ctk.CTkLabel(
            row,
            text="✓ Actif" if employee.is_active else "○ Inactif",
            text_color=status_color
        )
        status_label.pack(side="left", padx=10)

        detail_btn = ctk.CTkButton(
            row,
            text="Détail",
            width=80,
            command=lambda: self.show_employee_detail(employee)
        )
        detail_btn.pack(side="right", padx=5)

        return row

    def show_employee_detail(self, employee):
        """Affiche le détail d'un employé."""
        # Clear view and show detail
        self.master.clear_view()
        EmployeeDetailView(self.master.view_container, employee).pack(fill="both", expand=True)

    def on_search(self, *args):
        """Gère la recherche."""
        self.refresh_employee_list()

    def on_filter(self, value):
        """Gère le filtre."""
        self.refresh_employee_list()

    def add_employee(self):
        """Ajoute un nouvel employé."""
        dialog = EmployeeFormDialog(self)
        if dialog.result:
            self.refresh_employee_list()
```

#### 3.2. Formulaire Employé (employee_form.py)
**Fichier : `src/ui_ctk/forms/employee_form.py`**

**Responsabilités :**
- Formulaire de création/édition d'employé
- Validation des champs
- Sauvegarde en base de données

**Layout du formulaire :**
```
┌─────────────────────────────────────────┐
│  ➕ Nouvel Employé / ✏️ Modifier        │
├─────────────────────────────────────────┤
│  Prénom : [________________]  *         │
│  Nom :    [________________]  *         │
│  Email :  [________________]            │
│  Téléphone : [________]                 │
│  Statut : [Actif ▼]        *            │
│  Espace de travail : [________]  *      │
│  Rôle : [________]        *             │
│  Type de contrat : [CDI ▼]   *         │
│  Date d'entrée : [DD/MM/YYYY]  *       │
│                                         │
│     [Annuler]              [Sauvegarder]│
└─────────────────────────────────────────┘
```

#### 3.3. Vue Détail Employé (employee_detail.py)
**Fichier : `src/ui_ctk/views/employee_detail.py`**

**Layout :**
```
┌────────────────────────────────────────────┐
│  ← Retour    Jean Dupont                  │
├────────────────────────────────────────────┤
│  Informations                             │
│  ┌──────────────────────────────────────┐ │
│  │ Email : jean.dupont@example.com      │ │
│  │ Téléphone : 06 12 34 56 78           │ │
│  │ Statut : Actif                        │ │
│  │ Contrat : CDI                         │ │
│  │ Espace : Zone A                       │ │
│  │ Rôle : Cariste                        │ │
│  │ Date entrée : 15/01/2025              │ │
│  └──────────────────────────────────────┘ │
│                                          │
│  CACES                    [➕ Ajouter]   │
│  ┌──────────────────────────────────────┐ │
│  │ R489-1A | Expire : 15/01/2030 ✓     │ │
│  └──────────────────────────────────────┘ │
│                                          │
│  Visites Médicales         [➕ Ajouter]  │
│  ┌──────────────────────────────────────┐ │
│  │ Périodique | Expire : 15/01/2027 ✓  │ │
│  └──────────────────────────────────────┘ │
│                                          │
│           [✏️ Modifier] [🗑️ Supprimer]   │
└────────────────────────────────────────────┘
```

**Livrables :**
- ✅ Vue liste des employés fonctionnelle
- ✅ Recherche et filtres opérationnels
- ✅ Formulaire employé avec validation
- ✅ Vue détail employé complète
- ✅ CRUD employé complet

---

## ⚠️ PHASE 4 : VUE ALERTES

### Objectifs
- Créer la vue des alertes simples
- Implémenter les filtres par type et jours
- Afficher les alertes colorées par urgence

### Tâches

#### 4.1. Vue Alertes (alerts_view.py)
**Fichier : `src/ui_ctk/views/alerts_view.py`**

**Layout :**
```
┌────────────────────────────────────────────┐
│  ⚠️ Alertes                                │
├────────────────────────────────────────────┤
│  Type : [Tous ▼]    Jours : [30 ▼]        │
├────────────────────────────────────────────┤
│  🔴 CACES R489-1A - Jean Dupont            │
│     Expire dans 12 jours (15/02/2025)      │
│     [Voir Détail]                          │
├────────────────────────────────────────────┤
│  🟡 Visite médicale - Marie Martin         │
│     Expire dans 45 jours (15/03/2025)      │
│     [Voir Détail]                          │
├────────────────────────────────────────────┤
│  🟢 CACES R489-3 - Pierre Bernard          │
│     Expire dans 89 jours (15/04/2025)      │
│     [Voir Détail]                          │
└────────────────────────────────────────────┘
```

**Filtres disponibles :**
- **Type** : Tous, CACES, Visites médicales, Formations
- **Jours** : 30 (critique), 60 (avertissement), 90 (information), Toutes

**Code de couleurs :**
- 🔴 **Rouge** : Expiré ou moins de 30 jours
- 🟡 **Jaune** : 30-60 jours
- 🟢 **Vert** : 60-90 jours
- ⚪ **Gris** : Plus de 90 jours

**Livrables :**
- ✅ Vue alertes simple et claire
- ✅ Filtres par type et par jours
- ✅ Coloration par urgence
- ✅ Lien vers détail employé

---

## 📥 PHASE 5 : IMPORT EXCEL

### Objectifs
- Créer la vue d'import Excel
- Implémenter la validation des données
- Gérer les erreurs d'import

### Tâches

#### 5.1. Vue Import Excel (import_view.py)
**Fichier : `src/ui_ctk/views/import_view.py`**

**Layout :**
```
┌────────────────────────────────────────────┐
│  📥 Import Excel                           │
├────────────────────────────────────────────┤
│  Importez un fichier Excel contenant       │
│  la liste des employés à importer.         │
│                                          │
│  [Choisir un fichier Excel...]             │
│                                          │
│  Format attendu :                          │
│  ┌──────────────────────────────────────┐ │
│  │ Prénom | Nom | Email | Téléphone |  │ │
│  │ Jean   | Dupont | ... | ...        │ │
│  └──────────────────────────────────────┘ │
│                                          │
│  [📥 Télécharger le modèle]               │
│                                          │
│  ┌──────────────────────────────────────┐ │
│  │ Progression : ████░░░░░░ 50%        │ │
│  │ 5 employés importés / 10             │ │
│  └──────────────────────────────────────┘ │
│                                          │
│  [Importer]                               │
└────────────────────────────────────────────┘
```

**Fonctionnalités :**
- Sélection de fichier Excel
- Validation du format
- Affichage de la progression
- Rapport d'erreurs (ligne par ligne)
- Annulation possible

**Livrables :**
- ✅ Vue d'import Excel fonctionnelle
- ✅ Validation des données
- ✅ Gestion des erreurs
- ✅ Rapport d'import détaillé

---

## 🧪 PHASE 6 : TESTS & VALIDATION

### Objectifs
- Tester toutes les fonctionnalités
- Corriger les bugs
- Valider l'UX

### Tâches

#### 6.1. Tests manuels

**Scénarios à tester :**

1. **CRUD Employé :**
   - ✅ Créer un employé avec tous les champs
   - ✅ Créer un employé avec seulement les champs obligatoires
   - ✅ Modifier un employé existant
   - ✅ Supprimer un employé (avec confirmation)
   - ✅ Rechercher un employé par nom
   - ✅ Filtrer par statut (actif/inactif)

2. **CACES & Visites :**
   - ✅ Ajouter un CACES (vérifier le calcul d'expiration)
   - ✅ Ajouter une visite médicale (vérifier le calcul)
   - ✅ Vérifier les statuts (valid, warning, critical, expired)

3. **Alertes :**
   - ✅ Afficher les alertes CACES
   - ✅ Afficher les alertes visites médicales
   - ✅ Filtrer par type
   - ✅ Filtrer par jours (30, 60, 90)
   - ✅ Vérifier la coloration

4. **Import Excel :**
   - ✅ Importer un fichier valide
   - ✅ Importer un fichier avec des erreurs (vérifier la gestion)
   - ✅ Importer un fichier avec des formats incorrects
   - ✅ Annuler un import en cours

5. **Navigation :**
   - ✅ Changer de vue sans erreur
   - ✅ Retour à la liste depuis le détail
   - ✅ Persistance des données entre les vues

#### 6.2. Tests de performance

- ✅ Temps de chargement de la liste (avec 100+ employés)
- ✅ Rapidité de la recherche
- ✅ Fluidité de la navigation
- ✅ Mémoire utilisée

#### 6.3. Tests UX

- ✅ Intuitivité de l'interface
- ✅ Clarté des messages d'erreur
- ✅ Accessibilité (taille des boutons, lisibilité)
- ✅ Cohérence visuelle

**Livrables :**
- ✅ Tous les scénarios testés
- ✅ Bugs corrigés
- ✅ UX validée

---

## 📦 PHASE 7 : BUILD & DÉPLOIEMENT

### Objectifs
- Créer l'exécutable .exe
- Tester l'exécutable
- Préparer le déploiement

### Tâches

#### 7.1. Configuration PyInstaller

**Fichier : `build.spec`**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/ui_ctk/app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/database', 'src/database'),
        ('src/employee', 'src/employee'),
        ('src/controllers', 'src/controllers'),
        ('src/state', 'src/state'),
        ('src/lock', 'src/lock'),
    ],
    hiddenimports=[
        'peewee',
        'customtkinter',
        'PIL',
        'dateutil',
        'openpyxl',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WareflowEMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de console Windows
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico'  # Optionnel
)
```

#### 7.2. Script de build

**Fichier : `scripts/build.bat`**
```batch
@echo off
echo ========================================
echo Build Wareflow EMS
echo ========================================

echo.
echo [1/4] Nettoyage...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo [2/4] Installation des dépendances...
pip install -e .

echo.
echo [3/4] Build PyInstaller...
pyinstaller build.spec --clean

echo.
echo [4/4] Terminé !
echo.
echo L'exécutable est dans : dist\WareflowEMS.exe
pause
```

#### 7.3. Structure de déploiement

**Dossier à déployer :**
```
[Gestion_Salaries_2025/
├── WareflowEMS.exe              # L'application
├── data/                        # Données (créé au lancement)
│   └── employee_manager.db      # Base de données SQLite
├── documents/                   # Documents uploadés
│   ├── caces/                   # Certificats CACES
│   ├── medical/                 # Visites médicales
│   └── training/                # Formations
└── README.txt                   # Instructions
```

#### 7.4. Tests de l'exécutable

- ✅ Lancement sans erreur
- ✅ Connexion à la base de données
- ✅ Toutes les fonctionnalités testées
- ✅ Performance acceptable
- ✅ Aucune dépendance manquante

**Livrables :**
- ✅ Exécutable .exe fonctionnel
- ✅ Structure de déploiement prête
- ✅ Instructions d'installation
- ✅ README utilisateur

---

## 📊 RÉSUMÉ DU PLAN

### Durée estimée par phase

| Phase | Durée | Complexité |
|-------|-------|------------|
| **Phase 0** : Préparation | 2h | Faible |
| **Phase 1** : Modèle & Migration | 2h | Faible |
| **Phase 2** : Structure UI | 4h | Moyenne |
| **Phase 3** : Vue Employés | 8h | Moyenne |
| **Phase 4** : Vue Alertes | 4h | Faible |
| **Phase 5** : Import Excel | 6h | Moyenne |
| **Phase 6** : Tests | 4h | Faible |
| **Phase 7** : Build | 2h | Faible |
| **TOTAL** | **32h** (~5-7 jours) | - |

### Dependencies entre phases

```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 6 → Phase 7
                              ↘
                               Phase 4 ↗
                               Phase 5 ↗
```

### Points de contrôle

- **Fin Phase 1** : Migration validée ✅
- **Fin Phase 3** : CRUD employé fonctionnel ✅
- **Fin Phase 5** : Toutes les vues implémentées ✅
- **Fin Phase 6** : Application testée et validée ✅
- **Fin Phase 7** : .exe prêt à déployer ✅

---

## 🎯 CRITERES DE SUCCÈS

### Fonctionnels
- ✅ CRUD employé complet
- ✅ Ajout de CACES et visites médicales
- ✅ Vue alertes fonctionnelle
- ✅ Import Excel opérationnel
- ✅ Base de données SQLite persistante

### Non-fonctionnels
- ✅ Interface en français
- ✅ Design moderne (CustomTkinter)
- ✅ Performance acceptable (<2s pour charger 100 employés)
- ✅ Exécutable .exe autonome
- ✅ Une seule connexion à la fois (lock manager)

### UX
- ✅ Interface intuitive
- ✅ Messages d'erreur clairs
- ✅ Navigation fluide
- ✅ Feedback utilisateur (progression, confirmations)

---

## 🚀 PROCHAINES ÉTAPES

**Immédiat :**
1. Valider ce plan avec l'utilisateur
2. Ajouter les dépendances CustomTkinter au projet
3. Commencer Phase 0 (Préparation)

**Après validation :**
- Suivre les phases séquentiellement
- Marquer chaque étape comme terminée
- Faire des commits fréquents
- Tester à chaque phase

**Bon développement ! 🎉**
