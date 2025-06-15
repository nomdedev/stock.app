# Checklist Unificado de Mejoras UI/UX, Accesibilidad y Feedback

## Generales (aplican a todos los módulos)
- [x] Unificar QSS de cabecera de tablas: fondo `#f8fafc`, radio `4px`, fuente `10px`, altura filas `25px`, selección `#e3f6fd`.
- [x] Consistencia en fuente y tamaño de celdas (**estándar: 12 px** en todas las tablas principales).
- [x] Alinear columnas importantes (números a la derecha, texto a la izquierda).
- [x] Todos los botones principales/secundarios usan `estilizar_boton_icono`.
- [x] Botones ubicados en la misma zona de cada vista.
- [x] Todos los botones visibles con ícono SVG/PNG en `resources/icons` y documentados.
- [x] Añadir `setAccessibleName` y `setToolTip` descriptivos a todos los botones.
- [x] Bordes redondeados de diálogos entre 8 px y 12 px.
- [x] Deshabilitar botones durante acciones y mostrar feedback de carga.
- [x] Centralizar mensajes en `label_feedback` o equivalente.
- [x] Colores estándar de feedback: info `#e3f6fd`, éxito `#d1f7e7`, error `#fee2e2`, advertencia `#fef9c3`.
- [x] Permitir cerrar manualmente banners/mensajes largos.
- [x] Revisar orden de tabulación en formularios.
- [x] Incluir atajos de teclado en acciones frecuentes (ej: `Ctrl+E` para exportar).
- [x] Comprobar que lectores de pantalla anuncien correctamente botones e inputs.
- [x] Extender tests de UI para cubrir verificaciones de estilo, íconos y accesibilidad.

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
- [x] Centralizar mensajes de error en banner reutilizable.
- [x] Confirmar tooltips y `accessibleName` en botones.
- [x] Añadir filtros por fecha y estado.

### Configuración
- [x] Añadir validación visual al probar conexión de base de datos.
- [x] Guardar la configuración de tema y recargar la vista al aplicar cambios.
- [x] Incluir mensajes de éxito/error en `label_feedback`.

### Contabilidad
- [x] Incorporar filtros por fecha y por obra.
- [x] Implementar banner de feedback al registrar pagos.
- [x] Mejorar la legibilidad de la tabla de facturas (alineación de montos a la derecha).

### Notificaciones
- [x] Unificación visual y accesibilidad en botones principales.
- [x] Feedback visual centralizado y tabla accesible.

---

## Integración y lógica cruzada
- [ ] Unificar lógica de pedidos por obra en Inventario y Herrajes, y exponer estado.
- [ ] Impedir pedidos a obras inexistentes desde cualquier módulo (validar contra Obras).
- [ ] Integrar Producción y Logística para habilitar fabricación/entrega solo si todos los pedidos están realizados y pagados.
- [ ] Registrar y actualizar pagos de pedidos en Contabilidad, y exponer estado de pago por pedido.
- [ ] Implementar tests automáticos de integración y feedback visual.
