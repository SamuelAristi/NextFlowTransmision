"""
Script seguro para eliminar productos duplicados.
Primero actualiza las referencias en order_items, luego elimina duplicados.
"""
from src.database.connection import DatabaseConnection
from loguru import logger

def fix_duplicate_products_safe():
    """Eliminar productos duplicados de forma segura."""
    db = DatabaseConnection()

    print("=" * 80)
    print("ELIMINANDO PRODUCTOS DUPLICADOS (SEGURO)")
    print("=" * 80)
    print()

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                # 1. Contar productos antes
                cursor.execute("SELECT COUNT(*) FROM products")
                result = cursor.fetchone()
                total_before = list(result.values())[0] if isinstance(result, dict) else result[0]
                print(f"Total productos antes: {total_before}")

                # 2. Verificar si hay order_items
                cursor.execute("SELECT COUNT(*) FROM order_items")
                result = cursor.fetchone()
                order_items_count = list(result.values())[0] if isinstance(result, dict) else result[0]
                print(f"Total items en ordenes: {order_items_count}")
                print()

                # 3. Actualizar referencias en order_items para usar los IDs que vamos a mantener
                if order_items_count > 0:
                    print("Actualizando referencias en order_items...")

                    # Obtener mapeo de product_id viejo -> product_id nuevo (el menor)
                    cursor.execute("""
                        WITH product_mapping AS (
                            SELECT
                                product_id,
                                name,
                                MIN(product_id) OVER (PARTITION BY name) as keep_id
                            FROM products
                        )
                        SELECT product_id, keep_id
                        FROM product_mapping
                        WHERE product_id != keep_id
                    """)

                    mappings = cursor.fetchall()

                    for mapping in mappings:
                        old_id = mapping['product_id'] if isinstance(mapping, dict) else mapping[0]
                        new_id = mapping['keep_id'] if isinstance(mapping, dict) else mapping[1]

                        cursor.execute("""
                            UPDATE order_items
                            SET product_id = %s
                            WHERE product_id = %s
                        """, (new_id, old_id))

                    print(f"  [OK] {len(mappings)} referencias actualizadas")
                    print()

                # 4. Eliminar productos duplicados
                print("Eliminando productos duplicados...")
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

                # 5. Contar productos después
                cursor.execute("SELECT COUNT(*) FROM products")
                result = cursor.fetchone()
                total_after = list(result.values())[0] if isinstance(result, dict) else result[0]

                # Confirmar cambios
                conn.commit()

                print(f"  [OK] {deleted_count} productos duplicados eliminados")
                print(f"Total productos despues: {total_after}")
                print()

                # 6. Mostrar productos únicos restantes
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
                    pid = p['product_id'] if isinstance(p, dict) else p[0]
                    pname = p['name'] if isinstance(p, dict) else p[1]
                    pprice = p['price'] if isinstance(p, dict) else p[3]
                    pstock = p['stock_quantity'] if isinstance(p, dict) else p[4]
                    print(f"[{pid}] {pname} - ${pprice} - Stock: {pstock}")

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
    fix_duplicate_products_safe()
