# Historial de cambios visuales y de permisos

| Fecha        | Cambio                                                                                       |
|-------------|----------------------------------------------------------------------------------------------|
| 2025-05-27  | Unificación de headers de tablas: fondo #f8fafc, radio 4px, fuente 10px, sin negrita.        |
| 2025-05-27  | Migración de gestión de usuarios y permisos de Configuración a Usuarios.                      |
| 2025-05-27  | Refuerzo de permisos: solo admin puede modificar roles/permisos; feedback visual robusto.     |
| 2025-05-27  | Refuerzo de feedback visual en importación de inventario y gestión de usuarios.               |
| 2025-05-27  | Actualización de tests automáticos y documentación para reflejar nuevos estándares visuales.   |

---

# Estándares visuales y de estilos para la aplicación

## Política de estilos

- **Prohibido** el uso de `setStyleSheet` embebido en widgets/componentes, excepto para:
  - Aplicar el theme global (resources/qss/theme_light.qss o theme_dark.qss) a nivel de aplicación.
  - Personalización explícita de dialogs (ejemplo: QMessageBox, QDialog), debidamente documentada.
- **Todos los estilos visuales** (colores, bordes, feedback, etc.) deben centralizarse en los archivos QSS de theme global.
- **No existe** un QSS global adicional ni helpers que apliquen QSS embebido. Helpers solo pueden modificar tamaño de íconos, paddings, etc., pero nunca estilos visuales vía QSS embebido.
- Si algún widget requiere una excepción (por limitación de Qt), debe documentarse aquí y en el código.

## Archivos de theme
- `resources/qss/theme_light.qss`
- `resources/qss/theme_dark.qss`

## Ejemplo de excepción permitida
```python
# Solo permitido para dialogs personalizados:
dialog = QDialog()
dialog.setStyleSheet("background: #fff; border-radius: 12px;")
```

## Migración y auditoría
- Todos los módulos y widgets deben ser auditados para eliminar cualquier uso de setStyleSheet embebido.
- Si se detecta un uso, debe migrarse a QSS global y dejar comentario explicativo.

## Documentar excepciones
- Si un widget no soporta QSS global y requiere setStyleSheet, debe documentarse aquí:
  - [ ] (Ninguna excepción activa al 2024-06)

---

## Estándares visuales de la app

### Paleta de colores

- Fondo general: #fff9f3 (crema pastel muy claro)
- Azul pastel principal:rgb(79, 129, 238) (texto, íconos, botones principales)
- Celeste pastel: #e3f6fd (fondos de botones, headers, pestañas activas)
- Gris pastel: #e3e3e3 (bordes, líneas de tabla)
- Verde pastel: #d1f7e7 (éxito)
- Rojo pastel: #ffe5e5 (errores)
- Lila pastel: #f3eaff (hover)

### Tipografía y tamaños

- Fuente: Segoe UI, Roboto o similar sans-serif
- Tamaño base: 11px para secundarios, 12px para tablas y botones, 13-14px para títulos
- Peso: 500-600 para títulos y botones, 400-500 para textos normales

### Botones

- Solo ícono, sin texto visible (excepto justificación documentada)
- Bordes redondeados: 8px
- Sombra sutil
- Tamaño mínimo: 32x32px
- Usar helper `estilizar_boton_icono`

### Tablas

- Fondo: #fff9f3
- Headers: #f8fafc (mucho más claro que #e3f6fd), texto azul pastel (#2563eb), bordes redondeados 4px
- Celdas: altura máxima 25px
- Fuente: 10px en headers, 12px o menor en celdas
- Peso: normal (no negrita) en headers

> Desde 2025-05-27 todos los headers de tablas usan fondo #f8fafc, radio 4px, fuente 10px y no llevan negrita. Este estándar es obligatorio y se aplica por QSS global y refuerzo en cada vista.

### Layouts y diálogos

- Padding mínimo: 20px vertical, 24px horizontal
- Márgenes entre elementos: mínimo 16px
- Bordes redondeados: 8-12px

### Sidebar

- Fondo blanco
- Botones: borde gris pastel, activo azul pastel, fuente 12px

### QTabWidget

- Fondo crema, pestañas celeste pastel, activa con borde azul pastel
- Padding horizontal: 24px, vertical: 20px

### Prohibido

- Fondos oscuros, negro, gris oscuro
- Tamaños de fuente mayores a 14px en tablas/botones
- Sobrescribir estilos globales sin justificación

### Ejemplo de helper para botón

