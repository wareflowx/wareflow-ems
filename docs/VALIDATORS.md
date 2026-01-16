# Module de Validation

## Vue d'Ensemble

Le module de validation (`src/employee/validators.py`) fournit une validation structurée pour toutes les données liées aux employés. Il garantit l'intégrité des données, améliore la sécurité et offre des messages d'erreur clairs pour les utilisateurs.

### Objectifs

1. **Intégrité des données** : Garantir que toutes les données respectent les règles métier
2. **Sécurité** : Prévenir les attaques par path traversal et injection
3. **Expérience Utilisateur** : Messages d'erreur clairs et exploitables
4. **Maintenabilité** : Logique de validation centralisée et réutilisable

### Architecture

```
Application Layer (CLI, UI)
    ↓
Validation Layer (validators.py)
    ↓
Model Layer (before_save hooks)
    ↓
Database Layer (SQL constraints)
```

---

## ValidationError

### Description

Exception structurée pour les erreurs de validation. Fournit des informations détaillées sur les erreurs de validation.

### Attributs

- `field` : Nom du champ en erreur
- `value` : La valeur invalide
- `message` : Message d'erreur principal
- `details` : Dictionnaire avec informations supplémentaires

### Méthodes

- `__str__()` : Retourne le message d'erreur formaté
- `to_dict()` : Convertit l'exception en dictionnaire pour les réponses API

### Exemple

```python
from employee.validators import ValidationError

try:
    validate_external_id("../etc/passwd")
except ValidationError as e:
    print(e.field)        # "external_id"
    print(e.message)      # "Path traversal detected"
    print(e.details)      # {"forbidden_pattern": "../"}
    print(str(e))         # "Validation failed for field 'external_id': Path traversal detected"
```

---

## Validators Fonctionnels

### validate_external_id()

**Valide le format de l'ID externe d'un employé.**

#### Règles de validation

