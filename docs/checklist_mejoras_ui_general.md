# Checklist de Mejoras Generales de UI/UX

Fecha: 08/06/2025

Este checklist resume puntos de mejora transversales a todos los módulos de la aplicación.
El objetivo es unificar la apariencia y la interacción con el usuario.

## 1. Tablas
- [ ] Verificar que **todas** las tablas usen el mismo QSS de cabecera
  - Fondo `#f8fafc`, radio `4px`, fuente `10px`, sin negrita.
  - Altura máxima de filas `25px`, colores de selección `#e3f6fd`.
- [ ] Revisar que la fuente y tamaño de celdas sea consistente (12 px o menor).
- [ ] Confirmar que las columnas importantes estén alineadas (número a la derecha, texto a la izquierda).

## 2. Botones
- [ ] Todos los botones principales y secundarios deben utilizar el helper `estilizar_boton_icono`.
- [ ] Los botones de acción deben ubicarse en la misma zona de cada vista (por ejemplo, barra superior o panel lateral).
- [ ] Todos los botones visibles deben tener un ícono SVG/PNG definido en `resources/icons` y documentarse en `checklist_botones_iconos.txt`.
- [ ] Añadir `setAccessibleName` y `setToolTip` descriptivos.

## 3. Layout y modales
- [ ] Mantener márgenes y paddings mínimos de **20 px** vertical y **24 px** horizontal.
- [ ] Bordes redondeados de diálogos entre **8 px** y **12 px**.
- [ ] Deshabilitar botones mientras se realiza una acción (evita doble clic) y mostrar feedback de carga.

## 4. Feedback visual
- [ ] Centralizar todos los mensajes en `label_feedback` o componentes equivalentes.
- [ ] Colores estándar: info `#e3f6fd`, éxito `#d1f7e7`, error `#fee2e2`, advertencia `#fef9c3`.
- [ ] Permitir cerrar manualmente banners o mensajes largos.

## 5. Accesibilidad
- [ ] Revisar el orden de tabulación en formularios.
- [ ] Incluir atajos de teclado en acciones frecuentes (por ejemplo, `Ctrl+E` para exportar).
- [ ] Comprobar que lectores de pantalla anuncien correctamente botones e inputs.

## 6. Documentación y tests
- [ ] Actualizar este archivo al implementar cada mejora.
- [ ] Extender los tests de UI para cubrir nuevas verificaciones de estilo e íconos.