```python
from core.ui_components import estilizar_boton_icono
btn = QPushButton()
estilizar_boton_icono(btn)
```

---

Cualquier excepción debe estar documentada en el código y en este archivo.

---

## Estándar de parámetros para tests automáticos robustos (Inventario y App)

Todo test debe cumplir con estos parámetros para ser considerado robusto y profesional:

1. **Nombrado claro y descriptivo:**
   - Formato: `test_<funcionalidad>_<condición>_<resultado_esperado>`
   - Ejemplo: `test_exportar_excel_tabla_vacia_muestra_error`

1. **Estructura AAA (Arrange-Act-Assert):**
   - *Arrange*: Preparar entorno, mocks, datos y dependencias.
   - *Act*: Ejecutar la acción a testear.
   - *Assert*: Verificar el resultado esperado (feedback visual, datos, señales, etc).

1. **Mocking y aislamiento:**
   - Simular dependencias externas (DB, archivos, señales, red, etc) para aislar el test.
   - Usar `unittest.mock`, `pytest-mock` o fixtures según corresponda.

1. **Validación de feedback visual y accesibilidad:**
   - Comprobar que `QMessageBox`, `QLabel`, `QProgressDialog`, tooltips y headers visuales se muestran/cambian correctamente.
   - Verificar foco visible, contraste, tamaño de fuente >=12px, tooltips presentes y claros.

1. **Edge cases y errores:**
   - Incluir casos límite: tabla vacía, error de conexión, rutas inválidas, permisos insuficientes, archivo JSON corrupto, etc.
   - Verificar que la app no crashee y muestre feedback visual adecuado.

1. **Limpieza y restauración:**
   - Restaurar estado tras cada test (archivos, configs, mocks, base de datos temporal, etc).
   - Usar fixtures de setup/teardown o context managers.

1. **Documentación y claridad:**
   - Cada test debe tener un docstring breve explicando el objetivo y el porqué del caso probado.
   - Ejemplo:

```python
def test_exportar_excel_tabla_vacia_muestra_error(self):
    """Debe mostrar feedback de error si se intenta exportar una tabla vacía a Excel."""
```

1. **Cobertura y exhaustividad:**
   - Asegurar que cada flujo crítico y excepción visual está cubierto.
   - Validar señales emitidas, feedback visual, persistencia de configuración, accesibilidad y robustez.

1. **Independencia de datos reales:**
   - Usar datos simulados o temporales, nunca depender de datos reales o productivos.

1. **Validar señales y side effects:**
    - Comprobar que las señales se emiten correctamente y sólo cuando corresponde.
    - Verificar side effects en la UI y en la base de datos simulada.

1. **Visuales y estilos:**
    - Verificar estilos, tooltips y headers visuales según `docs/estandares_visuales.md`.
    - Validar que no haya overrides locales no justificados.

1. **Accesibilidad:**
    - Verificar tooltips y feedback accesible en todos los widgets interactivos.
    - Validar foco visible y contraste suficiente.

1. **Limpieza de recursos:**
    - Cerrar archivos, eliminar temporales y restaurar mocks tras cada test.

1. **Ejemplo de test robusto:**

```python
def test_exportar_excel_tabla_vacia_muestra_error(self):
    """Debe mostrar feedback de error si se intenta exportar una tabla vacía a Excel."""
    # Arrange
    ...
    # Act
    ...
    # Assert
    ...
```

Para cada test del checklist, seguir estos parámetros y actualizar el estado en este archivo.
Si un test no cumple con estos puntos, debe ser refactorizado o ampliado.

Documentar en el código y en este archivo cualquier excepción visual o lógica detectada durante los tests.

> FIN DE PARÁMETROS OBLIGATORIOS PARA TESTS ROBUSTOS

## Estándar de logo en LoginView

- El logo de la pantalla de inicio de sesión debe ser grande y visible (mínimo 500x500 px).
- Usar QLabel y QPixmap con escalado suave.
- Justificación: mejora la accesibilidad, refuerza la identidad visual y cumple con los requisitos de contraste y foco visual.
- Ejemplo de implementación:

```python
self.icono = QLabel()
pixmap = QPixmap("img/MPS_inicio_sesion.png")
self.icono.setPixmap(pixmap.scaled(500, 500, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
```

---

## [2025-05-26] Nota crítica sobre helpers de estilos y QSS en PyQt6