- Longueur : 3 à 50 caractères
- Caractères autorisés : Lettres (A-Za-z), chiffres (0-9), underscore (_), tiret (-)
- Pas d'espaces ou de caractères spéciaux
- Protection contre le path traversal (`../`, `..\\`, `./`, `.\\`, `/`, `\`)

#### Paramètres

- `external_id` (str) : ID externe à valider

#### Retourne

- `str` : L'ID validé (inchangé si valide)

#### Lève

- `ValidationError` : Si le format est invalide

#### Exemples

```python
from employee.validators import validate_external_id

# Valid
validate_external_id("WMS-001")  # → "WMS-001"
validate_external_id("R489_1A")  # → "R489_1A"
validate_external_id("ABC")      # → "ABC"

# Invalides
validate_external_id("R489 1A")  # ValidationError: invalid characters
validate_external_id("../etc/passwd")  # ValidationError: path traversal
validate_external_id("AB")       # ValidationError: too short
validate_external_id("A" * 51)   # ValidationError: too long
```

---

### validate_entry_date()

**Valide la date d'entrée d'un employé.**

#### Règles de validation

- La date ne peut pas être dans le futur
- La date doit être >= 1900-01-01
- La date est obligatoire

#### Paramètres

- `entry_date` (date) : Date d'entrée à valider

#### Retourne

- `date` : La date validée

#### Lève

- `ValidationError` : Si la date est invalide

#### Exemples

```python
from employee.validators import validate_entry_date
from datetime import date

# Valides
validate_entry_date(date(2020, 1, 15))  # → date(2020, 1, 15)
validate_entry_date(date(1900, 1, 1))   # → date(1900, 1, 1)
validate_entry_date(date.today())       # → date.today()

# Invalides
validate_entry_date(date(2100, 1, 1))  # ValidationError: future date
validate_entry_date(date(1800, 1, 1))  # ValidationError: too old
validate_entry_date(None)              # ValidationError: required
```

---

### validate_caces_kind()

**Valide le type de certification CACES.**

#### Règles de validation

- Le type doit être dans `CACES_TYPES` (R489-1A, R489-1B, R489-3, R489-4, R489-5)
- La validation est insensible à la casse (convertit en majuscules)

#### Paramètres

- `kind` (str) : Type de CACES à valider

#### Retourne

- `str` : Le type validé (en majuscules)

#### Lève

- `ValidationError` : Si le type n'est pas reconnu

#### Exemples

```python
from employee.validators import validate_caces_kind

# Valides
validate_caces_kind("R489-1A")  # → "R489-1A"
validate_caces_kind("r489-1b")  # → "R489-1B" (convertit en majuscules)
validate_caces_kind("R489-5")   # → "R489-5"

# Invalides
validate_caces_kind("R489-2")   # ValidationError: invalid type
validate_caces_kind("CACES 1A") # ValidationError: invalid type
```

---

### validate_medical_visit_consistency()

**Valide la cohérence entre le type de visite et le résultat.**

#### Règles de validation

- `visit_type` doit être dans `['initial', 'periodic', 'recovery']`
- `result` doit être dans `['fit', 'unfit', 'fit_with_restrictions']`
- **Règle métier** : Si `visit_type` est "recovery", le résultat DOIT être "fit_with_restrictions"

#### Paramètres

- `visit_type` (str) : Type de visite
- `result` (str) : Résultat de la visite

#### Retourne

- `tuple` : (visit_type, result) validé

#### Lève

- `ValidationError` : Si la combinaison est invalide

#### Exemples

```python
from employee.validators import validate_medical_visit_consistency

# Valides
validate_medical_visit_consistency("initial", "fit")  # → ("initial", "fit")
validate_medical_visit_consistency("periodic", "unfit")  # → ("periodic", "unfit")
validate_medical_visit_consistency("recovery", "fit_with_restrictions")  # → ("recovery", "fit_with_restrictions")

# Invalides
validate_medical_visit_consistency("recovery", "fit")  # ValidationError: must have restrictions
validate_medical_visit_consistency("recovery", "unfit")  # ValidationError: must have restrictions
validate_medical_visit_consistency("invalid", "fit")  # ValidationError: invalid type
```

#### Justification métier

Une visite de reprise ("recovery") survient après un arrêt maladie. Lorsqu'un employé retourne au travail après un arrêt, il a généralement des restrictions médicales temporaires. C'est pourquoi cette combinaison exige "fit_with_restrictions".

---

### validate_path_safe()

**Valide qu'un chemin de fichier est sûr (pas de path traversal).**

#### Règles de validation

- Pas de patterns de path traversal (`../`, `..\\`, `./`, `.\\`)
- Pas de chemins absolus (doit être relatif)
- Optionnel : validation de l'extension du fichier

#### Paramètres

- `file_path` (str) : Chemin de fichier à valider
- `allowed_extensions` (list, optionnel) : Liste des extensions autorisées (ex: [".pdf", ".jpg"])

#### Retourne

- `str` : Le chemin validé

#### Lève

- `ValidationError` : Si le chemin est dangereux

#### Exemples

```python
from employee.validators import validate_path_safe

# Valides
validate_path_safe("documents/caces.pdf")  # → "documents/caces.pdf"
validate_path_safe("file.txt")  # → "file.txt"
validate_path_safe("doc.pdf", allowed_extensions=[".pdf", ".jpg"])  # → "doc.pdf"

# Invalides
validate_path_safe("../../../etc/passwd")  # ValidationError: path traversal
validate_path_safe("./config.yml")  # ValidationError: path traversal
validate_path_safe("/etc/passwd")  # ValidationError: absolute path
validate_path_safe("C:\\Windows\\System32")  # ValidationError: absolute path
validate_path_safe("file.exe", allowed_extensions=[".pdf"])  # ValidationError: extension not allowed
```

---

## Validators de Classes

### UniqueValidator

**Validateur d'unicité réutilisable pour les modèles Peewee.**

#### Description

Vérifie qu'une valeur est unique dans une table de base de données. Peut exclure une instance spécifique (utile pour les mises à jour).

#### Constructeur

```python
UniqueValidator(model_class, field, exclude_instance=None)
```

- `model_class` (Model) : Classe du modèle Peewee
- `field` : Champ à vérifier
- `exclude_instance` (Model, optionnel) : Instance à exclure de la vérification

#### Méthodes

- `validate(value)` : Valide l'unicité de la valeur

#### Exemples

```python
from employee.validators import UniqueValidator
from employee.models import Employee

# Création : vérifie que l'ID n'existe pas
validator = UniqueValidator(Employee, Employee.external_id)
validator.validate("WMS-001")  # OK si n'existe pas
validator.validate("WMS-001")  # ValidationError si existe déjà

# Mise à jour : exclut l'instance courante
employee = Employee.get_by_id(1)
validator = UniqueValidator(Employee, Employee.external_id, exclude_instance=employee)
validator.validate(employee.external_id)  # OK - exclut lui-même
```

---

### DateRangeValidator

**Validateur de plage de dates réutilisable.**

#### Description

S'assure qu'une date est dans une plage spécifiée. Utile pour valider des dates comme les dates d'entrée, les dates de naissance, etc.

#### Constructeur

```python
DateRangeValidator(min_date=None, max_date=None, field_name="date")
```

- `min_date` (date, optionnel) : Date minimum
- `max_date` (date, optionnel) : Date maximum
- `field_name` (str) : Nom du champ pour les messages d'erreur

#### Méthodes

- `validate(value)` : Valide que la date est dans la plage

#### Exemples

```python
from employee.validators import DateRangeValidator
from datetime import date

# Date d'entrée : pas dans le futur, minimum 1900
validator = DateRangeValidator(
    min_date=date(1900, 1, 1),
    max_date=date.today(),
    field_name="entry_date"
)

validator.validate(date(2020, 1, 15))  # OK
validator.validate(date(2100, 1, 1))  # ValidationError: too late
validator.validate(date(1800, 1, 1))  # ValidationError: too early

# Sans minimum
validator = DateRangeValidator(max_date=date.today())
validator.validate(date(1800, 1, 1))  # OK - pas de minimum
```

---

## Intégration dans les Modèles

Les validators sont intégrés dans les modèles via les hooks `before_save()` :

### Employee

```python
def before_save(self):
    # Valide le format de l'external_id
    if self.external_id:
        self.external_id = validate_external_id(self.external_id)
        # Vérifie l'unicité
        validator = UniqueValidator(Employee, Employee.external_id, exclude_instance=self if self.id else None)
        validator.validate(self.external_id)

    # Valide la date d'entrée
    if self.entry_date:
        self.entry_date = validate_entry_date(self.entry_date)
```

### Caces

```python
def before_save(self):
    # Valide le type de CACES
    if self.kind:
        self.kind = validate_caces_kind(self.kind)
    # ... calcul de l'expiration
```

### MedicalVisit

```python
def before_save(self):
    # Valide la cohérence visit_type/result
    if self.visit_type and self.result:
        self.visit_type, self.result = validate_medical_visit_consistency(
            self.visit_type, self.result
        )
    # ... calcul de l'expiration
```

---

## Utilisation dans la CLI

Les validators peuvent être utilisés directement dans la CLI pour une validation précoce :

```python
from employee.validators import validate_external_id, ValidationError

# Dans une commande CLI
try:
    external_id = validate_external_id(user_input)
    # Créer l'employé...
except ValidationError as e:
    typer.echo(f"❌ {e.message}", err=True)
    raise typer.Exit(1)
```

---

## Tests

Le module de validation est couvert par **79 tests** :

- **59 tests unitaires** dans `tests/test_employee/test_validators.py`
- **21 tests d'intégration** dans `tests/test_integration/test_validators_integration.py`

### Couverture

La couverture de code pour `validators.py` est > 95%.

---

## Maintenance

### Quand ajouter un nouveau validator

1. Identifier la règle métier à implémenter
2. Créer la fonction de validation dans `validators.py`
3. Ajouter les tests unitaires
4. Intégrer dans le modèle concerné via `before_save()`
5. Ajouter la documentation dans ce fichier

### Exemple

```python
# 1. Créer le validator
def validate_role(role: str) -> str:
    """Valide que le rôle est dans la liste autorisée."""
    valid_roles = ["Cariste", "Magasinier", "Préparateur"]
    if role not in valid_roles:
        raise ValidationError("role", role, f"Role must be one of {valid_roles}")
    return role

# 2. Intégrer dans le modèle
class Employee(Model):
    def before_save(self):
        if self.role:
            self.role = validate_role(self.role)
        # ... autres validations
```

---

## Références

- **Code source** : `src/employee/validators.py`
- **Tests unitaires** : `tests/test_employee/test_validators.py`
- **Tests d'intégration** : `tests/test_integration/test_validators_integration.py`
- **Modèles** : `src/employee/models.py`
- **Constantes** : `src/employee/constants.py`

---

**Version** : 1.0
**Date de création** : 2026-01-16
**Auteur** : Phase 5 implementation
