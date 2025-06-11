# ---
# PENDIENTES DETALLADOS Y PRÓXIMOS PASOS (actualizado al 10/06/2025)
#
# - [ ] Integrar el flujo de gestión de obras y pedidos con los modelos y base de datos reales (requiere entorno y .env configurado). Validar que el test de integración dummy se replica correctamente con datos reales y documentar diferencias o bugs.
#   - Test de integración real documentado y marcado en tests/obras/test_obras_controller_integracion.py. Instrucciones de ejecución manual incluidas en el propio archivo.
#   - ADVERTENCIA: No ejecutar en CI ni en entornos productivos. Solo para QA manual y validación de integración.
#   - Actualizar este checklist y test_results/ tras cada ejecución real.
# - [ ] Profundizar la trazabilidad y feedback visual en la UI: mejorar mensajes, tooltips, accesibilidad y feedback en cada módulo. Validar que todos los estados y errores relevantes se reflejan visualmente y en logs/auditoría.
# - [ ] Actualizar y mantener los checklists tras cada mejora, bugfix o refactor. Revisar y marcar ítems en los archivos de checklists por módulo. Documentar excepciones o cambios de estándar.
# - [x] Refactorizar y aislar cualquier test unitario que aún dependa de la base de datos/configuración (revisar módulos menos críticos). Convertir a auto-contenidos usando dummies/mocks y documentar si requiere entorno real.
#   - [10/06/2025] Revisión completa: todos los tests unitarios de Inventario, Herrajes, Logística, Usuarios, Mantenimiento, Configuración, Compras y Contabilidad usan mocks/dummies y NO dependen de base real ni .env. Cumplen el estándar de aislamiento y auto-contenido.
# - [x] Marcar y documentar claramente los tests de integración real: indicar en el nombre y docstring que requieren entorno y .env, y agregar instrucciones para habilitarlos y ejecutarlos manualmente.
# - [x] Actualizar README y documentación de QA: incluir la política de tests, ejemplos y cómo ejecutar cada tipo de test. Asegurar onboarding rápido para nuevos integrantes.
#   - [10/06/2025] README principal actualizado: incluye política de tests, ejemplos, pasos de ejecución y onboarding rápido. Ver sección 'POLÍTICA DE TESTS Y QA' en README.md.
# - [x] Documentar cualquier bug, mejora o hallazgo adicional tras nuevas iteraciones, registrando en este archivo y en los logs de test.
#   - [10/06/2025] No se detectan bugs críticos ni hallazgos pendientes tras la última iteración. Todas las mejoras y edge cases documentados en los checklists y logs de test. Mantener este registro actualizado tras cada nueva iteración.
# ---

# ---
# [10/06/2025] RESUMEN DE AVANCE Y PENDIENTES ACTUALIZADO
#
# ✅ Ya realizado:
# - Checklists de UI/UX, botones, formularios y mejoras unificados y actualizados por módulo.
# - Flujo completo de gestión de obras y pedidos: checklist detallado y validado con test de integración dummy (tests/test_flujo_gestion_obras_pedidos_dummy.py).
# - Tests unitarios refactorizados para ser auto-contenidos (Inventario, Contabilidad, Obras headers), usando solo dummies/mocks, sin dependencia de base de datos ni entorno.
# - Tests de integración real documentados y aislados (requieren entorno y .env).
# - Documentación de política de tests y ejemplos claros en este archivo y en los tests.
# - Feedback visual, accesibilidad y logging validados y documentados en todos los módulos principales.
# - Cobertura de edge cases validada por tests automáticos y documentada.
# - Todos los tests auto-contenidos pasan correctamente (ver archivos en test_results/).
#
# ⏳ Pendiente / Próximos pasos:
# - Integrar el flujo de gestión de obras y pedidos con los modelos y base de datos reales (cuando el entorno esté disponible).
# - Profundizar la trazabilidad y feedback visual en la UI (mejoras de experiencia y accesibilidad).
# - Actualizar y mantener los checklists tras cada mejora, bugfix o refactor.
# - Refactorizar y aislar cualquier test unitario que aún dependa de la base de datos/configuración (revisar módulos menos críticos).
# - Marcar y documentar claramente los tests de integración real (y cómo habilitarlos).
# - Actualizar README y documentación de QA con la política de tests y ejemplos.
# - Documentar cualquier bug, mejora o hallazgo adicional tras nuevas iteraciones.
#
# ---

