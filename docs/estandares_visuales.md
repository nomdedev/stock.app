# Estándares visuales de la app

## Paleta de colores
- Fondo general: #fff9f3 (crema pastel muy claro)
- Azul pastel principal:rgb(79, 129, 238) (texto, íconos, botones principales)
- Celeste pastel: #e3f6fd (fondos de botones, headers, pestañas activas)
- Gris pastel: #e3e3e3 (bordes, líneas de tabla)
- Verde pastel: #d1f7e7 (éxito)
- Rojo pastel: #ffe5e5 (errores)
- Lila pastel: #f3eaff (hover)

## Tipografía y tamaños
- Fuente: Segoe UI, Roboto o similar sans-serif
- Tamaño base: 11px para secundarios, 12px para tablas y botones, 13-14px para títulos
- Peso: 500-600 para títulos y botones, 400-500 para textos normales

## Botones
- Solo ícono, sin texto visible (excepto justificación documentada)
- Bordes redondeados: 8px
- Sombra sutil
- Tamaño mínimo: 32x32px
- Usar helper `estilizar_boton_icono`

## Tablas
- Fondo: #fff9f3
- Headers: #e3f6fd, texto azul pastel, bordes redondeados 8px
- Celdas: altura máxima 25px
- Fuente: 12px o menor

## Layouts y diálogos
- Padding mínimo: 20px vertical, 24px horizontal
- Márgenes entre elementos: mínimo 16px
- Bordes redondeados: 8-12px

## Sidebar
- Fondo blanco
- Botones: borde gris pastel, activo azul pastel, fuente 12px

## QTabWidget
- Fondo crema, pestañas celeste pastel, activa con borde azul pastel
- Padding horizontal: 24px, vertical: 20px

## Prohibido
- Fondos oscuros, negro, gris oscuro
- Tamaños de fuente mayores a 14px en tablas/botones
- Sobrescribir estilos globales sin justificación

## Ejemplo de helper para botón

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
