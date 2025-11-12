# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NextFlow Dropshipping Platform - A comprehensive data management and e-commerce system for dropshipping operations. The project consists of two main applications:

1. **Admin Dashboard** (`web_app.py`) - Internal order management, data quality monitoring, and analytics
2. **Customer Store** (`store_app.py`) - Public-facing e-commerce storefront

Both applications share the same PostgreSQL database (`DropshipingDB`) but operate on separate tables and serve different purposes.

## Running the Applications

### Admin Dashboard (Port 5000)
```bash
python start_web_app.py
# Access at http://localhost:5000
```

Features: Order management, data quality reports, real-time updates via WebSocket, Power BI integration, n8n webhook notifications.

### Customer Store (Port 3000)
```bash
python start_store_app.py
# Access at http://localhost:3000
```

Features: Product catalog, shopping cart, checkout, order placement.

### Database Setup

First-time setup requires running SQL schema files:

```bash
# Core orders table (for admin dashboard)
psql -U postgres -d DropshipingDB -f database_schema.sql

# Store tables (for customer store)
psql -U postgres -d DropshipingDB -f database_schema_store.sql
```

## Architecture

### Database Layer
- **Connection Management**: `src/database/connection.py` - Singleton pattern with both psycopg2 (raw queries) and SQLAlchemy (ORM) support
- **Configuration**: `src/config/settings.py` - Pydantic-based settings loaded from `.env` file

### Core Tables
- `orders` - Internal order records for admin dashboard (legacy/imported data)
- `products` - Product catalog for store
- `customer_orders` - Orders placed through the store
- `order_items` - Line items for customer orders

### Service Layer Pattern
Services encapsulate business logic and database operations:
- `src/services/order_service.py` - Admin order operations, data quality checks, duplicate detection
- `src/services/product_service.py` - Product catalog management
- `src/services/store_service.py` - Shopping cart and customer order processing

### Models (Pydantic)
- `src/models/order.py` - Admin order models with validation
- `src/models/store_models.py` - Store models (Product, Cart, CustomerOrder)

### Integration Layer
- `src/integrations/n8n_webhook.py` - Event notifications to n8n workflows
  - Sends events for order created/updated/deleted, status changes, low stock alerts
  - Configured via `N8N_WEBHOOK_URL`, `N8N_WEBHOOK_ENABLED`, `N8N_WEBHOOK_SECRET` in `.env`

## Key Architectural Patterns

### Dual Application Architecture
Both Flask apps run independently but share database infrastructure:
- `web_app.py` - Uses Flask-SocketIO for real-time admin updates
- `store_app.py` - Uses Flask-Session for shopping cart persistence

### Data Quality Pipeline
The admin dashboard implements a comprehensive data cleaning workflow:
1. **Duplicate Detection** - Identifies duplicates by customer_name + order_date + category + quantity + subtotal_amount
2. **Incomplete Records** - Detects null/empty required fields
3. **Data Type Validation** - Validates numeric ranges and date formats
4. **Business Rules** - Validates status values, extreme values (quantity > 1000, subtotal > 100000, shipping > 1000)

Access via: `OrderService.get_data_quality_report()`, `clean_duplicate_orders()`, `validate_data_types()`, `validate_business_rules()`

### Real-time Updates (Admin Dashboard)
Uses Flask-SocketIO to broadcast changes:
- Order creation/updates trigger `broadcast_order_change()` and `broadcast_notification()`
- Clients receive live updates without page refresh

### n8n Integration
All order operations in admin dashboard trigger webhook events to n8n:
- Configure n8n endpoint in `.env`: `N8N_WEBHOOK_URL`
- Events: `order.created`, `order.updated`, `order.deleted`, `order.status_changed`, `order.bulk_status_update`

## Environment Configuration

Copy `config.env.example` to `.env` and configure:

```env
# Database (required)
PG_HOST=localhost
PG_PORT=5432
PG_DB=DropshipingDB
PG_USER=postgres
PG_PASS=postgres
PG_SCHEMA_RAW=public

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# n8n Webhooks (optional)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/nextflow-chatbot
N8N_WEBHOOK_ENABLED=true
N8N_WEBHOOK_SECRET=nextflow-secret-123
```

## API Endpoints

### Admin Dashboard (`web_app.py`)

**Dashboard & Stats**
- `GET /` - Dashboard UI
- `GET /api/dashboard/stats` - Order statistics by status, category, year

**Order Management**
- `GET /api/orders` - List all orders with pagination/filters
- `GET /api/orders/<id>` - Get specific order
- `POST /api/orders` - Create new order (triggers n8n webhook)
- `PUT /api/orders/<id>` - Update order (triggers n8n webhook)
- `DELETE /api/orders/<id>` - Delete order (triggers n8n webhook)
- `POST /api/orders/bulk-status` - Bulk update order status

**Data Quality**
- `POST /api/clean/duplicates` - Identify and remove duplicates
- `POST /api/clean/incomplete` - Clean incomplete records
- `POST /api/validate/types` - Validate data types
- `POST /api/validate/rules` - Validate business rules
- `GET /api/data-quality-report` - Full quality report

**Exports & Integration**
- `GET /api/export/csv` - Export orders to CSV
- `GET /api/powerbi/orders` - Power BI connector endpoint

**WebSocket Events**
- `connect/disconnect` - Client connection management
- `order_change` - Real-time order updates
- `notification` - Real-time notifications

### Customer Store (`store_app.py`)

