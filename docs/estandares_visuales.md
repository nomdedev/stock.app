# Estándares visuales de la app

## Paleta de colores
- Fondo general: #fff9f3 (crema pastel muy claro)
- Azul pastel principal: #2563eb (texto, íconos, botones principales)
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
