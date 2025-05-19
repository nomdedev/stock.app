# Configuración de conexión a la base de datos
DB_SERVER = "192.168.88.205"                    # Dirección o IP del servidor SQL
DB_SERVER_ALTERNATE = "localhost\\SQLEXPRESS"   # Nombre del servidor local actualizado
DB_USERNAME = "sa"                              # Usuario de la base de datos
DB_PASSWORD = "mps.1887"                        # Contraseña del usuario
DB_PORT = 1433                                  # Puerto del servidor SQL
DB_DEFAULT_DATABASE = "inventario"              # Base de datos predeterminada
DB_TIMEOUT = 10                                 # Tiempo de espera para la conexión (en segundos)

# Configuración general de la aplicación
DEBUG_MODE = False                  # Activar o desactivar modo de depuración
FILE_STORAGE_PATH = "./storage"     # Ruta para almacenar archivos
DEFAULT_LANGUAGE = "es"             # Idioma predeterminado
DEFAULT_TIMEZONE = "UTC-3"          # Zona horaria predeterminada
NOTIFICATIONS_ENABLED = True        # Activar o desactivar notificaciones
