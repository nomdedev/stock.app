# Estándares de logging y feedback visual

## Logging obligatorio
- Usar siempre el logger central (`core/logger.py`).
- Todos los errores, advertencias y eventos relevantes deben registrarse con contexto: módulo, función, usuario, acción, traceback.
- Formato: timestamp, nivel, módulo, función, usuario, mensaje.
- Los logs se guardan en `logs/app.log` y `logs/audit.log`.

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

Cualquier excepción debe estar documentada en el código y en este archivo.
