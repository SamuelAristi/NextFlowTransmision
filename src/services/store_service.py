"""
Store Service
Service layer for managing shopping cart and customer orders
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import uuid
from datetime import datetime
from psycopg2.extras import RealDictCursor
from loguru import logger

from src.database.connection import DatabaseConnection
from src.models.store_models import (
    Cart,
    CartItem,
    CustomerInfo,
    CheckoutRequest,
    CustomerOrderWithItems,
)
from src.services.product_service import ProductService


class StoreService:
    """Service for managing store operations (cart, checkout, orders)"""

    def __init__(self):
        self.db = DatabaseConnection()
        self.product_service = ProductService()

    def add_to_cart(self, cart: Cart, product_id: int, quantity: int) -> Cart:
        """Add item to cart"""
        try:
            # Get product details
            product = self.product_service.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Product {product_id} not found")

            if not product["is_active"]:
                raise ValueError(f"Product {product_id} is not available")

            # Check stock
            if not self.product_service.check_stock_availability(product_id, quantity):
                raise ValueError(f"Insufficient stock for product {product_id}")

            # Check if product already in cart
            existing_item = next(
                (item for item in cart.items if item.product_id == product_id), None
            )

            if existing_item:
                # Update quantity
                new_quantity = existing_item.quantity + quantity
                if not self.product_service.check_stock_availability(
                    product_id, new_quantity
                ):
                    raise ValueError(f"Insufficient stock for product {product_id}")

                existing_item.quantity = new_quantity
                existing_item.subtotal = existing_item.product_price * new_quantity
            else:
                # Add new item
                cart_item = CartItem(
                    product_id=product_id,
                    product_name=product["name"],
                    product_price=Decimal(str(product["price"])),
                    quantity=quantity,
                    subtotal=Decimal(str(product["price"])) * quantity,
                )
                cart.items.append(cart_item)

            # Recalculate totals
            cart.calculate_totals()

            logger.info(f"Added {quantity}x product {product_id} to cart")
            return cart

        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            raise

    def update_cart_item(self, cart: Cart, product_id: int, quantity: int) -> Cart:
        """Update quantity of item in cart"""
        try:
            if quantity <= 0:
                return self.remove_from_cart(cart, product_id)

            item = next((item for item in cart.items if item.product_id == product_id), None)
            if not item:
                raise ValueError(f"Product {product_id} not found in cart")

            # Check stock
            if not self.product_service.check_stock_availability(product_id, quantity):
                raise ValueError(f"Insufficient stock for product {product_id}")

            item.quantity = quantity
            item.subtotal = item.product_price * quantity

            cart.calculate_totals()

            logger.info(f"Updated product {product_id} quantity to {quantity}")
            return cart

        except Exception as e:
            logger.error(f"Error updating cart item: {e}")
            raise

    def remove_from_cart(self, cart: Cart, product_id: int) -> Cart:
        """Remove item from cart"""
        try:
            cart.items = [item for item in cart.items if item.product_id != product_id]
            cart.calculate_totals()

            logger.info(f"Removed product {product_id} from cart")
            return cart

        except Exception as e:
            logger.error(f"Error removing from cart: {e}")
            raise

    def clear_cart(self, cart: Cart) -> Cart:
        """Clear all items from cart"""
        try:
            cart.items = []
            cart.calculate_totals()

            logger.info("Cart cleared")
            return cart

        except Exception as e:
            logger.error(f"Error clearing cart: {e}")
            raise

    def process_checkout(self, checkout_request: CheckoutRequest) -> Dict[str, Any]:
        """Process checkout and create order"""
        try:
            cart = checkout_request.cart
            customer_info = checkout_request.customer_info

            # Validate cart is not empty
            if not cart.items:
                raise ValueError("Cart is empty")

            # Validate stock for all items
            for item in cart.items:
                if not self.product_service.check_stock_availability(
                    item.product_id, item.quantity
                ):
                    raise ValueError(
                        f"Insufficient stock for product {item.product_name}"
                    )

            # Recalculate totals to ensure accuracy
            cart.calculate_totals()

            # Generate session ID
            session_id = str(uuid.uuid4())

            # Create order in database
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Insert customer order
                    cursor.execute(
                        """
                        INSERT INTO customer_orders (
                            customer_name, customer_email, customer_phone,
                            shipping_address, shipping_city, shipping_state,
                            shipping_zip, shipping_country,
                            subtotal_amount, tax_amount, shipping_cost, total_amount,
                            status, payment_method, payment_status,
                            notes, session_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING customer_order_id
                        """,
                        (
                            customer_info.customer_name,
                            customer_info.customer_email,
                            customer_info.customer_phone,
                            customer_info.shipping_address,
                            customer_info.shipping_city,
                            customer_info.shipping_state,
                            customer_info.shipping_zip,
                            customer_info.shipping_country,
                            cart.subtotal,
                            cart.tax_amount,
                            cart.shipping_cost,
                            cart.total,
                            "pending",
                            checkout_request.payment_method,
                            "completed" if checkout_request.payment_method == "simulated" else "pending",
                            customer_info.notes,
                            session_id,
                        ),
                    )

                    order_id = cursor.fetchone()["customer_order_id"]

                    # Insert order items
                    for item in cart.items:
                        cursor.execute(
                            """
                            INSERT INTO order_items (
                                customer_order_id, product_id, product_name,
                                product_price, quantity, subtotal
                            ) VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                            (
                                order_id,
                                item.product_id,
                                item.product_name,
                                item.product_price,
                                item.quantity,
                                item.subtotal,
                            ),
                        )

                        # Update product stock directly in the same transaction
                        cursor.execute(
                            """
                            UPDATE products
                            SET stock_quantity = stock_quantity - %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE product_id = %s AND stock_quantity >= %s
                            """,
                            (item.quantity, item.product_id, item.quantity),
                        )

                    conn.commit()

                    logger.info(
                        f"Order {order_id} created successfully for {customer_info.customer_email}"
                    )

                    # Also create entries in the main 'orders' table for admin dashboard
                    # Each item becomes a separate order in the orders table

                    # Get the next order_id (max + 1)
                    cursor.execute("SELECT COALESCE(MAX(order_id), 0) + 1 FROM orders")
                    next_order_id = cursor.fetchone()[0]

                    for item in cart.items:
                        cursor.execute(
                            """
                            INSERT INTO orders (
                                order_id, status, customer_name, order_date, quantity,
                                subtotal_amount, tax_rate, shipping_cost, category, subcategory
                            ) VALUES (%s, %s, %s, CURRENT_DATE, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                next_order_id,
                                "pending",
                                customer_info.customer_name,
                                item.quantity,
                                item.subtotal,
                                cart.tax_rate,
                                cart.shipping_cost / len(cart.items),  # Distribute shipping cost
                                "Store Order",  # Category
                                item.product_name,  # Subcategory with product name
                            ),
                        )
                        next_order_id += 1  # Increment for next item

                    conn.commit()
                    logger.info(f"Created {len(cart.items)} order entries in orders table")

                    # Get complete order details within the same connection
                    cursor.execute(
                        "SELECT * FROM customer_orders WHERE customer_order_id = %s",
                        (order_id,),
                    )
                    order = cursor.fetchone()

                    if not order:
                        raise ValueError(f"Order {order_id} not found after creation")

                    order = dict(order)

                    # Get order items
                    cursor.execute(
                        "SELECT * FROM order_items WHERE customer_order_id = %s",
                        (order_id,),
                    )
                    items = [dict(item) for item in cursor.fetchall()]

                    order["items"] = items

                    logger.info(f"Retrieved order {order_id} details successfully")
                    return order

        except Exception as e:
            logger.error(f"Error processing checkout: {e}")
            raise

    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get order details with items"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Get order
                    cursor.execute(
                        "SELECT * FROM customer_orders WHERE customer_order_id = %s",
                        (order_id,),
                    )
                    order = cursor.fetchone()

                    if not order:
                        return None

                    order = dict(order)

                    # Get order items
                    cursor.execute(
                        "SELECT * FROM order_items WHERE customer_order_id = %s",
                        (order_id,),
                    )
                    items = [dict(item) for item in cursor.fetchall()]

                    order["items"] = items

                    return order

        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            raise

    def get_orders_by_email(self, email: str) -> List[Dict[str, Any]]:
        """Get all orders for a customer email"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM customer_orders
                        WHERE customer_email = %s
                        ORDER BY order_date DESC
                        """,
                        (email,),
                    )
                    orders = [dict(order) for order in cursor.fetchall()]

                    # Get items for each order
                    for order in orders:
                        cursor.execute(
                            "SELECT * FROM order_items WHERE customer_order_id = %s",
                            (order["customer_order_id"],),
                        )
                        order["items"] = [dict(item) for item in cursor.fetchall()]

                    logger.info(f"Retrieved {len(orders)} orders for {email}")
                    return orders

        except Exception as e:
            logger.error(f"Error getting orders for {email}: {e}")
            raise

    def get_all_customer_orders(
        self, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all customer orders (for admin view)"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        SELECT * FROM customer_orders
                        ORDER BY order_date DESC
                        LIMIT %s OFFSET %s
                        """,
                        (limit, offset),
                    )
                    orders = [dict(order) for order in cursor.fetchall()]

                    logger.info(f"Retrieved {len(orders)} customer orders")
                    return orders

        except Exception as e:
            logger.error(f"Error getting customer orders: {e}")
            raise

    def update_order_status(self, order_id: int, status: str) -> Optional[Dict[str, Any]]:
        """Update order status"""
        try:
            valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")

            with self.db.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(
                        """
                        UPDATE customer_orders
                        SET status = %s
                        WHERE customer_order_id = %s
                        RETURNING *
                        """,
                        (status, order_id),
                    )
                    order = cursor.fetchone()
                    conn.commit()

                    if order:
                        logger.info(f"Updated order {order_id} status to {status}")
                        return dict(order)
                    else:
                        return None

        except Exception as e:
            logger.error(f"Error updating order {order_id} status: {e}")
            raise
