# Buenas prácticas para la edición y visualización de configuraciones críticas (puertos, IP, credenciales)

## 1. Edición y visualización desde la app
- Todas las configuraciones críticas (puertos, IP, credenciales de base de datos, etc.) deben ser editables desde un panel de configuración accesible solo para administradores.
- Los campos sensibles (contraseñas, tokens) deben mostrarse ocultos (tipo password) y solo ser visibles bajo acción explícita del usuario administrador.
- Al guardar cambios, validar tipos y rangos (ej: IP válida, puerto entre 1024-65535, credenciales no vacías).
- Proveer feedback visual inmediato sobre éxito/error de la conexión al guardar cambios.
- Registrar en logs/auditoría cualquier cambio en configuraciones críticas, incluyendo usuario, IP y timestamp.

## 2. Seguridad y buenas prácticas
- Nunca almacenar ni mostrar contraseñas en texto plano fuera del campo de edición.
- Usar variables de entorno o archivos de configuración fuera del repo para valores por defecto.
- Limitar la edición de configuraciones críticas solo a usuarios con rol de administrador.
- Documentar en el código y en la ayuda de la app los riesgos de exponer credenciales.

## 3. Ejemplo de estructura sugerida en la app
- Panel de configuración con secciones: "Red y conexión", "Base de datos", "Notificaciones", etc.
- Cada sección debe tener campos editables, botones de "Probar conexión" y feedback visual (verde/rojo, ícono y texto).
- Botón de "Restaurar valores por defecto" solo visible para administradores.
- Tooltip en cada campo explicando el formato esperado y advertencias de seguridad.

## 4. Documentación para administradores de red
- Incluir en README y docs/ una tabla de configuraciones críticas, su ubicación y cómo editarlas de forma segura.
- Ejemplo:

| Configuración         | Ubicación en la app         | Archivo/Variable         | Notas de seguridad                  |
|----------------------|-----------------------------|--------------------------|-------------------------------------|
| IP del servidor SQL  | Configuración > Red         | config.py / .env         | No exponer fuera de red interna     |
| Puerto de conexión   | Configuración > Red         | config.py / .env         | Usar puertos no estándar si es posible |
| Usuario DB           | Configuración > Base de datos | config.py / .env       | Solo usuarios con permisos mínimos  |
| Contraseña DB        | Configuración > Base de datos | config.py / .env       | Nunca en texto plano fuera del campo|

- Recomendar cambiar credenciales periódicamente y auditar accesos.

## 5. Referencias cruzadas
- Ver `docs/estandares_seguridad.md` y `docs/estandares_feedback.md` para detalles de feedback visual y seguridad.
- Consultar `README.md` para la lista de configuraciones críticas y su documentación.