- Se detectó que helpers como `estilizar_boton_icono` y cualquier función que aplique QSS embebido pueden causar advertencias y bloquear la carga de la interfaz en PyQt6 si el QSS no es 100% compatible.
- Para evitar bloqueos globales:
  - Todo helper visual debe ser revisado y probado tras cada actualización de PyQt.
  - El uso de `setStyleSheet` embebido en helpers debe ser evitado o documentado como excepción.
  - Priorizar el uso de QSS global (archivos .qss) y helpers solo para tamaño, icono y accesibilidad, no para estilos visuales complejos.
  - Documentar cualquier excepción en este archivo y en el código fuente.
- Si aparecen advertencias como `Could not parse stylesheet of object ...`, revisar primero los helpers y QSS embebidos.

---

## Unificación de estilos visuales (mayo 2025)

A partir de mayo 2025, todos los estilos visuales deben centralizarse únicamente en dos archivos QSS globales:

- `themes/light.qss` (tema claro)
- `themes/dark.qss` (tema oscuro)

No se permite el uso de `setStyleSheet` directo en widgets individuales, salvo casos de refuerzo visual temporal documentado y justificado.

Eliminar y migrar todos los estilos embebidos en código a estos archivos QSS.
Esto simplifica el mantenimiento, asegura coherencia visual y facilita el cambio de tema en toda la app.

Ver este documento para detalles y excepciones justificadas.

Si encuentras estilos embebidos, migra su lógica visual a los QSS globales y elimina el `setStyleSheet` del código Python.

Para feedback visual, tooltips, bordes de error, etc., usar clases QSS y/o `objectName` para selectores específicos.

**Ejemplo de migración:**
Si un `label_feedback` usaba `setStyleSheet` para color y fondo, crear una clase QSS
`QLabel#label_feedback { ... }` en el QSS global y asignar `objectName` en el código.

Esta política aplica a todos los módulos: obras, usuarios, vidrios, pedidos, auditoría, producción, etc.

---

## Migración a QSS global y política de excepciones visuales (mayo 2025)

A partir de mayo 2025, todos los estilos visuales de la app se gestionan exclusivamente mediante los archivos QSS globales:
- `themes/light.qss` (tema claro)
- `themes/dark.qss` (tema oscuro)

### Proceso de migración
- Se eliminaron todos los usos activos de `setStyleSheet` con estilos visuales (especialmente `font-size`, colores, bordes, etc.) en los módulos principales.
- En este proceso, las líneas de código que aplicaban estilos embebidos fueron comentadas y se dejó constancia en el propio archivo fuente (ver `modules/contabilidad/view.py`).
- El feedback visual, tooltips, headers de tablas, botones y cualquier otro elemento visual relevante ahora se estilizan únicamente por QSS global.

### Justificación de líneas comentadas
- Las líneas comentadas con `setStyleSheet` en los módulos (especialmente en `ContabilidadView`) corresponden a estilos migrados a QSS global.
- No deben reactivarse salvo justificación documentada aquí y en el propio archivo fuente.
- Si los tests automáticos de estándares detectan falsos positivos por líneas comentadas, dejar constancia en este documento y en el archivo de la vista.

### Política de excepciones visuales
- Solo se permite el uso de `setStyleSheet` embebido en casos de refuerzo visual temporal, debidamente justificados y documentados aquí y en el código.
- Cualquier excepción debe indicar: motivo, alcance, y fecha de revisión.
- Actualmente no existen excepciones activas en los módulos principales.

### Validación y control
- Se revisó visualmente y por código que no queden estilos embebidos activos en métodos auxiliares ni diálogos personalizados.
- Los tests automáticos de estándares (`tests/test_estandares_modulos.py`) deben pasar sin errores. Si fallan por líneas comentadas, se considera falso positivo y se documenta aquí.

### Referencias
- Ver comentarios en `modules/contabilidad/view.py` para trazabilidad de la migración y justificación de líneas comentadas.
- Para detalles de feedback visual y accesibilidad, consultar también `docs/estandares_feedback.md`.

---

## [29/05/2025] Validación de migración a QSS global y falsos positivos en tests

- Se completó la migración de todos los estilos visuales a QSS global (`themes/light.qss` y `themes/dark.qss`).
- Todas las líneas de `setStyleSheet` con estilos visuales en los módulos principales han sido comentadas y justificadas en el código fuente y en este documento.
- No quedan estilos embebidos activos en métodos auxiliares ni diálogos personalizados.
- Los tests automáticos de estándares pueden arrojar falsos positivos por la presencia de líneas comentadas con `setStyleSheet`. Esto es esperado y está documentado aquí y en el propio archivo fuente (`modules/contabilidad/view.py`).
- Si un test de estándares falla únicamente por líneas comentadas y no por estilos activos, se considera falso positivo y no requiere acción adicional.
- Se recomienda a futuros desarrolladores mantener esta política y actualizar la documentación ante cualquier excepción visual.

