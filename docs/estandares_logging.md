# Estándares de logging y feedback visual

## Logging obligatorio

- Usar siempre el logger central (`core/logger.py`).
- Todos los errores, advertencias y eventos relevantes deben registrarse con contexto: módulo, función, usuario, acción, traceback.
- Formato: timestamp, nivel, módulo, función, usuario, mensaje.
- Los logs se guardan en `logs/app.log` y `logs/audit.log`.

## Formato y rotación de logs (JSON y texto)

El sistema de logging genera dos tipos de logs:
- **Texto legible:** en `logs/app.log` (rotativo, 5MB, 3 backups)
- **JSON estructurado:** en `logs/app_json.log` (rotativo, 5MB, 3 backups)
- **Auditoría:** en `logs/audit.log` (rotativo, 2MB, 2 backups)

Cada entrada JSON incluye:
- `timestamp`: fecha y hora
- `level`: nivel de log
- `message`: mensaje
- `correlation_id`: identificador único de la operación
- `module`, `funcName`, `lineno`: contexto de ejecución
- `exception`: (opcional) traza de error

**Convención:** Usa siempre el logger centralizado (`core/logger.py`). Si necesitas correlacionar logs de una operación, pasa un `correlation_id` único.

## Decoradores y registro de eventos

- Usar decoradores de auditoría en controladores para registrar acciones y errores.
- Ejemplo:

```python
@permiso_auditoria_modulo('accion')
def funcion():
    ...
```

## Feedback visual

- Todo error crítico debe mostrarse al usuario con `QMessageBox` o banner visual.
- Mensajes de éxito, advertencia e info: usar QLabel estilizado o QMessageBox.
- El feedback debe ser inmediato y claro, con color y/o ícono según tipo.

## Ejemplo de feedback visual

```python
label_feedback.setStyleSheet("color: #ef4444; font-weight: bold;")
label_feedback.setText("❌ Error al guardar")
QMessageBox.critical(self, "Error", "Ocurrió un error grave")
```

## Trazabilidad de errores

- Todo error debe poder rastrearse desde la terminal/log hasta el módulo y acción.
- Documentar en el log el nombre del módulo, función y usuario.
- Ejemplo de log:

```
2025-05-21 12:34:56 - ERROR - inventario.controller - agregar_item - usuario: admin - Traceback: ...
```

## Prohibido

- Ocultar errores críticos solo en consola.
- No registrar advertencias o errores en logs.

---

## Estado de cumplimiento y documentación (actualizado al 30/05/2025)

- Todos los módulos principales usan el logger central y registran errores, advertencias y eventos relevantes con contexto completo.
- Las excepciones y errores críticos se muestran al usuario con feedback visual inmediato y quedan registrados en los logs.
- Ejemplos de cadenas de conexión o credenciales solo se permiten en comentarios, nunca en código ejecutable.
- Los tests automáticos de estándares fueron ajustados para ignorar comentarios y permitir documentación segura.
- Las justificaciones de excepciones visuales y de feedback están documentadas en el código y, si corresponde, en este archivo y en los tests.

### Ejemplo de justificación en código

```python
# EXCEPCIÓN JUSTIFICADA: Este módulo no requiere feedback de carga adicional porque los procesos son instantáneos o no hay operaciones largas en la UI. Ver test_feedback_carga y docs/estandares_logging.md.
```

---

Cualquier excepción debe estar documentada en el código y en este archivo.
