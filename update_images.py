"""
Script para actualizar imágenes de productos de forma fácil.
"""
from src.database.connection import DatabaseConnection
from loguru import logger

# Mapeo de productos a URLs de imágenes
# Puedes reemplazar estas URLs con las que quieras usar
PRODUCT_IMAGES = {
    # Electronics - Computers
    "Laptop Pro 15\"": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80",

    # Electronics - Monitors
    "Monitor 27\"": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&q=80",

    # Electronics - Accessories
    "Wireless Mouse": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&q=80",
    "USB-C Hub": "https://images.unsplash.com/photo-1625948515291-69613efd103f?w=800&q=80",
    "Webcam HD": "https://images.unsplash.com/photo-1519558260268-cde7e03a0152?w=800&q=80",
    "Mechanical Keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&q=80",

    # Furniture - Office
    "Office Chair": "https://images.unsplash.com/photo-1580480055273-228ff5388ef8?w=800&q=80",
    "Standing Desk": "https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?w=800&q=80",

    # Furniture - Lighting
    "Desk Lamp": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&q=80",

    # Stationery
    "Notebook Set": "https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=800&q=80",
}


def update_product_images():
    """Actualizar las imágenes de los productos en la base de datos."""
    db = DatabaseConnection()

    print("=" * 80)
    print("ACTUALIZANDO IMÁGENES DE PRODUCTOS")
    print("=" * 80)
    print()

    updated_count = 0

    try:
        with db.get_connection() as conn:
            with conn.cursor() as cursor:
                for product_name, image_url in PRODUCT_IMAGES.items():
                    try:
                        # Actualizar la imagen del producto
                        cursor.execute(
                            "UPDATE products SET image_url = %s WHERE name = %s",
                            (image_url, product_name)
                        )

                        if cursor.rowcount > 0:
                            print(f"[OK] Actualizado: {product_name}")
                            updated_count += cursor.rowcount
                        else:
                            print(f"[WARN] No encontrado: {product_name}")

                    except Exception as e:
                        print(f"[ERROR] Error actualizando {product_name}: {e}")

                # Confirmar cambios
                conn.commit()

        print()
        print("=" * 80)
        print(f"[COMPLETADO] {updated_count} productos actualizados")
        print("=" * 80)
        print()
        print("Verifica los cambios en: http://localhost:3000/products")
        print()

    except Exception as e:
        logger.error(f"Error actualizando imagenes: {e}")
        print(f"[ERROR] {e}")


if __name__ == "__main__":
    update_product_images()