---

## Estándares de permisos y feedback visual

### Permisos y roles

- El usuario admin (id_rol=1) debe tener acceso total a todos los módulos y a la gestión de roles/permisos.
- Solo el admin puede modificar roles y permisos. Ningún otro usuario puede editar los permisos del admin ni modificar el rol admin.
- Si un usuario no tiene acceso a ningún módulo, la UI debe mostrar un mensaje visual claro y solo permitir acceso a Configuración.
- La lógica de visibilidad de módulos y pestañas debe ser robusta y segura: nunca mostrar ni permitir acceso a módulos/pestañas no permitidos.
- El backend debe validar siempre los permisos, incluso si la UI los oculta.

### Feedback visual y estilos

- Usar siempre el QSS global de `themes/light.qss`. Está prohibido aplicar estilos embebidos con `setStyleSheet` en widgets individuales, salvo excepciones documentadas.
- Los mensajes de error, advertencia y éxito deben ser claros, accesibles y visibles en la UI (status bar o feedback global).
- Si ocurre un error de permisos, mostrar un mensaje visual inmediato y registrar el evento en auditoría.
- No debe haber advertencias QSS ni bloqueos visuales tras login. Si ocurre, documentar la causa y solución.

### Ejemplo de mensaje visual si no hay módulos permitidos

> "No tienes acceso a ningún módulo. Contacta al administrador para revisar tus permisos."

---

### Recomendaciones para desarrolladores

- Antes de modificar la gestión de permisos, revisa y ejecuta el script `scripts/bootstrap_roles_permisos.sql` en la base de datos `users` para asegurar que el admin tiene permisos totales.
- Documenta cualquier excepción visual o de permisos en este archivo y en el código afectado.
- Consulta siempre los estándares de seguridad y feedback visual en `docs/estandares_seguridad.md` y `docs/estandares_feedback.md`.

---

## Temas visuales (light/dark)

A partir de 2025-05-29, la app utiliza dos archivos QSS separados para los temas visuales:
- `resources/qss/theme_light.qss`: contiene solo reglas para modo claro.
- `resources/qss/theme_dark.qss`: contiene solo reglas para modo oscuro.

### Estructura y convenciones
- Cada archivo QSS define únicamente los estilos de su modo (no mezclar reglas de ambos temas).
- Los selectores y nombres de variables deben ser consistentes entre ambos archivos para facilitar el mantenimiento.
- El cambio de tema se realiza en tiempo real desde Configuración, usando el Theme Manager (`utils/theme_manager.py`).
- El tema por defecto se define en `core/config.py` como `DEFAULT_THEME`.

### Ejemplo de uso
```python
from utils.theme_manager import set_theme
set_theme(app, 'light')  # o 'dark'
```

### Ejemplo de estructura de QSS
- `theme_light.qss`:
  ```css
  QWidget { background: #fff9f3; color: #222; }
  QPushButton { background: #e3f6fd; color: #2563eb; }
  ...
  ```
- `theme_dark.qss`:
  ```css
  QWidget { background: #232b36; color: #f3f4f6; }
  QPushButton { background: #2563eb; color: #f3f4f6; }
  ...
  ```

### Convenciones
- No usar reglas globales ambiguas, siempre especificar selectores claros.
- Mantener la paridad de estilos entre ambos archivos para evitar inconsistencias visuales.
- Documentar cualquier excepción visual o selector especial en este archivo.

### Capturas de pantalla
- [ ] Agregar capturas de ambos temas en próximas versiones.

---

## Estado de cumplimiento y justificación de excepciones (actualizado al 30/05/2025)

- Todos los módulos principales migraron a QSS global (light/dark) y helpers de estilo centralizados.
- No existen estilos embebidos activos ni credenciales/cadenas de conexión hardcodeadas en código ejecutable.
- Ejemplos de cadenas de conexión solo se permiten en comentarios, con justificación explícita y advertencia de no uso real.
- Las excepciones visuales (por ejemplo, botones con texto, ausencia de feedback de carga en procesos instantáneos) están documentadas en el código fuente y justificadas con comentarios normalizados.
- Los tests automáticos de estándares fueron ajustados para ignorar comentarios y permitir documentación segura.
- Cualquier excepción visual o de feedback debe estar documentada en el código y, si es relevante, en este archivo.

