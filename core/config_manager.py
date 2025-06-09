import os
from dotenv import load_dotenv, set_key

CONFIG_PATH = os.path.join(os.getcwd(), '.env')

class ConfigManager:
    """
    Utilidad para leer, actualizar y validar variables críticas de configuración (.env).
    """
    @staticmethod
    def load_env():
        load_dotenv(CONFIG_PATH, override=True)

    @staticmethod
    def get(key, default=None):
        ConfigManager.load_env()
        return os.environ.get(key, default)

    @staticmethod
    def set(key, value):
        set_key(CONFIG_PATH, key, value)
        ConfigManager.load_env()

    @staticmethod
    def get_all(keys):
        ConfigManager.load_env()
        return {k: os.environ.get(k, '') for k in keys}

    @staticmethod
    def validate(data):
        # Validaciones básicas: no vacíos, IP/host válido, etc.
        errors = {}
        if not data.get('DB_SERVER'):
            errors['DB_SERVER'] = 'Servidor requerido.'
        if not data.get('DB_USERNAME'):
            errors['DB_USERNAME'] = 'Usuario requerido.'
        if not data.get('DB_DATABASE'):
            errors['DB_DATABASE'] = 'Base de datos requerida.'
        # Contraseña puede estar vacía si SQL Server permite autenticación integrada
        # Validar IP/host si es necesario
        # ...agregar más validaciones según necesidad...
        return errors
