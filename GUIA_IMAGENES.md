# Guía para Agregar Imágenes a los Productos

## Estado Actual

✅ **40 productos actualizados** con imágenes de alta calidad desde Unsplash
✅ Puedes ver los productos con imágenes en: http://localhost:3000/products

---

## 3 Formas de Agregar/Cambiar Imágenes

### 🌐 Opción 1: URLs Externas (RECOMENDADO para Dropshipping)

**Ventajas:**
- No ocupan espacio en tu servidor
- Perfectas para dropshipping (usas imágenes del proveedor)
- Fácil de actualizar

**Fuentes recomendadas:**
- **Unsplash** (gratis, alta calidad): https://unsplash.com
- **Pexels** (gratis): https://pexels.com
- **Amazon product images** (si haces dropshipping de Amazon)
- **AliExpress** (si haces dropshipping de AliExpress)
- **Imágenes de tus proveedores**

**Ejemplo usando el script Python:**

1. Edita `update_images.py`
2. Modifica el diccionario `PRODUCT_IMAGES`:

```python
PRODUCT_IMAGES = {
    "Laptop Pro 15\"": "https://tu-url-de-imagen.jpg",
    "Wireless Mouse": "https://otra-url.jpg",
    # ... más productos
}
```

3. Ejecuta:
```bash
python update_images.py
```

**Ejemplo usando SQL directo:**

```sql
UPDATE products
SET image_url = 'https://ejemplo.com/laptop.jpg'
WHERE name = 'Laptop Pro 15"';
```

---

### 💾 Opción 2: Imágenes Locales (en tu servidor)

**Ventajas:**
- Control total sobre las imágenes
- No dependes de servicios externos
- Puedes optimizarlas como quieras

**Pasos:**

1. **Guarda tus imágenes en:**
   ```
   C:\Users\USUARIO\Desktop\Dropshiping\store_static\images\products\
   ```

2. **Nombra los archivos** (ejemplo):
   - `laptop.jpg`
   - `mouse.jpg`
   - `keyboard.jpg`

3. **Actualiza la base de datos:**

   **Opción A: Con SQL**
   ```sql
   UPDATE products
   SET image_url = '/static/images/products/laptop.jpg'
   WHERE name = 'Laptop Pro 15"';
   ```

   **Opción B: Edita `update_images.py`**
   ```python
   PRODUCT_IMAGES = {
       "Laptop Pro 15\"": "/static/images/products/laptop.jpg",
       "Wireless Mouse": "/static/images/products/mouse.jpg",
   }
   ```

   Y ejecuta: `python update_images.py`

**Formatos recomendados:**
- JPG (para fotos de productos)
- PNG (si necesitas transparencia)
- WebP (más ligero, navegadores modernos)

**Tamaño recomendado:**
- 800x800 píxeles
- Máximo 200KB por imagen

---

### ☁️ Opción 3: CDN / Cloud Storage

**Servicios recomendados:**
- **Cloudinary** (gratis hasta 25GB): https://cloudinary.com
- **AWS S3**: https://aws.amazon.com/s3/
- **Google Cloud Storage**: https://cloud.google.com/storage
- **imgbb**: https://imgbb.com (gratis)

**Pasos generales:**

1. Sube tus imágenes al servicio
2. Obtén las URLs públicas
3. Actualiza la base de datos con esas URLs

---

## Scripts Disponibles

### 📄 `update_images.py`

Script Python para actualizar imágenes de forma masiva.

**Uso:**
```bash
python update_images.py
```

**Personalizar:**
1. Abre `update_images.py`
2. Edita el diccionario `PRODUCT_IMAGES`
3. Ejecuta el script

### 📄 `update_product_images.sql`

Archivo SQL con ejemplos de queries para actualizar imágenes.

**Uso con psql:**
```bash
psql -U postgres -d DropshipingDB -f update_product_images.sql
```

**O ejecuta queries individuales** en cualquier cliente SQL.

---

## Buscar Imágenes Gratuitas

### Unsplash (Usado actualmente)

1. Ve a: https://unsplash.com
2. Busca tu producto (ejemplo: "laptop")
3. Haz clic en la imagen que quieras
4. Copia la URL y agrega `?w=800&q=80` al final

**Ejemplo:**
```
Original: https://images.unsplash.com/photo-1496181133206-80ce9b88a853
Optimizada: https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&q=80
```

### Pexels

1. Ve a: https://pexels.com
2. Busca tu producto
3. Descarga en tamaño mediano
4. Sube a tu servidor o usa el link directo

---

## Actualizar una Imagen Individual

### Método rápido (SQL):

```sql
-- Ver productos actuales
SELECT product_id, name, image_url FROM products WHERE name LIKE '%Laptop%';

-- Actualizar uno específico
UPDATE products
SET image_url = 'https://nueva-url.jpg'
WHERE product_id = 1;

-- Verificar cambio
SELECT product_id, name, image_url FROM products WHERE product_id = 1;
```

### Método con Python (un producto):

```python
from src.database.connection import DatabaseConnection

db = DatabaseConnection()

with db.get_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE products SET image_url = %s WHERE name = %s",
            ("https://nueva-url.jpg", "Laptop Pro 15\"")
        )
        conn.commit()

print("Imagen actualizada!")
```

---

## Ver los Cambios

Después de actualizar imágenes, visita:

- **Tienda (público)**: http://localhost:3000/products
- **Admin dashboard**: http://localhost:5000

Las imágenes deberían aparecer inmediatamente. Si no se ven:
1. Refresca la página (Ctrl+F5)
2. Verifica que la URL sea válida y pública
3. Revisa la consola del navegador por errores

---

## Tips y Buenas Prácticas

✅ **Usa imágenes de alta calidad** (mínimo 800x800px)
✅ **Optimiza el tamaño** (máximo 200-300KB)
✅ **URLs válidas** - Verifica que funcionen en el navegador
✅ **Imágenes cuadradas** - Se ven mejor en grids
✅ **Fondo blanco o transparente** - Más profesional
✅ **Misma iluminación** - Mantén consistencia visual

❌ **Evita:**
- Imágenes con marcas de agua
- URLs rotas o privadas
- Imágenes muy pequeñas (menos de 400px)
- Formatos exóticos (BMP, TIFF)

---

## Troubleshooting

### ❓ Las imágenes no se muestran

**Posibles causas:**
1. La URL no es pública
2. La URL está rota (404)
3. CORS bloqueado por el servidor de imágenes
4. Formato de URL incorrecto

**Solución:**
- Abre la URL de la imagen directamente en el navegador
- Si no carga, la URL no es válida
- Usa otra fuente o sube la imagen localmente

### ❓ Las imágenes cargan lento

**Solución:**
- Usa un CDN
- Optimiza las imágenes (compresión)
- Reduce el tamaño a 800x800px
- Usa formato WebP

### ❓ Necesito cambiar todas las imágenes

**Solución rápida:**
1. Edita `update_images.py`
2. Reemplaza todas las URLs en `PRODUCT_IMAGES`
3. Ejecuta: `python update_images.py`

---

## Próximos Pasos

1. ✅ Visita la tienda: http://localhost:3000/products
2. 📝 Personaliza las imágenes según tus necesidades
3. 🚀 Prueba el carrito y checkout con las nuevas imágenes
4. 💬 Pregunta al chatbot sobre los productos

---

**¿Necesitas más ayuda?**
- Revisa `update_images.py` para ejemplos de código
- Revisa `update_product_images.sql` para ejemplos SQL
- Las imágenes actuales son de Unsplash (alta calidad, gratis)
