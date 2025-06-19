import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Script de validación de permisos iniciales para usuarios 'admin' y 'prueba' en SQL Server
# ¡No exponer credenciales! Usa solo la configuración centralizada y helpers del core.
# Ejecutar este script en el entorno donde esté configurada la base de datos de la app.
# Muestra por consola los permisos de ambos usuarios para todos los módulos registrados.

import pyodbc
from dotenv import load_dotenv
from core.config import DB_DEFAULT_DATABASE
from core.database import get_connection_string, BaseDatabaseConnection
from core.logger import Logger

# Cargar variables de entorno desde .env (opcional, pero la app ya debe tener config centralizada)
load_dotenv()

# Usar solo la configuración centralizada del core (no exponer usuario, password ni IP)
# Forzar base de datos 'users' para validación de permisos iniciales
if DB_DEFAULT_DATABASE != "users":
    Logger().warning(f"⚠️  Advertencia: la base de datos predeterminada en config.py es '{DB_DEFAULT_DATABASE}', pero este script requiere 'users'. Se usará 'users' para la validación.")
    database = "users"
else:
    database = DB_DEFAULT_DATABASE
# Detectar driver ODBC automáticamente
try:
    driver = BaseDatabaseConnection.detectar_driver_odbc()
except Exception as e:
    Logger().error(f"❌ No se pudo detectar un driver ODBC compatible: {e}")
    exit(1)
# Construir string de conexión seguro (sin exponer credenciales)
CONNECTION_STRING = get_connection_string(driver, database)

QUERY = '''
SELECT u.usuario, pm.modulo, pm.puede_ver, pm.puede_modificar, pm.puede_aprobar
FROM usuarios u
JOIN permisos_modulos pm ON u.id = pm.id_usuario
WHERE u.usuario IN ('admin', 'prueba')
ORDER BY u.usuario, pm.modulo;
'''

CHECK_TABLE_QUERY = """
SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'permisos_modulos'
"""

# --- DOCUMENTACIÓN ---
# Este script SIEMPRE valida los permisos en la base 'users', sin importar la base default configurada.
# Usa la IP, usuario y password definidos en core/config.py (puede ser IP local o de red, soporta multi-PC/IP).
# Si necesitas validar en otra base, edita la variable 'database' arriba, pero por estándar debe ser 'users'.
# --- FIN DOCUMENTACIÓN ---

def main():
    import time
    try:
        Logger().info("[1/5] Conectando a la base de datos 'users' usando configuración centralizada...")
        Logger().info("    → Esperando respuesta del servidor (timeout=5s)...")
        t0 = time.time()
        try:
            conn = pyodbc.connect(CONNECTION_STRING, timeout=5)
        except Exception as e:
            Logger().error("❌ No se pudo establecer la conexión. Revisa IP, usuario, contraseña, firewall, permisos de SQL Server y que la base 'users' exista.")
            Logger().error(f"Detalle técnico: {e}")
            return
        t1 = time.time()
        if t1-t0 > 4.5:
            Logger().warning(f"⚠️  Advertencia: la conexión demoró {t1-t0:.1f} segundos. Puede haber problemas de red o firewall.")
        Logger().info("[2/5] Conexión exitosa. Abriendo cursor...")
        cur = conn.cursor()
        Logger().info("[3/5] Verificando existencia de la tabla 'permisos_modulos'...")
        cur.execute(CHECK_TABLE_QUERY)
        if not cur.fetchone():
            Logger().warning("⚠️  La tabla 'permisos_modulos' NO existe en la base de datos. Verifica la migración.")
            conn.close()
            return
        Logger().info("[4/5] Ejecutando consulta de permisos para 'admin' y 'prueba'...")
        cur.execute(QUERY)
        rows = cur.fetchall()
        if not rows:
            Logger().info("No se encontraron permisos para los usuarios 'admin' o 'prueba'.")
            conn.close()
            return
        Logger().info("Permisos de usuarios 'admin' y 'prueba':")
        for row in rows:
            usuario, modulo, puede_ver, puede_modificar, puede_aprobar = row
            Logger().info(f"Usuario: {usuario:8} | Módulo: {modulo:15} | Ver: {puede_ver} | Modificar: {puede_modificar} | Aprobar: {puede_aprobar}")
        Logger().info("[5/5] Cierre de conexión.")
        conn.close()
    except pyodbc.Error as e:
        Logger().error("❌ Error de conexión o consulta. Verifica la configuración y los permisos.")
        Logger().error(f"Detalle técnico: {e}")
    except Exception as e:
        Logger().error("❌ Error inesperado.")
        Logger().error(f"Detalle técnico: {e}")

if __name__ == "__main__":
    main()
