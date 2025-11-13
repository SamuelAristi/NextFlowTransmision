"""
Script para eliminar productos duplicados de la base de datos.
Mantiene solo el primer producto de cada nombre.
"""
from src.database.connection import DatabaseConnection
from loguru import logger

def remove_duplicate_products():
    """Eliminar productos duplicados, manteniendo solo uno por nombre."""
    db = DatabaseConnection()

    print("=" * 80)
    print("ELIMINANDO PRODUCTOS DUPLICADOS")
    print("=" * 80)
    print()

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # Contar productos antes
                cursor.execute("SELECT COUNT(*) FROM products")
                result = cursor.fetchone()
                total_before = result['count'] if isinstance(result, dict) else result[0] if result else 0
                print(f"Total productos antes: {total_before}")
                print()

                # Eliminar duplicados manteniendo el de menor product_id por cada nombre
                delete_query = """
                DELETE FROM products
                WHERE product_id NOT IN (
                    SELECT MIN(product_id)
                    FROM products
                    GROUP BY name
                )
                """

                cursor.execute(delete_query)
                deleted_count = cursor.rowcount

                # Contar productos después
                cursor.execute("SELECT COUNT(*) FROM products")
                result = cursor.fetchone()
                total_after = result['count'] if isinstance(result, dict) else result[0] if result else 0

                # Confirmar cambios
                conn.commit()

                print(f"Productos eliminados: {deleted_count}")
                print(f"Total productos despues: {total_after}")
                print()

                # Mostrar productos únicos restantes
                cursor.execute("""
                    SELECT product_id, name, category, price, stock_quantity
                    FROM products
                    ORDER BY category, name
                """)

                products = cursor.fetchall()
                print("=" * 80)
                print("PRODUCTOS UNICOS RESTANTES:")
                print("=" * 80)
                for p in products:
                    print(f"[{p['product_id']}] {p['name']} - ${p['price']} - Stock: {p['stock_quantity']}")

                print()
                print("=" * 80)
                print("[COMPLETADO] Duplicados eliminados exitosamente")
                print("=" * 80)
                print()
                print("Verifica los cambios en: http://localhost:3000/products")

    except Exception as e:
        logger.error(f"Error eliminando duplicados: {e}")
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    remove_duplicate_products()
