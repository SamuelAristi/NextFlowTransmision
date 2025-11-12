-- ============================================================================
-- SCRIPT PARA ACTUALIZAR IMÁGENES DE PRODUCTOS
-- ============================================================================

-- OPCIÓN 1: URLs externas (recomendado para dropshipping)
-- Puedes usar URLs de proveedores, AliExpress, Amazon, etc.

-- Ejemplo: Actualizar un producto específico
UPDATE products
SET image_url = 'https://ejemplo.com/laptop-pro-15.jpg'
WHERE name = 'Laptop Pro 15"';

-- Ejemplo: Actualizar múltiples productos a la vez
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/71TPda7cwUL._AC_SL1500_.jpg' WHERE name = 'Laptop Pro 15"';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/61X9Q0R3GEL._AC_SL1500_.jpg' WHERE name = 'Wireless Mouse';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/61jb8uKG5GL._AC_SL1500_.jpg' WHERE name = 'USB-C Hub';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/71r7oboMFsL._AC_SL1500_.jpg' WHERE name = 'Mechanical Keyboard';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/71aVHbrmp2L._AC_SL1500_.jpg' WHERE name = 'Webcam HD';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/71CwG3lKiPL._AC_SL1500_.jpg' WHERE name = 'Monitor 27"';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/71w3oQ8+I4L._AC_SL1500_.jpg' WHERE name = 'Office Chair';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/71g-zG8VeFL._AC_SL1500_.jpg' WHERE name = 'Standing Desk';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/61wg5u34HYL._AC_SL1500_.jpg' WHERE name = 'Desk Lamp';
UPDATE products SET image_url = 'https://m.media-amazon.com/images/I/71M2fDRN4jL._AC_SL1500_.jpg' WHERE name = 'Notebook Set';


-- ============================================================================
-- OPCIÓN 2: Imágenes locales (si subes imágenes a tu servidor)
-- ============================================================================

-- Estructura: /static/images/products/nombre-producto.jpg
-- La URL sería: http://localhost:3000/static/images/products/laptop.jpg

UPDATE products SET image_url = '/static/images/products/laptop.jpg' WHERE name = 'Laptop Pro 15"';
UPDATE products SET image_url = '/static/images/products/mouse.jpg' WHERE name = 'Wireless Mouse';
UPDATE products SET image_url = '/static/images/products/usb-hub.jpg' WHERE name = 'USB-C Hub';
-- ... etc


-- ============================================================================
-- OPCIÓN 3: Unsplash (imágenes de alta calidad gratis)
-- ============================================================================

-- Busca imágenes en: https://unsplash.com/s/photos/laptop
-- Usa el formato: https://images.unsplash.com/photo-[ID]?w=800

-- Ejemplos con Unsplash:
UPDATE products SET image_url = 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800' WHERE name = 'Laptop Pro 15"';
UPDATE products SET image_url = 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800' WHERE name = 'Wireless Mouse';
UPDATE products SET image_url = 'https://images.unsplash.com/photo-1625948515291-69613efd103f?w=800' WHERE name = 'USB-C Hub';


-- ============================================================================
-- VERIFICAR CAMBIOS
-- ============================================================================

-- Ver todos los productos con sus imágenes
SELECT product_id, name, image_url
FROM products
ORDER BY category, name;
