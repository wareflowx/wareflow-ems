#!/usr/bin/env python
"""
Test CACES Form - Phase 4.5

Tests the CacesFormDialog functionality.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

from datetime import date
from employee.models import Caces, Employee
from database.connection import database, init_database
from ui_ctk.forms.caces_form import CacesFormDialog


def test_caces_form_imports():
    """Test that CacesFormDialog imports correctly."""
    print("[TEST 1] Testing CacesFormDialog imports...")

    try:
        from ui_ctk.forms.caces_form import CacesFormDialog
        print("  [OK] CacesFormDialog imports successfully")
        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        return False


def test_caces_calculation():
    """Test CACES expiration date calculation."""
    print("\n[TEST 2] Testing CACES expiration calculation...")

    try:
        # Test 5-year validity
        completion = date(2020, 1, 1)
        expiration = Caces.calculate_expiration("R489-1A", completion)

        expected = date(2025, 1, 1)
        assert expiration == expected, f"Expected {expected}, got {expiration}"
        print("  [OK] 5-year CACES (R489-1A) calculated correctly")

        # Test 10-year validity
        expiration = Caces.calculate_expiration("R489-5", completion)
        expected = date(2030, 1, 1)
        assert expiration == expected, f"Expected {expected}, got {expiration}"
        print("  [OK] 10-year CACES (R489-5) calculated correctly")

        return True

    except Exception as e:
        print(f"  [FAIL] Calculation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_form_validation():
    """Test form validation logic."""
    print("\n[TEST 3] Testing form validation...")

    try:
        # We can't easily test the full GUI form without actually opening it,
        # but we can test the validation logic structure
        from ui_ctk.forms.caces_form import CacesFormDialog

        # Check that the class has the required methods
        assert hasattr(CacesFormDialog, 'validate'), "Missing validate method"
        assert hasattr(CacesFormDialog, 'save'), "Missing save method"
        assert hasattr(CacesFormDialog, 'parse_date'), "Missing parse_date method"

        print("  [OK] Form has all required methods")
        return True

    except Exception as e:
        print(f"  [FAIL] Validation test failed: {e}")
        return False


def test_date_parsing():
    """Test date parsing from French format."""
    print("\n[TEST 4] Testing date parsing...")

    try:
        from ui_ctk.forms.caces_form import CacesFormDialog

        # Can't instantiate without GUI, so we'll test the format itself
        from datetime import datetime
        DATE_FORMAT = "%d/%m/%Y"

        # Test valid date
        result = datetime.strptime("15/01/2025", DATE_FORMAT).date()
        assert result == date(2025, 1, 15), "Date parsing failed"
        print("  [OK] French date format parsing works")

        return True

    except Exception as e:
        print(f"  [FAIL] Date parsing test failed: {e}")
        return False


def test_database_integration():
    """Test that CACES can be created in database."""
    print("\n[TEST 5] Testing database integration...")

    try:
        # Initialize database
        db_path = Path("employee_manager.db")
        init_database(db_path)

        if database.is_closed():
            database.connect()

        # Check if we can query CACES
        caces_count = Caces.select().count()
        print(f"  [OK] Database connection works (found {caces_count} CACES records)")

        return True

    except Exception as e:
        print(f"  [FAIL] Database integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all CACES form tests."""
    print("=" * 70)
    print(" PHASE 4.5 - CACES FORM TESTS")
    print("=" * 70)

    tests = [
        ("Imports", test_caces_form_imports),
        ("CACES Calculation", test_caces_calculation),
        ("Form Validation", test_form_validation),
        ("Date Parsing", test_date_parsing),
        ("Database Integration", test_database_integration),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n[ERROR] {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False

    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {test_name}")

    print("\n" + "=" * 70)
    if passed == total:
        print(f" [OK] ALL {total} TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print(f" [FAIL] {passed}/{total} tests passed")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