**Store Pages**
- `GET /` - Store homepage
- `GET /products` - Product catalog UI
- `GET /cart` - Shopping cart UI
- `GET /checkout` - Checkout UI

**Product API**
- `GET /api/products` - List products (supports filters: search, category, min_price, max_price)
- `GET /api/products/<id>` - Get product details
- `GET /api/categories` - List available categories

**Cart API**
- `GET /api/cart` - Get current cart
- `POST /api/cart/add` - Add item to cart
- `PUT /api/cart/update` - Update item quantity
- `DELETE /api/cart/remove/<id>` - Remove item from cart
- `DELETE /api/cart/clear` - Empty cart

**Checkout API**
- `POST /api/checkout` - Process order (requires customer_info and payment_method)
- `GET /api/orders/<id>` - Get order details
- `GET /api/orders/email/<email>` - Get orders by customer email

## Development Workflow

### Adding New Order Validation Rules
Extend `OrderService` in `src/services/order_service.py`:
```python
def validate_custom_rule(self) -> OrderCleaningResult:
    df = self.get_orders_dataframe()
    # Add validation logic
    # Return OrderCleaningResult with results
```

### Adding New Store Products
Either insert via SQL or add API endpoint in `store_app.py`:
```sql
INSERT INTO products (name, description, category, subcategory, price, image_url, stock_quantity)
VALUES ('Product Name', 'Description', 'Category', 'Subcategory', 99.99, 'https://...', 100);
```

### Adding New n8n Event Types
Extend `N8NWebhook` class in `src/integrations/n8n_webhook.py`:
```python
def send_custom_event(self, data: Dict[str, Any]) -> bool:
    return self.send_event("custom.event_type", data)
```

Then call from your Flask route:
```python
from src.integrations.n8n_webhook import n8n_webhook
n8n_webhook.send_custom_event({"key": "value"})
```

## Common Operations

### Running Tests
No test suite currently implemented. Tests should be added in a `tests/` directory.

### Database Migrations
No migration system in place. Schema changes require manual SQL execution:
```bash
psql -U postgres -d DropshipingDB -c "ALTER TABLE ..."
```

### Viewing Logs
```bash
# Real-time log monitoring
tail -f logs/app.log

# Search for errors
grep ERROR logs/app.log
```

### Backup Database
```bash
pg_dump -U postgres DropshipingDB > backups/backup_$(date +%Y%m%d_%H%M%S).sql
```

## Important Notes

### Order vs Customer Order
- `orders` table - Admin dashboard, legacy/imported order data
- `customer_orders` table - Store frontend, new customer orders
- These are separate entities and should not be confused

### Session Management
- Admin dashboard: Uses Flask's default session
- Customer store: Uses Flask-Session with filesystem storage (`flask_session/` directory)

### Stock Management
When customer orders are placed, `product_service.py` should decrement `stock_quantity` in products table. Ensure this logic is properly implemented to avoid overselling.

### Status Values
Valid order statuses: `pending`, `processing`, `shipped`, `delivered`, `cancelled`, `returned`

Changing these requires updating:
- Business validation rules in `order_service.py`
- Frontend status filters in templates
- n8n workflow configurations

## Dependencies

Install all dependencies:
```bash
pip install -r requirements.txt
```

Key libraries:
- **Flask** - Web framework for both apps
- **Flask-SocketIO** - Real-time admin updates
- **Flask-Session** - Shopping cart persistence
- **SQLAlchemy** - ORM and database engine
- **psycopg2-binary** - PostgreSQL driver
- **pandas** - Data analysis and quality reports
- **pydantic** - Data validation and settings
- **loguru** - Logging
- **plotly/dash** - Data visualizations
- **requests** - n8n webhook calls

## File Structure

```
├── web_app.py              # Admin dashboard Flask app (port 5000)
├── store_app.py            # Customer store Flask app (port 3000)
├── start_web_app.py        # Admin dashboard launcher
├── start_store_app.py      # Customer store launcher
├── main.py                 # CLI tool for batch data operations
├── .env                    # Environment configuration (DO NOT COMMIT)
├── config.env.example      # Environment template
├── requirements.txt        # Python dependencies
├── database_schema_store.sql  # Store tables schema
├── src/
│   ├── config/
│   │   └── settings.py     # Pydantic settings from .env
│   ├── database/
│   │   └── connection.py   # Database connection singleton
│   ├── models/
│   │   ├── order.py        # Admin order models
│   │   └── store_models.py # Store models (Product, Cart, Order)
│   ├── services/
│   │   ├── order_service.py    # Admin order operations
│   │   ├── product_service.py  # Product catalog
│   │   └── store_service.py    # Cart and checkout
│   ├── integrations/
│   │   └── n8n_webhook.py  # n8n event sender
│   └── utils/
│       └── logger.py       # Logging configuration
├── templates/              # Admin dashboard HTML templates
├── store_templates/        # Customer store HTML templates
├── static/                 # Admin dashboard assets
├── store_static/          # Customer store assets
├── logs/                  # Application logs (git ignored)
├── flask_session/         # Session storage (git ignored)
└── backups/               # Database backups (git ignored)
```

## Power BI Integration

Connect Power BI to admin dashboard:
1. Use Web connector in Power BI
2. URL: `http://localhost:5000/api/powerbi/orders`
3. Returns all orders as JSON array
4. Configure refresh schedule as needed

For production, replace `localhost` with deployed server URL.
