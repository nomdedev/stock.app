# Buenas prácticas para la gestión de configuraciones críticas y variables sensibles en la app

## 1. Centralización de la configuración
- Todas las variables críticas (servidor, usuario, contraseña, base de datos, IP, timeout, etc.) deben estar en un único archivo de configuración: `.env` (preferido para credenciales) o `config.json` (más visual y flexible).
- El archivo debe estar fuera del control de versiones (agregar `.env` a `.gitignore`).
- Proveer un `.env.example` o `config.example.json` para referencia.

## 2. Utilidad para leer y escribir configuración
- Crear un módulo (por ejemplo, `core/config_manager.py`) que permita:
  - Leer variables desde `.env` o `config.json`.
  - Actualizar valores y guardar cambios de forma segura.
  - Validar los datos antes de guardar (por ejemplo, formato de IP, no dejar campos vacíos, etc.).

## 3. Interfaz gráfica para configuración
- Agregar una sección en la UI (por ejemplo, en `ConfiguracionView`) con un formulario editable para:
  - Servidor/IP
  - Usuario
  - Contraseña (campo tipo password, con opción de mostrar/ocultar)
  - Base de datos
  - Timeout
  - Otros parámetros relevantes
- Mostrar los valores actuales y permitir editarlos.
- Al guardar, validar y actualizar el archivo de configuración.
- Permitir probar la conexión antes de guardar definitivamente.

## 4. Seguridad y experiencia de usuario
- Nunca mostrar la contraseña en texto plano por defecto.
- Permitir mostrar/ocultar la contraseña solo bajo acción explícita del usuario.
- No guardar la contraseña en logs ni mostrarla en mensajes de error.
- Si la conexión falla, mostrar un mensaje claro y permitir reintentar.
- Registrar en logs solo los cambios de configuración, nunca los valores sensibles.

## 5. Recarga dinámica y robustez
- Tras guardar cambios, recargar la configuración en memoria y reconectar a la base de datos.
- Si la reconexión falla, revertir los cambios o permitir editar de nuevo.
- Documentar en la UI la última IP/servidor usado y el estado de la sesión/conexión.

## 6. Ampliaciones recomendadas
- Permitir perfiles de configuración (ej: desarrollo, producción, testing).
- Permitir exportar/importar la configuración para facilitar despliegues.
- Agregar logs de auditoría para cambios críticos de configuración.

## 7. Documentación y soporte
- Mantener este documento actualizado y referenciarlo desde el código y la UI.
- Incluir instrucciones paso a paso para admins sobre cómo editar y validar la configuración.

---

## Ejemplo de flujo recomendado
1. El admin abre la sección de Configuración.
2. Visualiza y edita los campos críticos.
3. Puede mostrar/ocultar la contraseña.
4. Prueba la conexión.
5. Si es exitosa, guarda y recarga la app.
6. Si falla, recibe feedback y puede corregir.

---

**Referencia técnica:**
- `.env` gestionado con `python-dotenv`.
- Validaciones y helpers en `core/config_manager.py`.
- UI en `modules/configuracion/view.py`.
- Documentar cualquier excepción o ampliación en este archivo.

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

---

# Guía paso a paso para la gestión de configuración crítica desde la app (para administradores)

## 1. Acceso a la pantalla de configuración
- Ingresa a la aplicación con un usuario con permisos de administrador.
- Dirígete al módulo de configuración (menú principal o barra lateral).
- Accede a la sección “Configuración de conexión” o similar.

## 2. Visualización y edición de variables críticas
- Se muestran los campos editables para:
  - Servidor de base de datos (DB_HOST)
  - Usuario (DB_USER)
  - Contraseña (DB_PASSWORD) — con opción de mostrar/ocultar
  - Nombre de base de datos (DB_NAME)
  - Timeout de conexión (DB_TIMEOUT)
- Los valores actuales se cargan automáticamente desde el archivo `.env` usando `core/config_manager.py`.

## 3. Edición segura
- Modifica los valores según sea necesario.
- La contraseña puede mostrarse temporalmente para evitar errores de tipeo.
- Al editar, la interfaz valida automáticamente los campos (formato, vacíos, etc.).

## 4. Prueba de conexión
- Antes de guardar, utiliza el botón “Probar conexión”.
- El sistema intentará conectarse con los datos ingresados, sin guardar aún los cambios.
- Si la conexión es exitosa, recibirás un mensaje de éxito.
- Si falla, se mostrará el error detallado (sin exponer la contraseña).

## 5. Guardado y auditoría
- Si la prueba es exitosa, presiona “Guardar cambios”.
- El sistema:
  - Vuelve a validar los datos.
  - Escribe los nuevos valores en el archivo `.env` de forma segura (usando `config_manager.py`).
  - Registra el cambio en el log de auditoría (usuario, fecha, variables modificadas, sin exponer valores sensibles).
- Solo usuarios con permisos de admin pueden guardar cambios.

## 6. Recarga y reconexión dinámica
- Tras guardar, la app:
  - Recarga la configuración en memoria.
  - Intenta reconectar automáticamente a la base de datos con los nuevos datos.
  - Si la reconexión es exitosa, muestra un mensaje de éxito.
  - Si falla, muestra un error y permite revertir o reintentar.
- No es necesario reiniciar la app, salvo que el cambio afecte otros módulos no recargables dinámicamente (esto se indicará en la UI).

## 7. Validación y feedback
- Todos los campos tienen validación en tiempo real y feedback visual (colores, íconos, mensajes).
- Los errores se muestran de forma clara y accesible.
- El log de auditoría registra cada intento de cambio, éxito o error.

## 8. Buenas prácticas y seguridad
- Nunca compartas el archivo `.env` fuera del entorno seguro.
- No expongas la contraseña en logs, pantallas o mensajes.
- Usa siempre la función de “Probar conexión” antes de guardar.
- Revisa el log de auditoría ante cualquier incidente.

## 9. Documentación y ayuda
- En la pantalla de configuración hay enlaces a la documentación interna (`docs/buenas_practicas_configuraciones_criticas.md`).
- Ante dudas, consulta la documentación o contacta al responsable de IT.

---

## Lógica técnica de recarga/reconexión

1. Al guardar cambios:
   - Se llama a `config_manager.save_env()` para persistir los nuevos valores.
   - Se ejecuta `config.reload()` para recargar variables en memoria.
   - Se llama a la función de reconexión de la base de datos (`database.reconnect()` o similar).
   - Se muestra feedback visual del resultado.

2. Si la reconexión falla:
   - Se permite reintentar o restaurar la configuración anterior.
   - El error se registra en el log de auditoría.

---

## Guardado seguro y recarga dinámica de la configuración de conexión

- La edición de IP, usuario, contraseña, base y timeout se realiza desde la UI (Configuración > Base de Datos).
- Al guardar, la app valida y prueba la conexión. Si es exitosa, sobrescribe el archivo `config/privado/.env` (nunca el código fuente).
- La recarga es inmediata: la app usa la nueva configuración sin reiniciar.
- Todo cambio queda registrado en auditoría.
- Solo usuarios administradores pueden modificar estos valores.
- Si usas IP, asegúrate de que SQL Server acepte conexiones remotas y el puerto esté abierto.

> Ver README y este documento para ejemplos y advertencias.

---

> Esta guía debe mantenerse actualizada ante cualquier cambio en la lógica de configuración o UI. Para ampliaciones (perfiles, export/import, historial, permisos granulares), ver la hoja de ruta técnica y sugerencias en este mismo documento.
