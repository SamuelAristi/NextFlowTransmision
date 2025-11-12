"""
Store Web Application
Customer-facing e-commerce store running on port 3000
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
try:
    from flask_session import Session
except ImportError:
    # For newer versions of flask-session
    from cachelib.file import FileSystemCache
    Session = None
from decimal import Decimal
import os
from datetime import timedelta
from loguru import logger

from src.services.product_service import ProductService
from src.services.store_service import StoreService
from src.models.store_models import (
    Cart,
    CartItem,
    CustomerInfo,
    CheckoutRequest,
    ProductCreate,
    ProductUpdate,
)

# Initialize Flask app
app = Flask(__name__,
            template_folder='store_templates',
            static_folder='store_static')

# Configuration
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_NAME'] = 'store_session'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'flask_session')

# Initialize session
if Session is not None:
    Session(app)
else:
    # For flask-session >= 0.6.0
    from flask_session import Session as FlaskSession
    FlaskSession(app)

# Enable CORS
CORS(app)

# Initialize services
product_service = ProductService()
store_service = StoreService()


# Helper functions
def get_cart_from_session() -> Cart:
    """Get cart from session or create new one"""
    if 'cart' not in session:
        session['cart'] = {
            'items': [],
            'subtotal': '0.00',
            'tax_rate': '0.08',
            'tax_amount': '0.00',
            'shipping_cost': '0.00',
            'total': '0.00'
        }

    cart_data = session['cart']
    items = [CartItem(**item) for item in cart_data['items']]

    cart = Cart(
        items=items,
        subtotal=Decimal(cart_data['subtotal']),
        tax_rate=Decimal(cart_data['tax_rate']),
        tax_amount=Decimal(cart_data['tax_amount']),
        shipping_cost=Decimal(cart_data['shipping_cost']),
        total=Decimal(cart_data['total'])
    )

    return cart


def save_cart_to_session(cart: Cart):
    """Save cart to session"""
    session['cart'] = {
        'items': [item.model_dump() for item in cart.items],
        'subtotal': str(cart.subtotal),
        'tax_rate': str(cart.tax_rate),
        'tax_amount': str(cart.tax_amount),
        'shipping_cost': str(cart.shipping_cost),
        'total': str(cart.total)
    }
    session.modified = True


def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


# Routes

@app.route('/')
def index():
    """Store home page"""
    return render_template('store_index.html')


@app.route('/products')
def products_page():
    """Products catalog page"""
    return render_template('store_products.html')


@app.route('/cart')
def cart_page():
    """Shopping cart page"""
    return render_template('store_cart.html')


@app.route('/checkout')
def checkout_page():
    """Checkout page"""
    cart = get_cart_from_session()
    if not cart.items:
        return render_template('store_cart.html', error="Your cart is empty")
    return render_template('store_checkout.html')


@app.route('/order-confirmation/<int:order_id>')
def order_confirmation(order_id):
    """Order confirmation page"""
    return render_template('store_confirmation.html', order_id=order_id)


# API Routes

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products with optional filters"""
    try:
        search = request.args.get('search')
        category = request.args.get('category')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')

        if any([search, category, min_price, max_price]):
            products = product_service.search_products(
                search_term=search,
                category=category,
                min_price=Decimal(min_price) if min_price else None,
                max_price=Decimal(max_price) if max_price else None
            )
        else:
            products = product_service.get_all_products(active_only=True)

        return jsonify(products), 200

    except Exception as e:
        logger.error(f"Error getting products: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get specific product"""
    try:
        product = product_service.get_product_by_id(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        return jsonify(product), 200

    except Exception as e:
        logger.error(f"Error getting product: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        categories = product_service.get_categories()
        return jsonify(categories), 200

    except Exception as e:
        logger.error(f"Error getting categories: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cart', methods=['GET'])
def get_cart():
    """Get current cart"""
    try:
        cart = get_cart_from_session()
        return jsonify(cart.model_dump()), 200

    except Exception as e:
        logger.error(f"Error getting cart: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        if not product_id:
            return jsonify({'error': 'Product ID is required'}), 400

        cart = get_cart_from_session()
        cart = store_service.add_to_cart(cart, product_id, quantity)
        save_cart_to_session(cart)

        return jsonify({
            'message': 'Product added to cart',
            'cart': cart.model_dump()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error adding to cart: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cart/update', methods=['PUT'])
def update_cart():
    """Update cart item quantity"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if not product_id or quantity is None:
            return jsonify({'error': 'Product ID and quantity are required'}), 400

        cart = get_cart_from_session()
        cart = store_service.update_cart_item(cart, product_id, quantity)
        save_cart_to_session(cart)

        return jsonify({
            'message': 'Cart updated',
            'cart': cart.model_dump()
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating cart: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cart/remove/<int:product_id>', methods=['DELETE'])
def remove_from_cart(product_id):
    """Remove item from cart"""
    try:
        cart = get_cart_from_session()
        cart = store_service.remove_from_cart(cart, product_id)
        save_cart_to_session(cart)

        return jsonify({
            'message': 'Product removed from cart',
            'cart': cart.model_dump()
        }), 200

    except Exception as e:
        logger.error(f"Error removing from cart: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cart/clear', methods=['DELETE'])
def clear_cart():
    """Clear cart"""
    try:
        cart = get_cart_from_session()
        cart = store_service.clear_cart(cart)
        save_cart_to_session(cart)

        return jsonify({
            'message': 'Cart cleared',
            'cart': cart.model_dump()
        }), 200

    except Exception as e:
        logger.error(f"Error clearing cart: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/checkout', methods=['POST'])
def checkout():
    """Process checkout"""
    try:
        data = request.get_json()

        # Get cart from session
        cart = get_cart_from_session()

        if not cart.items:
            return jsonify({'error': 'Cart is empty'}), 400

        # Create customer info
        customer_info = CustomerInfo(**data['customer_info'])

        # Create checkout request
        checkout_request = CheckoutRequest(
            customer_info=customer_info,
            cart=cart,
            payment_method=data.get('payment_method', 'simulated')
        )

        # Process checkout
        order = store_service.process_checkout(checkout_request)

        # Clear cart after successful checkout
        cart = store_service.clear_cart(cart)
        save_cart_to_session(cart)

        return jsonify({
            'message': 'Order created successfully',
            'order': order
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing checkout: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get order details"""
    try:
        order = store_service.get_order_by_id(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        return jsonify(order), 200

    except Exception as e:
        logger.error(f"Error getting order: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders/email/<email>', methods=['GET'])
def get_orders_by_email(email):
    """Get orders by customer email"""
    try:
        orders = store_service.get_orders_by_email(email)
        return jsonify(orders), 200

    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'store',
        'port': 3000
    }), 200


if __name__ == '__main__':
    logger.info("Starting Store Web Application on port 3000")
    app.run(host='0.0.0.0', port=3000, debug=True)
