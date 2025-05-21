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

Cualquier excepción debe estar documentada en el código y en este archivo.