### Ejemplo de justificación en código:
```python
# EXCEPCIÓN JUSTIFICADA: Este módulo no requiere feedback de carga adicional porque los procesos son instantáneos o no hay operaciones largas en la UI. Ver test_feedback_carga y docs/estandares_visuales.md.
# Ejemplo de cadena de conexión (solo documentación):
#   cadena_conexion = "server=SERVIDOR;database=DB;uid=USUARIO;pwd=CLAVE"  # ejemplo, no usar hardcodeado
```

---

Para más detalles sobre feedback visual y logging, ver también:
- [docs/estandares_feedback.md](estandares_feedback.md)
- [docs/estandares_logging.md](estandares_logging.md)

---

# Uso de QSS en la app: solo temas, nunca QSS global

- Está prohibido crear o mantener un QSS global (por ejemplo, stylesheet.qss o estilos compartidos fuera de los temas).
- Todos los estilos visuales deben definirse únicamente en los archivos de tema:
  - `resources/qss/theme_light.qss` (modo claro)
  - `resources/qss/theme_dark.qss` (modo oscuro)
- Cualquier personalización visual, color, tipografía, bordes, etc., debe agregarse en estos archivos.
- No se debe usar setStyleSheet embebido en widgets individuales, salvo en diálogos modales personalizados y solo si es estrictamente necesario.
- Si se requiere una excepción, debe justificarse y documentarse aquí.
- Si se detecta un nuevo QSS global, debe eliminarse y migrar los estilos a los archivos de tema.
- Esto asegura compatibilidad, coherencia visual y evita advertencias/errores en PyQt6.

---

# [2025-06-02] Migración completa de estilos embebidos en módulo Usuarios (login y vista principal) a QSS global (`theme_light.qss` y `theme_dark.qss`). Todas las líneas `setStyleSheet` han sido comentadas y justificadas en el código fuente. No existen excepciones activas. Ver comentarios en `modules/usuarios/login_view.py` y `modules/usuarios/view.py` para trazabilidad.

---

# [2025-06-02] Migración completa de estilos embebidos en módulo Pedidos a QSS global (`theme_light.qss` y `theme_dark.qss`). Todas las líneas `setStyleSheet` han sido comentadas y justificadas en el código fuente. No existen excepciones activas. Ver comentarios en `modules/pedidos/view.py` para trazabilidad.

---

# [2025-06-02] Migración completa de estilos embebidos en módulo Contabilidad a QSS global (`theme_light.qss` y `theme_dark.qss`). Todas las líneas `setStyleSheet` han sido comentadas y justificadas en el código fuente. No existen excepciones activas. Ver comentarios en `modules/contabilidad/view.py` para trazabilidad.

---

# [2025-06-02] Migración completa de estilos embebidos en módulo Herrajes a QSS global (`theme_light.qss` y `theme_dark.qss`). Todas las líneas `setStyleSheet` han sido eliminadas o migradas a uso de property y QSS. No existen excepciones activas. Ver comentarios en `modules/herrajes/view.py` y `modules/herrajes/controller.py` para trazabilidad.

---

# [2025-06-02] Migración completa de estilos embebidos en módulo Inventario a QSS global (`theme_light.qss` y `theme_dark.qss`). Todas las líneas `setStyleSheet` han sido eliminadas o migradas a uso de property y QSS. No existen excepciones activas. Ver comentarios en `modules/inventario/view.py` para trazabilidad.

---

# [2025-06-02] Migración completa de estilos embebidos en módulo Obras a QSS global (`theme_light.qss` y `theme_dark.qss`). Todas las líneas `setStyleSheet` han sido eliminadas o migradas a uso de property/objectName y QSS. No existen excepciones activas. Ver comentarios en `modules/obras/view.py` y `modules/obras/controller.py` para trazabilidad.

---

## Migración y cumplimiento de módulos (junio 2025)

| Módulo           | setStyleSheet eliminado | Estilos migrados a QSS | objectNames/properties | Documentación/trazabilidad |
|------------------|------------------------|------------------------|------------------------|----------------------------|
| Mantenimiento    | Sí                     | Sí                     | Sí                     | Ver comentarios en código y QSS |
| Notificaciones   | Sí                     | Sí                     | Sí                     | Ver comentarios en código y QSS |
| Vidrios          | N/A (no activos)       | Sí                     | Sí                     | Ver comentarios en código y QSS |
| Obras (cronograma, producción) | Sí | Sí | Sí | Ver comentarios en código y QSS |

