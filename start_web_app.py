"""
Script de inicio para la aplicación web con verificación de dependencias.
"""
import sys
import os
import subprocess
import time

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def check_dependencies():
    """Verificar que todas las dependencias estén instaladas."""
    required_packages = [
        'flask',
        'flask_cors',
        'plotly',
        'pandas',
        'psycopg2'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - FALTANTE")
    
    if missing_packages:
        print(f"\n📦 Instalando paquetes faltantes: {', '.join(missing_packages)}")
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} instalado correctamente")
            except subprocess.CalledProcessError:
                print(f"❌ Error instalando {package}")
                return False
    
    return True

def check_database_connection():
    """Verificar conexión a la base de datos."""
    try:
        # Add src to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        
        from src.database.connection import db_connection
        
        if db_connection.test_connection():
            print("✅ Conexión a base de datos - OK")
            return True
        else:
            print("❌ Error de conexión a base de datos")
            return False
    except Exception as e:
        print(f"❌ Error verificando base de datos: {e}")
        return False

def start_web_app():
    """Iniciar la aplicación web."""
    print("🚀 Iniciando aplicación web...")
    print("=" * 50)
    
    # Verificar dependencias
    print("1. Verificando dependencias...")
    if not check_dependencies():
        print("❌ Error: Dependencias faltantes")
        return False
    
    # Verificar conexión a base de datos
    print("\n2. Verificando conexión a base de datos...")
    if not check_database_connection():
        print("❌ Error: No se puede conectar a la base de datos")
        return False
    
    # Crear directorios necesarios
    print("\n3. Creando directorios necesarios...")
    os.makedirs('exports', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    print("✅ Directorios creados")
    
    # Iniciar aplicación
    print("\n4. Iniciando aplicación web...")
    print("🌐 Aplicación disponible en: http://localhost:5000")
    print("📊 Dashboard: http://localhost:5000")
    print("🔗 API Power BI: http://localhost:5000/api/powerbi/orders")
    print("\n💡 Presiona Ctrl+C para detener la aplicación")
    print("=" * 50)
    
    try:
        # Importar y ejecutar la aplicación web
        from web_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error iniciando aplicación: {e}")
        return False
    
    return True

if __name__ == "__main__":
    start_web_app()
