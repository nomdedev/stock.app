# Estándares de seguridad y manejo de datos sensibles

## Prácticas obligatorias

- Nunca exponer credenciales ni datos sensibles en el código fuente, ejemplos ni README.
- Usar variables de entorno y/o archivos `.env` para la configuración de la base de datos y otros secretos.
- El archivo `.env` nunca debe subirse al repositorio. Usar `.env.example` como plantilla.
- El string de conexión se debe construir siempre usando helpers seguros (ver `core/database.py`).
- El archivo `core/config.py` real nunca debe subirse, solo `config.example.py`.

## Ejemplo seguro de uso

```python
from dotenv import load_dotenv
import os
load_dotenv()
DB_CONFIG = {
    'server': os.getenv('DB_SERVER', ''),
    'database': os.getenv('DB_DATABASE', ''),
    'username': os.getenv('DB_USERNAME', ''),
    'password': os.getenv('DB_PASSWORD', ''),
    'driver': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
}
```

## Prohibido

- Hardcodear credenciales, IPs, usuarios o contraseñas en cualquier archivo.
- Subir archivos de configuración real al repositorio.

## Nombres únicos para archivos y carpetas

- Está prohibido que un archivo y una carpeta tengan el mismo nombre (por ejemplo, 'inventario/' y 'inventario.py' o 'modules/inventario/').
- Toda referencia, importación o script debe actualizarse si se renombra una carpeta o archivo para evitar ambigüedad y errores de importación.
- Justificación: Evita conflictos en imports, rutas relativas y errores en sistemas de archivos multiplataforma.

---

Cualquier excepción debe estar documentada en el código y en este archivo.