- Se agregaron los objectNames: `cronograma_view`, `cronograma_label`, `boton_produccion`, `tabla_produccion`, `tarjeta_kanban` para centralizar estilos de los módulos de Obras.
- Todos los estilos visuales de estos módulos están ahora centralizados en los archivos QSS globales.

---

## Advertencia y buenas prácticas: robustez con objetos PyQt6

- **Nunca asumas que métodos como `scene.addText`, `scene.addWidget`, o cualquier método de PyQt6 que crea objetos gráficos retornan siempre un objeto válido.**
- Siempre valida que el objeto retornado no sea `None` antes de llamar a métodos como `setHtml`, `setPlainText`, `setPos`, `setDefaultTextColor`, etc.
- Ejemplo correcto:

```python
text = scene.addText("Ejemplo", font)
if text is not None:
    text.setPlainText("Texto seguro")
    text.setPos(10, 10)
```

- Lo mismo aplica para el uso de `painter` en métodos de dibujo: verifica que no sea `None` antes de llamar a métodos como `setBrush`, `setPen`, `drawRoundedRect`, etc.
- Los eventos de tipo `QGraphicsSceneHoverEvent` no tienen métodos como `globalPos` o `screenPos` en PyQt6. No intentes mostrar tooltips usando estos métodos en ese contexto.
- Si tienes dudas, revisa la documentación oficial de PyQt6 y consulta este archivo antes de implementar lógica gráfica.

> Esta advertencia se agregó tras detectar errores recurrentes de atributos en módulos gráficos. Cumplirla es obligatorio para evitar bugs difíciles de depurar.

---

## [2025-06-06] Nota sobre tests automáticos de feedback visual (QMessageBox)

En algunos entornos, los tests automáticos que mockean `QMessageBox.information` pueden fallar aunque el patch esté correcto. Si la UI muestra el feedback visual esperado, considerar el fallo del test como falso negativo. Ver detalles en `docs/estandares_feedback.md` y en el propio test.

---

## Unificación visual y UX: reglas obligatorias (2025-06)

### 1. Títulos de los módulos
- Usar siempre un QLabel con setObjectName estándar (ej: label_titulo, label_titulo_pedidos, label_titulo_usuarios, titulo_label_logistica).
- Color, tamaño, peso y fuente definidos solo en QSS global.
- Ubicación: siempre arriba a la izquierda del módulo, antes de la tabla principal.
- Prohibido setStyleSheet embebido para títulos.

### 2. Botones principales y secundarios
- Usar QPushButton con setObjectName específico (ej: boton_agregar, boton_nuevo_compras, etc.).
- Color de fondo, borde, radio, fuente y sombra definidos en QSS global.
- Animación visual de click y hover solo por QSS.
- Bordes redondeados iguales en todos los botones.
- Ubicación: siempre arriba a la derecha de la tabla principal, en un QHBoxLayout junto al título.
- Prohibido setStyleSheet embebido para botones.

### 3. Feedback visual y errores
- Usar QLabel con setObjectName("label_feedback") para feedback visual.
- Colores y estilos de feedback (info, éxito, error, advertencia) definidos en QSS global.
- Ubicación: debajo del título o arriba de la tabla.
- Prohibido setStyleSheet embebido para feedback.

### 4. Tablas y headers
- Todas las tablas deben tener el mismo estilo visual (color de fondo, bordes, radio, fuente, selección, etc.) definido en QSS global.
- Todos los headers de tabla deben tener el mismo formato y color.
- Usar setObjectName en cada tabla y header para aplicar el QSS global.
- Prohibido setStyleSheet embebido para tablas y headers.

### 5. Accesibilidad y tooltips
- Todos los botones y campos deben tener setToolTip y/o setAccessibleName descriptivo.
- Orden de tabulación lógico y consistente.
- Documentar en este archivo cualquier excepción.

### 6. Bordes, paddings y márgenes
- Unificar bordes, paddings y márgenes en todos los componentes principales (títulos, botones, tablas, feedback) solo por QSS global.

### 7. Ubicación de elementos
- Título: arriba a la izquierda.
- Botones principales: arriba a la derecha.
- Feedback: debajo del título o arriba de la tabla.
- Tabla: siempre debajo del título y botones.

### 8. Excepciones y justificaciones
- Documentar aquí cualquier excepción visual o justificación de estilos distintos.
- [ ] (Ninguna excepción activa al 2025-06-09)

---
