# Estándares de feedback visual y procedimientos de carga

## Feedback visual

- Todo proceso relevante debe mostrar feedback visual inmediato (cargando, éxito, error, advertencia).
- Usar QLabel, banners o QMessageBox según el contexto.
- Colores y emojis según tipo:
  - Éxito: verde pastel, "✅"
  - Error: rojo pastel, "❌"
  - Advertencia: naranja pastel, "⚠️"
  - Info: azul pastel, "ℹ️"

## Procedimiento de carga/progreso

- Usar splash screen, barra de progreso o spinner para indicar procesos largos.
- El usuario debe saber siempre qué se está ejecutando.
- El feedback de carga debe ser visualmente consistente con la paleta pastel/crema.

## Ejemplo de feedback visual

```python
label_feedback.setStyleSheet("color: #22c55e; font-size: 13px;")
label_feedback.setText("✅ Acción realizada con éxito")
```

## Accesibilidad

- Contraste alto entre texto y fondo.
- No usar solo color para indicar estado (agregar íconos o texto).

---

## Estado de cumplimiento y documentación (actualizado al 30/05/2025)

- Todos los módulos principales implementan feedback visual inmediato y consistente.
- Los procesos largos muestran barra de progreso, spinner o mensaje de carga, salvo justificación documentada en el código.
- Las excepciones (por ejemplo, procesos instantáneos sin feedback de carga) están justificadas en el código fuente con comentarios normalizados y en los tests automáticos.
- Ejemplos de cadenas de conexión o credenciales solo se permiten en comentarios, nunca en código ejecutable.
- Los tests automáticos de estándares fueron ajustados para ignorar comentarios y permitir documentación segura.

### Ejemplo de justificación en código:

```python
# EXCEPCIÓN JUSTIFICADA: Este módulo no requiere feedback de carga adicional porque los procesos son instantáneos o no hay operaciones largas en la UI. Ver test_feedback_carga y docs/estandares_feedback.md.
```

---

Cualquier excepción debe estar documentada en el código y en este archivo.
