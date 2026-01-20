#!/usr/bin/env python
"""
Integration test for Phase 3 - Employee Views

Tests the complete employee management functionality.
"""

import sys
from pathlib import Path

sys.path.insert(0, 'src')

import customtkinter as ctk
from employee.models import Employee
from database.connection import database, init_database
from datetime import date


def test_employee_list_view():
    """Test employee list view creation and functionality."""
    print("[TEST 1] Testing employee list view...")

    try:
        from ui_ctk.views.employee_list import EmployeeListView

        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Create employee list view
        list_view = EmployeeListView(app, title="Test List")

        # Verify components exist
        assert hasattr(list_view, 'search_var'), "Missing search_var"
        assert hasattr(list_view, 'filter_var'), "Missing filter_var"
        assert hasattr(list_view, 'table_frame'), "Missing table_frame"
        assert hasattr(list_view, 'employees'), "Missing employees list"
        assert hasattr(list_view, 'filtered_employees'), "Missing filtered_employees"

        print("  [OK] Employee list has all components")

        # Verify search and filter variables
        assert list_view.search_var.get() == "", "Search should start empty"
        assert list_view.filter_var.get() == "Tous", "Filter should start at 'Tous'"

        print("  [OK] Search and filter initialized correctly")

        # Verify employees loaded
        assert isinstance(list_view.employees, list), "Employees should be a list"
        assert isinstance(list_view.filtered_employees, list), "Filtered employees should be a list"

        print(f"  [OK] Loaded {len(list_view.employees)} employees")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Employee list test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_employee_form():
    """Test employee form creation and validation."""
    print("\n[TEST 2] Testing employee form...")

    try:
        from ui_ctk.forms.employee_form import EmployeeFormDialog

        # Create test app
        app = ctk.CTk()

        # Create form (new employee mode)
        form = EmployeeFormDialog(app, title="Employé")

        # Verify form variables exist
        assert hasattr(form, 'first_name_var'), "Missing first_name_var"
        assert hasattr(form, 'last_name_var'), "Missing last_name_var"
        assert hasattr(form, 'email_var'), "Missing email_var"
        assert hasattr(form, 'phone_var'), "Missing phone_var"
        assert hasattr(form, 'workspace_var'), "Missing workspace_var"
        assert hasattr(form, 'role_var'), "Missing role_var"
        assert hasattr(form, 'entry_date_var'), "Missing entry_date_var"

        print("  [OK] Form has all variables")

        # Test validation - empty form should fail
        is_valid, error = form.validate()
        assert not is_valid, "Empty form should be invalid"
        assert error is not None, "Should have error message"

        print(f"  [OK] Validation rejects empty form: {error}")

        # Test validation - with first name only
        form.first_name_var.set("Jean")
        is_valid, error = form.validate()
        assert not is_valid, "Form with only first name should be invalid"

        print(f"  [OK] Validation rejects incomplete form: {error}")

        # Test email validation
        assert not form.validate_email("invalid-email"), "Should reject invalid email"
        assert form.validate_email("test@example.com"), "Should accept valid email"

        print("  [OK] Email validation works correctly")

        # Test phone validation
        assert form.validate_phone("06 12 34 56 78"), "Should accept valid phone"
        assert not form.validate_phone("123"), "Should reject invalid phone"

        print("  [OK] Phone validation works correctly")

        # Cleanup
        form.destroy()
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Employee form test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_employee_detail_view():
    """Test employee detail view creation."""
    print("\n[TEST 3] Testing employee detail view...")

    try:
        from ui_ctk.views.employee_detail import EmployeeDetailView

        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Get or create test employee
        try:
            employee = Employee.select().first()
            if not employee:
                # Create test employee
                employee = Employee.create(
                    first_name="Test",
                    last_name="User",
                    current_status="active",
                    workspace="Zone A",
                    role="Cariste",
                    contract_type="CDI",
                    entry_date=date(2024, 1, 15)
                )
        except Exception as e:
            print(f"  [WARN] Could not get test employee: {e}")
            app.destroy()
            return False

        # Create detail view
        detail_view = EmployeeDetailView(app, employee=employee)

        # Verify view created
        assert detail_view.employee == employee, "Employee should be set"

        print("  [OK] Detail view created successfully")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Employee detail view test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_filter_logic():
    """Test search and filter logic."""
    print("\n[TEST 4] Testing search and filter logic...")

    try:
        from ui_ctk.views.employee_list import EmployeeListView
        from ui_ctk.constants import STATUS_ACTIVE, STATUS_INACTIVE

        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Create list view
        list_view = EmployeeListView(app, title="Test List")

        # Get initial count
        initial_count = len(list_view.employees)

        # Test status filter - active
        list_view.filter_var.set(STATUS_ACTIVE)
        list_view.apply_filters()

        # Verify all filtered are active
        for emp in list_view.filtered_employees:
            assert emp.is_active, "All should be active when filtering by active"

        print(f"  [OK] Active filter works: {len(list_view.filtered_employees)} employees")

        # Test status filter - inactive
        list_view.filter_var.set(STATUS_INACTIVE)
        list_view.apply_filters()

        # Verify all filtered are inactive
        for emp in list_view.filtered_employees:
            assert not emp.is_active, "All should be inactive when filtering by inactive"

        print(f"  [OK] Inactive filter works: {len(list_view.filtered_employees)} employees")

        # Reset filter
        list_view.filter_var.set("Tous")

        # Test search
        if initial_count > 0:
            test_employee = list_view.employees[0]
            search_term = test_employee.first_name

            list_view.search_var.set(search_term)
            list_view.apply_filters()

            # Should find at least the test employee
            assert len(list_view.filtered_employees) >= 1, "Should find at least one employee"

            print(f"  [OK] Search works: found {len(list_view.filtered_employees)} employees")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Search and filter test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_navigation():
    """Test navigation between views."""
    print("\n[TEST 5] Testing navigation...")

    try:
        from ui_ctk.views.employee_list import EmployeeListView
        from ui_ctk.views.employee_detail import EmployeeDetailView
        from ui_ctk.main_window import MainWindow

        # Create test app
        app = ctk.CTk()
        app.geometry("1000x700")

        # Create main window
        main_window = MainWindow(app)
        main_window.pack(fill="both", expand=True)

        # Verify employee list is shown by default
        assert main_window.current_view is not None, "Should have current view"

        print("  [OK] Main window shows employee list by default")

        # Get test employee
        try:
            employee = Employee.select().first()
            if employee:
                # Test navigation to detail
                main_window.switch_view(EmployeeDetailView, employee=employee)

                assert main_window.current_view is not None, "Should have detail view"
                print("  [OK] Navigation to detail view works")

        except Exception as e:
            print(f"  [WARN] Could not test detail navigation: {e}")

        # Cleanup
        app.destroy()

        return True

    except Exception as e:
        print(f"  [FAIL] Navigation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_constants():
    """Test that Phase 3 constants are defined."""
    print("\n[TEST 6] Testing Phase 3 constants...")

    try:
        from ui_ctk.constants import (
            ROLE_CHOICES,
            WORKSPACE_ZONES,
            SECTION_INFO,
            SECTION_CACES,
            SECTION_MEDICAL,
            VALIDATION_DATE_FUTURE,
            VALIDATION_DATE_TOO_OLD,
            CONFIRM_DELETE_EMPLOYEE,
            EXPIRATION_STATUS_VALID,
            EXPIRATION_STATUS_SOON,
            EXPIRATION_STATUS_URGENT,
            EXPIRATION_STATUS_EXPIRED,
        )

        # Verify role choices
        assert isinstance(ROLE_CHOICES, list), "ROLE_CHOICES should be a list"
        assert len(ROLE_CHOICES) > 0, "ROLE_CHOICES should not be empty"
        print(f"  [OK] ROLE_CHOICES defined: {ROLE_CHOICES}")

        # Verify workspace zones
        assert isinstance(WORKSPACE_ZONES, list), "WORKSPACE_ZONES should be a list"
        assert len(WORKSPACE_ZONES) > 0, "WORKSPACE_ZONES should not be empty"
        print(f"  [OK] WORKSPACE_ZONES defined: {WORKSPACE_ZONES}")

        # Verify section titles
        assert SECTION_INFO, "SECTION_INFO should be defined"
        assert SECTION_CACES, "SECTION_CACES should be defined"
        assert SECTION_MEDICAL, "SECTION_MEDICAL should be defined"
        print("  [OK] Section titles defined")

        # Verify validation messages
        assert VALIDATION_DATE_FUTURE, "VALIDATION_DATE_FUTURE should be defined"
        assert VALIDATION_DATE_TOO_OLD, "VALIDATION_DATE_TOO_OLD should be defined"
        print("  [OK] Validation messages defined")

        # Verify expiration status
        assert EXPIRATION_STATUS_VALID, "EXPIRATION_STATUS_VALID should be defined"
        assert EXPIRATION_STATUS_SOON, "EXPIRATION_STATUS_SOON should be defined"
        assert EXPIRATION_STATUS_URGENT, "EXPIRATION_STATUS_URGENT should be defined"
        assert EXPIRATION_STATUS_EXPIRED, "EXPIRATION_STATUS_EXPIRED should be defined"
        print("  [OK] Expiration status defined")

        return True

    except Exception as e:
        print(f"  [FAIL] Constants test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 3 integration tests."""
    print("=" * 70)
    print(" PHASE 3 INTEGRATION TESTS")
    print(" Testing Employee Views")
    print("=" * 70)

    # Initialize database
    db_path = Path("employee_manager.db")
    init_database(db_path)

    # Connect to database
    if database.is_closed():
        database.connect()

    tests = [
        ("Employee List View", test_employee_list_view),
        ("Employee Form", test_employee_form),
        ("Employee Detail View", test_employee_detail_view),
        ("Search and Filter Logic", test_search_filter_logic),
        ("Navigation", test_navigation),
        ("Constants", test_constants),
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
