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

# Checklist de Seguridad para Login, Tests y Protección de Información Sensible

## 1. Seguridad en archivos y control de versiones

- [ ] Nunca subir archivos de tests automáticos de login o autenticación a repositorios públicos.
- [ ] Agregar los archivos de tests y configuración sensible a `.gitignore`.
- [ ] No subir archivos con credenciales, rutas de base de datos, claves API ni dumps de datos reales.
- [ ] Documentar en el README y en `docs/errores_frecuentes_login.md` esta política.

## 2. Seguridad en el código de login y feedback

- [ ] No mostrar mensajes de error detallados al usuario final (solo "Usuario o contraseña incorrectos").
- [ ] No loggear contraseñas ni datos sensibles en archivos de log.
- [ ] Usar hash seguro para contraseñas (ejemplo: SHA-256 o superior, nunca texto plano).
- [ ] Validar siempre el feedback visual y de error en producción.
- [ ] No dejar usuarios de prueba o contraseñas por defecto en producción.

## 3. Seguridad en la base de datos

- [ ] No exponer la estructura de la base de datos ni los scripts de creación en repositorios públicos si contienen información sensible.
- [ ] Usar roles y permisos mínimos necesarios para las cuentas de conexión.
- [ ] No dejar datos de usuarios reales en entornos de desarrollo o pruebas.

## 4. Seguridad en logs y auditoría

- [ ] No almacenar contraseñas ni tokens en logs.
- [ ] Registrar solo acciones relevantes y necesarias para auditoría.
- [ ] Proteger los archivos de logs con permisos adecuados.

## 5. Seguridad en dependencias y entorno

- [ ] Mantener actualizadas las dependencias críticas y revisar vulnerabilidades conocidas.
- [ ] No dejar scripts de instalación automática de dependencias accesibles en producción.
- [ ] Documentar el procedimiento de instalación y actualización segura.

## 6. Seguridad visual y accesibilidad

- [ ] No dejar advertencias visuales (como box-shadow no soportado) en producción.
- [ ] Validar contraste, feedback y accesibilidad en todos los formularios de login.

## 7. Seguridad en feedback y errores

- [ ] No mostrar trazas de error ni detalles internos al usuario final.
- [ ] Documentar y centralizar el manejo de errores críticos.

---

# Checklist de Seguridad y Privacidad - Proyecto StockApp

## 1. Seguridad de código fuente y repositorio

- [ ] Nunca subir archivos de tests automáticos con usuarios reales, contraseñas, lógica de autenticación o datos sensibles.
- [ ] Agregar los archivos de tests y configuración sensible a `.gitignore`.
- [ ] No subir archivos de configuración con credenciales, rutas de base de datos, claves API ni dumps de base de datos.
- [ ] Documentar en el README y en `docs/errores_frecuentes_login.md` que los tests de login y archivos de configuración nunca deben subirse a repositorios públicos.

## 2. Seguridad en el manejo de usuarios y contraseñas

- [ ] Las contraseñas deben almacenarse siempre con hash seguro (ej: SHA-256 o superior, nunca texto plano).
- [ ] Nunca mostrar contraseñas en logs, feedback visual ni mensajes de error.
- [ ] Validar siempre el feedback visual de error en login y documentar cualquier excepción.
- [ ] No dejar usuarios de prueba o contraseñas débiles en producción.

## 3. Seguridad en dependencias y entorno

- [ ] Verificar y actualizar dependencias críticas antes de cada despliegue.
- [ ] No dejar dependencias innecesarias o vulnerables en requirements.txt.
- [ ] Documentar y automatizar la instalación de dependencias críticas y secundarias.

## 4. Seguridad visual y feedback

- [ ] Eliminar cualquier referencia a `box-shadow` en QSS (no soportado por Qt, genera warnings y puede ocultar errores visuales).
- [ ] Usar siempre `QGraphicsDropShadowEffect` en Python para sombras visuales.
- [ ] Centralizar estilos visuales en QSS global o helpers, nunca hardcodear en cada widget.
- [ ] Validar contraste y accesibilidad en todos los campos de entrada y feedback visual.

## 5. Seguridad en base de datos y permisos

- [ ] Documentar y crear siempre la tabla `permisos_modulos` junto con la tabla `usuarios` en instalaciones nuevas.
- [ ] No dejar datos de prueba, usuarios temporales ni permisos excesivos en producción.
- [ ] Validar que los roles y permisos sean los mínimos necesarios para cada usuario.

## 6. Seguridad en logs y auditoría

- [ ] No registrar contraseñas ni datos sensibles en logs.
- [ ] Documentar y auditar todas las acciones críticas en logs de usuario.
- [ ] Revisar periódicamente los logs de auditoría y accesos.

## 7. Seguridad en manejo de errores

- [ ] No mostrar trazas de error ni detalles internos al usuario final.
- [ ] Mostrar mensajes de error claros pero sin información sensible.
- [ ] Documentar cualquier excepción visual o lógica en los archivos de estándares (`docs/estandares_visuales.md`, `docs/errores_frecuentes_login.md`).

## 8. Seguridad en ejecución y despliegue

- [ ] No dejar rutas absolutas, credenciales ni configuraciones de entorno hardcodeadas.
- [ ] Usar variables de entorno para credenciales y rutas sensibles.
- [ ] Validar que el entorno de producción no exponga puertos, logs ni archivos innecesarios.

---

**Actualizado:** 25/05/2025
