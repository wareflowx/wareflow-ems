"""
Migration to fix typo in table name: 'contarcts' → 'contracts'

This migration addresses the table name typo that was causing
the error "no such table: contarcts" when loading employee details.
"""

from peewee import *
from database.base import MigrationBase
from database.connection import database


class Migration(MigrationBase):
    """Fix contracts table name typo."""

    def up(self):
        """Rename 'contarcts' table to 'contracts'."""
        # Check if the typo table exists
        cursor = database.execute_sql("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='contarcts'
        """)

        if cursor.fetchone():
            # Rename the table with the typo
            database.execute_sql("ALTER TABLE contarcts RENAME TO contracts")
            print("[OK] Renamed table 'contarcts' → 'contracts'")
        else:
            # Check if correct table already exists
            cursor = database.execute_sql("""
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='contracts'
            """)
            if cursor.fetchone():
                print("[INFO] Table 'contracts' already exists, no fix needed")
            else:
                print("[WARN] Neither 'contarcts' nor 'contracts' table found")

    def down(self):
        """Revert: Rename 'contracts' back to 'contarcts'."""
        cursor = database.execute_sql("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='contracts'
        """)

        if cursor.fetchone():
            database.execute_sql("ALTER TABLE contracts RENAME TO contarcts")
            print("[OK] Reverted: table 'contracts' → 'contarcts'")
