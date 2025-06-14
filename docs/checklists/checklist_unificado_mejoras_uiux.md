# Checklist Unificado de Mejoras UI/UX, Accesibilidad y Feedback

## Generales (aplican a todos los módulos)
- [ ] Unificar QSS de cabecera de tablas: fondo `#f8fafc`, radio `4px`, fuente `10px`, altura filas `25px`, selección `#e3f6fd`.
- [ ] Consistencia en fuente y tamaño de celdas (≤12 px).
- [ ] Alinear columnas importantes (números a la derecha, texto a la izquierda).
- [ ] Todos los botones principales/secundarios usan `estilizar_boton_icono`.
- [ ] Botones ubicados en la misma zona de cada vista.
- [ ] Todos los botones visibles con ícono SVG/PNG en `resources/icons` y documentados.
- [ ] Añadir `setAccessibleName` y `setToolTip` descriptivos a todos los botones.
- [ ] Bordes redondeados de diálogos entre 8 px y 12 px.
- [ ] Deshabilitar botones durante acciones y mostrar feedback de carga.
- [ ] Centralizar mensajes en `label_feedback` o equivalente.
- [ ] Colores estándar de feedback: info `#e3f6fd`, éxito `#d1f7e7`, error `#fee2e2`, advertencia `#fef9c3`.
- [ ] Permitir cerrar manualmente banners/mensajes largos.
- [ ] Revisar orden de tabulación en formularios.
- [ ] Incluir atajos de teclado en acciones frecuentes (ej: `Ctrl+E` para exportar).
- [ ] Comprobar que lectores de pantalla anuncien correctamente botones e inputs.
- [ ] Extender tests de UI para cubrir verificaciones de estilo, íconos y accesibilidad.

---

## Por módulo (pendientes y mejoras específicas)

### Obras
- [ ] Simplificar filtros de búsqueda y permitir guardar filtros frecuentes.
- [ ] Incluir paginación en la tabla de registros.
- [ ] Mostrar resumen superior con totales (acciones por usuario/módulo).
- [ ] Atajos de teclado para exportar (`Ctrl+E`) y cerrar (`Esc`).
- [ ] Mostrar estado de pedidos de todos los módulos (vidrios, inventario, herrajes).

### Vidrios
- [ ] Confirmar unificación de layout, QSS y feedback visual.

### Compras
- [ ] Revisar que todos los botones usen `estilizar_boton_icono`.
- [ ] Búsqueda rápida de proveedores al crear pedido.
- [ ] Unificar diálogo de “Cargar presupuesto” (bordes 8–12 px).
- [ ] Documentar íconos faltantes.

### Pedidos
- [ ] Revisar sombra y tooltips de botones.
- [ ] Revisar paddings y bordes.

### Logística
- [ ] Revisar accesibilidad de tabs (tabulación y nombres accesibles).
- [ ] Agregar indicadores visuales de progreso de envío.
- [ ] Documentar excepciones de estilo.

### Producción
- [ ] Revisar paddings, sombra y tooltips de botones.

### Usuarios
- [ ] Revisar sombra, tooltips y paddings de botones.
- [ ] Confirmar setObjectName en títulos de módulo.

### Inventario
- [ ] Verificar headers de tablas según estándar.
- [ ] Mejorar feedback ante error de conexión a base de datos.
- [ ] Incorporar buscador global de items.
- [ ] Permitir personalizar columnas visibles desde la UI.

### Herrajes
- [ ] Completar checklist de herrajes (filtros avanzados, historial de cambios, notificaciones).
- [ ] Validar stock en tiempo real en el modal de pedido.
- [ ] Optimizar tabulación y atajos de teclado.
- [ ] Filtros por rango de fechas y tipo de herraje/stock bajo.
- [ ] Guardar filtros usados recientemente.
- [ ] Autocompletar código de herraje y mostrar imagen si está disponible.
- [ ] Exportar solo pedidos seleccionados y personalizar columnas a exportar.
- [ ] Alternar entre vista compacta y detallada de la tabla.
- [ ] Ver historial de cambios y auditoría desde la vista de pedidos.
- [ ] Notificación visual/sonora al cambiar estado de pedido.

### Mantenimiento
- [ ] Centralizar mensajes de error en banner reutilizable.
- [ ] Confirmar tooltips y `accessibleName` en botones.
- [ ] Añadir filtros por fecha y estado.

### Configuración
- [ ] Validación visual al probar conexión de base de datos.
- [ ] Guardar configuración de tema y recargar vista al aplicar cambios.
- [ ] Mensajes de éxito/error en `label_feedback`.

### Contabilidad
- [ ] Filtros por fecha y obra.
- [ ] Banner de feedback al registrar pagos.
- [ ] Mejorar legibilidad de tabla de facturas (alineación de montos).

### Notificaciones
- [ ] (Completar checklist específico si existe).

---

## Integración y lógica cruzada
- [ ] Unificar lógica de pedidos por obra en Inventario y Herrajes, y exponer estado.
- [ ] Impedir pedidos a obras inexistentes desde cualquier módulo (validar contra Obras).
- [ ] Integrar Producción y Logística para habilitar fabricación/entrega solo si todos los pedidos están realizados y pagados.
- [ ] Registrar y actualizar pagos de pedidos en Contabilidad, y exponer estado de pago por pedido.
- [ ] Implementar tests automáticos de integración y feedback visual.
