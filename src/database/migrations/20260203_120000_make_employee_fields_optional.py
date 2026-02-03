"""Migration script to make contract_type and entry_date optional in employees table.

This script updates the employees table to allow NULL values for:
- contract_type (was required, now optional)
- entry_date (was required, now optional)

This allows creating employees with minimal information (just name, workspace, role)
and filling in contract details later.

Run this script to upgrade existing databases.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.connection import database
from database.connection import init_database
from utils.logging_config import setup_logging, get_logger
from utils.config import get_database_path, ensure_database_directory

# Setup logging
setup_logging(level="INFO", enable_console=True, enable_file=True)
logger = get_logger(__name__)


def migrate():
    """
    Make contract_type and entry_date optional in employees table.

    In SQLite, we need to recreate the table since ALTER TABLE doesn't
    support modifying column constraints directly.

    Process:
    1. Create a new employees table with nullable columns
    2. Copy existing data to the new table
    3. Drop the old table
    4. Rename the new table to employees
    5. Recreate indexes
    """
    logger.info("Starting employee fields optional migration...")

    try:
        # Ensure database directory exists
        ensure_database_directory()

        # Get database path and initialize connection
        db_path = get_database_path()
        logger.info(f"Database path: {db_path}")

        if not db_path.exists():
            logger.error(f"Database file does not exist: {db_path}")
            logger.error("Please run the application first to create the database")
            return

        # Initialize database connection
        init_database(db_path)

        # Connect to database
        if database.is_closed():
            database.connect()

        cursor = database.cursor()

        # Check if contract_type is already nullable (migration already run)
        cursor.execute("PRAGMA table_info(employees)")
        columns = cursor.fetchall()

        contract_type_nullable = False
        entry_date_nullable = False

        for col in columns:
            col_name = col[1]
            col_not_null = col[3]  # 1 if NOT NULL, 0 if nullable

            if col_name == "contract_type" and col_not_null == 0:
                contract_type_nullable = True
                logger.info("contract_type is already nullable")

            if col_name == "entry_date" and col_not_null == 0:
                entry_date_nullable = True
                logger.info("entry_date is already nullable")

        # If both are already nullable, we're done
        if contract_type_nullable and entry_date_nullable:
            logger.info("Migration already applied - nothing to do")
            return

        # Start transaction
        database.begin()

        # Create new employees table with nullable columns
        logger.info("Creating new employees table with nullable columns...")

        cursor.execute("""
            CREATE TABLE employees_new (
                id TEXT PRIMARY KEY,
                external_id TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                current_status TEXT NOT NULL,
                workspace TEXT NOT NULL,
                role TEXT NOT NULL,
                contract_type TEXT,
                entry_date DATE,
                avatar_path TEXT,
                phone TEXT,
                email TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                deleted_at TIMESTAMP,
                deleted_by TEXT,
                deletion_reason TEXT
            )
        """)

        logger.info("New table created")

        # Copy data from old table to new table
        logger.info("Copying existing data...")

        cursor.execute("""
            INSERT INTO employees_new (
                id, external_id, first_name, last_name, current_status,
                workspace, role, contract_type, entry_date, avatar_path,
                phone, email, created_at, updated_at, deleted_at,
                deleted_by, deletion_reason
            )
            SELECT
                id, external_id, first_name, last_name, current_status,
                workspace, role, contract_type, entry_date, avatar_path,
                phone, email, created_at, updated_at, deleted_at,
                deleted_by, deletion_reason
            FROM employees
        """)

        row_count = cursor.rowcount
        logger.info(f"Copied {row_count} employee records")

        # Drop old table
        logger.info("Dropping old employees table...")
        cursor.execute("DROP TABLE employees")

        # Rename new table
        logger.info("Renaming employees_new to employees...")
        cursor.execute("ALTER TABLE employees_new RENAME TO employees")

        # Recreate indexes
        logger.info("Recreating indexes...")

        indexes = [
            ("idx_employees_external_id", "CREATE INDEX idx_employees_external_id ON employees (external_id)"),
            ("idx_employees_current_status", "CREATE INDEX idx_employees_current_status ON employees (current_status)"),
            ("idx_employees_workspace", "CREATE INDEX idx_employees_workspace ON employees (workspace)"),
            ("idx_employees_role", "CREATE INDEX idx_employees_role ON employees (role)"),
            ("idx_employees_contract_type", "CREATE INDEX idx_employees_contract_type ON employees (contract_type)"),
            ("idx_employees_deleted_at", "CREATE INDEX idx_employees_deleted_at ON employees (deleted_at)"),
        ]

        for index_name, sql in indexes:
            try:
                cursor.execute(sql)
                logger.info(f"Created index: {index_name}")
            except Exception as e:
                logger.warning(f"Index {index_name} may already exist: {e}")

        # Commit transaction
        database.commit()

        logger.info("Employee fields optional migration completed successfully!")
        logger.info("")
        logger.info("What's changed:")
        logger.info("- contract_type is now optional (can be NULL)")
        logger.info("- entry_date is now optional (can be NULL)")
        logger.info("- Employees can be created with just: first name, last name, workspace, role")
        logger.info("")
        logger.info("Next steps:")
        logger.info("- Employee creation form will allow optional fields")
        logger.info("- Users can fill in contract details later")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        database.rollback()
        raise
    finally:
        if not database.is_closed():
            database.close()


def rollback():
    """
    Rollback the migration (NOT RECOMMENDED).

    WARNING: This will make contract_type and entry_date required again.
    Any existing employees with NULL values in these columns will cause
    the rollback to fail.

    Only use this if you're sure all employees have values for these fields.
    """
    logger.warning("Starting employee fields optional ROLLBACK...")
    logger.warning("WARNING: This will make contract_type and entry_date REQUIRED again")
    logger.warning("Rollback will fail if any employees have NULL values")

    try:
        # Ensure database directory exists
        ensure_database_directory()

        # Get database path and initialize connection
        db_path = get_database_path()
        logger.info(f"Database path: {db_path}")

        if not db_path.exists():
            logger.error(f"Database file does not exist: {db_path}")
            return

        # Initialize database connection
        init_database(db_path)

        # Connect to database
        if database.is_closed():
            database.connect()

        cursor = database.cursor()

        # Check if there are any NULL values
        cursor.execute("""
            SELECT COUNT(*) FROM employees
            WHERE contract_type IS NULL OR entry_date IS NULL
        """)

        null_count = cursor.fetchone()[0]

        if null_count > 0:
            logger.error(f"Cannot rollback: {null_count} employees have NULL values")
            logger.error("Please update all employees to have contract_type and entry_date before rolling back")
            return

        # Start transaction
        database.begin()

        # Create new table with required columns
        logger.info("Creating new employees table with required columns...")

        cursor.execute("""
            CREATE TABLE employees_new (
                id TEXT PRIMARY KEY,
                external_id TEXT UNIQUE,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                current_status TEXT NOT NULL,
                workspace TEXT NOT NULL,
                role TEXT NOT NULL,
                contract_type TEXT NOT NULL,
                entry_date DATE NOT NULL,
                avatar_path TEXT,
                phone TEXT,
                email TEXT,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                deleted_at TIMESTAMP,
                deleted_by TEXT,
                deletion_reason TEXT
            )
        """)

        # Copy data
        logger.info("Copying existing data...")
        cursor.execute("""
            INSERT INTO employees_new (
                id, external_id, first_name, last_name, current_status,
                workspace, role, contract_type, entry_date, avatar_path,
                phone, email, created_at, updated_at, deleted_at,
                deleted_by, deletion_reason
            )
            SELECT
                id, external_id, first_name, last_name, current_status,
                workspace, role, contract_type, entry_date, avatar_path,
                phone, email, created_at, updated_at, deleted_at,
                deleted_by, deletion_reason
            FROM employees
        """)

        # Drop and rename
        cursor.execute("DROP TABLE employees")
        cursor.execute("ALTER TABLE employees_new RENAME TO employees")

        # Recreate indexes
        for index_name, sql in [
            ("idx_employees_external_id", "CREATE INDEX idx_employees_external_id ON employees (external_id)"),
            ("idx_employees_current_status", "CREATE INDEX idx_employees_current_status ON employees (current_status)"),
            ("idx_employees_workspace", "CREATE INDEX idx_employees_workspace ON employees (workspace)"),
            ("idx_employees_role", "CREATE INDEX idx_employees_role ON employees (role)"),
            ("idx_employees_contract_type", "CREATE INDEX idx_employees_contract_type ON employees (contract_type)"),
            ("idx_employees_deleted_at", "CREATE INDEX idx_employees_deleted_at ON employees (deleted_at)"),
        ]:
            cursor.execute(sql)

        database.commit()
        logger.info("Rollback completed successfully")

    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        database.rollback()
        raise
    finally:
        if not database.is_closed():
            database.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        rollback()
    else:
        migrate()
