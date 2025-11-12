"""
Store Application Startup Script
Initializes and starts the customer-facing store on port 3000
"""

import sys
import os
from loguru import logger

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.utils.logger import setup_logging
from src.database.connection import DatabaseConnection

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = [
        'flask',
        'flask_cors',
        'flask_session',
        'psycopg2',
        'pydantic',
        'loguru',
        'dotenv'
    ]

    print(">> Iniciando aplicacion de tienda...")
    print("=" * 50)
    print("1. Verificando dependencias...")

    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"[OK] {module} - OK")
        except ImportError:
            print(f"[X] {module} - NOT FOUND")
            missing_modules.append(module)

    if missing_modules:
        print("\n[!] Modulos faltantes. Instalados con:")
        print(f"pip install {' '.join(missing_modules)}")
        return False

    return True


def check_database():
    """Check database connection"""
    print("\n2. Verificando conexion a base de datos...")
    try:
        db = DatabaseConnection()
        if db.test_connection():
            print("[OK] Conexion a base de datos - OK")
            return True
        else:
            print("[X] No se pudo conectar a la base de datos")
            return False
    except Exception as e:
        print(f"[X] Error de base de datos: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    print("\n3. Creando directorios necesarios...")
    directories = [
        'logs',
        'flask_session',
        'store_static/images',
        'store_static/css',
        'store_static/js'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)

    print("[OK] Directorios creados")


def check_database_schema():
    """Check if store tables exist"""
    print("\n4. Verificando esquema de base de datos...")
    try:
        db = DatabaseConnection()

        # Check if products table exists
        result = db.execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'products'
            ) as exists
        """)
        products_exists = result[0]['exists'] if result else False

        # Check if customer_orders table exists
        result = db.execute_query("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'customer_orders'
            ) as exists
        """)
        orders_exists = result[0]['exists'] if result else False

        if products_exists and orders_exists:
            print("[OK] Tablas de la tienda - OK")
            return True
        else:
            print("[!] Las tablas de la tienda no existen")
            print("\n[?] Para crear las tablas, ejecuta:")
            print("python setup_store_database.py")
            return False

    except Exception as e:
        print(f"[!] Error verificando esquema: {e}")
        print("\n[?] Para crear las tablas, ejecuta:")
        print("python setup_store_database.py")
        return False


def main():
    """Main startup function"""
    # Setup logging
    setup_logging()

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check database
    if not check_database():
        sys.exit(1)

    # Create directories
    create_directories()

    # Check database schema
    schema_ok = check_database_schema()
    if not schema_ok:
        print("\n[!] Las tablas de la tienda no existen. Intentando crearlas...")
        try:
            # Try to create the database schema
            import subprocess
            result = subprocess.run([sys.executable, 'setup_store_database.py'],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print("[OK] Tablas creadas exitosamente")
            else:
                print(f"[X] Error creando tablas: {result.stderr}")
                print("\n[!] Continuando sin las tablas de la tienda...")
                print("[!] La aplicacion podria no funcionar correctamente")
        except Exception as e:
            print(f"[X] Error ejecutando setup: {e}")
            print("\n[!] Continuando sin las tablas de la tienda...")
            print("[!] La aplicacion podria no funcionar correctamente")

    # Start the application
    print("\n4. Iniciando aplicacion de tienda...")
    print("=" * 50)
    print("[>>] Aplicacion disponible en: http://localhost:3000")
    print("[>>] Tienda: http://localhost:3000")
    print("[>>] Productos: http://localhost:3000/products")
    print("[>>] Carrito: http://localhost:3000/cart")
    print("\n[!] Presiona Ctrl+C para detener la aplicacion")
    print("=" * 50)
    print()

    try:
        from store_app import app
        app.run(host='0.0.0.0', port=3000, debug=True)
    except KeyboardInterrupt:
        print("\n\n[OK] Aplicacion detenida")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        print(f"\n[X] Error iniciando aplicacion: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
