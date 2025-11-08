"""
Script para importar datos a Supabase desde archivos CSV o JSON.

Uso:
    python migrate_data_to_supabase.py --csv migration_exports/orders_data_XXXXXX.csv
    python migrate_data_to_supabase.py --json migration_exports/orders_data_XXXXXX.json
"""
import sys
import os
import argparse
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from loguru import logger
from typing import List, Dict, Any
import json


class SupabaseMigration:
    """Handles data migration to Supabase."""

    def __init__(self, host: str, port: int, database: str, user: str, password: str):
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }

    def test_connection(self) -> bool:
        """Test connection to Supabase."""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            logger.info(f"✅ Connected to Supabase: {version[0]}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"❌ Connection failed: {e}")
            return False

    def create_table_if_not_exists(self) -> bool:
        """Create the orders table if it doesn't exist."""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()

            create_table_sql = """
            CREATE TABLE IF NOT EXISTS orders (
              order_id        bigint PRIMARY KEY,
              status          text NOT NULL,
              customer_name   text NOT NULL,
              order_date      date NOT NULL,
              quantity        integer NOT NULL CHECK (quantity >= 0),
              subtotal_amount numeric(18,2) NOT NULL CHECK (subtotal_amount >= 0),
              tax_rate        numeric(6,4)  NOT NULL CHECK (tax_rate >= 0),
              shipping_cost   numeric(18,2) NOT NULL CHECK (shipping_cost >= 0),
              category        text NOT NULL,
              subcategory     text NOT NULL
            );
            """

            cursor.execute(create_table_sql)
            conn.commit()

            logger.info("✅ Table 'orders' created or already exists")

            cursor.close()
            conn.close()
            return True

        except Exception as e:
            logger.error(f"❌ Error creating table: {e}")
            return False

    def import_from_csv(self, csv_file: str, batch_size: int = 1000) -> bool:
        """Import data from CSV file."""
        try:
            logger.info(f"Reading CSV file: {csv_file}")
            df = pd.read_csv(csv_file)

            logger.info(f"Found {len(df)} records to import")

            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()

            # Prepare insert query
            insert_query = """
            INSERT INTO orders (
                order_id, status, customer_name, order_date,
                quantity, subtotal_amount, tax_rate, shipping_cost,
                category, subcategory
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (order_id) DO UPDATE SET
                status = EXCLUDED.status,
                customer_name = EXCLUDED.customer_name,
                order_date = EXCLUDED.order_date,
                quantity = EXCLUDED.quantity,
                subtotal_amount = EXCLUDED.subtotal_amount,
                tax_rate = EXCLUDED.tax_rate,
                shipping_cost = EXCLUDED.shipping_cost,
                category = EXCLUDED.category,
                subcategory = EXCLUDED.subcategory;
            """

            # Convert dataframe to list of tuples
            data = [
                (
                    row['order_id'],
                    row['status'],
                    row['customer_name'],
                    row['order_date'],
                    row['quantity'],
                    row['subtotal_amount'],
                    row['tax_rate'],
                    row['shipping_cost'],
                    row['category'],
                    row['subcategory']
                )
                for _, row in df.iterrows()
            ]

            # Import in batches
            total_batches = (len(data) + batch_size - 1) // batch_size

            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                execute_batch(cursor, insert_query, batch)
                conn.commit()

                batch_num = (i // batch_size) + 1
                logger.info(f"✅ Imported batch {batch_num}/{total_batches} ({len(batch)} records)")

            cursor.close()
            conn.close()

            logger.info(f"✅ Successfully imported {len(data)} records")
            return True

        except Exception as e:
            logger.error(f"❌ Error importing from CSV: {e}")
            return False

    def import_from_json(self, json_file: str, batch_size: int = 1000) -> bool:
        """Import data from JSON file."""
        try:
            logger.info(f"Reading JSON file: {json_file}")

            with open(json_file, 'r', encoding='utf-8') as f:
                data_list = json.load(f)

            logger.info(f"Found {len(data_list)} records to import")

            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()

            # Prepare insert query
            insert_query = """
            INSERT INTO orders (
                order_id, status, customer_name, order_date,
                quantity, subtotal_amount, tax_rate, shipping_cost,
                category, subcategory
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (order_id) DO UPDATE SET
                status = EXCLUDED.status,
                customer_name = EXCLUDED.customer_name,
                order_date = EXCLUDED.order_date,
                quantity = EXCLUDED.quantity,
                subtotal_amount = EXCLUDED.subtotal_amount,
                tax_rate = EXCLUDED.tax_rate,
                shipping_cost = EXCLUDED.shipping_cost,
                category = EXCLUDED.category,
                subcategory = EXCLUDED.subcategory;
            """

            # Convert to list of tuples
            data = [
                (
                    row['order_id'],
                    row['status'],
                    row['customer_name'],
                    row['order_date'],
                    row['quantity'],
                    row['subtotal_amount'],
                    row['tax_rate'],
                    row['shipping_cost'],
                    row['category'],
                    row['subcategory']
                )
                for row in data_list
            ]

            # Import in batches
            total_batches = (len(data) + batch_size - 1) // batch_size

            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                execute_batch(cursor, insert_query, batch)
                conn.commit()

                batch_num = (i // batch_size) + 1
                logger.info(f"✅ Imported batch {batch_num}/{total_batches} ({len(batch)} records)")

            cursor.close()
            conn.close()

            logger.info(f"✅ Successfully imported {len(data)} records")
            return True

        except Exception as e:
            logger.error(f"❌ Error importing from JSON: {e}")
            return False

    def verify_import(self) -> Dict[str, Any]:
        """Verify the imported data."""
        try:
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()

            # Get count
            cursor.execute("SELECT COUNT(*) FROM orders")
            count = cursor.fetchone()[0]

            # Get sample data
            cursor.execute("SELECT * FROM orders LIMIT 5")
            sample = cursor.fetchall()

            cursor.close()
            conn.close()

            logger.info(f"✅ Verification: Found {count} records in Supabase")

            return {
                'total_records': count,
                'sample_data': sample
            }

        except Exception as e:
            logger.error(f"❌ Error verifying import: {e}")
            return None


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Import data to Supabase')
    parser.add_argument('--csv', help='Path to CSV file to import')
    parser.add_argument('--json', help='Path to JSON file to import')
    parser.add_argument('--host', required=True, help='Supabase host (e.g., xxx.supabase.co)')
    parser.add_argument('--port', type=int, default=5432, help='Database port (default: 5432)')
    parser.add_argument('--database', default='postgres', help='Database name (default: postgres)')
    parser.add_argument('--user', default='postgres', help='Database user (default: postgres)')
    parser.add_argument('--password', required=True, help='Database password')
    parser.add_argument('--batch-size', type=int, default=1000, help='Batch size for import (default: 1000)')

    args = parser.parse_args()

    if not args.csv and not args.json:
        parser.error("Either --csv or --json must be provided")

    print("\n" + "🚀 Starting Supabase Data Import")
    print("="*60)

    # Initialize migration
    migration = SupabaseMigration(
        host=args.host,
        port=args.port,
        database=args.database,
        user=args.user,
        password=args.password
    )

    # Test connection
    print("\n1. Testing connection to Supabase...")
    if not migration.test_connection():
        print("❌ Connection failed. Please check your credentials.")
        return 1

    # Create table
    print("\n2. Creating table if not exists...")
    if not migration.create_table_if_not_exists():
        print("❌ Failed to create table.")
        return 1

    # Import data
    print("\n3. Importing data...")
    success = False

    if args.csv:
        success = migration.import_from_csv(args.csv, args.batch_size)
    elif args.json:
        success = migration.import_from_json(args.json, args.batch_size)

    if not success:
        print("❌ Import failed.")
        return 1

    # Verify
    print("\n4. Verifying import...")
    verification = migration.verify_import()

    if verification:
        print(f"\n✅ Import completed successfully!")
        print(f"   Total records in Supabase: {verification['total_records']}")
    else:
        print("❌ Verification failed.")
        return 1

    print("\n" + "="*60)
    print("Migration completed! Your data is now in Supabase.")
    print("Don't forget to update your .env file with the new credentials.")
    print("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
