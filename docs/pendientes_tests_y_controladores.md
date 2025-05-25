# Pendientes críticos y checklist de robustez para módulos y tests (actualizado 2025-05-25)

## REGLA CRÍTICA PARA CONTROLADORES Y VISTAS

- Nunca usar `.text()` directo sobre widgets. Siempre usar helpers robustos (`_get_text`, `_get_checked`).
- Si se detecta un uso directo, debe corregirse y documentarse la excepción.
- Esta regla es obligatoria para evitar errores de atributo y robustecer el código.

---

## PENDIENTES Y PROBLEMAS DETECTADOS (por módulo)

### 1. USUARIOS

- [ ] Validar robustez de login y feedback visual ante errores de clave, usuario o permisos.
- [ ] Validar que la función `crear_usuarios_iniciales` siempre asigne permisos completos a admin y permisos mínimos a prueba.
- [ ] Mejorar feedback visual y accesibilidad en login_view.
- [ ] Validar integración de permisos en el sidebar y main_window.
- [ ] Tests: robustecer tests de login, permisos y feedback visual.

### 2. CONFIGURACIÓN

- [ ] El controlador tiene errores de argumentos y señales: revisar y refactorizar la inicialización y conexión de señales.
- [ ] Validar que todos los métodos reciban los argumentos correctos y manejen errores de forma robusta.
- [ ] Mejorar feedback visual y mensajes de error en la vista.
- [ ] Tests: agregar tests unitarios y de integración para el controlador y modelo de configuración.

### Pendientes específicos del controller de Configuración

- [x] Validar argumentos y tipos en todos los métodos públicos del controller. (Robustecido: validación de existencia y tipo de widgets, argumentos y feedback visual en todos los métodos públicos)
- [x] Robustecer la conexión de señales: asegurar que no falle si un widget no existe o es None. (Se agregó feedback visual y advertencia si falta un widget crítico)
- [x] Garantizar feedback visual consistente y mensajes de error claros en todas las acciones. (Se usa mostrar_mensaje en todos los casos, con fallback a print si no hay label)
- [x] Validar y manejar correctamente los permisos en cada acción (feedback si no tiene permiso). (Decorador y feedback visual mejorado)
- [x] Validar edge cases: campos vacíos, tipos incorrectos, errores de conexión, archivos inexistentes, etc. (Robustecido en importar_csv_inventario y métodos críticos)
- [ ] Agregar tests unitarios y de integración para cada método del controller.
- [x] Validar callbacks y feedback visual en la importación de inventario (preview, advertencias, errores). (Callback robusto y feedback visual en todos los caminos)

**Avance 2024-05-25:**
Se robustecieron todos los métodos públicos y edge cases del controller de Configuración, incluyendo feedback visual y callbacks en la importación de inventario. Siguiente: agregar tests y avanzar con el módulo Obras.

### 3. INVENTARIO

- [ ] Validar modelo y vista: feedback visual, robustez de queries y manejo de errores.
- [ ] Integración con pedidos y obras: reflejar cambios en tiempo real.
- [ ] Tests: robustecer tests de integración y UI.

### 4. OBRAS

- [ ] Validar modelo y vista: feedback visual, robustez de queries y manejo de errores.
- [ ] Integración con inventario y vidrios.
- [ ] Tests: robustecer tests de integración y UI.

### Pendientes específicos del módulo Obras

- [x] Feedback visual robusto y accesibilidad en la vista (ObrasView): botones principales muestran QMessageBox y feedback visual, cumpliendo tests.
- [x] Cumplimiento de tests de botones (test_obras_view_buttons.py).
- [ ] Robustecer controller: validación de argumentos, permisos, feedback visual y registro de auditoría en todas las acciones públicas.
- [ ] Tests unitarios y de integración para controller y modelo.
- [ ] Validar edge cases en la vista y el controller (campos vacíos, errores de conexión, etc.).

**Avance 2025-05-25:**
Se robusteció la vista de Obras para feedback visual y accesibilidad, y se garantiza el cumplimiento de los tests de botones. Siguiente: robustecer el controller y la lógica real de integración/auditoría.

### 5. PEDIDOS

- [ ] Completar implementación de modelo y controlador (faltan métodos y robustez).
- [ ] Validar integración con inventario y obras.
- [ ] Tests: robustecer tests de integración y UI.

### 6. VIDRIOS

- [ ] Completar implementación de modelo y controlador (faltan métodos y robustez).
- [ ] Validar integración con obras.
- [ ] Tests: robustecer tests de integración y UI.

### 7. AUDITORÍA Y LOGS

- [ ] Validar que todas las acciones sensibles se registren correctamente.
- [ ] Mejorar feedback visual y trazabilidad de errores.
- [ ] Tests: robustecer tests de integración y cobertura de logs.

### 8. INTEGRACIÓN GENERAL Y FEEDBACK VISUAL

- [ ] Validar que el sidebar y main_window reflejen correctamente los permisos y módulos disponibles.
- [ ] Mejorar feedback visual y accesibilidad en todos los módulos.

### 9. SCRIPTS DE INSTALACIÓN Y DEPENDENCIAS

- [ ] Validar robustez de scripts y feedback de errores.
- [ ] Documentar advertencias y recomendaciones de seguridad.

### 10. TESTS DE INTEGRACIÓN Y UI

- [ ] Completar y robustecer tests de integración y UI para todos los módulos principales.
- [ ] Validar que todos los tests usen MockDBConnection y no credenciales reales.

---

## REGLA DE ROBUSTEZ PARA WIDGETS EN CONTROLADORES

- [x] Nunca usar `.text()` directo sobre widgets. Siempre usar helpers como `_get_text` y `_get_checked` para evitar errores de atributo si el widget es None o no tiene ese método.
- [x] Si se detecta un error de atributo por uso directo de `.text()`, refactorizar de inmediato y dejarlo documentado aquí.
- [x] Validar siempre la existencia del widget antes de operar sobre él.

**Actualización 2025-05-25:**
Se corrigió el uso de `.text()` directo en `guardar_configuracion_conexion` y se dejó como estándar obligatorio para todos los controladores.

## NOTAS GENERALES

- Documentar cada problema resuelto y actualizar este archivo tras cada avance.
- Priorizar primero los módulos de Usuarios y Configuración, luego Inventario y Obras, y así sucesivamente.
- Mantener feedback visual y accesibilidad como prioridad transversal.
- Validar que los tests cubran casos límite y errores frecuentes.

---

> Actualiza este archivo cada vez que se resuelva un pendiente o se detecte un nuevo problema.