# Estándares, Checklists y Documentación Unificada

Este documento consolida los principales estándares, checklists, pendientes y decisiones técnicas del proyecto. Úsalo como referencia central para desarrollo, QA y auditoría.

---

## Índice
1. [Estándares Visuales y de UI/UX](#estandares-visuales-y-de-uiux)
2. [Estándares de Feedback](#estandares-de-feedback)
3. [Estándares de Logging](#estandares-de-logging)
4. [Estándares de Seguridad](#estandares-de-seguridad)
5. [Estándares de Auditoría](#estandares-de-auditoria)
6. [Checklists de UI/UX y Funcionalidad](#checklists-de-uiux-y-funcionalidad)
7. [Checklists de Botones e Iconos](#checklists-de-botones-e-iconos)
8. [Checklists de Formularios y Acciones](#checklists-de-formularios-y-acciones)
9. [Checklists de Mejoras por Módulo](#checklists-de-mejoras-por-modulo)
10. [Pendientes y Tareas Críticas](#pendientes-y-tareas-criticas)
11. [Decisiones Técnicas y Justificaciones](#decisiones-tecnicas-y-justificaciones)

---

## Estándares Visuales y de UI/UX

- Uso exclusivo de QSS global para estilos visuales.
- Prohibido setStyleSheet embebido salvo excepciones documentadas.
- Bordes redondeados, tipografía moderna, colores pastel y accesibilidad reforzada.
- Ver detalles completos en `docs/estandares_visuales.md`.

## Estándares de Feedback

- Feedback visual inmediato y consistente en todas las acciones.
- Colores y emojis según tipo: éxito, error, advertencia, info.
- Prohibido hardcodear estilos de feedback; usar QSS global.
- Ver detalles y ejemplos en `docs/estandares_feedback.md`.

## Estándares de Logging

- Uso obligatorio del logger central (`core/logger.py`).
- Logs en texto y JSON, con rotación y contexto completo.
- Decoradores de auditoría para registrar acciones.
- Ver detalles y ejemplos en `docs/estandares_logging.md`.

## Estándares de Seguridad

- Nunca exponer credenciales ni datos sensibles en código ni README.
- Uso de variables de entorno y archivos `.env` (no subir `.env` real).
- Prohibido hardcodear rutas, usuarios o contraseñas.
- Checklist de seguridad para login y tests.
- Ver detalles en `docs/estandares_seguridad.md`.

## Estándares de Auditoría

- Registro obligatorio de toda acción relevante (alta, edición, eliminación, exportación, login, etc.).
- Uso de decoradores y logs de auditoría con usuario, módulo, acción, detalles y estado.
- Transacciones robustas y logs en cada intento.
- Ver ejemplos y detalles en `docs/estandares_auditoria.md`.

---

## Checklists de UI/UX y Funcionalidad

- Unificación de headers de tablas, botones, feedback y accesibilidad en todos los módulos.
- Uso de helpers para estilizar botones y centralizar feedback.
- Accesibilidad: tooltips, accessibleName, orden de tabulación, atajos de teclado.
- Ver checklist completo en `docs/checklist_mejoras_ui_general.md` y `docs/checklist_mejoras_uiux_por_modulo.md`.

## Checklists de Botones e Iconos

- Todos los botones principales y secundarios deben tener ícono SVG/PNG estándar.
- Documentar cada botón en `checklist_botones_iconos.txt`.
- Confirmar feedback modal, accesibilidad y estilo visual en `checklist_botones_accion.txt`.

## Checklists de Formularios y Acciones

- Formularios de alta, edición, eliminación y acciones principales validados por módulo.
- Feedback robusto, accesibilidad y logging/auditoría en cada acción.
- Ver checklist detallado en `checklist_formularios_botones_ui.txt`.

## Checklists de Mejoras por Módulo

- Mejoras y pendientes específicos para cada módulo (Obras, Inventario, Herrajes, etc.).
- Ver detalles y prioridades en `checklist_mejoras_uiux_por_modulo.md` y `checklist_mejoras_herrajes.md`.

## Pendientes y Tareas Críticas

- Tareas técnicas, features y tests por implementar.
- Pendientes críticos por módulo y reglas de robustez.
- Ver detalles en `cosas por hacer.txt` y `pendientes_tests_y_controladores.md`.

## Decisiones Técnicas y Justificaciones

- Decisiones clave de arquitectura, inicialización, modularidad y feedback.
- Justificaciones para cada estándar y flujo en main.py.
- Ver detalles en `decisiones_main.md`.

---

# ANEXO: Checklists completos de UI/UX, Botones, Formularios y Mejoras

## Checklist de botones principales de acción (QPushButton)

[docs/checklists/checklist_botones_accion.txt]

```
# Checklist de botones principales de acción (QPushButton) - ERP/Inventario
| Módulo         | Botón/Acción                | Confirmación | Feedback modal | Estilo visual | Accesibilidad | Estado    | Notas |
|---------------|-----------------------------|--------------|---------------|---------------|---------------|-----------|-------|
| Inventario    | Exportar a Excel            | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Inventario    | Reservar perfil/material      | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  | Modal robusto por fila. Bloqueo de stock negativo validado por tests edge cases (10/06/2025) |
| Herrajes      | Exportar a Excel            | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Vidrios       | Exportar a Excel            | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Contabilidad  | Exportar a Excel (Balance)  | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Contabilidad  | Exportar a Excel (Pagos)    | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Contabilidad  | Exportar a Excel (Recibos)  | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Logística     | Exportar a Excel            | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Logística     | Editar envío                | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  | Modal robusto, feedback, accesibilidad, cierre solo en éxito, logging/auditoría, tests validados (08/06/2025) |
| Logística     | Eliminar envío              | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  | Modal robusto, confirmación accesible, feedback visual, cierre solo en éxito, logging/auditoría, tests validados (08/06/2025) |
| Logística     | Ver Detalle envío           | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Configuración | Importar/Exportar           |              |               |               |               | PENDIENTE |      |
| Obras         | Editar obra                  | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Obras         | Eliminar obra                | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Obras         | Ver Detalle obra             | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  |      |
| Auditoría     | Filtrar Auditoría             | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  | Modal robusto, feedback accesible, tooltips, cierre solo en éxito, integración controller, logging/auditoría, refresco de tabla, validación visual/backend, cobertura de tests (08/06/2025) |
| Auditoría     | Exportar a Excel              | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  | Modal robusto, confirmación accesible, feedback visual, tooltips, cierre solo en éxito, logging/auditoría, refresco de tabla, validación visual/backend, integración controller, cobertura de tests (08/06/2025) |
| Usuarios       | Todos los botones y formularios principales (crear, editar, eliminar, editar permisos, feedback, columnas) | ✔️           | ✔️            | ✔️            | ✔️            | COMPLETO  | Robustez contra None/atributo, validación de tipos, feedback visual, edge cases documentados. Cumple el estándar de aislamiento y auto-contenido.
# ...agregar más según módulos y botones principales...
```

## Checklist de botones con y sin ícono SVG/PNG

[docs/checklists/checklist_botones_iconos.txt]

```
# Checklist de botones con y sin ícono SVG/PNG
# Actualizado: 08/06/2025

## Formato:
# [X] = Tiene ícono SVG/PNG correcto
# [ ] = Falta ícono SVG/PNG o no es el formato estándar
# (ruta o nombre del botón) - (ícono asignado o "FALTA") - (descripción de la acción)

# ...ver archivo completo para detalles por módulo...
```

## Checklist de formularios, botones y UI por módulo

[docs/checklists/checklist_formularios_botones_ui.txt]

```
# CHECKLIST DE FORMULARIOS, BOTONES, FUNCIONALIDADES Y UI POR MÓDULO (ERP/Inventario)

## 1. MÓDULO OBRAS
| Elemento                | Estado     | Incluye campos/acciones | UI/UX estándar | Backend/Controller | Feedback robusto | Auditoría | Notas |
|-------------------------|------------|------------------------|----------------|--------------------|------------------|-----------|-------|
| Formulario Alta de Obra | COMPLETO   | Nombre, Cliente, Fechas, Guardar/Cancelar | Modal, bordes redondeados, tooltips, feedback campo, botones accesibles y robustos | ObrasController.alta_obra | ✔️ | ✔️ | Validación visual y backend, botones UI/UX unificados (07/06/2025) |
| ...ver archivo completo para todos los módulos y tests...
```

## Checklist de mejoras UI/UX por módulo

[docs/checklists/checklist_mejoras_uiux_por_modulo.md]

```
# Checklist de Unificación Visual y UX por Módulo

| Módulo      | Título de módulo | Headers de tabla | Botones (sombra/color) | Feedback visual | Accesibilidad/tooltips | Documentación QSS | Bordes/Paddings/Márgenes |
|-------------|------------------|------------------|------------------------|-----------------|-----------------------|-------------------|--------------------------|
| Obras       | ✅ (setObjectName, layout y QSS global OK) | ✅ | ✅ (sombra, color, ubicación, accesibilidad) | ✅ | ✅ (tooltips y accesibilidad) | ✅ | ✅ (bordes, paddings, márgenes) |
| ...ver archivo completo para detalles y pendientes por módulo...
```

## Checklist de mejoras generales de UI/UX

[docs/checklists/checklist_mejoras_ui_general.md]

```
# Checklist de Mejoras Generales de UI/UX

- Unificación de tablas, botones, feedback y accesibilidad en todos los módulos.
- Uso de helpers para estilizar botones y centralizar feedback.
- Accesibilidad: tooltips, accessibleName, orden de tabulación, atajos de teclado.
- ...ver archivo completo para detalles y puntos de mejora...
```

## Checklist de mejoras UX/UI para Herrajes

[docs/checklists/checklist_mejoras_herrajes.md]

```
# Checklist de Mejoras UX/UI para el módulo Herrajes

- Feedback visual destacado, accesibilidad, acciones rápidas, filtros avanzados, exportaciones, usabilidad, historial y notificaciones.
- ...ver archivo completo para detalles y pendientes...
```

---

# Checklist detallado: Flujo de gestión de obras y pedidos (integración completa)

**Última actualización: 10/06/2025**

Este checklist documenta el flujo completo de gestión de obras y pedidos, cubriendo la integración entre módulos (Obras, Inventario, Vidrios, Herrajes, Contabilidad, Logística) y asegurando feedback visual, auditoría, edge cases y trazabilidad. Se utiliza como referencia para QA, automatización y auditoría.

---

## 1. Visualización y selección de obra
- [x] Listar todas las obras cargadas (mínimo 3 obras de prueba)
- [x] Acceso al detalle de cada obra (modal o vista dedicada)
- [x] Visualización de pedidos asociados y estado general
- [x] Feedback visual y logging de acceso

## 2. Solicitud y reserva de materiales
- [x] Solicitar materiales desde la obra (botón/acción)
- [x] Validación de stock en Inventario (bloqueo si stock negativo)
- [x] Feedback visual inmediato (éxito/error)
- [x] Registro en auditoría de cada intento/reserva
- [x] Edge case: intento de reservar más de lo disponible (debe bloquear y auditar)

## 3. Asociación de pedidos a obra
- [x] Crear pedido y asociar a obra seleccionada
- [x] Reflejar pedido en módulos de Vidrios y Herrajes si corresponde
- [x] Feedback visual y registro en auditoría
- [x] Edge case: pedido duplicado o inconsistente (debe bloquear y auditar)

## 4. Reflejo en módulos de Vidrios y Herrajes
- [x] Actualización automática de requerimientos de vidrios/herrajes según pedido
- [x] Validación de stock y reserva en cada módulo
- [x] Feedback visual y logging/auditoría
- [x] Edge case: falta de stock en vidrios/herrajes (debe bloquear y auditar)

## 5. Registro y control de pagos (Contabilidad)
- [x] Generar registro de pago asociado al pedido/obra
- [x] Validación de monto, estado y feedback visual
- [x] Registro en auditoría y logging contable
- [x] Edge case: pago duplicado o monto inconsistente (debe bloquear y auditar)

## 6. Integración logística (envíos, entregas)
- [x] Generar envío/logística para el pedido
- [x] Validación de datos de envío y feedback visual
- [x] Registro en auditoría y logging de logística
- [x] Edge case: datos incompletos o envío fallido (debe bloquear y auditar)

## 7. Validación cruzada y feedback
- [x] Validar que cada acción se refleje en todos los módulos relacionados
- [x] Feedback visual consistente en cada paso
- [x] Auditoría completa de cada acción (usuario, fecha, módulo, estado)
- [x] Edge cases documentados y cubiertos por tests automáticos

## 8. Automatización y tests de integración
- [x] Script/test de integración que recorra el flujo completo para las tres obras
- [x] Validación automática de resultados esperados y feedback
- [x] Registro de resultados y observaciones en este archivo y en logs de test

---

**Observaciones:**
- Cada paso debe estar cubierto por feedback visual y registro en auditoría.
- Los edge cases deben estar validados por tests automáticos y documentados.
- El script/test de integración debe ejecutarse tras cada cambio relevante.
- Actualizar este checklist tras cada mejora, bugfix o refactor en el flujo.

---

**Nota:** Para ver el detalle completo de cada checklist, consulta los archivos originales en `docs/checklists/`. Actualiza este anexo tras cada mejora o refactor importante.

---

**Convención:**
- Actualiza este archivo tras cada mejora, refactor o cambio de estándar.
- Marca los ítems completados en los checklists y documenta cualquier excepción en los archivos fuente y aquí.
- Usa los enlaces a los archivos originales para detalles y trazabilidad.

Última actualización: 10 de junio de 2025

# ---
# [10/06/2025] Resultado de automatización de flujo completo de gestión de obras y pedidos
#
# Se implementó y ejecutó exitosamente un test de integración aislado (tests/test_flujo_gestion_obras_pedidos_dummy.py)
# que valida el checklist completo de gestión de obras y pedidos para 3 obras dummy, cubriendo:
# - Visualización y alta de obras
# - Solicitud y reserva de materiales (con edge cases de stock)
# - Asociación de pedidos
# - Reflejo en módulos de vidrios y herrajes (con edge cases de stock)
# - Registro de pagos (con edge case de monto inválido)
# - Generación de logística/envío (con edge case de datos incompletos)
# - Feedback y validación de resultados esperados
#
# El test pasó correctamente, validando la robustez del flujo y la cobertura de edge cases.
#
# Próximos pasos sugeridos:
# - Integrar este flujo con los modelos reales y la base de datos (cuando el entorno esté disponible)
# - Profundizar la trazabilidad y feedback visual en la UI
# - Documentar cualquier bug, mejora o hallazgo adicional tras nuevas iteraciones
#
# Archivo de referencia del test: tests/test_flujo_gestion_obras_pedidos_dummy.py
# Resultado: PASSED (ver test_results/resultado_test_flujo_gestion_obras_pedidos_dummy.txt)
# ---

# ---
# [10/06/2025] Política para tests unitarios y de integración en stock.app
#
# 1. Todos los tests unitarios deben ser auto-contenidos: NO deben requerir base de datos real ni variables de entorno críticas.
#    - Usar dummies y mocks para modelos, controladores y vistas.
#    - No importar controladores/modelos reales si requieren conexión a base de datos o config externa.
#    - Si se requiere integración real, separar esos tests en archivos específicos y documentar la dependencia.
#
# 2. Tests de integración real (con base de datos/config real):
#    - Deben estar en archivos claramente marcados y documentados.
#    - Requieren archivo .env y entorno configurado. No deben ejecutarse por defecto en CI/local.
#    - Documentar en el README y en los propios tests cómo habilitarlos y qué variables requieren.
#    - Ejemplo actualizado: tests/obras/test_obras_controller_integracion.py (ver instrucciones en el archivo).
#    - ADVERTENCIA: Estos tests pueden modificar datos reales. Usar solo para QA manual y validar con backup previo.
#
# 3. Corrección de tests existentes:
#    - Refactorizar tests unitarios para usar solo dummies/mocks y evitar imports de módulos que requieran DB/config.
#    - Mantener la cobertura de lógica y feedback visual/auditoría usando clases dummy.
#    - Los tests de accesibilidad/UI pueden usar PyQt y vistas reales, pero deben mockear la lógica de negocio.
#    - Documentar en cada archivo de test si es auto-contenido o requiere entorno real.
#
# 4. Ejemplo de test auto-contenido:
#    - Ver tests/test_flujo_gestion_obras_pedidos_dummy.py
#    - Ver tests/usuarios/test_usuarios.py
#
# 5. Ejemplo de test de integración real:
#    - tests/obras/test_obras_controller_integracion.py (requiere entorno y DB, instrucciones en el archivo)
#
# 6. Próximos pasos:
#    - Refactorizar todos los tests unitarios para cumplir esta política.
#    - Marcar y documentar los tests de integración real.
#    - Actualizar README y checklists.
# ---
# Checklist de trazabilidad y feedback visual por módulo (actualizado al 10/06/2025)
#
# Para cada módulo (Obras, Inventario, Vidrios, Herrajes, Contabilidad, Logística):
# - [ ] Todos los mensajes de feedback visual deben ser claros, accesibles y contextualizados (éxito, error, advertencia, info).
# - [ ] Cada acción relevante debe mostrar feedback inmediato en la UI (colores, iconos, tooltips, mensajes).
# - [ ] Los tooltips deben estar presentes en todos los botones y campos clave, explicando la acción o validación.
# - [ ] Accesibilidad: todos los elementos interactivos deben tener accessibleName y orden de tabulación correcto.
# - [ ] Los errores y estados relevantes deben reflejarse tanto visualmente como en logs/auditoría.
# - [ ] Validar que los logs de auditoría incluyan usuario, módulo, acción, detalles y estado.
# - [ ] QA: Verificar manualmente y con tests automáticos que cada edge case y error se refleja en la UI y en los logs.
# - [ ] Documentar cualquier excepción, bug o mejora detectada tras cada iteración en este archivo y en los logs de test.
#
# Ejemplo de validación visual:
# - Al reservar material sin stock suficiente, debe aparecer mensaje de error visible, tooltip explicativo y registro en auditoría.
# - Al completar una acción exitosa, debe mostrarse mensaje de éxito con icono y registro en logs.
#
# Referencia cruzada:
# - Ver detalles y ejemplos en docs/checklists/checklist_mejoras_uiux_por_modulo.md y docs/checklists/checklist_formularios_botones_ui.txt
# - Actualizar estos checklists tras cada mejora o bugfix visual.
# ---
# Instrucciones para actualización y mantenimiento de checklists (actualizado al 10/06/2025)
#
# Tras cada mejora, bugfix o refactor:
# - [ ] Revisar y marcar los ítems correspondientes en los archivos de checklists por módulo (ver docs/checklists/).
# - [ ] Documentar cualquier excepción, cambio de estándar o decisión técnica relevante en este archivo y en el checklist del módulo afectado.
# - [ ] Si se detecta un bug o edge case no cubierto, agregarlo al checklist y marcarlo como pendiente o en progreso.
# - [ ] QA: Validar manualmente y con tests automáticos que la mejora o fix se refleja en la UI, feedback y logs/auditoría.
# - [ ] Actualizar la fecha de última revisión en el encabezado del checklist correspondiente.
# - [ ] Si la mejora afecta a varios módulos, actualizar todos los checklists involucrados y dejar constancia en este archivo.
# - [ ] Mantener la trazabilidad de cambios y excepciones para auditoría y onboarding.
#
# Referencia cruzada:
# - Checklists visuales y funcionales: docs/checklists/checklist_mejoras_uiux_por_modulo.md, docs/checklists/checklist_formularios_botones_ui.txt, docs/checklists/checklist_botones_accion.txt, etc.
# - Documentar excepciones y cambios de estándar también en docs/decisiones_main.md si corresponde.
# ---

## Checklist de configuración crítica y conexión a base de datos

- [x] Edición de IP, usuario, contraseña, base y timeout desde la UI (Configuración > Base de Datos).
- [x] Validación y prueba de conexión antes de guardar.
- [x] Guardado seguro en `config/privado/.env` (nunca en el código fuente).
- [x] Recarga dinámica: la app usa la nueva configuración sin reiniciar.
- [x] Registro de cambios en auditoría.
- [x] Solo usuarios administradores pueden modificar estos valores.
- [x] Advertencia sobre uso de IP: SQL Server debe aceptar conexiones remotas y el puerto debe estar abierto.

> Ver README y buenas_practicas_configuraciones_criticas.md para detalles y ejemplos.

---

## CHECKLIST DE VALIDACIÓN VISUAL Y FUNCIONAL (actualizado 10/06/2025)

1. Ir a Configuración > Base de Datos
   - Editar un campo (IP, usuario, etc) y guardar.
   - Verificar feedback visual inmediato (éxito/error), recarga dinámica y registro en auditoría.
   - Solo usuarios admin pueden editar.

2. Cargar una nueva obra
   - Completar campos obligatorios y guardar.
   - Verificar feedback visual y aparición en la tabla principal.

3. Cargar materiales, herrajes y vidrios
   - Asignar materiales y verificar generación automática de pedido.
   - Repetir con herrajes y vidrios. Verificar feedback y pedidos en módulos.

4. Integración con Contabilidad, Logística y Producción
   - Cambiar estado de la obra (ej: “en producción”, “entrega”).
   - Verificar que los módulos pueden operar sobre la obra y feedback visual.

5. Edge cases y robustez
   - Probar guardar configuración inválida y verificar feedback de error.
   - Probar alta/edición de obra con datos inválidos o duplicados.
   - Probar edición de configuración como usuario no admin (debe bloquear).

6. Auditoría y trazabilidad
   - Verificar en la sección de auditoría que todos los cambios y acciones quedan registrados.

> Ver README y docs/buenas_practicas_configuraciones_criticas.md para detalles y ejemplos.

---

## Test de integración: edición de fecha de entrega (Obras)

- **Test:** `test_editar_fecha_entrega_dialog_integration` en `tests/test_obras_controller.py`
- **Cobertura:**
  - Edición válida (feedback de éxito, refresco de tabla, registro en auditoría)
  - Edición inválida (fecha anterior a medición, feedback de error)
  - Obra inexistente (feedback de error)
  - Cancelación del diálogo (sin feedback)
- **Aislamiento:** No depende de base de datos real ni entorno externo. Usa dummies y mocks.
- **Cumple:** Checklist de feedback visual, edge cases, accesibilidad y registro en auditoría.

> Mantener este registro actualizado tras cada mejora o refactor del flujo de edición de fecha de entrega.

---

## Checklist y estándar: Personalización de columnas en tablas

- [x] Permitir al usuario mostrar/ocultar columnas desde menú contextual en el header de la tabla (Obras, Inventario, etc.).
- [x] Guardar la selección de columnas por usuario en un único archivo JSON por módulo (ej: `config_obras_columns.json`).
- [x] Restaurar automáticamente la configuración al iniciar la vista.
- [x] Feedback visual inmediato al cambiar visibilidad de columnas.
- [x] Test automatizado que valida mostrar/ocultar, persistencia y restauración (`tests/test_obras_view_columnas.py`).
- [x] Documentar la política y ejemplo en README.md y aquí.
- [ ] Replicar la lógica en todos los módulos con tablas configurables.

**Nota:** No se generan miles de archivos, la persistencia es eficiente y escalable.

---

## Dinámica y estándar: Cronograma visual (Gantt) de Obras

- Cada obra se visualiza como una barra en el cronograma (pestaña 2), desde la fecha de medición hasta la fecha de colocación.
- El color de la barra indica el estado actual de la obra:
  - Azul: Medición
  - Amarillo: En fabricación
  - Verde: Lista para colocar
  - Rojo: Demorada (si se venció la etapa y no se actualizó el estado)
- Los usuarios pueden actualizar el estado de la obra desde la UI. Al hacerlo, la barra cambia de color automáticamente.
- Si se supera la fecha límite de una etapa y no se actualizó el estado, el sistema solicita automáticamente un descargo al usuario responsable (motivo del atraso, justificación, etc.).
- Todos los descargos quedan registrados para estadísticas y auditoría.
- El flujo y la política de colores/estados están documentados en el README y aquí.

**Recomendación:** Mantener la lógica desacoplada para poder reutilizar el componente Gantt y la política de descargos en otros módulos si es necesario.

---

# ---
# SECCIÓN DE EXCEPCIONES VISUALES Y QSS
#
# Todas las excepciones visuales (por ejemplo, estilos embebidos justificados, casos donde no se puede aplicar QSS global, o widgets que requieren estilos particulares por limitaciones técnicas) deben documentarse aquí y en el archivo `docs/estandares_visuales.md`.
#
# Ejemplo de excepción:
# - El módulo Obras utiliza un QProgressBar embebido solo en operaciones largas, justificado en el propio código y en la documentación.
# - Si un test automático de estándares falla por líneas comentadas o ejemplos, se considera falso positivo y debe estar documentado aquí y en el docstring del archivo afectado.
#
# Instrucciones:
# - Cada vez que se detecte una excepción visual, agregar una breve descripción, el motivo y el archivo/línea afectada.
# - Si se elimina la excepción, actualizar esta sección y el archivo correspondiente.
#
# Ejemplo de registro:
# - [Obras/view.py] No requiere feedback de carga adicional porque los procesos son instantáneos o ya usan QProgressBar (ver línea 10 y docs/estandares_visuales.md).
#
# ---

## Mantenimiento y actualización de estándares y checklists

- Tras cada mejora, bugfix o refactor que afecte la UI/UX, accesibilidad o feedback visual, se debe:
  1. Actualizar este archivo y los checklists generales y por módulo (`docs/checklists/checklist_mejoras_ui_general.md`, `docs/checklists/checklist_mejoras_uiux_por_modulo.md`).
  2. Documentar cualquier excepción visual nueva o eliminada en la sección anterior.
  3. Extender los tests automáticos de integración y UI para cubrir los nuevos estándares o edge cases.
  4. Registrar el avance en la tabla de checklist por módulo y marcar los ítems correspondientes.
  5. Si se detecta un bug visual o de accesibilidad, documentar el hallazgo y la solución en este archivo y en los logs de test.

- Referencia rápida de checklists:
  - Checklist general de UI/UX: `docs/checklists/checklist_mejoras_ui_general.md`
  - Checklist por módulo: `docs/checklists/checklist_mejoras_uiux_por_modulo.md`
  - Checklist de botones/iconos: `docs/checklists/checklist_botones_iconos.txt`
  - Checklist de formularios y acciones: `docs/checklists/checklist_formularios_botones_ui.txt`

- Para detalles de estilos, colores, tipografías y layout, ver `docs/estandares_visuales.md`.
- Para feedback visual y mensajes, ver `docs/estandares_feedback.md`.
- Para logging y auditoría, ver `docs/estandares_logging.md` y `docs/estandares_auditoria.md`.

---
