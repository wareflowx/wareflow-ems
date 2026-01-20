#!/usr/bin/env python
"""Test migration script."""

import sys
import sqlite3
from pathlib import Path
from datetime import date

sys.path.insert(0, 'src')

from database.connection import init_database
from employee.models import Employee


def test_migration(db_path: str = "test_employee.db"):
    """Test that migration was successful."""
    print("=" * 50)
    print(" TESTING MIGRATION")
    print("=" * 50)

    # Initialize database
    init_database(Path(db_path))

    # Test 1: Check columns exist
    print("\n[Test 1] Checking columns...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(employees)")
    columns = [row[1] for row in cursor.fetchall()]

    assert "phone" in columns, "Column 'phone' not found"
    assert "email" in columns, "Column 'email' not found"
    print("[OK] Columns 'phone' and 'email' exist")

    conn.close()

    # Test 2: Query employee with Peewee
    print("\n[Test 2] Querying employees...")
    employees = Employee.select()
    count = employees.count()
    print(f"[OK] Queried {count} employees")

    # Test 3: Access phone and email fields
    print("\n[Test 3] Accessing new fields...")
    for emp in employees:
        # Should not raise AttributeError
        _ = emp.phone
        _ = emp.email
    print("[OK] Can access phone and email fields")

    # Test 4: Create employee with contact info
    print("\n[Test 4] Creating employee with contact info...")
    test_emp = Employee.create(
        first_name="Test",
        last_name="User",
        current_status="active",
        workspace="Zone C",
        role="Testeur",
        contract_type="CDI",
        entry_date=date(2024, 1, 1),
        phone="06 12 34 56 78",
        email="test@example.com"
    )
    print(f"[OK] Created employee with phone: {test_emp.phone}, email: {test_emp.email}")

    # Test 5: Update employee with contact info
    print("\n[Test 5] Updating employee with contact info...")
    test_emp.phone = "06 98 76 54 32"
    test_emp.email = "updated@example.com"
    test_emp.save()
    test_emp = Employee.get_by_id(test_emp.id)
    assert test_emp.phone == "06 98 76 54 32"
    assert test_emp.email == "updated@example.com"
    print("[OK] Updated phone and email successfully")

    # Test 6: NULL values work
    print("\n[Test 6] Testing NULL values...")
    test_emp.phone = None
    test_emp.email = None
    test_emp.save()
    test_emp = Employee.get_by_id(test_emp.id)
    assert test_emp.phone is None
    assert test_emp.email is None
    print("[OK] NULL values work correctly")

    # Test 7: Query with filters
    print("\n[Test 7] Querying with contact filters...")
    with_phone = Employee.select().where(Employee.phone.is_null(False))
    count_with_phone = with_phone.count()
    print(f"[OK] {count_with_phone} employees with phone")

    with_email = Employee.select().where(Employee.email.is_null(False))
    count_with_email = with_email.count()
    print(f"[OK] {count_with_email} employees with email")

    print("\n" + "=" * 50)
    print(" [OK] ALL MIGRATION TESTS PASSED")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test migration")
    parser.add_argument("--db", default="test_employee.db", help="Path to test database")

    args = parser.parse_args()

    # Check if test database exists
    if not Path(args.db).exists():
        print(f"[ERROR] Test database not found: {args.db}")
        print("[INFO] Run: python scripts/create_test_db.py")
        sys.exit(1)

    sys.exit(test_migration(args.db))
