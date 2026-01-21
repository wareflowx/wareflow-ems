"""Unit tests for Excel import functionality."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_imports():
    """Test 1: Verify all imports work correctly."""
    print("[TEST 1] Testing Excel import module imports...")

    try:
        from excel_import import (
            ExcelImporter,
            ImportError as ImportErrorData,
            ImportResult,
            ExcelTemplateGenerator
        )
        print("  [OK] ExcelImporter imported")
        print("  [OK] ImportError imported")
        print("  [OK] ImportResult imported")
        print("  [OK] ExcelTemplateGenerator imported")
        return True
    except Exception as e:
        print(f"  [FAIL] Import failed: {e}")
        return False


def test_import_error_dataclass():
    """Test 2: Verify ImportError dataclass structure."""
    print("\n[TEST 2] Testing ImportError dataclass...")

    try:
        from excel_import import ImportError as ImportErrorData

        # Create test error
        error = ImportErrorData(
            row_num=5,
            column="First Name",
            value=None,
            error_type="required",
            message="First name is required",
            severity="warning"
        )

        assert error.row_num == 5, "row_num should be 5"
        assert error.column == "First Name", "column should be 'First Name'"
        assert error.error_type == "required", "error_type should be 'required'"
        assert error.severity == "warning", "severity should be 'warning'"
        assert "Row 5" in str(error), "str(error) should contain row number"

        print("  [OK] ImportError fields work correctly")
        print("  [OK] __str__ method formats error correctly")
        return True

    except Exception as e:
        print(f"  [FAIL] Test failed: {e}")
        return False


def test_import_result_dataclass():
    """Test 3: Verify ImportResult dataclass structure."""
    print("\n[TEST 3] Testing ImportResult dataclass...")

    try:
        from excel_import import ImportResult, ImportError as ImportErrorData

        # Create test result with errors
        error = ImportErrorData(
            row_num=5,
            column="Email",
            value="invalid",
            error_type="format",
            message="Invalid email format"
        )

        result = ImportResult(
            total_rows=10,
            successful=8,
            failed=1,
            skipped=1,
            errors=[error],
            duration=2.5,
            file_path=Path("/test/file.xlsx")
        )

        assert result.total_rows == 10, "total_rows should be 10"
        assert result.successful == 8, "successful should be 8"
        assert result.failed == 1, "failed should be 1"
        assert result.skipped == 1, "skipped should be 1"
        assert result.duration == 2.5, "duration should be 2.5"
        assert result.has_errors == True, "has_errors should be True when errors list is not empty"
        assert result.success_rate == 80.0, "success_rate should be 80.0"

        # Test has_errors with no errors
        result_no_errors = ImportResult(
            total_rows=5,
            successful=5,
            failed=0,
            errors=[]
        )
        assert result_no_errors.has_errors == False, "has_errors should be False with empty errors list"

        print("  [OK] ImportResult fields work correctly")
        print("  [OK] has_errors property works (with and without errors)")
        print(f"  [OK] success_rate property calculates correctly: {result.success_rate}%")
        return True

    except Exception as e:
        print(f"  [FAIL] Test failed: {e}")
        return False


def test_template_generator_columns():
    """Test 4: Verify ExcelTemplateGenerator column definitions."""
    print("\n[TEST 4] Testing ExcelTemplateGenerator column definitions...")

    try:
        from excel_import import ExcelTemplateGenerator

        # Check column definitions
        expected_columns = [
            "First Name", "Last Name", "Email", "Phone",
            "External ID", "Status", "Workspace", "Role",
            "Contract", "Entry Date"
        ]

        assert ExcelTemplateGenerator.COLUMNS == expected_columns, \
            "COLUMNS should match expected list"

        print(f"  [OK] All {len(expected_columns)} columns defined correctly")

        # Check required columns detection
        assert ExcelTemplateGenerator._is_required_column("First Name") == True, \
            "First Name should be required"
        assert ExcelTemplateGenerator._is_required_column("Email") == False, \
            "Email should be optional"
        assert ExcelTemplateGenerator._is_required_column("Entry Date") == True, \
            "Entry Date should be required"

        print("  [OK] Required column detection works correctly")
        return True

    except Exception as e:
        print(f"  [FAIL] Test failed: {e}")
        return False


def test_excel_importer_validations():
    """Test 5: Verify ExcelImporter validation logic."""
    print("\n[TEST 5] Testing ExcelImporter validation methods...")

    try:
        from excel_import import ExcelImporter

        # Test _clean_string method
        assert ExcelImporter._clean_string(None) is None, "None should return None"
        assert ExcelImporter._clean_string("") is None, "Empty string should return None"
        assert ExcelImporter._clean_string("  test  ") == "Test", \
            "String should be trimmed and capitalized"

        print("  [OK] _clean_string method works correctly")

        # Test _parse_date method
        from datetime import date

        # French format
        result = ExcelImporter._parse_date("15/01/2025")
        assert result == date(2025, 1, 15), "Should parse DD/MM/YYYY format"

        # ISO format
        result = ExcelImporter._parse_date("2025-01-15")
        assert result == date(2025, 1, 15), "Should parse YYYY-MM-DD format"

        # Invalid format
        result = ExcelImporter._parse_date("invalid")
        assert result is None, "Invalid format should return None"

        print("  [OK] _parse_date method handles multiple formats correctly")
        print("    - DD/MM/YYYY (French): [OK]")
        print("    - YYYY-MM-DD (ISO): [OK]")
        print("    - Invalid format: [OK]")
        return True

    except Exception as e:
        print(f"  [FAIL] Test failed: {e}")
        return False


def test_importer_required_columns():
    """Test 6: Verify ExcelImporter required columns."""
    print("\n[TEST 6] Testing ExcelImporter required columns...")

    try:
        from excel_import import ExcelImporter

        expected_required = [
            "First Name", "Last Name", "Status",
            "Workspace", "Role", "Contract", "Entry Date"
        ]

        assert ExcelImporter.REQUIRED_COLUMNS == expected_required, \
            "REQUIRED_COLUMNS should match expected list"

        print(f"  [OK] All {len(expected_required)} required columns defined")

        expected_optional = ["Email", "Phone", "External ID"]
        assert ExcelImporter.OPTIONAL_COLUMNS == expected_optional, \
            "OPTIONAL_COLUMNS should match expected list"

        print(f"  [OK] All {len(expected_optional)} optional columns defined")

        assert ExcelImporter.BATCH_SIZE == 100, "BATCH_SIZE should be 100"
        print("  [OK] BATCH_SIZE set to 100")

        return True

    except Exception as e:
        print(f"  [FAIL] Test failed: {e}")
        return False


def run_all_tests():
    """Run all unit tests."""
    print("=" * 60)
    print("EXCEL IMPORT UNIT TESTS")
    print("=" * 60)

    tests = [
        test_imports,
        test_import_error_dataclass,
        test_import_result_dataclass,
        test_template_generator_columns,
        test_excel_importer_validations,
        test_importer_required_columns,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Test crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    print(f"Tests run: {total}")
    print(f"Tests passed: {passed}")
    print(f"Tests failed: {total - passed}")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n[OK] ALL TESTS PASSED")
        return 0
    else:
        print(f"\n[FAIL] {total - passed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
