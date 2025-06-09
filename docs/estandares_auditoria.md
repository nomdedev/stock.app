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

## Transacciones robustas: uso y justificación

Para garantizar la integridad de los datos y la trazabilidad de las operaciones críticas, se implementó un context manager de transacciones y métodos explícitos (`begin_transaction`, `commit`, `rollback`) en la clase `BaseDatabaseConnection`.

### Justificación técnica
- Permite manejar operaciones atómicas y seguras, evitando inconsistencias ante errores o caídas.
- Soporta timeout y reintentos configurables con backoff exponencial, lo que mejora la robustez ante fallos temporales de la base de datos.
- El manejo explícito de autocommit previene errores comunes en entornos multiusuario o con conexiones compartidas.
- El uso de logs en cada intento y en los eventos de commit/rollback facilita la auditoría y el diagnóstico de problemas.

### Ejemplo de uso del context manager

```python
from core.database import db

with db.transaction(timeout=10, retries=3):
    # Operaciones atómicas
    db.ejecutar("INSERT INTO ...")
    db.ejecutar("UPDATE ...")
# Si ocurre una excepción, se hace rollback automáticamente
```

### Ejemplo de uso manual de begin/commit/rollback

```python
db.begin_transaction(timeout=10, retries=3)
try:
    db.ejecutar("DELETE FROM ...")
    db.commit()
except Exception as e:
    db.rollback()
    raise
```

### Buenas prácticas
- Usar siempre el context manager para operaciones múltiples o críticas.
- Evitar dejar transacciones abiertas; preferir bloques `with` para manejo automático.
- Registrar en logs cualquier excepción o rollback para trazabilidad.

### Beneficios para auditoría
- Cada intento de conexión y cada evento de commit/rollback queda registrado con correlation_id, facilitando la reconstrucción de flujos y la detección de anomalías.
- Permite justificar ante auditorías externas la robustez y trazabilidad de las operaciones sobre la base de datos.

Cualquier excepción debe estar documentada en el código y en este archivo.
