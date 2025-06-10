import os
from dotenv import load_dotenv, set_key

# Buscar primero en config/privado/.env, luego fallback a .env en raíz
PRIVADO_DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config', 'privado', '.env'))
ROOT_DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
CONFIG_PATH = PRIVADO_DOTENV_PATH if os.path.exists(PRIVADO_DOTENV_PATH) else ROOT_DOTENV_PATH

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
    def save_env(data: dict):
        # Sobrescribe el archivo .env con los valores de data (dict)
        lines = []
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        keys_written = set()
        new_lines = []
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                k = line.split('=', 1)[0].strip()
                if k in data:
                    new_lines.append(f"{k}={data[k]}\n")
                    keys_written.add(k)
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        # Agregar claves nuevas
        for k, v in data.items():
            if k not in keys_written:
                new_lines.append(f"{k}={v}\n")
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
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
