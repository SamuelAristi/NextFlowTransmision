"""
Product Service
Service layer for managing products in the store
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger

from src.database.connection import DatabaseConnection
from src.models.store_models import ProductBase, ProductCreate, ProductUpdate


class ProductService:
    """Service for managing products"""

    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_products(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all products from the database"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    if active_only:
                        cursor.execute(
                            "SELECT * FROM products WHERE is_active = TRUE ORDER BY category, name"
                        )
                    else:
                        cursor.execute("SELECT * FROM products ORDER BY category, name")

                    products = cursor.fetchall()
                    logger.info(f"Retrieved {len(products)} products from database")
                    return [dict(product) for product in products]

        except Exception as e:
            logger.error(f"Error getting products: {e}")
            raise

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        "SELECT * FROM products WHERE product_id = %s", (product_id,)
                    )
                    product = cursor.fetchone()

                    if product:
                        logger.info(f"Retrieved product {product_id}")
                        return dict(product)
                    else:
                        logger.warning(f"Product {product_id} not found")
                        return None

        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            raise

    def search_products(
        self,
        search_term: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
    ) -> List[Dict[str, Any]]:
        """Search products with filters"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    query = "SELECT * FROM products WHERE is_active = TRUE"
                    params = []

                    if search_term:
                        query += " AND (name ILIKE %s OR description ILIKE %s)"
                        params.extend([f"%{search_term}%", f"%{search_term}%"])

                    if category:
                        query += " AND category = %s"
                        params.append(category)

                    if min_price is not None:
                        query += " AND price >= %s"
                        params.append(min_price)

                    if max_price is not None:
                        query += " AND price <= %s"
                        params.append(max_price)

                    query += " ORDER BY category, name"

                    cursor.execute(query, params)
                    products = cursor.fetchall()

                    logger.info(f"Found {len(products)} products matching search criteria")
                    return [dict(product) for product in products]

        except Exception as e:
            logger.error(f"Error searching products: {e}")
            raise

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT DISTINCT category FROM products WHERE is_active = TRUE ORDER BY category"
                    )
                    categories = [row[0] for row in cursor.fetchall()]
                    logger.info(f"Retrieved {len(categories)} categories")
                    return categories

        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            raise

    def create_product(self, product_data: ProductCreate) -> Dict[str, Any]:
        """Create a new product"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO products (name, description, category, subcategory,
                                            price, image_url, stock_quantity, is_active)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (
                            product_data.name,
                            product_data.description,
                            product_data.category,
                            product_data.subcategory,
                            product_data.price,
                            product_data.image_url,
                            product_data.stock_quantity,
                            product_data.is_active,
                        ),
                    )
                    product = cursor.fetchone()
                    conn.commit()

                    logger.info(f"Created product {product['product_id']}: {product['name']}")
                    return dict(product)

        except Exception as e:
            logger.error(f"Error creating product: {e}")
            raise

    def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[Dict[str, Any]]:
        """Update an existing product"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Build dynamic update query
                    update_fields = []
                    params = []

                    data_dict = product_data.model_dump(exclude_unset=True)

                    for field, value in data_dict.items():
                        if value is not None:
                            update_fields.append(f"{field} = %s")
                            params.append(value)

                    if not update_fields:
                        return self.get_product_by_id(product_id)

                    update_fields.append("updated_at = CURRENT_TIMESTAMP")
                    params.append(product_id)

                    query = f"""
                        UPDATE products
                        SET {', '.join(update_fields)}
                        WHERE product_id = %s
                        RETURNING *
                    """

                    cursor.execute(query, params)
                    product = cursor.fetchone()
                    conn.commit()

                    if product:
                        logger.info(f"Updated product {product_id}")
                        return dict(product)
                    else:
                        logger.warning(f"Product {product_id} not found for update")
                        return None

        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}")
            raise

    def update_stock(self, product_id: int, quantity_change: int) -> bool:
        """Update product stock (can be positive or negative)"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE products
                        SET stock_quantity = stock_quantity + %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE product_id = %s AND stock_quantity + %s >= 0
                        RETURNING stock_quantity
                        """,
                        (quantity_change, product_id, quantity_change),
                    )
                    result = cursor.fetchone()
                    conn.commit()

                    if result:
                        logger.info(
                            f"Updated stock for product {product_id}: new stock = {result[0]}"
                        )
                        return True
                    else:
                        logger.warning(
                            f"Could not update stock for product {product_id} - insufficient stock"
                        )
                        return False

        except Exception as e:
            logger.error(f"Error updating stock for product {product_id}: {e}")
            raise

    def check_stock_availability(self, product_id: int, quantity: int) -> bool:
        """Check if product has sufficient stock"""
        try:
            product = self.get_product_by_id(product_id)
            if not product:
                return False

            return product["stock_quantity"] >= quantity

        except Exception as e:
            logger.error(f"Error checking stock for product {product_id}: {e}")
            return False

    def delete_product(self, product_id: int) -> bool:
        """Soft delete a product (set is_active to False)"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE products
                        SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                        WHERE product_id = %s
                        """,
                        (product_id,),
                    )
                    conn.commit()

                    logger.info(f"Deleted (deactivated) product {product_id}")
                    return True

        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}")
            raise
