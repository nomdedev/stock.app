# Estándares de auditoría y registro de acciones

## Auditoría obligatoria

- Toda acción relevante (alta, edición, eliminación, exportación, login, etc.) debe quedar registrada en logs de auditoría.
- Usar decoradores de auditoría en los controladores para registrar automáticamente las acciones.
- El log de auditoría debe incluir: usuario, módulo, acción, detalles, estado (éxito/error), timestamp.

## Ejemplo de decorador

```python
@permiso_auditoria_modulo('accion')
def funcion():
    ...
```

## Ejemplo de registro manual

```python
self.auditoria_model.registrar_evento(usuario_id, "modulo", "accion", "detalle", ip)
```

## Prohibido

- Omitir el registro de acciones sensibles.
- No registrar el usuario o el detalle de la acción.

---

Cualquier excepción debe estar documentada en el código y en este archivo.
