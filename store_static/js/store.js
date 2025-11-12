// Store JavaScript

// API Base URL
const API_BASE = window.location.origin;

// Utility functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background-color: ${type === 'success' ? '#10b981' : '#ef4444'};
        color: white;
        border-radius: 0.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Cart functions
async function getCart() {
    try {
        const response = await fetch(`${API_BASE}/api/cart`);
        const cart = await response.json();
        return cart;
    } catch (error) {
        console.error('Error getting cart:', error);
        return { items: [], total: 0 };
    }
}

async function addToCart(productId, quantity = 1) {
    try {
        const response = await fetch(`${API_BASE}/api/cart/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_id: productId, quantity })
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Product added to cart!');
            updateCartBadge();
            return data.cart;
        } else {
            showNotification(data.error || 'Error adding to cart', 'error');
            return null;
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showNotification('Error adding to cart', 'error');
        return null;
    }
}

async function updateCartItem(productId, quantity) {
    try {
        const response = await fetch(`${API_BASE}/api/cart/update`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ product_id: productId, quantity })
        });

        const data = await response.json();

        if (response.ok) {
            return data.cart;
        } else {
            showNotification(data.error || 'Error updating cart', 'error');
            return null;
        }
    } catch (error) {
        console.error('Error updating cart:', error);
        showNotification('Error updating cart', 'error');
        return null;
    }
}

async function removeFromCart(productId) {
    try {
        const response = await fetch(`${API_BASE}/api/cart/remove/${productId}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (response.ok) {
            showNotification('Product removed from cart');
            return data.cart;
        } else {
            showNotification(data.error || 'Error removing from cart', 'error');
            return null;
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
        showNotification('Error removing from cart', 'error');
        return null;
    }
}

async function updateCartBadge() {
    const cart = await getCart();
    const badge = document.querySelector('.cart-badge');
    if (badge) {
        const itemCount = cart.items.reduce((sum, item) => sum + item.quantity, 0);
        badge.textContent = itemCount;
        badge.style.display = itemCount > 0 ? 'inline' : 'none';
    }
}

// Product functions
async function loadProducts(filters = {}) {
    try {
        const queryParams = new URLSearchParams(filters).toString();
        const response = await fetch(`${API_BASE}/api/products?${queryParams}`);
        const products = await response.json();
        return products;
    } catch (error) {
        console.error('Error loading products:', error);
        return [];
    }
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/api/categories`);
        const categories = await response.json();
        return categories;
    } catch (error) {
        console.error('Error loading categories:', error);
        return [];
    }
}

function renderProducts(products) {
    const grid = document.getElementById('products-grid');
    if (!grid) return;

    if (products.length === 0) {
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem;">No products found</p>';
        return;
    }

    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image_url || '/static/images/placeholder.png'}"
                 alt="${product.name}"
                 class="product-image"
                 onerror="this.src='/static/images/placeholder.png'">
            <div class="product-info">
                <div class="product-category">${product.category}</div>
                <h3 class="product-name">${product.name}</h3>
                <p class="product-description">${product.description || ''}</p>
                <div class="product-footer">
                    <div>
                        <div class="product-price">${formatCurrency(product.price)}</div>
                        <span class="stock-badge ${getStockClass(product.stock_quantity)}">
                            ${getStockText(product.stock_quantity)}
                        </span>
                    </div>
                    <button class="btn btn-primary btn-small"
                            onclick="addToCart(${product.product_id})"
                            ${product.stock_quantity === 0 ? 'disabled' : ''}>
                        Add to Cart
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

function getStockClass(stock) {
    if (stock === 0) return 'stock-out';
    if (stock < 10) return 'stock-low';
    return 'stock-in';
}

function getStockText(stock) {
    if (stock === 0) return 'Out of Stock';
    if (stock < 10) return `Only ${stock} left`;
    return 'In Stock';
}

// Cart page functions
async function renderCart() {
    const cart = await getCart();
    const cartItemsContainer = document.getElementById('cart-items');
    const cartSummary = document.getElementById('cart-summary');
    const emptyCart = document.getElementById('empty-cart');
    const cartContent = document.getElementById('cart-content');

    if (cart.items.length === 0) {
        if (emptyCart) emptyCart.style.display = 'block';
        if (cartContent) cartContent.style.display = 'none';
        return;
    }

    if (emptyCart) emptyCart.style.display = 'none';
    if (cartContent) cartContent.style.display = 'grid';

    // Render cart items
    if (cartItemsContainer) {
        cartItemsContainer.innerHTML = cart.items.map(item => `
            <div class="cart-item" data-product-id="${item.product_id}">
                <img src="${item.product_image || '/static/images/placeholder.png'}"
                     alt="${item.product_name}"
                     class="cart-item-image"
                     onerror="this.src='/static/images/placeholder.png'">
                <div class="cart-item-info">
                    <h3>${item.product_name}</h3>
                    <div class="cart-item-price">${formatCurrency(item.product_price)} each</div>
                    <div class="cart-item-quantity">
                        <button class="quantity-btn" onclick="updateQuantity(${item.product_id}, ${item.quantity - 1})">-</button>
                        <input type="number" class="quantity-input" value="${item.quantity}"
                               min="1" onchange="updateQuantity(${item.product_id}, this.value)">
                        <button class="quantity-btn" onclick="updateQuantity(${item.product_id}, ${item.quantity + 1})">+</button>
                    </div>
                </div>
                <div class="cart-item-actions">
                    <div class="cart-item-total">${formatCurrency(item.subtotal)}</div>
                    <button class="btn btn-danger btn-small" onclick="removeItem(${item.product_id})">Remove</button>
                </div>
            </div>
        `).join('');
    }

    // Render cart summary
    if (cartSummary) {
        cartSummary.innerHTML = `
            <h2>Order Summary</h2>
            <div class="summary-row">
                <span>Subtotal:</span>
                <span>${formatCurrency(cart.subtotal)}</span>
            </div>
            <div class="summary-row">
                <span>Tax (8%):</span>
                <span>${formatCurrency(cart.tax_amount)}</span>
            </div>
            <div class="summary-row">
                <span>Shipping:</span>
                <span>${cart.shipping_cost > 0 ? formatCurrency(cart.shipping_cost) : 'FREE'}</span>
            </div>
            ${cart.subtotal < 100 ? '<p style="font-size: 0.875rem; color: #6b7280; margin-top: 0.5rem;">Free shipping on orders over $100</p>' : ''}
            <div class="summary-row total">
                <span>Total:</span>
                <span>${formatCurrency(cart.total)}</span>
            </div>
            <a href="/checkout" class="btn btn-success checkout-btn">Proceed to Checkout</a>
        `;
    }

    updateCartBadge();
}

async function updateQuantity(productId, quantity) {
    quantity = parseInt(quantity);
    if (quantity < 1) quantity = 1;

    const cart = await updateCartItem(productId, quantity);
    if (cart) {
        await renderCart();
    }
}

async function removeItem(productId) {
    const cart = await removeFromCart(productId);
    if (cart) {
        await renderCart();
    }
}

// Checkout functions
async function loadCheckoutCart() {
    const cart = await getCart();
    const checkoutItems = document.getElementById('checkout-items');
    const checkoutSummary = document.getElementById('checkout-summary');

    if (cart.items.length === 0) {
        window.location.href = '/cart';
        return;
    }

    // Render checkout items
    if (checkoutItems) {
        checkoutItems.innerHTML = cart.items.map(item => `
            <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #e5e7eb;">
                <div>
                    <strong>${item.product_name}</strong>
                    <div style="color: #6b7280; font-size: 0.875rem;">Qty: ${item.quantity} × ${formatCurrency(item.product_price)}</div>
                </div>
                <div><strong>${formatCurrency(item.subtotal)}</strong></div>
            </div>
        `).join('');
    }

    // Render checkout summary
    if (checkoutSummary) {
        checkoutSummary.innerHTML = `
            <div class="summary-row">
                <span>Subtotal:</span>
                <span>${formatCurrency(cart.subtotal)}</span>
            </div>
            <div class="summary-row">
                <span>Tax (8%):</span>
                <span>${formatCurrency(cart.tax_amount)}</span>
            </div>
            <div class="summary-row">
                <span>Shipping:</span>
                <span>${cart.shipping_cost > 0 ? formatCurrency(cart.shipping_cost) : 'FREE'}</span>
            </div>
            <div class="summary-row total">
                <span>Total:</span>
                <span>${formatCurrency(cart.total)}</span>
            </div>
        `;
    }
}

async function processCheckout(event) {
    event.preventDefault();

    const form = event.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    // Disable button and show loading
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="loading"></span> Processing...';

    // Get form data
    const formData = {
        customer_info: {
            customer_name: form.customer_name.value,
            customer_email: form.customer_email.value,
            customer_phone: form.customer_phone.value,
            shipping_address: form.shipping_address.value,
            shipping_city: form.shipping_city.value,
            shipping_state: form.shipping_state.value,
            shipping_zip: form.shipping_zip.value,
            shipping_country: form.shipping_country.value,
            notes: form.notes.value
        },
        payment_method: 'simulated'
    };

    try {
        const response = await fetch(`${API_BASE}/api/checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (response.ok) {
            // Redirect to confirmation page
            window.location.href = `/order-confirmation/${data.order.customer_order_id}`;
        } else {
            showNotification(data.error || 'Error processing checkout', 'error');
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    } catch (error) {
        console.error('Error processing checkout:', error);
        showNotification('Error processing checkout', 'error');
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Order confirmation
async function loadOrderConfirmation(orderId) {
    try {
        const response = await fetch(`${API_BASE}/api/orders/${orderId}`);
        const order = await response.json();

        const orderDetails = document.getElementById('order-details');
        if (orderDetails) {
            orderDetails.innerHTML = `
                <h3>Order #${order.customer_order_id}</h3>
                <p><strong>Customer:</strong> ${order.customer_name}</p>
                <p><strong>Email:</strong> ${order.customer_email}</p>
                <p><strong>Total:</strong> ${formatCurrency(order.total_amount)}</p>
                <p><strong>Status:</strong> ${order.status}</p>
                <p style="margin-top: 1rem; color: #6b7280;">A confirmation email has been sent to ${order.customer_email}</p>
            `;
        }
    } catch (error) {
        console.error('Error loading order:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateCartBadge();
});
