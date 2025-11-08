"""
Script de migración de base de datos local PostgreSQL a Supabase.

Este script:
1. Exporta el esquema de la base de datos local
2. Exporta los datos existentes
3. Permite importar a Supabase
"""
import sys
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from loguru import logger

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database.connection import db_connection


class DatabaseMigration:
    """Handles database migration from local PostgreSQL to Supabase."""

    def __init__(self):
        self.export_dir = "migration_exports"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(self.export_dir, exist_ok=True)

    def export_schema(self) -> str:
        """Export the database schema (DDL)."""
        logger.info("Exporting database schema...")

        schema_sql = """
-- Database Schema for Supabase Migration
-- Generated: {timestamp}

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

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_customer_name ON orders(customer_name);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_category ON orders(category);
CREATE INDEX IF NOT EXISTS idx_orders_subcategory ON orders(subcategory);

-- Row Level Security (RLS) policies for Supabase
-- Uncomment and adjust based on your security requirements
-- ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- Example policy (adjust as needed):
-- CREATE POLICY "Enable read access for authenticated users"
-- ON orders FOR SELECT
-- TO authenticated
-- USING (true);

-- CREATE POLICY "Enable insert access for authenticated users"
-- ON orders FOR INSERT
-- TO authenticated
-- WITH CHECK (true);

-- CREATE POLICY "Enable update access for authenticated users"
-- ON orders FOR UPDATE
-- TO authenticated
-- USING (true);

-- CREATE POLICY "Enable delete access for authenticated users"
-- ON orders FOR DELETE
-- TO authenticated
-- USING (true);
""".format(timestamp=self.timestamp)

        schema_file = os.path.join(self.export_dir, f"schema_{self.timestamp}.sql")
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(schema_sql)

        logger.info(f"Schema exported to: {schema_file}")
        return schema_file

    def export_data_to_csv(self) -> str:
        """Export all data from orders table to CSV."""
        logger.info("Exporting data to CSV...")

        try:
            query = "SELECT * FROM orders ORDER BY order_id"

            with db_connection.get_connection() as conn:
                df = pd.read_sql_query(query, conn)

            csv_file = os.path.join(self.export_dir, f"orders_data_{self.timestamp}.csv")
            df.to_csv(csv_file, index=False, encoding='utf-8')

            logger.info(f"✅ Exported {len(df)} records to: {csv_file}")
            return csv_file

        except Exception as e:
            logger.error(f"❌ Error exporting data: {e}")
            raise

    def export_data_to_json(self) -> str:
        """Export all data from orders table to JSON."""
        logger.info("Exporting data to JSON...")

        try:
            query = "SELECT * FROM orders ORDER BY order_id"
            results = db_connection.execute_query(query)

            # Convert date objects to strings
            for row in results:
                if 'order_date' in row and row['order_date']:
                    row['order_date'] = row['order_date'].isoformat()
                # Convert Decimal to float for JSON serialization
                for key in ['subtotal_amount', 'tax_rate', 'shipping_cost']:
                    if key in row and row[key] is not None:
                        row[key] = float(row[key])

            json_file = os.path.join(self.export_dir, f"orders_data_{self.timestamp}.json")
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Exported {len(results)} records to: {json_file}")
            return json_file

        except Exception as e:
            logger.error(f"❌ Error exporting data to JSON: {e}")
            raise

    def generate_migration_report(self, schema_file: str, csv_file: str, json_file: str):
        """Generate a migration report with statistics."""
        logger.info("Generating migration report...")

        try:
            # Get table statistics
            stats_query = """
            SELECT
                COUNT(*) as total_records,
                COUNT(DISTINCT status) as unique_statuses,
                COUNT(DISTINCT customer_name) as unique_customers,
                COUNT(DISTINCT category) as unique_categories,
                MIN(order_date) as earliest_order,
                MAX(order_date) as latest_order,
                SUM(quantity) as total_quantity,
                SUM(subtotal_amount) as total_revenue
            FROM orders
            """

            stats = db_connection.execute_query(stats_query)[0]

            report = f"""
# Migration Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Database Statistics
- Total Records: {stats['total_records']:,}
- Unique Customers: {stats['unique_customers']:,}
- Unique Statuses: {stats['unique_statuses']}
- Unique Categories: {stats['unique_categories']}
- Date Range: {stats['earliest_order']} to {stats['latest_order']}
- Total Quantity: {stats['total_quantity']:,}
- Total Revenue: ${stats['total_revenue']:,.2f}

## Exported Files
1. Schema: {schema_file}
2. CSV Data: {csv_file}
3. JSON Data: {json_file}

## Next Steps for Supabase Migration

### 1. Create a Supabase Project
- Go to https://supabase.com
- Click "New Project"
- Choose your organization and region
- Set a database password (save it securely!)
- Wait for the project to be created

### 2. Get Your Connection Credentials
In your Supabase dashboard:
- Go to Project Settings > Database
- Find your connection string under "Connection string"
- Note down these values:
  * Host
  * Database name
  * Port (usually 5432)
  * User (usually postgres)
  * Password (the one you set)

### 3. Execute the Schema
Option A - Using Supabase SQL Editor:
- Go to SQL Editor in Supabase dashboard
- Copy contents from: {schema_file}
- Paste and run the SQL

Option B - Using psql command line:
```bash
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres" < {schema_file}
```

### 4. Import the Data
Option A - Using Supabase Dashboard:
- Go to Table Editor > orders table
- Click "Insert" > "Import data from CSV"
- Upload: {csv_file}

Option B - Using psql command line:
```bash
psql "postgresql://postgres:[YOUR-PASSWORD]@[YOUR-PROJECT-REF].supabase.co:5432/postgres" \\
  -c "\\COPY orders FROM '{csv_file}' CSV HEADER"
```

Option C - Using the migration script:
```bash
python migrate_data_to_supabase.py --csv {csv_file}
```

### 5. Update Application Configuration
Update your .env file with Supabase credentials:
```env
PG_HOST=[YOUR-PROJECT-REF].supabase.co
PG_PORT=5432
PG_DB=postgres
PG_USER=postgres
PG_PASS=[YOUR-SUPABASE-PASSWORD]
PG_SCHEMA_RAW=public
```

### 6. Test the Connection
```bash
python start_web_app.py
```

## Important Notes
- ⚠️ Keep your Supabase password secure
- ⚠️ Consider enabling Row Level Security (RLS) in production
- ⚠️ Review the commented RLS policies in the schema file
- ⚠️ Test the migration in a development environment first
- ⚠️ Backup your local database before making changes

## Supabase Features You Can Use
- Real-time subscriptions
- Row Level Security
- Auto-generated REST API
- Built-in authentication
- Storage for files
- Edge Functions
"""

            report_file = os.path.join(self.export_dir, f"migration_report_{self.timestamp}.md")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            logger.info(f"✅ Migration report generated: {report_file}")
            print("\n" + "="*60)
            print(report)
            print("="*60)

            return report_file

        except Exception as e:
            logger.error(f"❌ Error generating report: {e}")
            raise

    def run_export(self):
        """Run the complete export process."""
        print("\n" + "🚀 Starting Database Export for Supabase Migration")
        print("="*60)

        try:
            # Export schema
            schema_file = self.export_schema()

            # Export data
            csv_file = self.export_data_to_csv()
            json_file = self.export_data_to_json()

            # Generate report
            report_file = self.generate_migration_report(schema_file, csv_file, json_file)

            print("\n✅ Export completed successfully!")
            print(f"\n📁 All files saved to: {os.path.abspath(self.export_dir)}")
            print(f"\n📊 Read the migration report for next steps:")
            print(f"   {os.path.abspath(report_file)}")

            return True

        except Exception as e:
            logger.error(f"❌ Export failed: {e}")
            print(f"\n❌ Export failed: {e}")
            return False


def main():
    """Main function."""
    migration = DatabaseMigration()
    success = migration.run_export()

    if success:
        print("\n" + "="*60)
        print("Next: Follow the steps in the migration report to complete")
        print("the migration to Supabase.")
        print("="*60)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
