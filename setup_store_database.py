"""
Setup Store Database
Creates the necessary tables for the store module
"""

import sys
from loguru import logger
from src.database.connection import DatabaseConnection


def setup_database():
    """Create store tables in the database"""
    logger.info("Setting up store database tables...")

    # Read SQL schema
    with open('database_schema_store.sql', 'r') as f:
        sql_script = f.read()

    try:
        db = DatabaseConnection()
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # Execute the SQL script
                cursor.execute(sql_script)
                conn.commit()

                logger.info("Store database tables created successfully!")
                print("[OK] Store database setup complete!")
                print("\nTables created:")
                print("  - products")
                print("  - customer_orders")
                print("  - order_items")
                print("\n10 sample products have been added to get you started!")

                return True

    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        print(f"[ERROR] Error: {e}")
        return False


if __name__ == '__main__':
    success = setup_database()
    sys.exit(0 if success else 1)
