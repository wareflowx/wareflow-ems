"""Migration to add contract history tables.

This migration creates:
- contracts: Employment contract tracking
- contract_amendments: Contract change tracking

Migrates existing employee data to create initial contracts.
"""

import uuid
from datetime import datetime

from database.connection import database
from database.migrations.base import BaseMigration
from utils.logging_config import get_logger

logger = get_logger(__name__)


class AddContractHistory(BaseMigration):
    """Add contract history tables and migrate existing data."""

    @property
    def name(self) -> str:
        return "20260128_120000_add_contract_history"

    def up(self) -> None:
        """Create contract tables and migrate existing data."""
        cursor = database.cursor()

        # Create contracts table
        logger.info("Creating contracts table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contracts (
                id TEXT PRIMARY KEY,
                employee_id TEXT NOT NULL,
                contract_type TEXT NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE,
                trial_period_end DATE,
                gross_salary DECIMAL(10,2),
                weekly_hours DECIMAL(4,2) DEFAULT 35.0,
                position TEXT NOT NULL,
                department TEXT NOT NULL,
                manager TEXT,
                status TEXT DEFAULT 'active',
                end_reason TEXT,
                contract_document_path TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                created_by TEXT,
                notes TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for contracts
        logger.info("Creating indexes for contracts table...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_employee_start ON contracts(employee_id, start_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_end_date ON contracts(end_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_status ON contracts(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_position ON contracts(position)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contracts_department ON contracts(department)")

        # Create contract_amendments table
        logger.info("Creating contract_amendments table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contract_amendments (
                id TEXT PRIMARY KEY,
                contract_id TEXT NOT NULL,
                amendment_date DATE NOT NULL,
                amendment_type TEXT NOT NULL,
                description TEXT NOT NULL,
                old_field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                document_path TEXT,
                created_at TIMESTAMP NOT NULL,
                created_by TEXT,
                FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for contract_amendments
        logger.info("Creating indexes for contract_amendments table...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contract_amendments_contract_date ON contract_amendments(contract_id, amendment_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contract_amendments_type ON contract_amendments(amendment_type)")

        # Migrate existing employees to initial contracts
        logger.info("Migrating existing employees to contracts...")
        cursor.execute("""
            INSERT INTO contracts (
                id, employee_id, contract_type, start_date, end_date,
                position, department, status, created_at, updated_at
            )
            SELECT
                lower(hex(randomblob(16))),
                id,
                contract_type,
                entry_date,
                NULL,
                role,
                'Logistics',
                'active',
                created_at,
                created_at
            FROM employees
            WHERE deleted_at IS NULL
        """)

        database.commit()
        logger.info("Contract history migration completed successfully")

    def down(self) -> None:
        """Rollback contract history tables."""
        cursor = database.cursor()

        logger.info("Dropping contract_amendments table...")
        cursor.execute("DROP TABLE IF EXISTS contract_amendments")

        logger.info("Dropping contracts table...")
        cursor.execute("DROP TABLE IF EXISTS contracts")

        database.commit()
        logger.info("Contract history rollback completed")

    def pre_check(self) -> bool:
        """Verify safe to migrate."""
        cursor = database.cursor()

        # Check if contracts table already exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='contracts'
        """)
        result = cursor.fetchone()

        if result:
            logger.warning("Contracts table already exists, skipping migration")
            return False

        return True

    def post_check(self) -> bool:
        """Verify migration success."""
        cursor = database.cursor()

        # Check contracts table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='contracts'
        """)
        if not cursor.fetchone():
            logger.error("Contracts table was not created")
            return False

        # Check contract_amendments table exists
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='contract_amendments'
        """)
        if not cursor.fetchone():
            logger.error("Contract amendments table was not created")
            return False

        # Check that all employees have at least one contract
        cursor.execute("""
            SELECT COUNT(*) FROM employees e
            LEFT JOIN contracts c ON e.id = c.employee_id
            WHERE e.deleted_at IS NULL AND c.id IS NULL
        """)
        employees_without_contracts = cursor.fetchone()[0]

        if employees_without_contracts > 0:
            logger.error(f"{employees_without_contracts} employees without contracts after migration")
            return False

        logger.info("All post-checks passed")
        return True
