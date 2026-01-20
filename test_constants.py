"""Test constants module."""

import sys
sys.path.insert(0, 'src')

from ui_ctk.constants import *

def test_constants():
    """Test that all constants are defined."""

    # Test app metadata
    assert APP_NAME == "Wareflow EMS"
    assert APP_VERSION == "1.0.0"
    print("[OK] App metadata constants")

    # Test theme
    assert DEFAULT_THEME == "blue"
    assert DEFAULT_MODE == "System"
    print("[OK] Theme constants")

    # Test colors
    assert COLOR_CRITICAL == "#DC3545"
    assert COLOR_WARNING == "#FFC107"
    assert COLOR_SUCCESS == "#28A745"
    print("[OK] Color constants")

    # Test status
    assert STATUS_ACTIVE == "Actif"
    assert STATUS_INACTIVE == "Inactif"
    print("[OK] Status constants")

    # Test contract types
    assert len(CONTRACT_TYPE_CHOICES) == 4
    assert "CDI" in CONTRACT_TYPE_CHOICES
    print("[OK] Contract type constants")

    # Test CACES types
    assert len(CACES_TYPES) == 5
    assert "R489-1A" in CACES_TYPES
    print("[OK] CACES type constants")

    # Test visit types
    assert len(VISIT_TYPE_CHOICES) == 3
    assert "initial" in VISIT_TYPE_CHOICES
    print("[OK] Visit type constants")

    # Test buttons
    assert BTN_ADD == "Ajouter"
    assert BTN_SAVE == "Sauvegarder"
    print("[OK] Button label constants")

    # Test form labels
    assert FORM_FIRST_NAME == "Prénom"
    assert FORM_LAST_NAME == "Nom"
    assert FORM_EMAIL == "Email"
    print("[OK] Form label constants")

    # Test messages
    assert MSG_SAVE_SUCCESS == "Employé sauvegardé avec succès !"
    assert MSG_CONFIRM_DELETE == "Êtes-vous sûr de vouloir supprimer cet employé ?"
    print("[OK] Message constants")

    # Test validation
    assert VALIDATION_FIRST_NAME_REQUIRED == "Le prénom est requis"
    assert VALIDATION_EMAIL_INVALID == "Format d'email invalide"
    print("[OK] Validation message constants")

    print("\n[OK] ALL CONSTANT TESTS PASSED")

if __name__ == "__main__":
    test_constants()
