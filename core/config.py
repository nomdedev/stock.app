import os
from dotenv import load_dotenv

# Cargar variables desde .env si existe
load_dotenv()

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
DEFAULT_THEME = os.getenv("DEFAULT_THEME", "light")

def get_db_server():
    # Devuelve el servidor de base de datos principal, permite lógica futura para alternar
    return DB_SERVER
