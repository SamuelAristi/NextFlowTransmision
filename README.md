Aquí tienes el README reorganizado, claro y consistente en Markdown.

---

# Data Cleaning Project — DropshipingDB

Herramienta para conectar a **PostgreSQL** (`DropshipingDB`) y realizar **limpieza, validación y reporte de calidad** sobre la tabla `orders`. Incluye **app web** con dashboard, API para Power BI y utilidades de exportación.

## Tabla de Contenido

* [Características](#características)
* [Arquitectura del Proyecto](#arquitectura-del-proyecto)
* [Requisitos](#requisitos)
* [Instalación](#instalación)
* [Configuración](#configuración)
* [Estructura de Datos](#estructura-de-datos)

  * [DDL en PostgreSQL](#ddl-en-postgresql)
  * [Modelo Pydantic](#modelo-pydantic)
* [Uso por Línea de Comandos](#uso-por-línea-de-comandos)
* [Aplicación Web](#aplicación-web)
* [Operaciones de Limpieza y Validación](#operaciones-de-limpieza-y-validación)
* [Extensión de Funcionalidad](#extensión-de-funcionalidad)
* [Logging](#logging)
* [Dependencias](#dependencias)
* [Próximos Pasos](#próximos-pasos)

---

## Características

* **Reporte de calidad de datos**: perfilado y métricas clave.
* **Limpieza de duplicados** según lógica de negocio.
* **Detección de registros incompletos** (nulos, vacíos).
* **Validación de tipos y reglas** (rangos, dominios de estado, límites).
* **App Web** (dashboard, herramientas de limpieza, filtros y exportación).
* **API para Power BI** y **descarga CSV**.

---

## Arquitectura del Proyecto

```
├── src/
│   ├── config/               # Configuración de la aplicación
│   │   ├── __init__.py
│   │   └── settings.py       # DB & logging
│   ├── database/             # Conexión y operaciones de DB
│   │   ├── __init__.py
│   │   └── connection.py     # Gestión de conexiones PostgreSQL
│   ├── models/               # Modelos de datos
│   │   ├── __init__.py
│   │   └── order.py          # Modelo para 'orders'
│   ├── services/             # Lógica de negocio
│   │   ├── __init__.py
│   │   └── order_service.py  # Servicios para 'orders'
│   └── utils/                # Utilidades
│       ├── __init__.py
│       └── logger.py         # Configuración de logging
├── main.py                   # Punto de entrada (CLI)
├── start_web_app.py          # Punto de entrada (Web)
├── requirements.txt          # Dependencias
├── config.env.example        # Ejemplo de configuración
└── README.md                 # Este archivo
```

---

## Requisitos

* **Python 3.10+**
* **PostgreSQL 12+** en ejecución
* Base de datos **`DropshipingDB`** existente
* Tabla **`orders`** creada (ver [DDL](#ddl-en-postgresql))

---

## Instalación

1. **Clonar o descargar** este repositorio.
2. **Instalar dependencias**:

   ```bash
   pip install -r requirements.txt
   ```
3. **Configurar variables de entorno**:

   * Copia `config.env.example` a `.env`.
   * Variables por defecto:

     ```env
     PG_HOST=localhost
     PG_PORT=5432
     PG_DB=DropshipingDB
     PG_USER=postgres
     PG_PASS=postgres
     PG_SCHEMA_RAW=public
     ```

---

## Configuración

Asegúrate de que PostgreSQL esté activo y accesible con las credenciales definidas en `.env`. Los logs se configuran mediante `loguru` (ver [Logging](#logging)).

---

## Estructura de Datos

### DDL en PostgreSQL

```sql
CREATE TABLE orders (
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
```

### Modelo Pydantic

```python
from datetime import date
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional

class OrderBase(BaseModel):
    order_id: Optional[int] = Field(None, description="Primary key - bigint")
    status: str = Field(..., description="Order status - text NOT NULL")
    customer_name: str = Field(..., description="Customer name - text NOT NULL")
    order_date: date = Field(..., description="Order date - date NOT NULL")
    quantity: int = Field(..., ge=0, description="Quantity - integer NOT NULL")
    subtotal_amount: Decimal = Field(..., ge=0, description="Subtotal amount - numeric(18,2)")
    tax_rate: Decimal = Field(..., ge=0, description="Tax rate - numeric(6,4)")
    shipping_cost: Decimal = Field(..., ge=0, description="Shipping cost - numeric(18,2)")
    category: str = Field(..., description="Product category - text NOT NULL")
    subcategory: str = Field(..., description="Product subcategory - text NOT NULL")
```

---

## Uso por Línea de Comandos

Ejecuta la aplicación principal (operaciones batch/CLI):

```bash
python main.py
```

Funciones disponibles:

1. **Reporte de calidad de datos**
2. **Limpieza de duplicados**
3. **Limpieza de registros incompletos**
4. **Validación de tipos de datos**
5. **Validación de reglas de negocio**

> La selección de operación y parámetros puede estar guiada por prompts en consola o banderas (según implementación en `main.py`).

---

## Aplicación Web

### Iniciar la app

```bash
python start_web_app.py
```

### Acceso

* **URL principal**: [http://localhost:5000](http://localhost:5000)
* **Dashboard**: visualizaciones y métricas en tiempo real
* **API Power BI**: [http://localhost:5000/api/powerbi/orders](http://localhost:5000/api/powerbi/orders)

### Funcionalidades

1. **Dashboard interactivo**
2. **Gestión de limpieza** (herramientas para reglas y duplicados)
3. **Visualización de órdenes** (tabla paginada con filtros)
4. **Conexión Power BI** (endpoints listos)
5. **Exportación CSV**

---

## Operaciones de Limpieza y Validación

Validaciones específicas implementadas:

* **Registros incompletos**: nulos y cadenas vacías en campos requeridos
* **Valores negativos**: `quantity`, `subtotal_amount`, `shipping_cost`
* **Tax rate inválido**: tasas **> 100%**
* **Valores extremos**:

  * `quantity > 1000`
  * `subtotal_amount > 100000`
  * `shipping_cost > 1000`
* **Estados inválidos**: dominio permitido → `pending`, `processing`, `shipped`, `delivered`, `cancelled`, `returned`
* **Duplicados**: detección basada en combinación de **cliente + fecha + categoría + cantidad + monto** (o la lógica definida en `order_service.py`)

---

## Extensión de Funcionalidad

Para agregar nuevas reglas de limpieza o validación, extiende `OrderService`:

```
src/services/order_service.py
```

Ejemplos de extensiones:

* Reglas por categoría/subcategoría
* Normalización de nombres de cliente
* Recalculo de impuestos/total a partir de `subtotal_amount`, `tax_rate` y `shipping_cost`
* Catálogos de `status` o `category` desde tablas de referencia

---

## Logging

* **Consola**: durante desarrollo
* **Archivo**: `logs/app.log` (ruta y rotación configurables en `utils/logger.py`)
* Framework: **loguru**

---

## Dependencias

Principales librerías:

* `psycopg2-binary` — Conexión PostgreSQL
* `pandas` — Análisis y manipulación
* `sqlalchemy` — ORM
* `pydantic` — Validación de datos
* `loguru` — Logging
* `python-dotenv` — Variables de entorno

Consulta `requirements.txt` para el listado completo y versiones.

---

## Próximos Pasos

1. ✅ Modelo `Order` actualizado con la estructura real
2. ✅ Credenciales de base de datos configuradas
3. ✅ Aplicación web implementada
4. Ejecuta `python start_web_app.py` para iniciar la **Web App**
5. Accede a `http://localhost:5000` para usar el **dashboard**
6. Conecta **Power BI** usando `http://localhost:5000/api/powerbi/orders`
7. Revisa `logs/app.log` para detalles de ejecución y diagnósticos

---

 curl -X POST https://n8n.srv998948.hstgr.cloud/webhook/43a50d3a-6c9c-41b0-9e66-9e330554be12 \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"test\"}"