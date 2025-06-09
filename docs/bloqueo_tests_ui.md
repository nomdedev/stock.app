# BLOQUEO DETECTADO EN TESTS AUTOMÁTICOS DE UI (PyQt)

## Resumen del problema
- Se implementaron tests automáticos de UI para InventarioView en `tests/test_inventario_ui.py` siguiendo el checklist y los parámetros robustos documentados.
- Los tests no son detectados ni ejecutados por `unittest` ("NO TESTS RAN"), incluso tras agregar un test dummy.
- Se descarta error de sintaxis, de nombres de métodos o de herencia, ya que la clase y los métodos cumplen el estándar de unittest.
- El problema puede deberse a:
  - Entorno gráfico no disponible (PyQt requiere entorno gráfico, incluso para tests dummy si hay inicialización de widgets).
  - Restricciones del entorno de ejecución (Windows, PowerShell, o configuración de unittest).
  - Algún error silencioso en la inicialización de QApplication o en la importación de módulos de PyQt.

## Acciones realizadas
- Se corrigió y validó la documentación de parámetros de tests robustos en Markdown.
- Se implementaron y revisaron tests de UI para feedback visual, tooltips, headers, accesibilidad y progreso.
- Se agregó un test dummy para descartar problemas de unittest.
- Se intentó ejecutar los tests con diferentes comandos y patrones, sin éxito.

## Próximos pasos sugeridos
- Probar la ejecución de los tests en un entorno con soporte gráfico real (no headless).
- Alternativamente, usar `pytest-qt` o una solución como `xvfb` (en Linux) para simular un entorno gráfico.
- Documentar este bloqueo en el checklist y en la documentación del proyecto.
- Si se requiere cobertura de UI en CI/CD, considerar migrar los tests de UI a un framework especializado o a un entorno Docker con soporte gráfico.

## Documentación de la excepción
- Este bloqueo y su diagnóstico quedan documentados en este archivo y en el checklist de cosas por hacer.
- Se recomienda revisar la configuración del entorno antes de dar por finalizada la cobertura de tests de UI.

---

Fecha: 2025-05-22
Responsable: GitHub Copilot
