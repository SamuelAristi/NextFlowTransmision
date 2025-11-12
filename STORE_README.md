# NextFlow Store Module

Módulo de tienda e-commerce para usuarios finales del proyecto Dropshipping.

## Características

- 🛍️ **Catálogo de productos** con búsqueda y filtros
- 🛒 **Carrito de compras** con gestión de sesión
- ✅ **Proceso de checkout completo**
- 📦 **Sistema de gestión de inventario**
- 💳 **Pagos simulados** (para desarrollo)
- 📱 **Diseño responsive**
- 🔄 **Sin necesidad de registro** - compra como invitado

## Arquitectura

```
store_app.py              # Aplicación Flask principal (puerto 3000)
start_store_app.py        # Script de inicio
database_schema_store.sql # Schema de base de datos

src/
├── models/
│   └── store_models.py   # Modelos Pydantic
└── services/
    ├── product_service.py # Servicio de productos
    └── store_service.py   # Servicio de carrito/órdenes

store_templates/          # Templates HTML
├── base.html
├── store_index.html
├── store_products.html
├── store_cart.html
├── store_checkout.html
└── store_confirmation.html

store_static/             # Assets estáticos
├── css/
│   └── store.css
└── js/
    └── store.js
```

## Instalación

### 1. Instalar dependencias

```bash
pip install flask-session
```

O reinstalar todas las dependencias:

```bash
pip install -r requirements.txt
```

### 2. Crear tablas de base de datos

Ejecuta el script SQL para crear las tablas necesarias:

```bash
psql -U postgres -d DropshipingDB -f database_schema_store.sql
```

Esto creará las siguientes tablas:
- `products` - Catálogo de productos
- `customer_orders` - Órdenes de clientes
- `order_items` - Items de cada orden

El script también incluye 10 productos de ejemplo para empezar.

### 3. Iniciar la aplicación

```bash
python start_store_app.py
```

La tienda estará disponible en: **http://localhost:3000**

## Uso

### Para Clientes

1. **Navegar productos**: Ve a http://localhost:3000/products
2. **Buscar y filtrar**: Usa los filtros por categoría, precio, o búsqueda por texto
3. **Agregar al carrito**: Click en "Add to Cart" en cualquier producto
4. **Ver carrito**: Click en "Cart" en el menú de navegación
5. **Checkout**: Click en "Proceed to Checkout" y llena el formulario
6. **Confirmar orden**: Verás una página de confirmación con el número de orden

### API Endpoints

#### Productos

```bash
# Obtener todos los productos
GET /api/products

# Buscar productos
GET /api/products?search=laptop&category=Electronics&min_price=100&max_price=1000

# Obtener producto específico
GET /api/products/{product_id}

# Obtener categorías
GET /api/categories
```

#### Carrito

```bash
# Obtener carrito actual
GET /api/cart

# Agregar al carrito
POST /api/cart/add
Body: {"product_id": 1, "quantity": 2}

# Actualizar cantidad
PUT /api/cart/update
Body: {"product_id": 1, "quantity": 3}

# Eliminar del carrito
DELETE /api/cart/remove/{product_id}

# Vaciar carrito
DELETE /api/cart/clear
```

#### Checkout y Órdenes

```bash
# Procesar checkout
POST /api/checkout
Body: {
  "customer_info": {
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "555-0123",
    "shipping_address": "123 Main St",
    "shipping_city": "New York",
    "shipping_state": "NY",
    "shipping_zip": "10001",
    "shipping_country": "USA"
  },
  "payment_method": "simulated"
}

# Obtener orden por ID
GET /api/orders/{order_id}

# Obtener órdenes por email
GET /api/orders/email/{email}
```

## Configuración

### Impuestos y Envío

En `src/models/store_models.py`, puedes ajustar:

```python
# Tasa de impuesto (por defecto 8%)
tax_rate: Decimal = Field(Decimal('0.08'), description="Tax rate (8%)")

# Envío gratis sobre $100, sino $10
if self.subtotal >= 100:
    self.shipping_cost = Decimal('0.00')
else:
    self.shipping_cost = Decimal('10.00')
```

### Puerto de la aplicación

Por defecto corre en el puerto 3000. Para cambiarlo, edita `store_app.py`:

```python
app.run(host='0.0.0.0', port=3000, debug=True)
```

## Gestión de Productos

### Agregar productos manualmente

```sql
INSERT INTO products (name, description, category, subcategory, price, image_url, stock_quantity)
VALUES (
    'Nuevo Producto',
    'Descripción del producto',
    'Electronics',
    'Accessories',
    99.99,
    'https://example.com/image.jpg',
    100
);
```

### Actualizar inventario

```sql
UPDATE products
SET stock_quantity = stock_quantity - 5
WHERE product_id = 1;
```

## Estados de Orden

Las órdenes pueden tener los siguientes estados:
- `pending` - Orden creada, pendiente de procesamiento
- `processing` - Siendo procesada
- `shipped` - Enviada
- `delivered` - Entregada
- `cancelled` - Cancelada

## Integración con el Dashboard Principal

Ambas aplicaciones (Dashboard admin en puerto 5000 y Tienda en puerto 3000) pueden correr simultáneamente:

```bash
# Terminal 1: Dashboard admin
python start_web_app.py

# Terminal 2: Tienda de clientes
python start_store_app.py
```

- **Dashboard Admin** (puerto 5000): Para gestionar órdenes internas y reportes
- **Tienda de Clientes** (puerto 3000): Para que los usuarios finales compren

## Próximos Pasos

- [ ] Integrar pasarela de pago real (Stripe, PayPal, MercadoPago)
- [ ] Sistema de usuarios con login opcional
- [ ] Historial de órdenes para clientes registrados
- [ ] Sistema de reviews y ratings
- [ ] Wishlist/favoritos
- [ ] Notificaciones por email
- [ ] Panel de administración de productos
- [ ] Códigos de descuento y promociones
- [ ] Integración con sistemas de shipping (tracking)
- [ ] Multi-idioma
- [ ] Multi-moneda

## Troubleshooting

### Error: Tablas no existen

```
ERROR: relation "products" does not exist
```

**Solución**: Ejecuta el script SQL:
```bash
psql -U postgres -d DropshipingDB -f database_schema_store.sql
```

### Error: flask_session no encontrado

```
ModuleNotFoundError: No module named 'flask_session'
```

**Solución**: Instala la dependencia:
```bash
pip install flask-session
```

### Puerto 3000 en uso

**Solución**: Cambia el puerto en `store_app.py` o mata el proceso que usa el puerto 3000.

## Licencia

Parte del proyecto DropshipingDB.
