import os
from dotenv import load_dotenv

# Cargar variables desde .env usando ruta absoluta para máxima compatibilidad
DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(dotenv_path=DOTENV_PATH, override=True)

# Configuración de conexión a la base de datos
DB_SERVER = os.getenv("DB_SERVER", "")
DB_SERVER_ALTERNATE = os.getenv("DB_SERVER_ALTERNATE", "")
DB_USERNAME = os.getenv("DB_USERNAME", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_PORT = int(os.getenv("DB_PORT", 1433))
DB_DEFAULT_DATABASE = os.getenv("DB_DEFAULT_DATABASE", "inventario")
DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", 10))

# Configuración general de la aplicación
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
FILE_STORAGE_PATH = os.getenv("FILE_STORAGE_PATH", "./storage")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "es")
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC-3")
NOTIFICATIONS_ENABLED = os.getenv("NOTIFICATIONS_ENABLED", "True") == "True"
DEFAULT_THEME = "dark"

# Solo imprimir diagnóstico si DEBUG_MODE está activo
if DEBUG_MODE:
    print("[DEBUG CONFIG] DB_SERVER:", DB_SERVER)
    print("[DEBUG CONFIG] DB_USERNAME:", DB_USERNAME)
    # Nunca imprimir la contraseña

# Validación temprana de variables críticas
if not DB_SERVER or not DB_USERNAME or not DB_PASSWORD:
    raise RuntimeError("[CONFIG ERROR] Faltan variables críticas de conexión a la base de datos. Revisa el archivo .env.")

def get_db_server():
    # Devuelve el servidor de base de datos principal, permite lógica futura para alternar
    return DB_SERVER

# Para el estándar de inicialización robusto y el flujo recomendado de arranque, ver:
# docs/decisiones_main.md y docs/estandares_seguridad.md
#
# Para los principios de diseño UI/UX y buenas prácticas visuales, ver:
# docs/estandares_visuales.md
#
# Para detalles de logging, feedback y manejo de errores críticos, ver:
# docs/estandares_feedback.md y docs/estandares_logging.md
#
# Para reglas de seguridad y manejo de variables sensibles, ver:
# docs/estandares_seguridad.md
